from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.input.text import TextInput

from .getter import *
from .handler import *
from states import AdminSG
from dialogs import back, send_answer


admin_dialog = Dialog(
    Window(
        Format('{admin_panel}'),
        Button(Format('{button_send_messages}'), id='b_send_messages', on_click=send_messages),
        Row(
            Button(Format('{button_edit_promocode}'), id='b_edit_promocode', on_click=edit_promocode),
            Button(Format('{button_ban_player}'), id='b_ban_player', on_click=ban_player)
            ),        
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=main_admin_getter,
        state=AdminSG.main
        ),
    Window(
        Format('{send_messages}'),
        Button(Format('{button_back}'), id='b_back_admin', on_click=back_admin),
        TextInput(
            id='enter_messages',
            type_factory=str,
            on_success=complete_send_messages,
            on_error=send_answer
            ),
        getter=send_messages_getter,
        state=AdminSG.send_messages
        ),
    Window(
        Format('{edit_promocode}'),
        Button(Format('{button_back}'), id='b_back_admin', on_click=back_admin),
        TextInput(
            id='command_promocode',
            type_factory=str,
            on_success=complete_edit_promocode,
            on_error=send_answer
            ),
        getter=edit_promocode_getter,
        state=AdminSG.edit_promocode
        ),
    Window(
        Format('{ban_player}'),
        Button(Format('{button_back}'), id='b_back_admin', on_click=back_admin),
        TextInput(
            id='user_for_ban',
            type_factory=str,
            on_success=complete_ban_player,
            on_error=send_answer
            ),
        getter=ban_player_getter,
        state=AdminSG.ban_player
        )
    )


