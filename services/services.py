import logging
import asyncio
import random
import services.db_services

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest
from base64 import b64decode
from aiogram_dialog import DialogManager
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import async_sessionmaker
from fluentogram import TranslatorRunner

from states import LobbySG, DemoSG


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
        '[%(asctime)s] - %(name)s - %(message)s')


# Countig value of comission by referrals count
async def coef_counter(user_id: int,
                       session: async_sessionmaker) -> dict:
    
    get_user = services.db_services.get_user
    coef = 1.55
    comission = 0.03
    user_data = await get_user(session, user_id)
    referrals = user_data.referrals

    if 1 <= referrals < 15:
        coef = 1.6
        comission = 0.1
    elif 15 <= referrals < 90:
        coef = 1.75
        comission = 0.2
    elif 90 <= referrals:
        coef = 1.9
        comission = 0.3
        
    return {'referrals': referrals,
            'coef': coef,
            'comission': comission}


# Checking for valid invite code to game
def is_private_room(invite_code: str) -> str:
    
    logger.info(f'is_private_room({invite_code})')
    invite_code_bytes = str.encode(invite_code)
    decoded = b64decode(invite_code_bytes)
    logger.info(f'Invite_code {invite_code} (decoded: {b64decode(invite_code_bytes)})')
    decoded_str = str(decoded, encoding='utf-8')

    if decoded_str[:3] == 'pr_' and (decoded_str[3:]).isdigit():
        return decoded_str
    raise ValueError


# Checking for valid promocode
def is_promocode(promocode: str) -> str:

    logger.info(f'is_promocode({promocode})')
    
    # For example
    if len(promocode) != 0:
        return promocode
    raise ValueError


# Making Deposit and go to wati for game, if success  
async def create_room_query(user_id: int,
                            dialog_manager: DialogManager):

    deposit = float(dialog_manager.current_context().dialog_data['deposit'])
    ton_value = float(dialog_manager.current_context().dialog_data['ton'])
    mode = dialog_manager.current_context().dialog_data['mode']

    logger.info(f'User {user_id} make Deposit {deposit}, in users account {ton_value} TON')
    
    if ton_value >= deposit:
        
        # Private of Public game
        if mode == 'public':

            # Create Public Room or Query
            logger.info(f'User {user_id} search for Public game with deposit {deposit} TON')

            if (await get_game(deposit)) == 'no_rooms':
                
                dialog_manager.current_context().dialog_data['find_create'] = 'create'
                r = aioredis.Redis(host='localhost', port=6379)
                
                # Creating empty room with Users Game for another players            
                room_1vs1 = {
                             'owner': user_id,
                             'guest': 'wait',
                             'deposit': deposit,
                }          
                # Put room to Redis. 
                await r.hmset('r_' + str(user_id), room_1vs1)
                
                # After writing Data to Redis
                await dialog_manager.switch_to(LobbySG.owner_public)
                   
            else:
                dialog_manager.current_context().dialog_data['find_create'] = 'find'
                await dialog_manager.switch_to(LobbySG.search)   
        else:
            logger.info(f'User {user_id} creating Private game with deposit {deposit}')
            
            # Create Private room
            r = aioredis.Redis(host='localhost', port=6379)
            
            # Creating empty room with Users Game for another players            
            room_private = {
                             'owner': user_id,
                             'guest': 'wait',
                             'deposit': deposit,
            }          
            # Put room to Redis.
            await r.hmset('pr_' + str(user_id), room_private)
            
            # After writing Data to Redis
            await dialog_manager.switch_to(LobbySG.owner_private)
    else:
        await dialog_manager.switch_to(LobbySG.not_enough_ton)
        
        
