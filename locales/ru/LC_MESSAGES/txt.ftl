####################################################################

 /$$                   /$$     /$$                                  
| $$                  | $$    | $$                                  
| $$$$$$$  /$$   /$$ /$$$$$$ /$$$$$$    /$$$$$$  /$$$$$$$   /$$$$$$$
| $$__  $$| $$  | $$|_  $$_/|_  $$_/   /$$__  $$| $$__  $$ /$$_____/
| $$  \ $$| $$  | $$  | $$    | $$    | $$  \ $$| $$  \ $$|  $$$$$$ 
| $$  | $$| $$  | $$  | $$ /$$| $$ /$$| $$  | $$| $$  | $$ \____  $$
| $$$$$$$/|  $$$$$$/  |  $$$$/|  $$$$/|  $$$$$$/| $$  | $$ /$$$$$$$/
|_______/  \______/    \___/   \___/   \______/ |__/  |__/|_______/

####################################################################

button-subscribe = Подписаться
button-check-subscribe = Проверить подписку
button-confirm = Принять
button-play = Играть
button-balance = Баланс
button-howtoplay = Как играть
button-referrals = Реферралы
button-community = Комьюнити
button-tonimport = Внести
button-getwallet = Кошелек
button-tonexport = Вывести
button-importcheck = Проверить ввод
button-public-game = Найти случайную Игру
button-private-game = Создать закрытую Игру
button-mode1vs1 = 1VS1
button-modesuper = SUPER
button-game-confirm = Подтвердить
button-game-exit = Выйти из Игры
button-game-end = Закончить игру
button-wait-check-o = Проверить...
button-wait-check-s = Проверить...
button-owner-ready = Готов!
button-wait-check-search = Проверить...
button-joined-check-s = Проверить...
button-joined-ready = Готов!
button-game-ready = Играть!
button-back = Назад
button-hide-first = 1
button-hide-second = 2
button-hide-third = 3



#######################################################################
                                                                                   
                                                                                   
 /$$$$$$/$$$$   /$$$$$$   /$$$$$$$ /$$$$$$$  /$$$$$$   /$$$$$$   /$$$$$$   /$$$$$$$
| $$_  $$_  $$ /$$__  $$ /$$_____//$$_____/ |____  $$ /$$__  $$ /$$__  $$ /$$_____/
| $$ \ $$ \ $$| $$$$$$$$|  $$$$$$|  $$$$$$   /$$$$$$$| $$  \ $$| $$$$$$$$|  $$$$$$ 
| $$ | $$ | $$| $$_____/ \____  $$\____  $$ /$$__  $$| $$  | $$| $$_____/ \____  $$
| $$ | $$ | $$|  $$$$$$$ /$$$$$$$//$$$$$$$/|  $$$$$$$|  $$$$$$$|  $$$$$$$ /$$$$$$$/
|__/ |__/ |__/ \_______/|_______/|_______/  \_______/ \____  $$ \_______/|_______/ 
                                                      /$$  \ $$                    
                                                     |  $$$$$$/                    
                                                      \______/ 
#######################################################################


start-dialog = Для продолжения подпишись 
               на наше коммьюнити 

need-subscribe = 🚀 Для начала - подпишись на канал

welcome-dialog = Добро пожаловать, { $name }!
                 Теперь ты настоящий пират ☠

                 Вот что нужно знать о нашей игре:
                 1. Вноси депозит в TON.
                 2. Отгадывай сундукs с сокровищами.
                 3. Выводи приз на свой кошелек (любой кошелек, поддерживающий TON).

                 Режимы игры:
                 1. Стандартный режим:
                 - Игроков: 2
                 - Сундуков: 3 (1 выигрышный)
                 - Роли: Один прячет, другой ищет (определяет бот)
                 - Приз: Тот, кто лучше справился с ролью
                 - Время на ход: 1 минута

                 2. Многопользовательский режим (Super):
                 - Игроков: от 3 до 10
                 - Сундуков:3 (1 выигрышный, у каждого игрока разный)
                 - Бот прячет сундук, все игроки ищут
                 - Если никто не нашел: депозит возвращается (удерживается комиссия)
                 - В случае ничьи: переигрываем до 3х раз (после разделения приза между
                 победителями, если ничья)
                 - Время на ход: 1 минута

                 Условия:
                 - Минимальный депозит: 0,5 TON
                 - Комиссия: 8%
                 - Вывод: от 1 TON (на любой кошелек, принимающий TON)

                 Приглашай друзей, зарабатывай с их побед и проигрышей, уменьшай комиссию на
                 свои игры.

                 Удачи, пират!🦜

