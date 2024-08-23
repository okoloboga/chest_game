from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.input.text import TextInput

from .getter import *
from .handler import *
from states import LobbySG
from dialogs import back
from dialogs.game.game import game_start
from dialogs.demo.game import demo_start
from services import is_private_room


lobby_dialog = Dialog(
    Window(
        Format('{lobby_menu}'),
        Row(
            Button(Format('{button_public_game}'), id='b_public_game', on_click=public_game),
            Button(Format('{button_private_game}'), id='b_private_game', on_click=private_game)
        ),
        Button(Format('{button_demo_game}'), id='b_demo_game', on_click=demo_game),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        TextInput(
            id='admin_panel',
            type_factory=is_private_room,
            on_success=join_private_game,
            on_error=wrong_input
            ),
        getter=lobby_getter,
        state=LobbySG.main
    ),
    Window(
        Format('{select_deposit}'),
        Button(Const('0.5'), id='b_deposit_0_5', on_click=deposit),
        Row(
            Button(Const('1'), id='b_deposit_1', on_click=deposit),
            Button(Const('2'), id='b_deposit_2', on_click=deposit)          
        ),
        Row(
            Button(Const('4'), id='b_deposit_4', on_click=deposit),
            Button(Const('8'), id='b_deposit_8', on_click=deposit),            
            Button(Const('25'), id='b_deposit_25', on_click=deposit)            
        ),
        Row(
            Button(Const('50'), id='b_deposit_50', on_click=deposit),
            Button(Const('100'), id='b_deposit_100', on_click=deposit)            
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
        Format('{owner_private}'),
        Button(Format('{button_wait_check_o}'), id='b_wait_check_o', on_click=wait_check_o),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=wait_owner_private_getter,
        state=LobbySG.owner_private
        ),
    Window(
        Format('{owner_public}'),
        Button(Format('{button_wait_check_o}'), id='b_wait_check_o', on_click=wait_check_o),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=wait_owner_public_getter,
        state=LobbySG.owner_public
    ),
    Window(
        Format('{search_game}'),
        Button(Format('{button_wait_check_search}'), id='b_wait_check_search', on_click=wait_check_search),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=search_getter,
        state=LobbySG.search
    ),
    Window(
        Format('{game_ready}'),
        Button(Format('{button_game_ready}'), id='b_game_ready', on_click=game_start),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=game_ready_getter,
        state=LobbySG.game_ready
    ),
    Window(
        Format('{game_ready}'),
        Button(Format('{button_game_ready}'), id='b_demo_ready', on_click=demo_start),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=game_ready_getter,
        state=LobbySG.demo_ready
    )
)
