import asyncio
import logging

from sqlalchemy.ext.asyncio import async_sessionmaker
from database import User, TransactionHashes


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Add new User to database
async def create_user(sessionmaker: async_sessionmaker,
                      telegram_id: int,
                      first_name: str,
                      last_name: str | None = None
                      ):
    user = User(telegram_id = telegram_id,
                first_name = first_name,
                last_name = last_name,
                games = 0,
                wins = 0,
                lose = 0,
                wins_ton = 0,
                lose_ton = 0,
                referrals = 0,
                ton = 0
                )
    
    async with sessionmaker() as session:
        session.add(user)
        await session.commit()
        logger.info(f'New User created {user}')
        

# Read User data from Database
async def get_user(sessionmaker: async_sessionmaker,
                   telegram_id: int
                   ) -> User | None:
    async with sessionmaker() as session:
        result = await session.get(User, telegram_id)
    
    logger.info(f'User from database {result}')
    
    return result


# Try to get Transaction with same Hash
# If it new - add to databaase
async def process_transaction(sessionmaker: async_sessionmaker,
                              transaction_hash: str,
                              transaction_value: str
                              ) -> bool:
    async with sessionmaker() as session:
        result = await session.get(TransactionHashes, transaction_hash)
        
    if result is None:
        # Transaction is new - add to Database
        transaction = TransactionHashes(transaction_hash = transaction_hash,
                                        transaction_value = transaction_value)
        async with sessionmaker() as session:
            session.add(transaction)
            await session.commit()
            logger.info(f'New transaction for {transaction_value} TON added')
        return True
    
    else: 
        # Transaction is old
        logger.info(f'Transaction is old for {transaction_value} TON')
        return False
        



