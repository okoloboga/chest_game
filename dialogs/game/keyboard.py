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

    return InlineKeyboardMarkup(inline_keyboard=[[button_game_first,
                                              button_game_second,
                                              button_game_third]
                                            ])


# End Game - when one of players is lose
def game_end_keyboard(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    button_play_again = InlineKeyboardButton(text=i18n.button.play.again(),
                                             callback_data='play_again')
    button_game_end = InlineKeyboardButton(text=i18n.button.game.end(),
                                            callback_data='game_end')

    return InlineKeyboardMarkup(inline_keyboard=[[button_play_again], [button_game_end]])

   

