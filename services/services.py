import logging
import pprint

from sqlalchemy.ext.asyncio import async_sessionmaker
from aiogram_dialog import DialogManager, StartMode
from redis import asyncio as aioredis


# Countig value of comission by referrals count
def comission_counter(user_id: int) -> dict:
    
    comission: int  # result comission by referrals
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

    ton_value = dialog_manager.current_context().dialog_manager['ton']
    logger.info(f'User {user_id} make Deposit {deposit}, in users account {ton_value} TON')
    
    if ton_value >= deposit:
        
        # Create Room or Query
        find_create = dialog_manager.current_context().dialog_data['find_create']
        deposit = dialog_manager.current_context().dialog_data['deposit']
        mode = dialog_manager.current_context().dialog_data['mode']
        logger.info(f'User {user_id} {find_create} {mode} Game for {deposit} TON')

        if find_create == 'create':   
            
            # Creating empty room with Users Game for another players            
            if mode == '1vs1':        
                room_1vs1 = {
                             'owner': user_id,
                             'guest': 'wait',
                             'deposit': deposit,
                }          
                # Put room to Redis. ro: room one (vs one)
                await r.hmset('ro_' + str(room_id), room_1vs1)
                
                # After writing Data to Redis
                await dialog_manager.start(LobbySG.owner_o)
                
                
            elif mode == 'super':
                room_super = {
                              'room_id': user_id,
                              'deposit': deposit, 
                }
                # Put room to Redis. rs: room super
                await r.hmset('rs_' + str(room_id), room_super)
                
                # After writing Data to Redis
                await dialog_manager.start(LobbySG.owner_s)
                
        elif find_create == 'find':
            
            await dialog_manager.start(LobbySG.search,
                                       data={'mode': mode,
                                             'deposit': deposit})   
    else:
        await dialog_manager.switch_to(LobbySG.not_enough_ton)
        
        
# Get require Game
async def get_game(query: dict
                   ) -> dict | str:
    
    r = aioredis.Redis(host='localhost', port=6379)
    
    result: dict | str  # Success for suitable request

    logger.info(f'User deposit: {query['deposit']}, Query Mode: {query['mode']}')
    
    mode_map = {'1vs1': 'o',
                'super': 's'}
    # 'o' or 's'
    mode = mode_map[query['mode']]
    
    # Search for required room
    for key in await r.keys(f'r{mode}_*'):
            
        room = await r.get(key)
        room_deposit = room[b'deposit']
        room_guest = room[b'guest']
            
        logger.info(f'Checking Room: {pprint.pprint(room)}')
            
        if room_deposit == query['deposit'] and room_guest == b'wait':
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
    
    logger.info(f'User {user_id} write himself as Guest to room {room[b'owner']}\
        with Deposit {room[b'deposit']} in 1VS1 Game')
    
    room = await r.hgetall('ro_'+str(room[b'owner'], encoding='utf-8'))
    room[b'guest'] = str(user_id)
    await r.hmset('ro_'+str(room[b'owner'], encoding='utf-8'), room)
    
    logger.info(f'Should be writed...')


# From Room to Game 1VS1
async def room_to_game(user_id: int):
    
    r = aioredis.Redis(host='localhost', port=6379)
    room = await r.hgetall('ro_'+str(user_id))
    
    
    
        
    
    