# Get require Game
async def get_game(deposit: str | int | float
                   ) -> dict | str:

    r = aioredis.Redis(host='localhost', port=6379)
    
    result: dict | str  # Success for suitable request

    logger.info(f'User deposit: {deposit}')

    # Search for required room
    for key in await r.keys(f'r_*'):
        logger.info(f'Searching... {key}')

        room = await r.hgetall(key)
        logger.info(f'Founded room: {room}')

        room_deposit = float(str(room[b'deposit'], encoding='utf-8'))
        room_guest = str(room[b'guest'], encoding='utf-8')
        logger.info(f'room_deposit: {room_deposit},\ndeposit: {deposit}\n\
                room_guest: {room_guest}')
            
        if room_deposit == float(deposit) and room_guest == 'wait':
            logger.info(f'Founded!')
            result = room
            break
        else:
            continue
    else:
        result = 'no_rooms' 
        
    return result  


# For Searcher - Write self to Room
async def write_as_guest(room: dict,
                         user_id: int):

    r = aioredis.Redis(host='localhost', port=6379)
   
    logger.info(f'User {user_id} write himself as Guest to room {room[b'owner']}\
        with Deposit {room[b'deposit']} in 1VS1 Game')
    
    room[b'guest'] = str(user_id)
    if await r.exists('pr_'+str(room[b'owner'], encoding='utf-8')) != 0:
        await r.hmset('pr_'+str(room[b'owner'], encoding='utf-8'), room)
    else:
        await r.hmset('r_'+str(room[b'owner'], encoding='utf-8'), room)
    
    logger.info(f'Should be writed... {room}')


# From Room to Game 1VS1 and get random Hidder
async def room_to_game(user_id: int,
                       owner: str) -> str:

    r = aioredis.Redis(host='localhost', port=6379)

    if await r.exists('r_'+str(user_id)) != 0:
        room = await r.hgetall('r_'+str(user_id))
        logger.info(f'public room {room} exists')
    else:
        room = await r.hgetall('pr_'+str(user_id))
        logger.info(f'private room {room} exists')
    logger.info(f'room_to_game({user_id}, {owner}), room: {room}')

    if len(room) > 0:
        logger.info(f'room is {room} with id {user_id}')

        # Chosing hidder for first turn
        chose_hidder = random.choice([room[b'owner'], room[b'guest']])
        logger.info(f"Chosing hidder... Owner: {room[b'owner']}, Guest: {room[b'guest']}\
                Hidder: {chose_hidder}")

        # Game Dictionary - all process save here
        game = {
                'owner': str(room[b'owner'], encoding='utf-8'),
                'guest': str(room[b'guest'], encoding='utf-8'),
                'deposit': str(room[b'deposit'], encoding='utf-8'),
                'hidder': str(chose_hidder, encoding='utf-8'),  # Player, witch hide prize. Select randomly
                'target': 'none'  # Chest with prize, chosen by Hidder
                }
        
        logger.info(f'Game dict: {game}')

        # Write Game to Redis Database, and delete Room
        await r.hmset('g_'+str(user_id), game)

        # Checking for writing game:
        just_writed_game = await r.hgetall('g_'+str(user_id))
        logger.info(f'Just writed game is {just_writed_game}')
        await r.delete('r_'+str(user_id))
        await r.delete('pr_'+str(user_id))
        
        await r.set(user_id, 'g_'+owner)       
        return 'owner'

    else:
        # Write flag for Guest for easy find
        await r.set(user_id, 'g_'+owner)
        logger.info(f'User {user_id} is guest')
        return 'guest'

    
# Game result processong
async def game_result(owner: int,
                      deposit: float,
                      winner_id: int,
                      loser_id: int) -> dict:

    r = aioredis.Redis(host='localhost', port=6379)
    await r.delete('g_'+str(owner))

    return {'game_deposit': deposit,
            'winner_id': winner_id,
            'loser_id': loser_id}
        
   
