import asyncio
import logging
import services.services

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
from database import User, TransactionHashes


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Add new User to database
async def create_user(session: AsyncSession,
                      telegram_id: int,
                      first_name: str,
                      last_name: str | None = None
                      ):

    user = insert(User).values(
            {
                'telegram_id': int(telegram_id),
                'first_name': first_name,
                'last_name': last_name,
                'games': 0,
                'wins': 0,
                'lose': 0,
                'wins_ton': 0,
                'lose_ton': 0,
                'referrals': 0,
                'ton': 0
                }
            )    
    await session.execute(user)
    await session.commit()
 

# Read User data from Database:w

async def get_user(session: AsyncSession,
                   telegram_id: int
                   ) -> User | None:

    logger.info(f'Getting User from Database with id {telegram_id}')
    
    
    user = await session.get(
            User, {'telegram_id': telegram_id}
            )

    return user


# Add referrals to referral link Parent
async def add_referral(session: AsyncSession,
                       telegram_id: int):
    
    logger.info(f'Adding referral to User {telegram_id}')
    
    user_stmt = select(User).where(int(telegram_id) == User.telegram_id)
    async with session:
        result = await session.execute(user_stmt)
        user = result.scalar()
        user.referrals = int(user.referrals) + 1 
        logger.info(f'Parent user referrals {user.referrals}')
        await session.commit()



# Try to get Transaction with same Hash
# If it new - add to databaase
async def process_transaction(session: AsyncSession,
                              telegram_id: int,
                              transaction_hash: str,
                              transaction_value: float
                              ) -> bool:

    logger.info(f'Getting info about transaction {transaction_hash} for {transaction_value} TON')
    
    transaction_stmt = await session.get(
            TransactionHashes, {'transaction_hash': transaction_hash}
            )
    
    logger.info(f'Transaction is {transaction_hash}')

    if transaction_stmt is None:
        
        new_transaction = insert(TransactionHashes).values(
                {
                    'transaction_hash': transaction_hash,
                    'transaction_value': transaction_value
                    }
                )
        await session.execute(new_transaction)
        
        # Update Users TON value in Database
        user_stmt = select(User).where(telegram_id == User.telegram_id)
        async with session:
            result = await session.execute(user_stmt)
            user = result.scalar()
            user.ton = float(user.ton) + float(transaction_value)
            await session.commit()
        await session.commit()

        logger.info(f'New transaction for {transaction_value} TON added')
        return True
    
    else:
        # Transaction is old
        logger.info(f'Transaction is old for {transaction_value} TON')
        return False


# Decrement TON value from User
async def decrement_ton(session: AsyncSession,
                        telegram_id: int,
                        value: float):

    logger.info(f'Decrement Users {telegram_id} TON value by {value}')

    user_stmt = select(User).where(telegram_id == User.telegram_id)
    async with session:

        result = await session.execute(user_stmt)
        user = result.scalar()

        if float(user.ton) > float(value):
            user.ton = float(user.ton) - float(value)
            await session.commit()

            return True
        else:
            return False


# Changing data of Users after game results
async def game_result_writer(session: AsyncSession,
                             deposit: float,
                             winner_id: int,
                             loser_id: int):

    comission_counter = services.services.comission_counter

    # Get Entities from database
    winner_statement = select(User).where(winner_id == User.telegram_id)
    loser_statement = select(User).where(loser_id == User.telegram_id)
    
    async with session:
        winner = (await session.execute(winner_statement)).scalar()
        loser = (await session.execute(loser_statement)).scalar()

        # Writing winner data
        winner_comission = ((await comission_counter(winner_id, session))['comission'] / 100) * deposit
        winner.games = winner.games + 1
        winner.wins = winner.wins + 1
        winner.wins_ton = winner.wins_ton + deposit - winner_comission
        winner.ton = winner.ton + deposit - winner_comission

        # Writing loser data
        loser_comission = ((await comission_counter(loser_id, session))['comission'] / 100) * deposit
        loser.games = loser.games + 1
        loser.lose = loser.lose + 1
        loser.lose_ton = loser.lose_ton + deposit + loser_comission
        loser.ton = loser.ton - deposit - loser_comission
        
        await session.commit()


