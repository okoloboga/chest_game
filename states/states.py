from aiogram.fsm.state import State, StatesGroup

class StartSG(StatesGroup):
    start = State()
    welcome = State()
    

class MainSG(StatesGroup):
    main = State()
    referrals = State()
    ton_balance = State()
    ton_import = State()
    ton_export = State()
    promocode = State()  
    

class LobbySG(StatesGroup):
    main = State()
    mode = State()
    deposit = State()
    not_enough_ton = State()
    waiting = State()
    create_join = State()
    owner_public = State()
    owner_private = State()
    search = State()
    game_ready = State()
    game_confirm = State()
    demo_ready = State()
    

class DemoSG(StatesGroup):
    game = State()


class GameSG(StatesGroup):
    main = State()
 

class AdminSG(StatesGroup):
    main = State()
    edit_promocode = State()
    send_messages = State()
    ban_player = State()
    write_off = State()
    
