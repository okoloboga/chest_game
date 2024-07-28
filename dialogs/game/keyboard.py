from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorRunner


# Hidder Keyboard
def hidder_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:

    button_hide_first = InlineKeyboardButton(text=i18n.button.hide.first(),
                                             callback_data='hide_first')
    
    button_hide_second = InlineKeyboardButton(text=i18n.button.hide.second(),
                                              callback_data='hide_second')
    
    button_hide_third = InlineKeyboardButton(text=i18n.button.hide.third(),
                                             callback_data='hide_third')

    button_exit_game = InlineKeyboardButton(text=i18n.button.exit.game(),
                                            callback_data='exit_game')

    return InlineKeyboardMarkup(inline_keyboard=[[button_hide_first,
                                                  button_hide_second,
                                                  button_hide_third],
                                                 [button_exit_game]
                                                ])


# Searcher waiting for Hidder choice
# Or Hidder waiting for Searcher choice
def game_wait_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:

    button_game_wait = InlineKeyboardButton(text=i18n.button.game.wait(),
                                            callback_data='game_wait')

    button_exit_game = InlineKeyboardButton(text=i18n.button.exit.game(),
                                            callback_data='exit_game')

    return InlineKeyboardMarkup(inline_keyboard=[[button_game_wait],
                                                 [button_exit_game]])

