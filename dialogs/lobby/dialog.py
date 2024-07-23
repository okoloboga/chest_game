from aiogram.types import ContentType

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.input.text import TextInput

from .getter import *
from .handler import *
from states import LobbySG
from dialogs import back

lobby_dialog = Dialog(
    Window(
        Format('{lobby_menu}'),
        Button(Format('{button_find_game}'), id='b_find_game', on_click=find_game),
        Button(Format('{button_create_game}'), id='b_create_game', on_click=create_game),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=lobby_getter,
        state=LobbySG.main
    ),
    Window(
        Format('{select_mode}'),
        Button(Format('{button_mode_1vs1}'), id='b_find_1vs1', on_click=mode_1vs1),
        Button(Format('{button_mode_super}'), id='b_find_super', on_click=mode_super),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=mode_getter,
        state=LobbySG.mode
    ),
    Window(
        Format('{select_deposit}'),
        Button(Const('0.5'), id='b_deposit_0_5', on_click=deposit_0_5),
        Row(
            Button(Const('1'), id='b_deposit_1', on_click=deposit_1),
            Button(Const('2'), id='b_deposit_2', on_click=deposit_2)          
        ),
        Row(
            Button(Const('4'), id='b_deposit_4', on_click=deposit_4),
            Button(Const('8'), id='b_deposit_8', on_click=deposit_8),            
            Button(Const('25'), id='b_deposit_25', on_click=deposit_25)            
        ),
        Row(
            Button(Const('50'), id='b_deposit_50', on_click=deposit_50),
            Button(Const('100'), id='b_deposit_100', on_click=deposit_100)            
        ),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=deposit_getter,
        state=LobbySG.deposit               
    ),
    Window(
        Format('{wait_game}'),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=wait_game_getter,
        state=LobbySG.wait_game
    ),
    Window(
        Format('{not_enough_ton}'),
        Button(Format('{button_tonimport}'), id='b_import_from_lobby', on_click=import_from_lobby),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=not_enough_ton_getter,
        state=LobbySG.not_enough_ton   
    )
)