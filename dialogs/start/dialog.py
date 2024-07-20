from aiogram.types import ContentType

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.kbd import Button, Row

from .getter import *
from .handler import *
from states import StartSG

'''Starting dialog, subscribe to channel'''
start_dialog = Dialog(
    Window(
        Format('{start_dialog}'),
        Button(Format('{button_subscribe}'), id='b_subscribe', on_click=subscribe),
        Button(Format('{button_check_subscribe}'), id='b_check_subscribe', on_click=check_subscribe),
        getter=start_getter,
        state=StartSG.start
        ),
    Window(
        Format('{welcome_dialog}'),
        Button(Format('{button_confirm}'), id='b_confirm', on_click=start_confirm),
        getter=welcome_getter,
        state=StartSG.welcome
        )
    )
