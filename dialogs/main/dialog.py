from aiogram.types import ContentType

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.input.text import TextInput

from .getter import *
from .handler import *
from states import MainSG
from services import check_value_and_address
from dialogs import back

main_dialog = Dialog(
    Window(
        Format('{main_menu}'),
        Button(Format('{button_play}'), id='b_play', on_click=switch_to_lobby),
        Row(
            Button(Format('{button_balance}'), id='b_balacne', on_click=balance),
            Button(Format('{button_how_to_play}'), id='b_how_to_play', on_click=how_to_play)
        ),
        Row(
            Button(Format('{button_referrals}'), id='b_referrals', on_click=referrals),
            Button(Format('{button_community}'), id='b_community', on_click=community)
        ),
        getter=main_getter,
        state=MainSG.start
    ),
    Window(
        Format('{referrals}'),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=referrals_getter,
        state=MainSG.referrals
    ),
    Window(
        Format('{balance}'),
        Row(
            Button(Format('{button_import}'), id='b_import', on_click=ton_import),
            Button(Format('{button_export}'), id='b_export', on_click=ton_export)
        ),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=ton_balance_getter,
        state=MainSG.ton_balance
    ),
    Window(
        Format('{import}'),
        Format('{central_wallet}'),
        Button(Format('{button_import_check}'), id='b_import_check', on_click=import_check),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=ton_import_getter,
        state=MainSG.ton_import
    ),
    Window(
        Format('{export}'),
        TextInput(
            id='export_ton',
            type_factory=check_value_and_address,
            on_success=do_export,
            on_error=wrong_export
        ),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=ton_export_getter,
        state=MainSG.ton_export
    )
)

