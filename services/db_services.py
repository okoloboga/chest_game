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
                'parent': 0,
                'ton': 0,
                'promo': 0
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
                       parent_id: int,
                       user_id: int):
    
    logger.info(f'Adding referral to User {parent_id}')
    
    parent_stmt = select(User).where(int(parent_id) == User.telegram_id)
    user_stmt = select(User).where(int(user_id) == User.telegram_id)
    
    async with session:
        parent = (await session.execute(parent_stmt)).scalar()
        user = (await session.execute(user_stmt)).scalar()
        
        parent.referrals = int(parent.referrals) + 1 
        user.parent = parent_id
        logger.info(f'Parent user referrals {parent.referrals}')
        logger.info(f'Added Parent {parent_id} to User {user_id}')
        
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

    coef_counter = services.services.coef_counter

    # Get Entities from database
    winner_statement = select(User).where(winner_id == User.telegram_id)
    loser_statement = select(User).where(loser_id == User.telegram_id)
    
    async with session:
        winner = (await session.execute(winner_statement)).scalar()
        loser = (await session.execute(loser_statement)).scalar()

        # Writing winner data
        winner_coef = (await coef_counter(winner_id, session))['coef']
        winner.games = winner.games + 1
        winner.wins = winner.wins + 1
        
        if winner.promo == 1:
            winner.wins_ton = winner.wins_ton + deposit 
            winner.ton = winner.ton + deposit
            winner.promo = 0
            flag = True
        else:
            winner.wins_ton = winner.wins_ton + (deposit * (winner_coef - 1)
            winner.ton = winner.ton + (deposit * (winner_coef - 1))
            flag = False

        # Writing loser data
        loser.games = loser.games + 1
        loser.lose = loser.lose + 1
        loser.lose_ton = loser.lose_ton + deposit
        loser.ton = loser.ton - deposit
        
        # Prepare vars to write referral parents %
        winner_parent_id = winner.parent
        loser_parent_id = loser.parent
        
        await session.commit()
    
    # If Winner haven't promocode - parents have 3% from deposit
    if flag is False:
        winner_parent_statement = select(User).where(int(winner_parent_id) == User.telegram_id)
        loser_parent_statement = select(User).where(int(loser_parent_id) == User.telegram_id)
        
        async with session:
            winner_parent = (await session.execute(winner_parent_statement)).scalar()
            loser_parent = (await session.execute(loser_parent_statement)).scalar()
            
            if winner_parent is not None:
                logger.info(f'winner_parent is {winner_parent.telegram_id}')
                winner_parent.ton = winner_parent.ton + (deposit * 0.03)
            if loser_parent is not None:
                logger.info(f'loser_parent is {loser_parent.telegram_id}')
                loser_parent.ton = loser_parent.ton + (deposit * 0.03)



