# Game timer - 1 minute for game
async def turn_timer(dialog_manager: DialogManager,
                     game_id: int,
                     loser_id: int,
                     game_end_keyboard: InlineKeyboardMarkup):

    await asyncio.sleep(60)
    r = aioredis.Redis(host='localhost', port=6379)
    game = await r.hgetall('g_'+str(game_id))

    if len(game) == 0:
        logger.info(f"g_{game_id} doesn't exists, well done!")
    
    else:
        game_result_writer = services.db_services.game_result_writer
        session: async_sessionmaker = dialog_manager.middleware_data.get('session')
        bot: Bot = dialog_manager.middleware_data.get('bot')
        i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')

        deposit = str(game[b'deposit'], encoding='utf-8')
        owner = str(game[b'owner'], encoding='utf-8')
        guest = str(game[b'guest'], encoding='utf-8')
        logger.info(f'Game ended by timer: {game}')
        logger.info(f'Owner: {owner}, Guest: {guest}, Loser: {loser_id}')

        winner_id = owner if int(loser_id) != int(owner) else guest

        # Send notification to Winner
        winner_msg = await bot.send_message(chat_id=winner_id, 
                                            text=i18n.game.youwin(deposit=deposit),
                                            reply_markup=game_end_keyboard(i18n))
        try:
            await bot.delete_messages(winner_id, [msg for msg in range(winner_msg.message_id - 1, winner_msg.message_id - 10, -1)])
        except TelegramBadRequest as ex:
            logger.info(f'{ex.message}')

        # Send notification to Loser
        loser_msg = await bot.send_message(chat_id=loser_id, 
                                           text=i18n.game.youlose(deposit=deposit),
                                           reply_markup=game_end_keyboard(i18n))
        try:
            await bot.delete_messages(loser_id, [msg for msg in range(loser_msg.message_id - 1, loser_msg.message_id - 10, -1)])
        except TelegramBadRequest as ex:
            logger.info(f'{ex.message}')
    
        await game_result_writer(session, 
                                 float(deposit), 
                                 int(winner_id), 
                                 int(loser_id))

        
# Imitation Bots Thinking
async def bot_thinking(dialog_manager: DialogManager,
                       user_id: int,
                       role: str,
                       demo_result_writer,
                       game_end_keyboard: InlineKeyboardMarkup,
                       game_chest_keyboard: InlineKeyboardMarkup):
    
    seconds = random.randint(2, 10)
    await asyncio.sleep(seconds)
    
    r = aioredis.Redis(host='localhost', port=6379)
    session = dialog_manager.middleware_data.get('session')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    demo = await r.hgetall('d_'+str(user_id))

    logger.info(f'Demo game is {demo}')

    mode = str(demo[b'mode'], encoding='utf-8')
    deposit = str(demo[b'deposit'], encoding='utf-8')

    if role == 'hidder':
                
        # Count Result
        if mode != 'demo':
            is0 = random.randint(0, 9)
            result = 'win' if is0 == 0 else 'lose'
            await demo_result_writer(session, deposit, user_id, result)
        else:
            is0 = random.randint(0, 1)
            result = 'win' if is0 == 0 else 'lose'
        
        if result == 'win':
            try:
                msg = await bot.send_message(chat_id=user_id,
                                             text=i18n.game.youwin(deposit=deposit),
                                             reply_markup=game_end_keyboard(i18n))
                await bot.delete_messages(user_id, [msg for msg in range(msg.message_id - 1, msg.message_id - 5, -1)])
            except TelegramBadRequest as ex:
                logger.info(f'{ex.message}')
        else:
            try:
                msg = await bot.send_message(chat_id=user_id,
                                             text=i18n.game.youlose(deposit=deposit),
                                             reply_markup=game_end_keyboard(i18n))
                await bot.delete_messages(user_id, [msg for msg in range(msg.message_id - 1, msg.message_id - 5, -1)])
            except TelegramBadRequest as ex:
                logger.info(f'{ex.message}')
        
    elif role == 'searcher':
        msg = await bot.send_message(chat_id=user_id, 
                                     text=i18n.game.searcher(),
                                     reply_markup=game_chest_keyboard(i18n))
        try:
            await bot.delete_messages(user_id, [msg for msg in range(msg.message_id - 1, msg.message_id - 5, -1)])
        except TelegramBadRequest as ex:
            logger.info(f'{ex.message}')



        

