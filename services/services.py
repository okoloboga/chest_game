import logging
import random
import services.db_services

from aiogram_dialog import DialogManager
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import async_sessionmaker

from states import LobbySG


# Countig value of comission by referrals count
async def comission_counter(user_id: int,
                      session: async_sessionmaker) -> dict:
    
    get_user = services.db_services.get_user
    comission: int | float  # result comission by referrals
    user_data = await get_user(session, user_id)
    referrals = user_data.referrals
    
    if referrals < 5:
        comission = 8
    elif 5 <= referrals < 15:
        comission = 7
    elif 15 <= referrals < 30:
        comission = 6
    elif 30 <= referrals < 50:
        comission = 5
    elif 50 <= referrals < 100:
        comission = 4.5
    elif referrals >= 100:
        comission = 3.5
        
    return {'referrals': referrals,
            'comission': comission}   

# Making Deposit and go to wati for game, if success  
async def create_room_query(user_id: int,
                            dialog_manager: DialogManager):

    logger = logging.getLogger(__name__)

    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
            '[%(asctime)s] - %(name)s - %(message)s')

    deposit = float(dialog_manager.current_context().dialog_data['deposit'])
    ton_value = float(dialog_manager.current_context().dialog_data['ton'])

    logger.info(f'User {user_id} make Deposit {deposit}, in users account {ton_value} TON')
    
    if ton_value >= deposit:
        
        # Create Room or Query
        logger.info(f'User {user_id} search for Game with deposit {deposit} TON')

        if (await get_game(deposit)) == 'no_rooms':
            
            dialog_manager.current_context().dialog_data['find_create'] = 'create'
            r = aioredis.Redis(host='localhost', port=6379)
            
            # Creating empty room with Users Game for another players            
            room_1vs1 = {
                         'owner': user_id,
                         'guest': 'wait',
                         'deposit': deposit,
            }          
            # Put room to Redis. ro: room one (vs one)
            await r.hmset('r_' + str(user_id), room_1vs1)
            
            # After writing Data to Redis
            await dialog_manager.switch_to(LobbySG.owner_o)
               
        else:
            dialog_manager.current_context().dialog_data['find_create'] = 'find'
            await dialog_manager.switch_to(LobbySG.search)   
    else:
        await dialog_manager.switch_to(LobbySG.not_enough_ton)
        
        
# Get require Game
async def get_game(deposit: str | int | float
                   ) -> dict | str:
    
    logger = logging.getLogger(__name__)

    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
            '[%(asctime)s] - %(name)s - %(message)s')


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
 
    logger = logging.getLogger(__name__)

    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
            '[%(asctime)s] - %(name)s - %(message)s')

    r = aioredis.Redis(host='localhost', port=6379)
   
    logger.info(f'User {user_id} write himself as Guest to room {room[b'owner']}\
        with Deposit {room[b'deposit']} in 1VS1 Game')
    
    room = await r.hgetall('r_'+str(room[b'owner'], encoding='utf-8'))
    room[b'guest'] = str(user_id)
    await r.hmset('r_'+str(room[b'owner'], encoding='utf-8'), room)
    
    logger.info(f'Should be writed... {room}')


# From Room to Game 1VS1 and get random Hidder
async def room_to_game(user_id: int,
                       owner: str) -> str:
    
    logger = logging.getLogger(__name__)

    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
            '[%(asctime)s] - %(name)s - %(message)s')


    r = aioredis.Redis(host='localhost', port=6379)

    room = await r.hgetall('r_'+str(user_id))
    
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
        
        await r.set(user_id, 'g_'+str(room[b'owner'], encoding='utf-8'))       
        return 'owner'

    else:

        # Write flag for Guest for easy find
        await r.set(user_id, 'g_'+owner)
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
        
    
    
