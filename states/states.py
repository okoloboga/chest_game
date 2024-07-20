from aiogram.fsm.states import States, StatesGroup

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
