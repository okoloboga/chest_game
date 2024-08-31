import logging

from aiogram import Bot
from aiogram_dialog import DialogManager
from aiogram.types import User
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import async_sessionmaker
from redis import asyncio as aioredis
from base64 import b64encode

from services import get_user, create_room_query


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Main menu of Lobby:
async def lobby_getter(dialog_manager: DialogManager,
                       session: async_sessionmaker,
                       i18n: TranslatorRunner,
                       bot: Bot,
                       event_from_user: User,
                       **kwargs
                       ) -> dict:
    
    user_id = event_from_user.id
    
    # Get TON value of user
    user_data = await get_user(session,
                               user_id)
    dialog_manager.current_context().dialog_data['ton'] = float(user_data.ton)
    
    return {'lobby_menu': i18n.lobby.menu(),
            'button_public_game': i18n.button.public.game(),
            'button_private_game': i18n.button.private.game(),
            'button_demo_game': i18n.button.demo.game(),
            'button_back': i18n.button.back()}
       
    
# Select deposit for game. For Create and Find
async def deposit_getter(dialog_manager: DialogManager,
                         session: async_sessionmaker,
                         i18n: TranslatorRunner,
                         bot: Bot,
                         event_from_user: User,
                         **kwargs
                         ) -> dict:
    
    user_id = event_from_user.id
       
    return {'select_deposit': i18n.select.deposit(),
            'button_back': i18n.button.back()}
    

# Create or Join to Private game
async def create_join_getter(dialog_manager: DialogManager,
    	                     session: async_sessionmaker,
                             i18n: TranslatorRunner,
              	             bot: Bot,
                   	         event_from_user: User,
                     	     **kwargs
                         	 ) -> dict:
    
    logger.info(f'Player {event_from_user.id} select create or join\n\
            to private game')
    
    return {'create_or_join': i18n.create.join(),
            'button_create_private_game': i18n.button.private.game(),
            'button_back': i18n.button.back()}
 

# Confirming requirements for game 
async def game_confirm_getter(dialog_manager: DialogManager,
    	                      session: async_sessionmaker,
         	                  i18n: TranslatorRunner,
              	              bot: Bot,
                   		      event_from_user: User,
                     	      **kwargs
                         	  ) -> dict:
    
    deposit = dialog_manager.current_context().dialog_data['deposit']   
    
    return {'game_confirm': i18n.game.confirm(deposit=deposit),
            'button_game_confirm': i18n.button.confirm(),
            'button_back': i18n.button.back()}
 
    
# Not enough TON to make Deposit
async def not_enough_ton_getter(dialog_manager: DialogManager,
                                session: async_sessionmaker,
                                i18n: TranslatorRunner,
                                bot: Bot,
                                event_from_user: User,
                                **kwargs
                                ) -> dict:
    
    user_id = event_from_user.id
    
    return {'not_enough_ton': i18n.notenough.ton(),
            'button_tonimport': i18n.button.tonimport(),
            'button_back': i18n.button.back()}
    

# User is owner of private and waiting for guest
async def search_getter(dialog_manager: DialogManager,
                        session: async_sessionmaker,
                        i18n: TranslatorRunner,
                        bot: Bot,
                        event_from_user: User,
                        **kwargs
                        ) -> dict:
    user_id = event_from_user.id
    try:
        logger.info(f'User {user_id} search new game after game ')
        mode = dialog_manager.start_data['mode']
        deposit = dialog_manager.start_data['deposit']
        find_create = 'create'
        dialog_manager.current_context().dialog_data['mode'] = mode
        dialog_manager.current_context().dialog_data['deposit'] = deposit
        dialog_manager.current_context().dialog_data['find_create'] = find_create
        
        r = aioredis.Redis(host='localhost', port=6379)
        room = {
                'mode': mode,
                'owner': user_id,
                'guest': 'wait',
                'deposit': deposit
                }
        if mode != 'private':
            await r.hmset('r_' + str(user_id), room)
        else:
            await r.hmset('pr_' + str(user_id), room)

    except KeyError:
        logger.info(f'User {user_id} search new game')
        deposit = dialog_manager.current_context().dialog_data['deposit']
        mode = dialog_manager.current_context().dialog_data['mode']
        find_create = dialog_manager.current_context().dialog_data['find_create']        
    if mode == 'private':
        invite_code = b64encode(('pr_' + str(user_id)).encode('utf-8'))
        answer = i18n.ownerprivate(invite_code=str(invite_code, encoding='utf-8'),
                                   deposit=deposit)
    else:
        if find_create == 'create':
            answer = i18n.ownerpublic(deposit=deposit)
        elif find_create == 'find':
            answer = i18n.search.game(deposit=deposit)

    logger.info(f'User {user_id} waiting for {mode} game as\
      Owner, deposit: {deposit}')
   
    return {'search_game': answer,
            'button_wait_check': i18n.button.wait.check.o(),
            'button_back': i18n.button.back()}


# Game is Ready! Need to Confirm
async def game_ready_getter(dialog_manager: DialogManager,
                            session: async_sessionmaker,
                            i18n: TranslatorRunner,
                            event_from_user: User,
                            **kwargs
                            ) -> dict:

    user_id = event_from_user.id
    try:
        try:
            room_id = dialog_manager.start_data['game_id']
        except KeyError:
            logger.info(f"User {user_id} hasn't room, don't worry, it should be game against bot")
        mode = dialog_manager.start_data['mode']
        deposit = dialog_manager.start_data['deposit']
        dialog_manager.current_context().dialog_data['mode'] = mode
        dialog_manager.current_context().dialog_data['deposit'] = deposit
        if mode != 'demo':
            try:
                r = aioredis.Redis(host='localhost', port=6379)
                if mode == 'private':
                    room = await r.hgetall('pr_' + str(room_id))
                elif mode == 'public':
                    room = await r.hgetall('r_' + str(room_id))
                dialog_manager.current_context().dialog_data['room'] = room
            except UnboundLocalError:
                logger.info(f'User {user_id} havent room, cause it vs bot')
    except KeyError:
        mode = dialog_manager.current_context().dialog_data['mode']    
        deposit = dialog_manager.current_context().dialog_data['deposit']
    
    game_ready = i18n.demo.ready() if mode == 'demo' else i18n.game.ready(deposit=deposit)
    
    logger.info(f'User {user_id}; offer to confirm game\
     with deposit {deposit} in {mode} mode')
 
    return {'game_ready': game_ready,
            'button_game_ready': i18n.button.game.ready(),
            'button_back': i18n.button.back()}
    
