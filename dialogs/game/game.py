import logging
import asyncio

from aiogram import F, Router, Bot
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorRunner
from redis import asyncio as aioredis

from states import GameSG, LobbySG, MainSG
from services import room_to_game, game_result
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
async def game_start(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager
                     ):
    room = dialog_manager.current_context().dialog_data['room']
    logger.info(f'Room is {room}')

    user_id = callback.from_user.id
    result = await room_to_game(user_id, str(room[b'owner'], encoding='utf-8'))
    r = aioredis.Redis(host='localhost', port=6379)

    logger.info(f'User {callback.from_user.id} start game as {result}')
    # pprint.pprint(dialog_manager.middleware_data)

    i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    
    # Getting hidder from Game data
    user_game_str = await r.get(user_id)
    logger.info(f'user_game_str: {user_game_str}')
    user_game = await r.hgetall(str(user_game_str, encoding='utf-8'))
    logger.info(f'user_game is {user_game}')
    
    # If Game owner didn't create Game yet
    if len(user_game) > 0:

        await dialog_manager.reset_stack()
        hidder = int(str(user_game[b'hidder'], encoding='utf-8'))
        
        state = dialog_manager.middleware_data.get('state')
        await state.set_state(GameSG.main)

        # Checking users Role in that game
        if hidder == int(user_id):
            logger.info(f'Hidder is {hidder}')
            msg = await callback.message.answer(text=i18n.game.hidder(),
                                                reply_markup=game_chest_keyboard(i18n))
        else:
            msg = await callback.message.answer(text=i18n.game.wait.searcher(),
                                                reply_markup=game_exit_keyboard(i18n))

        try:
            await bot.delete_message(user_id, msg.message_id - 1)
        except TelegramBadRequest:
            await callback.answer()
    else:
        await dialog_manager.switch_to(LobbySG.game_ready)
        
# All game in one handler
@game_router.callback_query(F.data.in_(['first', 'second', 'third', 
                                        'game_exit', 'game_end']),
                            StateFilter(GameSG.main))
async def main_game_process(callback: CallbackQuery,
                            state: FSMContext,
                            i18n: TranslatorRunner,
                            dialog_manager: DialogManager,
                            bot: Bot
                            ):
        # It an end of Game - press buttom GAME END
    if callback.data == 'game_end':
        await dialog_manager.start(state=MainSG.main,
                                   mode=StartMode.RESET_STACK)
    else:
        # Init variables

        r = aioredis.Redis(host='localhost', port=6379)
        user_id = callback.from_user.id
        chat_id = callback.chat_instance
        user_game_str = await r.get(user_id)

        logger.info(f'user_game_str: {user_game_str}')

        user_game = await r.hgetall(str(user_game_str, encoding='utf-8'))
        
        logger.info(f'user_game: {user_game}')

        owner = str(user_game[b'owner'], encoding='utf-8')
        guest = str(user_game[b'guest'], encoding='utf-8')
        enemy = owner if guest == user_id else guest
        hidder = str(user_game[b'hidder'], encoding='utf-8') 
        searcher = guest if hidder == owner else owner

        logger.info(f'Hidder: {hidder}, Searcher: {searcher}')
        
        # If it Not Exit from Game
        if callback.data != 'game_exit' and callback.data != 'game_end':
            # If User is Hidder
            if int(user_id) == int(hidder):
               
                # Writing to Redis database
                user_game[b'target'] = callback.data

                logger.info(f'user_game after hidding: {user_game}')

                await r.hmset(user_game_str, user_game)

                try: 
                    msg = await callback.message.edit_text(text=i18n.game.hidden(),
                                                           reply_markup=game_exit_keyboard(i18n))
                    await bot.delete_message(chat_id, msg.message_id - 1)
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

                logger.info(f'Target is {target}')

                # Checking for success or not 
                if target == callback.data:
                    deposit = str(user_game[b'deposit'], encoding='utf-8')
                
                    result = await game_result(int(owner), float(deposit), 
                                               winner_id=int(searcher),
                                               loser_id=int(hidder))

                    try:
                        await callback.message.answer(text=i18n.game.youwin(deposit=deposit))
                    except TelegramBadRequest:
                        await callback.answer()

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
                    
                    # Switch Roles
                    user_game[b'hidder'] = searcher
                    await r.hmset(user_game_str, user_game)

                    # Send notifications to players
                    try:
                        await callback.message.edit_text(text=i18n.game.wrong.choice(),
                                                         reply_markup=game_chest_keyboard(i18n))
                    except TelegramBadRequest:
                        await callback.answer()

                    # Give turn to Hidder                
                    await asyncio.sleep(2)
                    msg = await bot.send_message(hidder, text=i18n.game.searcher(),
                                                 reply_markup=game_exit_keyboard(i18n))
                    try:
                        await bot.delete_message(hidder, msg.message_id - 1)
                    except TelegramBadRequest:
                        await callback.answer()
                        
                    
        elif callback.data == 'game_exit':
            
            deposit = str(user_game[b'deposit'], encoding='utf-8')
     
            result = await game_result(int(owner), float(deposit), 
                                       winner_id=int(enemy),
                                       loser_id=int(user_id))
            try:           
                await callback.message.answer(text=game.youlose(deposit=deposit))
            except TelegramBadRequest:
                await callback.answer()

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

                
'''
# Processing End Game button, when User is lose
# For exit to Lobby
@game_router.callback_query(F.text == 'game_end', )
                           # StateFilter(GameSG.main))
async def game_end_process(callback: CallbackQuery,
                           state: FSMContext,
                           dialog_manager: DialogManager
                           ):

    user_id = callback.from_user.id
    await state.clear()
    await dialog_manager.start(state=MainSG.main,
                               mode=StartMode.RESET_STACK)
'''



