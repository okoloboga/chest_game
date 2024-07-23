import logging

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
            max_players: int  # Count of players for current mode          
            if mode == '1vs1':        
                room_1vs1 = {
                             'room_id': user_id,
                             'deposit': deposit,
                             'max_players': 2
                }          
                # Put room to Redis. ro: room one (vs one)
                await r.hmset('ro_' + str(room_id), room_1vs1)
                
            elif mode == 'super':
                room_super = {
                              'room_id': user_id,
                              'deposit': deposit, 
                              'current_players': 1
                }
                # Put room to Redis. rs: room super
                await r.hmset('rs_' + str(room_id), room_super)
        elif find_create == 'find':
            
            # Createing Query for Game by requirements
            if mode == '1vs1':
                query_1vs1 = {
                              'query_id': user_id,
                              'deposit': deposit,                
                }
                # Put query to Redis. qo: query one (vs one)
                await r.hmset('qo_' + str(room_id), query_1vs1)
            
            elif mode == 'super':
                query_super = {
                               'query_id': user_id,
                               'deposit': deposit,                
                }
                # Put query to Redis. qs: query super
                await r.hmset('qs_' + str(room_id), query_1vs1)
                
        # After writing dData to Redis
        await dialog_manager.start(GameSG.waiting,
                                   mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.switch_to(LobbySG.not_enough_ton)