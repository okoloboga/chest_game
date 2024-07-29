import logging
import pprint
import asyncio

from aiogram import F, Router, Bot
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest

from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorRunner
from redis import asyncio as aioredis

from states import GameSG, LobbySG
from config import get_config, BotConfig
from services import get_game, room_to_game, game_result
from .keyboard import *

game_router = Router()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Created Room or Query - now un GameSG, without Dialog
# Returning Game menu for HIdder or Searcher 
# And delete last message
@game_router.callback_query(StateFilter(LobbySG.game_confirm))
async def confirm_game(callback: CallbackQuery,
                       button: Button,
                       dialog_manager: DialogManager,
                       state: FSMContext
                       ):
    
    user_id = callback.from_user.id
    result = await room_to_game(user_id)
    r = aioredis.Redis(host='localhost', port=6379)
    logger.info(f'User {callback.from_user.id} start game: {result}')
    
    await dialog_manager.reset_stack()

    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    
    # Getting hidder from Game data
    user_game_str = await r.get(user_id)
    user_game = await r.hgetall('go_'+str(user_game_str, encoding='utf-8'))
    hidder = str(user_game[b'hidder'], encoding='utf-8')

    # Checking users Role in that game
    if hidder == user_id:
        msg = await callback.message.answer(text=i18n.game.hidder(),
                                            reply_markup=game_chest_keyboard(i18n))
    else:
        msg = await callback.message.answer(text=i18n.game.wait.searcher(),
                                            reply_markup=game_exit_keyboard(i18n))

    # Init bot
    bot_config = get_config(BotConfig, 'bot')
    bot = Bot(token=bot_config.token.get_secret_value(),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    await bot.delete_message(user_id, msg.message_id - 1)

    # And close it
    await (await bot.get_session()).close()

    await state.set_state(GameSG.main)


# All game in one handler
@game_router.callback_query(F.data.in_(['first', 'second', 'third', 'game_exit']),
                            StateFilter(GameSG.main))
async def main_game_process(callback: CallbackQuery,
                            state: FSMContext,
                            i18n: TranslatorRunner,
                            dialog_manager: DialogManager,
                            bot: Bot
                            ):
    
    # Init variables

    r = aioredis.Redis(host='localhost', port=6379)
    user_id = callback.from_user.id
    last_message = callback.message.message_id - 1
    chat_id = callback.chat_instance
    user_game_str = await r.get(user_id)
    user_game = await r.hgetall('go_'+str(user_game_str, encoding='utf-8'))
    
    owner = str(user_game[b'owner'], encoding='utf-8')
    guest = str(user_game[b'guest'], encoding='utf-8')
    enemy = owner if guest == user_id else guest
    hidder = str(user_game[b'hidder'], encoding='utf-8') 
    searcher = guest if hidder == owner else owner
    
    # If it Not Exit from Game
    if callback.data != 'game_exit':
        # If User is Hidder
        if user_id == hidder:
           
            # Writing to Redis database
            user_game[b'target'] = callback.data
            await r.hmset(str(callback.from_user.id), user)

            try: 
                await callback.message.edit_text(text=i18n.game.hidden(),
                                                 reply_markup=game_exit_keyboard(i18n))
                await bot.delete_message(chat_id, id)
            except TelegramBadRequest:
                await callback.answer()

            # Give turn to Searcher
            await asyncio.sleep(2)
            msg = await bot.send_message(searcher, text=i18n.game.searcher(),
                                         reply_markup=game_chest_keyboard(i18n))
            try:
                await bot.delete_message(searcher, msg.message_id - 1)
            except TelegramBadRequest:
                await callback.answer()

        # If User is Searcher
        else:
           target = str(user_game[b'target'], encoding='utf-8')

            # Checking for success or not 
            if target == callback.data:
                deposit = str(user_game[b'deposit'], encoding='utf-8')
            
                result = await game_result(int(owner), float(deposit), 
                                           winner_id=int(searcher),
                                           loser_id=int(hidder)

                try:
                    await callback.message.edit_text(text=i18n.game.youwin(deposit=deposit))
                except TelegramBadRequest:
                    await callback.answer()

                await state.clear()   

                # Initiator of game_result() will bring data about result to lobby and database
                await dialog_manager.start(state=MainSG.main,
                                           mode=StartMode.RESET_STACK,
                                           data={**result})
                 
                # Send notification to Hidder
                await asyncio.sleep(2)
                msg = await bot.send_message(hidder, text=i18n.game.youlose(deposit=deposit),
                                             reply_markup=game_end_keyboard(i18n))
                try:
                    await bot.delete_message(hidder, msg.message_id - 1)
                except TelegramBadRequest:
                    await callback.answer()
                
            else:
                try:
                    await callback.message.edit_text(text=i18n.game.wrong.choice(),
                                                     reply_markup=game_exit_keyboard(i18n))
                except TelegramBadRequest:
                    await callback.answer()

                # Give turn to Hidder                
                await asyncio.sleep(2)
                msg = await bot.send_message(hidder, text=i18n.game.hidder(),
                                             reply_markup=game_chest_keyboard(i18n))
                try:
                    await bot.delete_message(hidder, msg.message_id - 1)
                except TelegramBadRequest:
                    await callback.answer()

    else:
        
        deposit = str(user_game[b'deposit'], encoding='utf-8')
 
        result = await game_result(int(owner), float(deposit), 
                                   winner_id=int(enemy),
                                   loser_id=int(user_id))
        try:           
            await callback.message.edit_text(text=game.youlose(deposit=deposit))
        except TelegramBadRequest:
            await callback.answer()

        await state.clear()

        # Initiator of game_result() will bring data about result to lobby and database
        await dialog_manager.start(state=MainSG.main,
                                   mode=StartMode.RESET_STACK,
                                   data={**result})
                 
        # Send notification to enemy
        await asyncio.sleep(2)
        msg = await bot.send_message(enemy, text=i18n.game.youwin(deposit=deposit),
                                     reply_markup=game_end_keyboard(i18n))
        try:
            await bot.delete_message(enemy, msg.message_id - 1)
        except TelegramBadRequest:
            await callback.answer()
                

# Processing End Game button, when User is lose
# For exit to Lobby
@game_router.callback_query(F.text == 'game_end', 
                            StateFilter(GameSG.main))
async def game_end_process(callback: CallbackQuery,
                           state: FSMContext,
                           dialog_manager: DialogManager
                           ):

    user_id = callback.from_user.id
    await state.clear()
    await dialog_manager.start(state=MainSG.main,
                               mode=StartMode.RESET_STACK)




