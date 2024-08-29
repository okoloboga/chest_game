import asyncio
import logging
import datetime
from database.tables import Variables
import services.services

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.dialects.postgresql import insert
from redis import asyncio as aioredis
from sqlalchemy import select
from database import User, TransactionHashes, Variables


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')

# Create Variables at begin of Bot work session
async def create_variables(engine):

    async with AsyncSession(engine) as session:
        session.add_all(
                [
                    Variables(name='promocodes', value='PROMOCODE1 PROMOCODE2'),
                    Variables(name='using_promocodes', value='0'),
                    Variables(name='income', value='0'),
                    Variables(name='outcome', value='0'),
                    Variables(name='pure_income', value='0'),
                    Variables(name='to_parents', value='0'),
                    Variables(name='total_games_players', value='0'),
                    Variables(name='total_games_bot', value='0'),
                    Variables(name='total_bets', value='0'),
                    Variables(name='bets', value='')
                ]
            )
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
                'last_game': '',
                'last_roles': '',
                'wins': 0,
                'lose': 0,
                'wins_ton': 0,
                'lose_ton': 0,
                'bot_income': 0,
                'referrals': 0,
                'parent': 0,
                'ton': 0,
                'promo': 0,
                'used_promo': '',
                'status': 'user',
                'banned': 'no'
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


# Getting all users id
async def get_users_id(session: AsyncSession) -> list:
    
    logger.info('getting all users_id')
    users_stms = select(User)
    result = []

    async with session:
        users_id = await session.execute(users_stms)
        for user in users_id:
            result.append(user[0].telegram_id)
    logger.info(f'result list after appendin all users {result}')

    return result


# Is user - admin?
async def is_admin(session: AsyncSession,
                   user_id: int) -> bool:

    logger.info(f'Getting user {user_id} status from database')
    status = (await get_user(session, user_id)).status
    return True if status == 'admin' else False


# Is user - banned?
async def is_banned(session: AsyncSession,
                    user_id: int) -> bool:

    logger.info(f'Getting user {user_id} banned status from database')
    status = (await get_user(session, user_id)).banned
    return True if status == 'banned' else False


# Get count of using promocodes
async def promocode_use_count(session: AsyncSession) -> int:
    
    logger.info('getting count of promocode uses')
    promocode_stms = select(Variables).where('using_promocodes' == Variables.name)

    async with session:
        return int(((await session.execute(promocode_stms)).scalar()).value)


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
                          promocode: str) -> str:

    logger.info(f'Increment Users {telegram_id} promo')

    user_stmt = select(User).where(telegram_id == User.telegram_id)
    promo_stmt = select(Variables).where('promocodes' == Variables.name)
    using_promo = select(Variables).where('using_promocodes' == Variables.name)

    async with session:
        
        actual_promo = (((await session.execute(promo_stmt)).scalar()).value).split()
        user = (await session.execute(user_stmt)).scalar()
        count_promo = (await session.execute(using_promo)).scalar()
        used_promo = (user.used_promo).split()

        logger.info(f'User promo status: {user.promo}, users used promo: {used_promo}, promo: {promocode}')
        logger.info(f'Actual promos: {actual_promo}')

        if user.promo != 1: 
            if promocode not in used_promo: 
                if promocode in actual_promo:
                    user.promo = 3
                    user.used_promo = str(user.used_promo) + ' ' + str(promocode)
                    count_promo.value = str(int(count_promo.value) + 1)
                    await session.commit()
                    return 'approved'
                else:
                    return 'wrong promo'
            else:
                return 'used yet'
        else:
            return 'promo is active'



# Changing data of Users after game results
async def game_result_writer(session: AsyncSession,
                             owner: int,
                             deposit: float,
                             winner_id: int,
                             loser_id: int):

    coef_counter = services.services.coef_counter

    # Get Entities from database
    winner_statement = select(User).where(winner_id == User.telegram_id)
    loser_statement = select(User).where(loser_id == User.telegram_id)
    pure_income_statement = select(Variables).where('pure_income' == Variables.name)
    to_parents_statement = select(Variables).where('to_parents' == Variables.name)
    games_counter_statement = select(Variables).where('total_games_players' == Variables.name)
    total_bets_statement = select(Variables).where('total_bets' == Variables.name)
    bets_statement = select(Variables).where('bets' == Variables.name)

    winner_coef = float((await coef_counter(winner_id, session))['coef'] - 1)
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
        
        if winner.promo > 0:
            winner_prize = deposit
            winner.promo = winner.promo - 1
            flag = True
        else:
            flag = False

        winner.wins_ton = winner.wins_ton + winner_prize
        winner.ton = winner.ton + winner_prize
        winner.last_game = str(datetime.datetime.now())
        
        # Writing loser data
        loser.games = loser.games + 1
        loser.lose = loser.lose + 1
        loser.lose_ton = loser.lose_ton + deposit
        loser.ton = loser.ton - deposit
        loser.last_game = str(datetime.datetime.now())
        
        # Prepare vars to write referral parents %
        winner_parent_id = winner.parent
        loser_parent_id = loser.parent
        
        await session.commit()
    
    our_income = deposit - winner_prize

    # If Winner haven't promocode - parents have 3% from deposit
    if flag is False:
        logger.info(f'Winner parent: {winner_parent_id}, Loser parent: {loser_parent_id}')

        winner_parent_statement = select(User).where(int(winner_parent_id) == User.telegram_id)
        loser_parent_statement = select(User).where(int(loser_parent_id) == User.telegram_id)
        
        # Is winner parent exists?
        if int(winner_parent_id) == 0:
            logger.info('Winner parent is 0')
        else:
            logger.info(f'Winner parent is not 0: {winner_parent_id}')
            winner_parent_comission = (await coef_counter(winner_parent_id, session))['comission'] * our_income

        # Is loser parent exists?
        if int(loser_parent_id) == 0:
            logger.info('Loser parent is 0')
        else:
            logger.info(f'Loser parent is not 0: {loser_parent_id}')
            loser_parent_comission = (await coef_counter(loser_parent_id, session))['comission'] * our_income

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
    pure_income = our_income - winner_parent_comission - loser_parent_comission
    
    logger.info(f'Game result after counting:\nwinner prize = {winner_prize}\n\
                income before parents comission = {our_income}\n\
                winner parent comission = {winner_parent_comission}\n\
                loser parent comission = {loser_parent_comission}\n\
                pure income = {pure_income}')

    async with session: 
        pure_income_scalar = (await session.execute(pure_income_statement)).scalar()
        to_parents_scalar = (await session.execute(to_parents_statement)).scalar()
        games_counter = (await session.execute(games_counter_statement)).scalar()
        total_bets = (await session.execute(total_bets_statement)).scalar()
        bets = (await session.execute(bets_statement)).scalar()

        pure_income_scalar.value = str(float(pure_income_scalar.value) + float(pure_income))
        to_parents_scalar.value = str(float(to_parents_scalar.value) + float(winner_parent_comission + loser_parent_comission))
        games_counter.value = str(int(games_counter.value) + 1)
        total_bets.value = str(float(total_bets.value) + (deposit * 2))
        bets.value = bets.value + ' ' + str(deposit)

        await session.commit()


