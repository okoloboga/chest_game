import asyncio
import logging

from sqlalchemy.ext.asyncio import async_sessionmaker
from database import User


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
                referrals = 0
                )
    
    async with sessionmaker() as session:
        session.add(user)
        await session.commit()
        logger.info(f'New User created {user})

