import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram_dialog import setup_dialogs
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from fluentogram import TranslatorHub
from redis.asyncio.client import Redis

from config import get_config, BotConfig, DbConfig, Config, load_config
from dialogs import dialogs, routers, unknown_router
from utils import TranslatorHub, create_translator_hub
from middlewares import TranslatorRunnerMiddleware, DbSessionMiddleware
from database import Base

logger = logging.getLogger(__name__)


# Configuration and boot Bot
async def main():

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s'
    )
    logger.info('Starting Bot')

    # Config
    db_config = get_config(DbConfig, "db")
    storage = RedisStorage(Redis(),
                           key_builder=DefaultKeyBuilder(with_destiny=True))

    engine = create_async_engine(
        url=str(db_config.dsn),
        echo=db_config.is_echo
    )
    
    # Connection test with databas
    # async with engine.begin() as connection:
    #     await connection.run_sync(Base.metadata.drop_all)
    #     await connection.run_sync(Base.metadata.create_all)
    
    Sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
 

    # Init Bot in Dispatcher
    bot_config = get_config(BotConfig, "bot")
    bot = Bot(token=bot_config.token.get_secret_value(),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(db_engine=engine, storage=storage)

    # i18n init
    translator_hub: TranslatorHub = create_translator_hub()
    
    # Adding Sessionmaker to Dispatcher
    dp = Dispatcher(session=Sessionmaker)

    # Routers, dialogs, middlewares
    dp.include_routers(*dialogs)
    dp.include_routers(*routers)
    dp.include_routers(unknown_router)
    
    dp.update.middleware(TranslatorRunnerMiddleware())
    dp.update.middleware(DbSessionMiddleware(Sessionmaker))

    setup_dialogs(dp)

    # Skipping old updates
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, _translator_hub=translator_hub)
    return bot

if __name__ == '__main__':
    asyncio.run(main())
