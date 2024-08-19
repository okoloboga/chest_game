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
    
    
class LobbySG(StatesGroup):
    main = State()
    mode = State()
    deposit = State()
    not_enough_ton = State()
    waiting = State()
    owner_o = State()
    search = State()
    game_ready = State()
    game_confirm = State()
    
class GameSG(StatesGroup):
    main = State()
    
