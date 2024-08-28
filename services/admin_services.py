import logging
import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import Variables, User

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')



# Checking for valid admin_password from Mian dialogs
def admin_password(password: str):
    if password == '#admin_panel':
        return password
    raise ValueError


# Add or remove Promocodes in Database
async def edit_promocode_process(session: AsyncSession,
                                 promocode_command: str) -> str:
    
    logger.info(f'Editing promocode {promocode_command}')
    promocode_statement = select(Variables).where('promocodes' == Variables.name)
    
    async with session:
        promocodes = (await session.execute(promocode_statement)).scalar()
        logger.info(f'promocodes: {promocodes.value}')

        if promocode_command[0] == '+':
            promocodes.value = str(promocodes.value + ' ' + promocode_command[1:])
            result = 'added'
        elif promocode_command[0] == '-':
            promocodes_list = (promocodes.value).split()
            if promocode_command[1:] in promocodes_list:
                promocodes.value = str(' '.join(promocodes_list.remove(promocode_command[1:])))
                result = 'removed'
            else:
                result = 'no_promocode'
        else:
            result = 'invalid_command'

        await session.commit()
    return result


# Add to ban player
async def ban_player_process(session: AsyncSession,
                             user_for_ban: int) -> str:

    logger.info(f'Banning user {user_for_ban}')
    user_statement = select(User).where(int(user_for_ban) == int(User.telegram_id))

    async with session:
        user = (await session.execute(user_statement)).scalar()
        if user_for_ban[0] == '+':
            if user.banned == 'no':
                user.banned = 'yes'
                result = 'banned'
            else:
                result = 'banned_yet'
        elif user_for_ban[0] == '-':
            if user.banned == 'yes':
                user.banned = 'no' 
                result = 'unbanned'
            else:
                result = 'notbanned'
        else:
            result = 'invalid_command'
        await session.commit()
    return result


# Get information for main admin panel
async def admin_panel_info(session: AsyncSession) -> dict:

    logger.info(f'Getting info for main admin panel')

    delta = datetime.timedelta(days=1)
    current_datetime = datetime.datetime.now()
    target_datetime = current_datetime - delta

    users_count_stmt = (select(func.count())
                        .select_from(User))
    new_users_stmt = (select(func.count())
                      .select_from(User)
                      .where(target_datetime < User.created_at))
    total_games_players_stmt = (select(Variables).where('total_games_players' == Variables.name))
    total_games_bot_stmt = (select(Variables).where('total_games_bot' == Variables.name))
    total_bets_stmt = (select(Variables).where('total_bets' == Variables.name))
    pure_income_stmt = (select(Variables).where('pure_income' == Variables.name))
    bets_stmt = (select(Variables).where('bets' == Variables.name))
    
    async with session:
        users_count = ((await session.execute(users_count_stmt)).scalar())
        new_users = ((await session.execute(new_users_stmt)).scalar())
        total_games_players = ((await session.execute(total_games_players_stmt)).scalar()).value
        total_games_bot = ((await session.execute(total_games_bot_stmt)).scalar()).value
        total_bets = ((await session.execute(total_bets_stmt)).scalar()).value
        pure_income = ((await session.execute(pure_income_stmt)).scalar()).value
        bets = (((await session.execute(bets_stmt)).scalar()).value).split()

    popular_bet = max(set(bets), key=bets.count)

    result = {'users_count': users_count,
              'new_users': new_users,
              'total_games_players': total_games_players,
              'total_games_bot': total_games_bot,
              'total_bets': total_bets,
              'pure_income': pure_income,
              'popular_bet': popular_bet}
    
    return result


# Getting list of promocodes
async def get_promocodes(session: AsyncSession) -> str:

    promo_stmt = select(Variables).where('promocodes' == Variables.name)

    async with session:
        return ((await session.execute(promo_stmt)).scalar()).value
        
     
