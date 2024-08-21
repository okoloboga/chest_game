import asyncio
import logging
import datetime
from database.tables import Variables
import services.services

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
from database import User, TransactionHashes, Variables


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')

# Create Variables at begin of Bot work session
async def create_variables(session: AsyncSession):

    variables = insert(Variables).values([
            {
                'name': 'promocodes',
                'value': 'PROMOCODE1 PROMOCODE2'
                },
            {
                'name': 'income',
                'value': '0'
                },
            {
                'name': 'outcome',
                'value': '0'
                },
            {
                'name': 'pure_income',
                'value': '0'
                },
            {
                'name': 'to_parents',
                'value': '0'
                },
            ])
    await session.execute(variables)
    await session.commit()


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
                'promo': 0,
                'used_promo': ''
                }
            )    
    await session.execute(user)
    await session.commit()
 

# Read User data from Database
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
            TransactionsHashes, {'transaction_hash': transaction_hash}
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
        income_stmt = select(Variables).where('income' == Variables.name)

        async with session:
            user = (await session.execute(user_stmt)).scalar()
            income = (await session.execute(income_stmt)).scalar()
            income.value = str(float(income.value) + float(transaction_value))
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

    logger.info(f'Decrement Users {telegram_id} TON value for {value}')

    user_stmt = select(User).where(telegram_id == User.telegram_id)
    outcome_stmt = select(Variables).where('outcome' == Variables.name)

    async with session:

        user = (await session.execute(user_stmt)).scalar()
        outcome = (await session.execute(outcome_stmt)).scalar()

        if float(user.ton) > float(value):
            outcome.value = str(float(outcome.value) + float(value))
            user.ton = float(user.ton) - float(value)
            await session.commit()
            return True
        else:
            return False


# Increment promocode to 1, not mode
async def increment_promo(session: AsyncSession,
                          telegram_id: int,
                          promocode: str):

    logger.info(f'Increment Users {telegram_id} promo')

    user_stmt = select(User).where(telegram_id == User.telegram_id)
    promo_stmt = select(Variables).where('promocodes' == Variables.name)

    async with session:
        
        actual_promo = (((await session.execute(promo_stmt)).scalar()).value).split()
        user = (await session.execute(user_stmt)).scalar()
        used_promo = (user.used_promo).split()

        logger.info(f'User promo status: {user.promo}, users used promo: {used_promo}, promo: {promocode}')
        logger.info(f'Actual promos: {actual_promo}')

        if (user.promo != 1) and (promocode not in used_promo) and (user.promo not in actual_promo):
            user.promo = 1
            user.used_promo = str(user.used_promo) + ' ' + str(promocode) 
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
    pure_income_statement = select(Variables).where('pure_income' == Variables.name)
    to_parent_statement = select(Variables).where('to_parent' == Variables.name)

    winner_coef = (await coef_counter(winner_id, session))['coef']
    winner_prize = winner_coef * deposit
    winner_parent_comission = 0
    loser_parent_comission = 0

    logger.info(f'Default game results: winner prize = {winner_prize}')

    async with session:
        winner = (await session.execute(winner_statement)).scalar()
        loser = (await session.execute(loser_statement)).scalar()

        # Writing winner data        
        winner.games = winner.games + 1
        winner.wins = winner.wins + 1
        
        if winner.promo == 1:
            winner_prize = deposit
            winner.promo = 0
            flag = True
        else:
            flag = False

        winner.wins_ton = winner.wins_ton + winner_prize
        winner.ton = winner.ton + winner_prize
        
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
        logger.info(f'Winner parent: {winner_parent_id}, Loser parent: {loser_parent_id}')

        winner_parent_statement = select(User).where(int(winner_parent_id) == User.telegram_id)
        loser_parent_statement = select(User).where(int(loser_parent_id) == User.telegram_id)
        
        # Is winner parent exists?
        if int(winner_parent_id) == 0:
            logger.info(f'Winner parent is 0')
            winner_parent_comission = 0.03 * deposit
        else:
            logger.info(f'Winner parent is not 0: {winner_parent_id}')
            winner_parent_comission = (await coef_counter(winner_parent_id, session))['comission'] * deposit

        # Is loser parent exists?
        if int(loser_parent_id) == 0:
            logger.info(f'Loser parent is 0')
            loser_parent_comission = 0.03 * deposit
        else:
            logger.info(f'Loser parent is not 0: {loser_parent_id}')
            loser_parent_comission = (await coef_counter(loser_parent_id, session))['comission'] * deposit

        async with session:
            winner_parent = (await session.execute(winner_parent_statement)).scalar()
            loser_parent = (await session.execute(loser_parent_statement)).scalar()
            
            if winner_parent is not None:
                logger.info(f'winner_parent is {winner_parent.telegram_id}')
                winner_parent.ton = winner_parent.ton + winner_parent_comission
            if loser_parent is not None:
                logger.info(f'loser_parent is {loser_parent.telegram_id}')
                loser_parent.ton = loser_parent.ton + loser_parent_comission
            
            await session.commit()


    # Write parent comission and pure income to Variables Database
    pure_income = (deposit * 2) - winner_prize - winner_parent_comission - loser_parent_comission
    
    logger.info(f'Game result after counting:\nwinner prize = {winner_prize}\n\
                winner parent comission = {winner_parent_comission}\n\
                loser parent comission = {loser_parent_comission}\n\
                pure income = {pure_income}')

    async with session: 
        pure_income_scalar = (await session.execute(pure_income_statement)).scalar()
        to_parent_scalar = (await session.execute(to_parent_statement)).scalar()

        pure_income_scalar.value = str(float(pure_income_scalar.value) + float(pure_income))
        to_parent_scalar.value = str(float(to_parent_scalar.value) + float(winner_parent_comission + loser_parent_comission))

        await session.commit()



















