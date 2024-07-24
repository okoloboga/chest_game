import logging

from aiogram_dialog import DialogManager
from aiogram.types import User
from aiogram.utils.deep_linking import create_start_link
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import async_sessionmaker
from redis import asyncio as aioredis

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
            'button_find_game': i18n.button.find.game(),
            'button_create_game': i18n.button.create.game(),
            'button_back': i18n.button.back()}
    
    
# Select type of game: Suber and 1VS1. For Create and Find
async def mode_getter(dialog_manager: DialogManager,
                      session: async_sessionmaker,
                      i18n: TranslatorRunner,
                      bot: Bot,
                      event_from_user: User,
                      **kwargs
                      ) -> dict:
    
    user_id = event_from_user.id
    logger.info(f'User {user_id} in Select Mode')
    
    return {'select_mode': i18n.select.mode(),
            'button_mode_1vs1': i18n.button.mode1vs1(),
            'button_mode_super': i18n.button.modesuper(),
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
    

# Confirming requirements for game 
async def game_confirm_getter(dialog_manager: DialogManager,
    	                      session: async_sessionmaker,
         	                  i18n: TranslatorRunner,
              	              bot: Bot,
                   		      event_from_user: User,
                     	      **kwargs
                         	  ) -> dict:
    
    find_create = dialog_manager.current_context().dialog_data['find_create']
    mode = dialog_manager.current_context().dialog_data['mode']
    deposit = dialog_manager.current_context().dialog_data['deposit']
    
    speech_map = {'find': i18n.find.speech(),
               	  'create': i18n.create.speech()}
    
    find_create_speech = speech_map[find_create]
    
    return {'game_confirm': i18n.game.confirm(find_create_speech=find_create_speech,
                                              mode=mode.capitalize(),
                                              deposit=deposit),
            'button_game_confirm': i18n.game.confirm(),
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
    
    
# User is owner of room 1VS1 and waiting for guest
async def wait_owner_1vs1_getter(dialog_manager: DialogManager,
                                 session: async_sessionmaker,
                                 i18n: TranslatorRunner,
                                 bot: Bot,
                                 event_from_user: User,
                                 **kwargs
                                 ) -> dict:
    
    deposit = dialog_manager.current_context().dialog_data['deposit']
    logger.info(f'User {event_from_user.id} waiting for 1VS1 game as\
      Owner, deposit: {deposit}')   
    
    return {'owner_1vs1': i18n.owner1vs1(deposit=deposit),
            'button_wait_check_o': i18n.wait.check.o(),
            'button_back': i18n.button.back()}


# User is owner of room SUPER and waiting for guests
async def wait_owner_super_getter(dialog_manager: DialogManager,
                                  session: async_sessionmaker,
                                  i18n: TranslatorRunner,
                                  bot: Bot,
                                  event_from_user: User,
                                  **kwargs
                                  ) -> dict:

    deposit = dialog_manager.current_context().dialog_data['deposit']
    players = deialog_manager.current_context().dialog_data['players']
    players_ready = deialog_manager.current_context().dialog_data['players_ready']    
    logger.info(f'User {event_from_user.id} waiting for SUPER game as\
      Owner, deposit: {deposit}, players joined: {players}, players ready: {players_ready}')
        
    return {'owner_super': i18n.ownersuper(deposit=deposit,
                                       	   players=players,
                                           players_ready=players_ready),
            'button_wait_check_s': i18n.wait.check.o(),
            'button_owner_ready': i18n.owner.ready(),
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
    mode = dialog_manager.current_context().dialog_data['mode']
    logger.info(f'User {event_from_user.id} waiting for {mode} game as\
      Searcher, deposit: {deposit}')  
          
    return {'search_game': i18n.search.game(deposit=deposit,
                                            mode=mode),
            'button_wait_check_search': i18n.wait.check.search(),
            'button_back': i18n.button.back()}


# User joined for SUPER game
async def wait_joined_super_getter(dialog_manager: DialogManager,
                                   session: async_sessionmaker,
                                   i18n: TranslatorRunner,
                                   bot: Bot,
                                   event_from_user: User,
                                   **kwargs
                                   ) -> dict:

    deposit = dialog_manager.current_context().dialog_data['deposit']
    players = deialog_manager.current_context().dialog_data['players']
    players_ready = deialog_manager.current_context().dialog_data['players_ready']    
    logger.info(f'User {event_from_user.id} waiting for SUPER game as\
      Joined, deposit: {deposit}, players joined: {players}, players ready: {players_ready}')

    
    return {'joined_super': i18n.joined1vs1(deposit=deposit,
                                       	    players=players,
                                            players_ready=players_ready),
            'button_joined_check_s': i18n.joined.check.o(),
            'button_joined_ready': i18n.joined.ready(),
            'button_back': i18n.button.back()}


# Game is Ready! Need to Confirm
async def game_ready_getter(dialog_manager: DialogManager,
                            session: async_sessionmaker,
                            i18n: TranslatorRunner,
                            bot: Bot,
                            event_from_user: User,
                            **kwargs
                            ) -> dict:

    deposit = dialog_manager.current_context().dialog_data['deposit']
    mode = deialog_manager.current_context().dialog_data['mode']
    players = deialog_manager.current_context().dialog_data['players']    
    logger.info(f'User {event_from_user.id}; offer to confirm {mode} game\
     with deposit {deposti}, total {players} players')
 
    return {'game_ready': i18n.game.ready(deposit=deposit,
                                       	  mode=mode,
                                          players=players),
            'button_game_confirm': i18n.button.game.confirm(),
            'button_back': i18n.button.back()}
    
