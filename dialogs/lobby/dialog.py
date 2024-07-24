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
        Format('{game_confirm}'),
        Button(Format('{button_game_confirm}'), id='b_game_confirm', on_click=confirm_game),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=game_confirm_getter,
        state=LobbySG.game_confirm  
    ),
    Window(
        Format('{not_enough_ton}'),
        Button(Format('{button_tonimport}'), id='b_import_from_lobby', on_click=import_from_lobby),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=not_enough_ton_getter,
        state=LobbySG.not_enough_ton   
    ),
    Window(
        Format('{owner_1vs1}'),
        Button(Format('{button_wait_check_o}'), id='b_wait_check_o', on_click=wait_check_o),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=wait_owner_1vs1_getter,
        state=LobbySG.owner_o
    ),
    Window(
        Format('{owner_super}'),
        Button(Format('{button_wait_check_s}'), id='b_wait_check_s', on_click=wait_check_s),
        Button(Format('{button_owner_ready}'), id='b_owner_ready', on_click=owner_ready),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=wait_owner_super_getter,
        state=LobbySG.owner_s
    ),
    Window(
        Format('{search_game}'),
        Button(Format('{button_wait_check_search}'), id='b_wait_check_search', on_click=wait_check_search),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=search_getter,
        state=LobbySG.search
    ),
    Window(
        Format('{joined_super}'),
        Button(Format('{button_joined_check_s}'), id='b_joined_check_s', on_click=joined_check_s),
        Button(Format('{button_joined_ready}'), id='b_joined_ready', on_click=joined_ready),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=wait_joined_super_getter,
        state=LobbySG.joined_s
    ),
    Window(
        Format('{game_ready}'),
        Button(Format('{button_game_confirm}'), id='b_game_confirm', on_click=game_confirm),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=game_ready_getter,
        state=LobbySG.game_ready
    )
)