from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, Row, Url
from aiogram_dialog.widgets.input.text import TextInput

from .getter import *
from .handler import *
from states import MainSG
from services import (check_address, is_promocode, admin_password,
                      TELEGRAPH, CHANNEL, HOW_TO_GET_TON_RU)
from dialogs.buttons import back

main_dialog = Dialog(
    Window(
        StaticMedia(
            path="img/main.jpg",
            type=ContentType.PHOTO
            ),
        Format('{main_menu}'),
        Button(Format('{button_play}'), id='b_play', on_click=switch_to_lobby),
        Row(
            Button(Format('{button_promocode}'), id='b_promocode', on_click=promocode),
            Button(Format('{button_referrals}'), id='b_referrals', on_click=referrals)
        ),
        Button(Format('{button_balance}'), id='b_balacne', on_click=balance),
        Url(Format('{button_community}'), Const(CHANNEL)),
        TextInput(
            id='admin_enter',
            type_factory=admin_password,
            on_success=to_admin,
            on_error=wrong_password
            ),
        getter=main_getter,
        state=MainSG.main
    ),
    Window(
        StaticMedia(
            path="img/referral.jpg",
            type=ContentType.PHOTO
            ),
        Format('{referrals}'),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=referrals_getter,
        state=MainSG.referrals
    ),
    Window(
        StaticMedia(
            path="img/balance.jpg",
            type=ContentType.PHOTO
            ),
        Format('{balance}'),
        Button(Format('{button_import_check}'), id='b_import_check', on_click=import_check),
        Row(
            Button(Format('{button_import}'), id='b_import', on_click=ton_import),
            Button(Format('{button_export}'), id='b_export', on_click=ton_export)
        ),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=ton_balance_getter,
        state=MainSG.ton_balance
    ),
    Window(
        StaticMedia(
            path="img/balance.jpg",
            type=ContentType.PHOTO
            ),
        Format('{import}'),
        Row(
            Button(Format('{button_import_check}'), id='b_import_check', on_click=import_check),
            Button(Format('{button_get_wallet}'), id='b_get_wallet', on_click=get_wallet)
            ),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=ton_import_getter,
        state=MainSG.ton_import
    ),
    Window(
        StaticMedia(
            path="img/balance.jpg",
            type=ContentType.PHOTO
            ),
        Format('{export}'),
        TextInput(
            id='export_ton',
            type_factory=check_address,
            on_success=do_export,
            on_error=wrong_export
        ),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=ton_export_getter,
        state=MainSG.ton_export
    ),
    Window(
        Format('{enter_promocode}'),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        TextInput(
            id='promocode',
            type_factory=is_promocode,
            on_success=check_promocode,
            on_error=wrong_input
            ),
        getter=promocode_getter,
        state=MainSG.promocode
        )
)

