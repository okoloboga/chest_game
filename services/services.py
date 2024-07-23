import logging

from sqlalchemy.ext.asyncio import async_sessionmaker
from aiogram_dialog import DialogManager


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

# Making Deposit...    
async def deposit(user_id: int,
                  dialog_manager: DialogManager,
                  deposit: int | float):

    logger = logging.getLogger(__name__)

    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
            '[%(asctime)s] - %(name)s - %(message)s')

    ton_value = dialog_manager.current_context().dialog_manager['ton']
    logger.info(f'User {user_id} make Deposit {deposit}, in users account {ton_value} TON')
    
    if ton_value >= deposit:
        dialog_manager.current_context().dialog_data['deposit'] = deposit
        await dialog_manager.switch_to(LobbySG.wait_game)
    else:
        await dialog_manager.switch_to(LobbySG.not_enough_ton)