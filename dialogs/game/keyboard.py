from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fluentogram import TranslatorRunner


# Hidder Keyboard
def game_chest_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:

    button_game_first = InlineKeyboardButton(text=i18n.button.chest.first(),
                                             callback_data='first')
    
    button_game_second = InlineKeyboardButton(text=i18n.button.chest.second(),
                                              callback_data='second')
    
    button_game_third = InlineKeyboardButton(text=i18n.button.chest.third(),
                                             callback_data='third')

    button_exit_game = InlineKeyboardButton(text=i18n.button.game.exit(),
                                            callback_data='game_exit')

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


# End Game - when one of players is lose
def game_end_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    button_game_end = InlineKeyboardButton(text=i18n.button.game.end(),
                                            callback_data='game_end')

    return InlineKeyboardMarkup(inline_keyboard=[[button_game_end]])

   

