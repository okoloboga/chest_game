from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorRunner


# Hidder Keyboard
def game_chest_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:

    button_game_first = InlineKeyboardButton(text=i18n.button.hide.first(),
                                             callback_data='first')
    
    button_game_second = InlineKeyboardButton(text=i18n.button.hide.second(),
                                              callback_data='second')
    
    button_game_third = InlineKeyboardButton(text=i18n.button.hide.third(),
                                             callback_data='third')

    button_exit_game = InlineKeyboardButton(text=i18n.button.exit.game(),
                                            callback_data='exit_game')

    return InlineKeyboardMarkup(inline_keyboard=[[button_game_first,
                                                  button_game_second,
                                                  button_game_third],
                                                 [button_exit_game]
                                                ])


# Exit game
def game_exit_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    button_game_exit = InlineKeyboardButton(text=i18n.button.game.exit(),
                                            callback_data='game_exit')

    return InlineKeyboardMarkup(inline_keyboard=[[button_game_exit]])