main-menu = Главное Меню

referrals = 👋 Ваша реферальная ссылка на PIRATES. Приглашай!

            <code>{ $link }</code>

            Вы позвали: { $referrals } друзей

            Ваш коэфициент при выйгрыше: { $coef }

            • Зарабатывайте 3% со всех удачных и неудачных игр ваших друзей!

            • Повышайте свой коэфициент:

            1 друг: x1.6
            15 друзей: x1.75
            90 друзей: x1.9

#################
#  TRANSACTIONS #
#################

balance =  Баланс { $ton_balance }

           Условия пополнения от 0,5 TON
           Вывод от 1 TON

tonimport = Что бы ввести TON необходимо
            совершить транзакцию на 
            кошелек указанный ниже.

            Что бы мы знали что, транзакция
            сделана именно тобой - напиши в комментарии
            к транзакции свой ID (без пробелов!):
            { $id }

            Минимальная сумма - 0.5 TON.
            Если отправишь меньше 
            или без комментария - она не будет засчитана!

            Нажми Кошелек - что бы получить адрес
            кошелька для пополнения

central-wallet = { $wallet }

tonexport = Минимальная сумма для вывода: 1 TON
         
            Что бы вывести TON - напиши в чат свой кошелек
            и через пробел сумму вывода

            Например:
            <code>UQDIkS1d_Lhd7EDttTtcmr9Xzg78uEMDEsYFde-PZCgfoOtU 2</code>

wrong-export = Введены неверные данные 
               для вывод TON!

               Неверный адрес кошелька
               или количество. 
               Напомним, что минимальный вывод - 1 TON

notenough-transaction = Перевод меньше 0.5 TON!
                        Такой перевод не может быть засчитан

no-transaction = Не было транзакции с комментарием
                 содержащим твой ID

tonimport-success = { $value } TON Успешно поступили
                    на твой игровой счёт!

old-transaction = Новой транзакции не было.
                  Последняя транзакция от тебя:
                  <code>{ $t_hash }</code>

                  На сумму { $t_value } TON

tonexport-success = Успешный вывод { $value } TON
                    На кошелек
                    <code>{ $address }</code>

tonexport-notenough = Недостаточно TON
                      На аккаунте { $user_ton } TON
                      Запрос на вывод { $value }

tonexport-error = Что то пошло не по плану
                  Твоя транзакция не была отправлена
    
########################
# GAME MOD AND DEPOSIT #
########################

lobby-menu = Хочешь найти случайную игру или
             играть с друзьями?

             Если друг тебе дал код-приглашение
             Просто введи его и отправь в чат!


select-deposit = Выбери размер депозита

notenough-ton = Недостаточно TON на аккаунте!
                Предлагаем пополнить счёт 
                прямо сейчас

game-notexists = Такой игры нет!

game-confirm = Ты ищешь игру
               С депозитом { $deposit } TON


####################
# WAITING FOR GAME #
####################

ownerpublic = Ожидаем соперника для Игры!              
              Депозит: { $deposit } TON

ownerprivate = Ты создал приватную игру
               с депозитом { $deposit } TON
               Ты можешь пригласить в нее друга
               при помощи кода:
               <code>{ $invite_code }</code> 

search-game = Ищем для тебя игру!
              Депозит: { $deposit } TON

game-ready = Игра готова!
             C депозитом { $deposit } TON
             
             Нажми Готов что бы начать!

still-waiting-opponent = Пока ждём соперника!

still-searching-game = Пока ищем подходящую игру!

########
# GAME #
########

game-wait-searcher = Ты - Искатель!
                     Жди, пока сундук будет спрятан

game-hidder = Ты - прячешь клад!
              Выбери, где будет спрятано
              сокровище

game-searcher = Ты - Искатель!
                Где спрятаны сокровища?

game-hidden = Спрятано!
              Ждем хода Искателя

game-wrong-choice = Неправильно! 
                    Теперь ты прячешь клад

game-youwin = У Вас Дар!
              Вы забираете приз

game-youlose = Ты был близок к победе, 
               но твой соперник ближе

###################
# Unknown Message #
###################

unknown-message = Не понял, что ты сказал....
