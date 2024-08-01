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

    '''
    user = User(telegram_id = int(telegram_id),
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
    '''    

# Read User data from Database:w

async def get_user(session: AsyncSession,
                   telegram_id: int
                   ) -> User | None:

    logger.info(f'Getting User from Database with id {telegram_id}')
    
    
    user = await session.get(
            User, {'telegram_id': telegram_id}
            )
    '''
    async with sessionmaker() as session:
        user_stmt = select(User).where(int(telegram_id) == User.telegram_id)
        #result = await session.execute(user_stmt)
        result = await session.get(User, telegram_id)
        logger.info(f'User from database {result}')
    '''

    return user


# Add referrals to referral link Parent
async def add_referral(session: AsyncSession,
                       telegram_id: int):
    
    logger.info(f'Adding referral to User {telegram_id}')
    
    user_stmt = await session.get(
                User, {'telegram_id': telegram_id}
                )
    user = await session.execute(user_stmt)
    user_scalar = user.scalar()
    user_scalar.referrals = user_scalar + 1
    await session.commit()



# Try to get Transaction with same Hash
# If it new - add to databaase
async def process_transaction(session: AsyncSession,
                              transaction_hash: str,
                              transaction_value: str
                              ) -> bool:    
    result = await session.get(TransactionHashes, transaction_hash)
        
    if result is None:
        # Transaction is new - add to Database
        transaction = TransactionHashes(transaction_hash = transaction_hash,
                                        transaction_value = transaction_value)
        session.add(transaction)
        await session.commit()
        logger.info(f'New transaction for {transaction_value} TON added')
        return True
    
    else: 
        # Transaction is old
        logger.info(f'Transaction is old for {transaction_value} TON')
        return False


# Changing data of Users after game results
async def game_result_writer(session: AsyncSession,
                             deposit: float,
                             winner_id: int,
                             loser_id: int):

    comission_counter = services.services.comission_counter

    # Get Entities from database
    winner_statement = session(User).where(winner_id == User.telegram_id)
    loser_statement = session(User).where(loser_id == User.telegram_id)
    
    winner = (await session.execute(winner_statement)).scalar()
    loser = (await session.execute(loser_statement)).scalar()

    # Writing winner data
    winner_comission = ((await comission_counter(winner_id, session)) / 100) * deposit
    winner.games = winner.games + 1
    winner.wins = winner.wins + 1
    winner.wins_ton = winner.wins_ton + deposit + winner_comission
    winner.ton = winner.ton + deposit + winner_comission

    # Writing loser data
    loser_comission = ((await comission_counter(loser_id, session)) / 100) * deposit
    loser.games = loser.games + 1
    loser.lose = loser.lose + 1
    loser.lose_ton = loser.lose_ton + deposit + loser_comission
    loser.ton = loser.ton - deposit - loser_comission
    
    await session.commit()


