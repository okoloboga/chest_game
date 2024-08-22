import logging

from aiogram import Bot
from aiogram_dialog import DialogManager
from aiogram.types import User
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import async_sessionmaker
from redis import asyncio as aioredis
from base64 import b64encode

from services import get_user


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
    logger.info(f'User {user_id} in Lobby Menu')
    
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
    logger.info(f'User {user_id} in Deposit Type')
    
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
    logger.info(f'Player {event_from_user.id} search for game with {deposit}')
    
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
    logger.info(f'User {user_id} has not enough TON for Deposit')
    
    return {'not_enough_ton': i18n.notenough.ton(),
            'button_tonimport': i18n.button.tonimport(),
            'button_back': i18n.button.back()}
    

# User is owner of private and waiting for guest
async def wait_owner_private_getter(dialog_manager: DialogManager,
                                    session: async_sessionmaker,
                                    i18n: TranslatorRunner,
                                    bot: Bot,
                                    event_from_user: User,
                                    **kwargs
                                    ) -> dict:
    
    deposit = dialog_manager.current_context().dialog_data['deposit']
    invite_code = b64encode(('pr_' + str(event_from_user.id)).encode('utf-8'))
    logger.info(f'User {event_from_user.id} waiting for Private game as\
      Owner, deposit: {deposit}, invite_code is {invite_code}')   
    
    return {'owner_private': i18n.ownerprivate(invite_code=str(invite_code, encoding='utf-8'),
                                               deposit=deposit),
            'button_wait_check_o': i18n.button.wait.check.o(),
            'button_back': i18n.button.back()}

    
# User is owner of public and waiting for guest
async def wait_owner_public_getter(dialog_manager: DialogManager,
                                   session: async_sessionmaker,
                                   i18n: TranslatorRunner,
                                   bot: Bot,
                                   event_from_user: User,
                                   **kwargs
                                   ) -> dict:
    
    deposit = dialog_manager.current_context().dialog_data['deposit']
    logger.info(f'User {event_from_user.id} waiting for Public game as\
      Owner, deposit: {deposit}')   
    
    return {'owner_public': i18n.ownerpublic(deposit=deposit),
            'button_wait_check_o': i18n.button.wait.check.o(),
            'button_back': i18n.button.back()}


# User searching for Game...
async def search_getter(dialog_manager: DialogManager,
                        session: async_sessionmaker,
                        i18n: TranslatorRunner,
                        bot: Bot,
                        event_from_user: User,
                        **kwargs
                        ) -> dict:
	
    deposit = dialog_manager.current_context().dialog_data['deposit']	
    logger.info(f'User {event_from_user.id} waiting for game as\
      Searcher, deposit: {deposit}')  
          
    return {'search_game': i18n.search.game(deposit=deposit),
            'button_wait_check_search': i18n.button.wait.check.search(),
            'button_back': i18n.button.back()}


# Game is Ready! Need to Confirm
async def game_ready_getter(dialog_manager: DialogManager,
                            session: async_sessionmaker,
                            i18n: TranslatorRunner,
                            event_from_user: User,
                            **kwargs
                            ) -> dict:

    deposit = dialog_manager.current_context().dialog_data['deposit']
        
    logger.info(f'User {event_from_user.id}; offer to confirm game\
     with deposit {deposit}')
 
    return {'game_ready': i18n.game.ready(deposit=deposit),
            'button_game_ready': i18n.button.game.ready(),
            'button_back': i18n.button.back()}
    
