import logging

from aiogram.types import User
from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner

from services import admin_panel_info, get_promocodes


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')


# Getter of main admin menu
async def main_admin_getter(dialog_manager: DialogManager,
                            i18n: TranslatorRunner,
                            event_from_user: User,
                            **kwargs) -> dict:
    user_id = event_from_user.id
    logger.info(f'User {user_id} entered admin menu')
    session = dialog_manager.middleware_data.get('session')

    result = await admin_panel_info(session)

    return {'admin_panel': i18n.admin.panel(users_count = result['users_count'],
                                            new_users = result['new_users'],
                                            total_games_players = result['total_games_players'],
                                            total_games_bot = result['total_games_bot'],
                                            total_bets = result['total_bets'],
                                            pure_income = result['pure_income'],
                                            popular_bet = result['popular_bet']),
            'button_send_messages': i18n.button.send.messages(),
            'button_edit_promocode': i18n.button.edit.promocode(),
            'button_ban_player': i18n.button.ban.player(),
            'button_back': i18n.button.back()}


# Getter for Sending Messages
async def send_messages_getter(dialog_manager: DialogManager,
                               i18n: TranslatorRunner,
                               event_from_user: User,
                               **kwargs) -> dict:

    return {'send_messages': i18n.send.messages(),
            'button_back': i18n.button.back()}


# Getter for Edditing Promocode
async def edit_promocode_getter(dialog_manager: DialogManager,
                                i18n: TranslatorRunner,
                                event_from_user: User,
                                **kwargs) -> dict:

    session = dialog_manager.middleware_data.get('session')
    result = await get_promocodes(session)

    return {'edit_promocode': i18n.edit.promocode(promocodes = result),
            'button_back': i18n.button.back()}


# Getter for Ban Player
async def ban_player_getter(dialog_manager: DialogManager,
                            i18n: TranslatorRunner,
                            event_from_user: User,
                            **kwargs) -> dict:

    return {'ban_player': i18n.ban.player(),
            'button_back': i18n.button.back()}
