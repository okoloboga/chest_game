import asyncio
import logging
import time

from environs import Env
from TonTools import *
from sqlalchemy import values

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
    return [env('BOT_TOKEN'), env('API'), env('CENTRAL_WALLET_MNEMONICS'), env('CENTRAL_WALLET')]

    
# Checking for correct export input
def check_address(address_and_value: str) -> list:
    
    result_list = address_and_value.split()
    logger.info(f'User want send {result_list[1]} TON to {result_list[0]}')
    logger.info("Could he do this? Let's se!...")
    
    # Connecting to TonCenterClient
    config = _load_config()
    client = TonCenterClient(key=config[1], testnet=False)
    logger.info('TonCenterClient started')
    
    wallet = Wallet(provider=client, address=result_list[0], version='v4r2')

    if wallet is not None and result_list[1].isdigit:
        return result_list
    raise ValueError


# Checking for TON value of Central Wallet
async def ton_value(wallet: str) -> int:

    logger.info(f'TON value of wallet {wallet}')

    # Connecting to TonCenterClient
    config = _load_config()
    client = TonCenterClient(key=config[1], testnet=False)
    logger.info('TonCenterClient started')

    wallet = Wallet(provider=client, address=config[3], version='v4r2')
    balance = await wallet.get_balance()
    
    logger.info(f'Wallet {wallet} have {balance / 1000000000}')

    return balance / 1000000000


# Export TON from game
async def export_ton(user_id: int,
                     amount: float,
                     destination_address: str
                     ) -> bool:
    
    logger.info(f'Exporting {amount} TON to {destination_address}')
    
    # Connecting to TonCenterClient
    config = _load_config()
    client = TonCenterClient(key=config[1], testnet=False)
    logger.info('TonCenterClient started')
    
    central_wallet = Wallet(provider=client, mnemonics=config[2].split(), version='v4r2')
    logger.info(f'Central wallet connected {central_wallet.address}')
    
    # Checking Balance of central wallet
    balance = await central_wallet.get_balance()
    logger.info(f'central_wallet balance is {balance} TON')

    if balance > amount:
        comment = f'export_{user_id}'
        
        logger.info(f'Prepared transaction from central_wallet\n \
                {central_wallet.address}\nto =>\n{destination_address}\n\
                by')
        logger.info(f'With comment: {comment}')
        
        await central_wallet.transfer_ton(destination_address=destination_address,
                                          amount=float(amount),
                                          message=comment
                                          ) 
        logger.info(f'TON export complete')
        
        # Checking for successful
        transactions = await central_wallet.get_transactions(limit=10)
        await asyncio.sleep(5)

        for transaction in transactions:
            logger.info(f'{transaction.to_dict_user_friendly()}')
            if transaction.to_dict_user_friendly()['comment'] == comment:
                return True
        else:
            return False
    else: 
        return False


# Check import transaction
async def import_ton_check(user_id: int) -> dict | str:
    logger.info(f'Importing by {user_id}')
    result: dict = {} # Put result of successful transaction here

    # Connecting to TonCenterClient
    config = _load_config()
    client = TonCenterClient(key=config[1], testnet=False)
    logger.info('TonCenterClient started')
    
    wallet = Wallet(provider=client, address=config[3], version='v4r2')
    logger.info(f'Central wallet addres {wallet.address}')
    transaction = await wallet.get_transactions(limit=10)
    
    for t in transaction:
        
        logger.info(f'{t.to_dict_user_friendly()}')
        comment_raw = t.to_dict_user_friendly()['comment']
        comment = ''
        for i in comment_raw:
            if i.isdigit():
                comment = comment + i
        try:
            logger.info(f'comment: {comment}, user_id: {user_id}')
            if int(comment) == int(user_id):
                logger.info(f'Is comment == user_id? {int(comment) == int(user_id)}')
                result['value'] = float(t.to_dict_user_friendly()['value'])
                result['hash'] = str(t.to_dict_user_friendly()['hash'])
                result['comment'] = comment
             
                return result
            else:
                return 'no_transaction'
        except ValueError as ex:
            logger.info(f'{ex}')
    