# Writing result of Game with Bot
async def demo_result_writer(session: AsyncSession,
                             deposit: float,
                             user_id: int,
                             result: str):
    
    coef_counter = services.services.coef_counter

    # Get Entities from database
    user_statement = select(User).where(user_id == User.telegram_id)
    pure_income_statement = select(Variables).where('pure_income' == Variables.name)
    to_parents_statement = select(Variables).where('to_parents' == Variables.name)
    games_counter_statement = select(Variables).where('total_games_bot' == Variables.name)
    total_bets_statement = select(Variables).where('total_bets' == Variables.name)
    bets_statement = select(Variables).where('bets' == Variables.name)

    user_coef = float((await coef_counter(user_id, session))['coef'] - 1)
    user_prize = user_coef * float(deposit) if result == 'win' else (-1.0 * deposit)
    user_parent_comission = 0

    logger.info(f'Default game results: winner prize = {user_prize}')
    logger.info(f'Game result for User {user_id} - {result}')
    flag = None

    async with session:
        user = (await session.execute(user_statement)).scalar()
        logger.info(f'Executed user: {user}')

        # Writing winner data        
        user.games = user.games + 1
        user.last_game = str(datetime.datetime.now())
        
        '''
        if result == 'win': 
            user.wins = user.wins + 1

            if user.promo == 1:
                user_prize = deposit
                user.promo = 0
                flag = True
            else:
                flag = False
            
            user.wins_ton = user.wins_ton + user_prize
            user.ton = user.ton + user_prize
            user.bot_income = user.bot_income - user_prize
    
        elif result == 'lose':
        '''
        user.lose = user.lose + 1
        user.games = user.games + 1
        user.lose_ton = user.lose_ton + deposit
        user.ton = user.ton - deposit
        user.bot_income = user.bot_income + deposit
        
        # Prepare vars to write referral parents %
        user_parent_id = user.parent
        await session.commit()
    '''
    if result == 'win':
        our_income = deposit - user_prize
    elif result == 'lose':
    '''
    our_income = deposit
    parent_coef = float((await coef_counter(user_parent_id, session))['comission']) 
    logger.info(f'Our income from bot: {our_income}')
          
    # If Winner haven't promocode - parents have 3% from deposit
    logger.info(f'User parent: {user_parent_id}')

    user_parent_statement = select(User).where(int(user_parent_id) == User.telegram_id)
    
    # Is users parent exists?
    if int(user_parent_id) == 0:
        logger.info('User parent is 0')
    else:
        logger.info(f'User parent is not 0: {user_parent_id}')
        user_parent_comission = parent_coef * our_income

    async with session:
        user_parent = (await session.execute(user_parent_statement)).scalar()
        
        if user_parent is not None:
            logger.info(f'user_parent is {user_parent.telegram_id}')
            user_parent.ton = float(user_parent.ton) + user_parent_comission

        await session.commit()

    # Write parent comission and pure income to Variables Database
    pure_income = float(our_income - user_parent_comission)
    
    logger.info(f'Game result after counting:\nuser prize = {user_prize}\n\
                our income before parent comission = {our_income}\n\
                user parent comission = {user_parent_comission}\n\
                pure income = {pure_income}')

    async with session: 
        pure_income_scalar = (await session.execute(pure_income_statement)).scalar()
        to_parents_scalar = (await session.execute(to_parents_statement)).scalar()
        games_counter = (await session.execute(games_counter_statement)).scalar()
        total_bets = (await session.execute(total_bets_statement)).scalar()
        bets = (await session.execute(bets_statement)).scalar()

        pure_income_scalar.value = str(float(pure_income_scalar.value) + pure_income)
        to_parents_scalar.value = str(float(to_parents_scalar.value) + user_parent_comission)
        games_counter.value = str(int(games_counter.value) + 1)
        total_bets.value = str(float(total_bets.value) + deposit)
        bets.value = bets.value + ' ' + str(deposit)

        await session.commit()





















