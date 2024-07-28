import asyncio
import logging
import time

from environs import Env
from TonTools import *

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Getting hidden consts
def _load_config(path: str | None = None) -> list:
    env = Env()
    env.read_env(path)
    logger.info("Enviroment executed")
    return [env('BOT_TOKEN'), env('API'), env('API_TEST'), env('CENTRAL_WALLET_MNEMONICS'), env('CENTRAL_WALLET')]

    
# Checking for correct export input
def check_value_and_address(address_and_value: str) -> list:
    
    result_list = address_and_value.split()
    logger.info(f'User want send {result_list[1]} TON to {result_list[0]}')
    logger.info("Could he do this? Let's se!...")
    
    # Connecting to TonCenterClient TESTNET
    config = _load_config()
    client = TonCenterClient(key=config[1], testnet=True)
    logger.info('TonCenterClient started')
    
    wallet = Wallet(provider=client, address=result_list[0], version='v4r2')

    if wallet is not None and result_list[1].isdigit:
        if float(result_list[1]) >= 1:
            return result_list
        raise ValueError
    raise ValueError


# Checking for TON value of Central Wallet
async def ton_value(wallet: str) -> int:

    logger.info(f'TON value of wallet {wallet}')

    # Connecting to TonCenterClient TESTNET
    config = _load_config()
    client = TonCenterClient(key=config[1], testnet=True)
    logger.info('TonCenterClient started')

    wallet = Wallet(provider=client, address=config[4], version='v4r2')
    balance = await wallet.get_balance()
    
    logger.info(f'Wallet {wallet} have {balance / 1000000000}')

    return balance / 1000000000


# Export TON from game
async def export_ton(user_id: int,
                     amount: float,
                     destination_address: str
                     ) -> bool:
    
    logger.info(f'Exporting {amount} TON to {destination_address}')
    
    # Connecting to TonCenterClient TESTNET
    config = _load_config()
    client = TonCenterClient(key=config[1], testnet=True)
    logger.info('TonCenterClient started')
    
    central_wallet = Wallet(provider=client, mnemonics=config[3].split(), version='v4r2')
    
    logger.info(f'Central wallet connected')
    current_time = time.time()
    comment = f'export {user_id} at {current_time}'
    
    await central_wallet.transfer_ton(destination_address=destination_address,
                                      amount=amount,
                                      message=comment)
    logger.info('TON export complete')
    
    # Checking for successful
    transactions = await central_wallet.get_transactions(limit=10)
    
    for transaction in transactions:
        logger.info(f'{transaction.to_dict_user_friendly()}')
        if transaction.to_dict_user_friendly()['comment'] == comment:
            return True
            break
    else:
        return False
    

# Check import transaction
async def import_ton_check(user_id: int) -> dict | str:
    logger.info(f'Importing by {user_id}')
    result: dict = {} # Put result of successful transaction here

    # Connecting to TonCenterClient TESTNET
    config = _load_config()
    client = TonCenterClient(key=config[1], testnet=True)
    logger.info('TonCenterClient started')
    
    wallet = Wallet(client, config[4], version='v4r2')
    transaction = await wallet.get_transactions(limit=10)
    
    for t in transaction:
        
        logger.info(f'{transaction.to_dict_user_friendly()}')
        
        if transaction.to_dict_user_friendly()['comment'] == user_id:
            if float(transaction.to_dict_user_friendly()['value']) >= 0.5:

                result['value'] = float(transaction.to_dict_user_friendly()['value'])
                result['hash'] = int(transaction.to_dict_user_friendly()['hash'])
                result['comment'] = int(transaction.to_dict_user_friendly()['comment'])
             
                return result

            else: 
                return 'not_enough'
        else:
            return 'no_transaction'
    
