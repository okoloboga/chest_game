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
        Format('{find_type}'),
        Button(Format('{button_find_1vs1}'), id='b_find_1vs1', on_click=find_1vs1),
        Button(Format('{button_find_super}'), id='b_find_super', on_click=find_super),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=find_getter,
        state=LobbySG.find
    ),
    Window(
        Format('{create_type}'),
        Button(Format('{button_create_1vs1}'), id='b_create_1vs1', on_click=create_1vs1),
        Button(Format('{button_create_super}'), id='b_create_super', on_click=create_super),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=create_getter,
        state=LobbySG.create
    ),
    Window(
        Format('{find_deposit}'),
        Button(Const('0.5'), id='b_find_deposit_0_5', on_click=find_deposit_0_5),
        Row(
            Button(Const('1'), id='b_find_deposit_1', on_click=find_deposit_1),
            Button(Const('2'), id='b_find_deposit_2', on_click=find_deposit_2)          
        ),
        Row(
            Button(Const('4'), id='b_find_deposit_4', on_click=find_deposit_4),
            Button(Const('8'), id='b_find_deposit_8', on_click=find_deposit_8),            
            Button(Const('25'), id='b_find_deposit_25', on_click=find_deposit_25)            
        ),
        Row(
            Button(Const('50'), id='b_find_deposit_50', on_click=find_deposit_50),
            Button(Const('100'), id='b_find_deposit_100', on_click=find_deposit_100)            
        ),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=find_deposit_getter,
        state=LobbySG.find_deposit               
    ),
    Window(
        Format('{create_deposit}'),
        Button(Const('0.5'), id='b_create_deposit_0_5', on_click=create_deposit_0_5),
        Row(
            Button(Const('1'), id='b_create_deposit_1', on_click=create_deposit_1),
            Button(Const('2'), id='b_create_deposit_2', on_click=create_deposit_2)          
        ),
        Row(
            Button(Const('4'), id='b_create_deposit_4', on_click=create_deposit_4),
            Button(Const('8'), id='b_create_deposit_8', on_click=create_deposit_8),            
            Button(Const('25'), id='b_create_deposit_25', on_click=create_deposit_25)            
        ),
        Row(
            Button(Const('50'), id='b_create_deposit_50', on_click=create_deposit_50),
            Button(Const('100'), id='b_create_deposit_100', on_click=create_deposit_100)            
        ),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=create_deposit_getter,
        state=LobbySG.create_deposit               
    )
)