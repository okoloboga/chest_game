from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Button, Row

from .getter import *
from .handler import *
from dialogs import back
from states import DemoSG


demo_dialog = Dialog(
    Window(
        Format('{demo_game_ready}'),
        Button(Format('{button_demo_game_ready}'), id='b_demo_game_ready', on_click=game_demo_start),
        Button(Format('{button_back}'), id='b_back', on_click=back),
        getter=demo_game_ready_getter,
        state=DemoSG.main
    ),
    Window(
        Format('{demo_hidder_active}'),
        Row(
            Button(Format('{button_chest_1}'), id='b_chest_1', on_click=select_chest),
            Button(Format('{button_chest_2}'), id='b_chest_2', on_click=select_chest),
            Button(Format('{button_chest_3}'), id='b_chest_3', on_click=select_chest)
            ),
        Button(Format('{button_demo_exit}'), id='b_demo_exit', on_click=demo_exit),
        getter=demo_hidder_active_getter,
        state=DemoSG.hidder_active
    ),
    Window(
        Format('{demo_hidder_wait}'),
        Button(Format('{button_demo_exit}'), id='b_demo_exit', on_click=demo_exit),
        getter=demo_hidder_wait_getter,
        state=DemoSG.hidder_wait
    ),
    Window(
        Format('{demo_searcher_active}'),
        Row(
            Button(Format('{button_chest_1}'), id='b_chest_1', on_click=select_chest),
            Button(Format('{button_chest_2}'), id='b_chest_2', on_click=select_chest),
            Button(Format('{button_chest_3}'), id='b_chest_3', on_click=select_chest)
            ),
        Button(Format('{button_demo_exit}'), id='b_demo_exit', on_click=demo_exit),
        getter=demo_searcher_active_getter,
        state=DemoSG.searcher_active
    ),
    Window(
        Format('{demo_searcher_wait}'),
        Button(Format('{button_demo_exit}'), id='b_demo_exit', on_click=demo_exit),
        getter=demo_searcher_wait_getter,
        state=DemoSG.searcher_wait
    ),
    Window(
        Format('{gemo_game_result}'),
        Button(Format('{button_demo_end}'), id='b_demo_end', on_click=demo_end),
        getter=demo_game_end_getter,
        state=DemoSG.end
        )
)
