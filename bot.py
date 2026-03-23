try:
    import telebot
    from telebot import types
except ImportError:
    print("Ошибка: telebot не установлен. pip install pyTelegramBotAPI")
    exit(1)

import random
import json
import os
import time
import threading
import string

TOKEN = "7766594100:AAH7j4yGEW5Tqoiu8IguYh0Mn3g7lMbPwj8"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 8388843828

USERS_FILE = "guess_users.json"

DEFAULT_WORDS = {
    "ru": ["КОТ", "ДОМ", "ЛЕС", "ГОРОД", "МАШИНА", "СОЛНЦЕ", "ЗВЕЗДА", "КНИГА", "СТОЛ", "ДРУГ"],
    "en": ["CAT", "DOG", "HOUSE", "CAR", "SUN", "STAR", "BOOK", "TABLE", "FRIEND"]
}

SHOP_ITEMS = {
    "hint": {"name": "🔍 Подсказка", "price": 50, "emoji": "🔍"},
    "time": {"name": "⏱️ +15 секунд", "price": 75, "emoji": "⏱️"},
    "reroll": {"name": "🔄 Сменить слово", "price": 100, "emoji": "🔄"},
    "shield": {"name": "🛡️ Защита", "price": 150, "emoji": "🛡️"},
    "double": {"name": "💎 Кристалл x2", "price": 500, "emoji": "💎"}
}

active_games = {}

def load_json(file):
    if os.path.exists(file):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(file, data):
    try:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except:
        pass

def generate_random_word(lang, length=6):
    if lang == "en":
        letters = string.ascii_uppercase
    else:
        letters = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    return ''.join(random.choices(letters, k=length))

def get_word(lang):
    words_dict = load_json("guess_words.json")
    if lang not in words_dict or not words_dict[lang]:
        words_dict[lang] = DEFAULT_WORDS[lang].copy()
        save_json("guess_words.json", words_dict)
    
    # 70% случайное слово, 30% из словаря
    if random.random() < 0.7:
        return generate_random_word(lang, random.randint(4, 8))
    else:
        return random.choice(words_dict[lang])

def get_user(user_id):
    users = load_json(USERS_FILE)
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            'crystals': 100,
            'wins': 0,
            'games': 0,
            'fastest_win': None,
            'streak': 0,
            'best_streak': 0,
            'username': None,
            'lang': 'ru'
        }
        save_json(USERS_FILE, users)
    return users[uid]

def update_user(user_id, data):
    users = load_json(USERS_FILE)
    users[str(user_id)] = data
    save_json(USERS_FILE, users)

def add_crystals(user_id, amount):
    user = get_user(user_id)
    user['crystals'] += amount
    update_user(user_id, user)
    return user['crystals']

def add_win(user_id, time_taken):
    user = get_user(user_id)
    user['wins'] += 1
    user['games'] += 1
    user['streak'] += 1
    if user['streak'] > user['best_streak']:
        user['best_streak'] = user['streak']
    if user['fastest_win'] is None or time_taken < user['fastest_win']:
        user['fastest_win'] = time_taken
    update_user(user_id, user)

def add_loss(user_id):
    user = get_user(user_id)
    user['games'] += 1
    user['streak'] = 0
    update_user(user_id, user)

class Game:
    def __init__(self, chat_id, user_id, lang):
        self.chat_id = chat_id
        self.user_id = user_id
        self.word = get_word(lang).upper()
        self.lang = lang
        self.start_time = time.time()
        self.guessed_letters = []
        self.wrong_letters = []
        self.attempts = 6
        self.message_id = None
        self.active = True
        self.effects = {}
        self.time_extension = 0
    
    def get_display_word(self):
        """Показывает слово с угаданными буквами на правильных местах"""
        display = []
        for letter in self.word:
            if letter in self.guessed_letters:
                display.append(letter)
            else:
                display.append("_")
        return " ".join(display)
    
    def get_time_left(self):
        elapsed = time.time() - self.start_time
        return max(0, 60 + self.time_extension - int(elapsed))
    
    def guess_letter(self, letter):
        letter = letter.upper()
        
        # Если ввели целое слово
        if len(letter) > 1:
            if letter == self.word:
                time_taken = int(time.time() - self.start_time)
                reward = 50
                if self.effects.get("double"):
                    reward *= 2
                add_crystals(self.user_id, reward)
                add_win(self.user_id, time_taken)
                self.active = False
                return True, f"🏆 ПОБЕДА! 🏆\n\nСлово: {self.word}\nВремя: {time_taken} сек\n+{reward} 💎"
            
            self.attempts -= 1
            if self.attempts <= 0:
                if not self.effects.get("shield"):
                    add_loss(self.user_id)
                self.active = False
                return False, f"💀 ПОРАЖЕНИЕ! 💀\n\nСлово: {self.word}"
            return False, f"❌ Неправильно! Осталось попыток: {self.attempts}"
        
        # Проверка буквы
        if letter in self.guessed_letters or letter in self.wrong_letters:
            return False, "❌ Эта буква уже называлась"
        
        # Проверяем, есть ли буква в слове
        if letter in self.word:
            self.guessed_letters.append(letter)
            
            # Проверяем, все ли буквы угаданы
            if all(l in self.guessed_letters for l in self.word):
                time_taken = int(time.time() - self.start_time)
                reward = 50
                if self.effects.get("double"):
                    reward *= 2
                add_crystals(self.user_id, reward)
                add_win(self.user_id, time_taken)
                self.active = False
                return True, f"🏆 ПОБЕДА! 🏆\n\nСлово: {self.word}\nВремя: {time_taken} сек\n+{reward} 💎"
            
            return True, f"✅ Есть такая буква! {self.get_display_word()}"
        else:
            self.wrong_letters.append(letter)
            self.attempts -= 1
            
            if self.attempts <= 0:
                if not self.effects.get("shield"):
                    add_loss(self.user_id)
                self.active = False
                return False, f"💀 ПОРАЖЕНИЕ! 💀\n\nСлово: {self.word}"
            
            return False, f"❌ Нет такой буквы! Осталось попыток: {self.attempts}"
    
    def use_hint(self):
        not_guessed = [l for l in self.word if l not in self.guessed_letters]
        if not_guessed:
            hint_letter = random.choice(not_guessed)
            self.guessed_letters.append(hint_letter)
            return f"🔍 Подсказка: буква {hint_letter} есть в слове!\n\nСлово: {self.get_display_word()}"
        return "❌ Все буквы уже открыты!"
    
    def add_time(self):
        self.time_extension += 15
        return f"⏱️ Добавлено 15 секунд! Осталось: {self.get_time_left()} сек"
    
    def reroll_word(self):
        self.word = get_word(self.lang).upper()
        self.guessed_letters = []
        self.wrong_letters = []
        self.attempts = 6
        return f"🔄 Слово заменено!\n\nСлово: {self.get_display_word()}"

def main_menu_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎮 Начать игру", callback_data="start_game"),
        types.InlineKeyboardButton("🛒 Магазин", callback_data="shop"),
        types.InlineKeyboardButton("🏆 Топ игроков", callback_data="top"),
        types.InlineKeyboardButton("📊 Моя статистика", callback_data="stats"),
        types.InlineKeyboardButton("🌐 Выбрать язык", callback_data="lang"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="help")
    )
    return markup

def admin_panel_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 Общая статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton("💎 Выдать кристаллы", callback_data="admin_give"),
        types.InlineKeyboardButton("📝 Добавить слово", callback_data="admin_addword"),
        types.InlineKeyboardButton("📚 Список слов", callback_data="admin_words"),
        types.InlineKeyboardButton("👥 Список пользователей", callback_data="admin_users"),
        types.InlineKeyboardButton("🖼️ Установить фото", callback_data="admin_setimage"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
    )
    return markup

def shop_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for item_id, item in SHOP_ITEMS.items():
        markup.add(types.InlineKeyboardButton(
            f"{item['emoji']} {item['name']} — {item['price']}💎",
            callback_data=f"buy_{item_id}"
        ))
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
    return markup

def top_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💰 По кристаллам", callback_data="top_crystals"),
        types.InlineKeyboardButton("🏆 По победам", callback_data="top_wins"),
        types.InlineKeyboardButton("⚡ По скорости", callback_data="top_speed"),
        types.InlineKeyboardButton("🔥 По серии", callback_data="top_streak"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
    )
    return markup

def lang_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
    )
    return markup

@bot.message_handler(commands=['start', 'guess', 'menu'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    user = get_user(user_id)
    user['username'] = username
    update_user(user_id, user)
    
    text = f"""🎮 УГАДАЙ СЛОВО

Добро пожаловать, {username}!

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}
🎮 Игр: {user['games']}

Нажми «Начать игру», чтобы играть!"""
    
    bot.send_message(message.chat.id, text, reply_markup=main_menu_kb())

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    text = f"""📊 ТВОЯ СТАТИСТИКА

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}
🎮 Игр: {user['games']}
⚡ Лучшее время: {user['fastest_win'] or '—'} сек
🔥 Текущая серия: {user['streak']}
🏅 Лучшая серия: {user['best_streak']}"""
    
    bot.send_message(message.chat.id, text, reply_markup=main_menu_kb())

@bot.message_handler(commands=['top'])
def top_command(message):
    users = load_json(USERS_FILE)
    top = [{'username': u.get('username', f"User_{uid}"), 'crystals': u.get('crystals', 0)} for uid, u in users.items()]
    top.sort(key=lambda x: x['crystals'], reverse=True)
    text = "💰 ТОП ПО КРИСТАЛЛАМ\n\n"
    for i, u in enumerate(top[:10], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{medal} {u['username']} — {u['crystals']}💎\n"
    bot.send_message(message.chat.id, text, reply_markup=main_menu_kb())

@bot.message_handler(commands=['shop'])
def shop_command(message):
    text = "🛒 МАГАЗИН\n\nВыбери товар в меню ниже:"
    bot.send_message(message.chat.id, text, reply_markup=shop_kb())

@bot.message_handler(commands=['lang'])
def lang_command(message):
    text = "🌐 Выбери язык игры:"
    bot.send_message(message.chat.id, text, reply_markup=lang_kb())

@bot.message_handler(commands=['help'])
def help_command(message):
    text = """📚 ПОМОЩЬ

Команды:
/start — Главное меню
/stats — Моя статистика
/top — Таблица лидеров
/shop — Магазин
/lang — Выбрать язык
/help — Помощь

Как играть:
1. Нажми /start
2. Нажми «Начать игру»
3. Отвечай на сообщение бота буквой или словом
4. Угадай слово за 60 секунд
5. Получай кристаллы за победы

Магазин:
🔍 Подсказка — открывает букву (50💎)
⏱️ +15 секунд — добавляет время (75💎)
🔄 Сменить слово — новое слово (100💎)
🛡️ Защита — не теряешь кристаллы (150💎)
💎 Кристалл x2 — удваивает выигрыш (500💎)"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ У вас нет прав администратора")
        return
    
    text = "🔧 АДМИН ПАНЕЛЬ\n\nВыберите действие:"
    bot.send_message(message.chat.id, text, reply_markup=admin_panel_kb())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    
    if data == "back_to_main":
        user = get_user(user_id)
        text = f"🎮 УГАДАЙ СЛОВО\n\n💰 Кристаллов: {user['crystals']}\n🏆 Побед: {user['wins']}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "help":
        text = """📚 КАК ИГРАТЬ

1️⃣ Нажми «Начать игру»
2️⃣ Введи букву или слово
3️⃣ Угадай слово за 60 секунд

💡 Советы:
- Буквы отображаются на своих местах
- Можно использовать подсказки в магазине
- За победу дают кристаллы

🏆 За победу: +50 кристаллов
⏱️ Время на слово: 60 секунд
🔤 Попыток: 6 ошибок"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "lang":
        bot.edit_message_text("🌐 Выбери язык игры:", call.message.chat.id, call.message.message_id, reply_markup=lang_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "lang_ru":
        user = get_user(user_id)
        user['lang'] = 'ru'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "🇷🇺 Язык: русский")
        text = f"🎮 УГАДАЙ СЛОВО\n\n💰 Кристаллов: {user['crystals']}\n🏆 Побед: {user['wins']}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb())
    
    elif data == "lang_en":
        user = get_user(user_id)
        user['lang'] = 'en'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "🇬🇧 Language: English")
        text = f"🎮 GUESS THE WORD\n\n💰 Crystals: {user['crystals']}\n🏆 Wins: {user['wins']}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb())
    
    elif data == "start_game":
        user = get_user(user_id)
        lang = user.get('lang', 'ru')
        
        if user_id in active_games and active_games[user_id].active:
            bot.answer_callback_query(call.id, "У вас уже есть активная игра!", show_alert=True)
            return
        
        game = Game(call.message.chat.id, user_id, lang)
        active_games[user_id] = game
        
        display = game.get_display_word()
        wrong = ", ".join(game.wrong_letters) if game.wrong_letters else "—"
        text = f"""⏱️ УГАДАЙ СЛОВО — 60 сек

Слово: {display}
Попыток: {game.attempts}
❌ Уже называли: {wrong}
💎 За победу: +50

Напишите букву или слово целиком:"""
        
        sent = bot.send_message(call.message.chat.id, text, reply_markup=types.ForceReply(selective=True))
        game.message_id = sent.message_id
        
        def end_game():
            time.sleep(60)
            if user_id in active_games and active_games[user_id].active:
                game = active_games[user_id]
                if game.active:
                    game.active = False
                    try:
                        bot.edit_message_text(f"⏰ Время вышло! Слово: {game.word}", game.chat_id, game.message_id)
                    except:
                        pass
                    del active_games[user_id]
        
        threading.Thread(target=end_game, daemon=True).start()
        bot.answer_callback_query(call.id)
    
    elif data == "shop":
        bot.edit_message_text("🛒 МАГАЗИН\n\nВыбери товар:", call.message.chat.id, call.message.message_id, reply_markup=shop_kb())
        bot.answer_callback_query(call.id)
    
    elif data.startswith("buy_"):
        item_id = data[4:]
        item = SHOP_ITEMS.get(item_id)
        if not item:
            bot.answer_callback_query(call.id, "❌ Товар не найден")
            return
        
        user = get_user(user_id)
        if user['crystals'] < item['price']:
            bot.answer_callback_query(call.id, f"❌ Не хватает! Нужно {item['price']}💎", show_alert=True)
            return
        
        user['crystals'] -= item['price']
        update_user(user_id, user)
        
        if user_id not in active_games:
            active_games[user_id] = {}
        if not hasattr(active_games[user_id], 'effects'):
            if isinstance(active_games[user_id], dict):
                active_games[user_id]['effects'] = {}
            else:
                active_games[user_id].effects[item_id] = True
        
        bot.answer_callback_query(call.id, f"✅ Куплено: {item['name']}!", show_alert=True)
        bot.edit_message_text("🛒 МАГАЗИН\n\nВыбери товар:", call.message.chat.id, call.message.message_id, reply_markup=shop_kb())
    
    elif data == "top":
        bot.edit_message_text("🏆 ТАБЛИЦА ЛИДЕРОВ\n\nВыбери категорию:", call.message.chat.id, call.message.message_id, reply_markup=top_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "top_crystals":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'crystals': u.get('crystals', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['crystals'], reverse=True)
        text = "💰 ТОП ПО КРИСТАЛЛАМ\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['crystals']}💎\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "top_wins":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'wins': u.get('wins', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['wins'], reverse=True)
        text = "🏆 ТОП ПО ПОБЕДАМ\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['wins']}🏆\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "top_speed":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'speed': u['fastest_win']} for uid, u in users.items() if u.get('fastest_win')]
        top.sort(key=lambda x: x['speed'])
        text = "⚡ ТОП ПО СКОРОСТИ\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['speed']} сек\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "top_streak":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'streak': u.get('best_streak', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['streak'], reverse=True)
        text = "🔥 ТОП ПО СЕРИИ\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['streak']}🏆\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "stats":
        user = get_user(user_id)
        text = f"""📊 ТВОЯ СТАТИСТИКА

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}
🎮 Игр: {user['games']}
⚡ Лучшее время: {user['fastest_win'] or '—'} сек
🔥 Текущая серия: {user['streak']}
🏅 Лучшая серия: {user['best_streak']}"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb())
        bot.answer_callback_query(call.id)
    
    # Админ-панель
    elif data == "admin_stats":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        
        users = load_json(USERS_FILE)
        total_users = len(users)
        total_games = sum(u.get('games', 0) for u in users.values())
        total_wins = sum(u.get('wins', 0) for u in users.values())
        total_crystals = sum(u.get('crystals', 0) for u in users.values())
        
        text = f"""📊 ОБЩАЯ СТАТИСТИКА

👥 Всего игроков: {total_users}
🎮 Всего игр: {total_games}
🏆 Всего побед: {total_wins}
💰 Всего кристаллов: {total_crystals}
⚡ Средний выигрыш: {total_wins/total_users if total_users > 0 else 0:.1f} на игрока"""
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "admin_users":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        
        users = load_json(USERS_FILE)
        text = "👥 СПИСОК ПОЛЬЗОВАТЕЛЕЙ\n\n"
        for uid, u in list(users.items())[:20]:
            text += f"ID: {uid}\n👤 {u.get('username', 'Без имени')}\n💰 {u.get('crystals', 0)}💎 | 🏆 {u.get('wins', 0)}\n\n"
        
        if len(users) > 20:
            text += f"... и еще {len(users)-20} пользователей"
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "admin_give":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        
        bot.edit_message_text("💎 ВЫДАЧА КРИСТАЛЛОВ\n\nВведите ID пользователя и сумму через пробел:\nПример: 123456789 100", 
                            call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
        bot.answer_callback_query(call.id)
        bot.register_next_step_handler(call.message, admin_give_crystals)
    
    elif data == "admin_addword":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        
        bot.edit_message_text("📝 ДОБАВЛЕНИЕ СЛОВА\n\nВведите язык и слово через пробел:\nПример: ru КОТ\nили: en CAT", 
                            call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
        bot.answer_callback_query(call.id)
        bot.register_next_step_handler(call.message, admin_add_word)
    
    elif data == "admin_words":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        
        words = load_json("guess_words.json")
        text = "📚 СПИСОК СЛОВ\n\n"
        for lang, word_list in words.items():
            text += f"{lang}: {', '.join(word_list[:15])}\n"
            if len(word_list) > 15:
                text += f"... и еще {len(word_list)-15} слов\n"
            text += "\n"
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
        bot.answer_callback_query(call.id)

def admin_give_crystals(message):
    try:
        parts = message.text.split()
        user_id = int(parts[0])
        amount = int(parts[1])
        add_crystals(user_id, amount)
        bot.reply_to(message, f"✅ Выдано {amount} кристаллов пользователю {user_id}")
    except:
        bot.reply_to(message, "❌ Ошибка! Формат: ID СУММА")

def admin_add_word(message):
    try:
        parts = message.text.split()
        lang = parts[0].lower()
        word = parts[1].upper()
        
        words = load_json("guess_words.json")
        if lang not in words:
            words[lang] = []
        if word not in words[lang]:
            words[lang].append(word)
            save_json("guess_words.json", words)
            bot.reply_to(message, f"✅ Слово {word} добавлено в словарь {lang}")
        else:
            bot.reply_to(message, f"❌ Слово {word} уже есть")
    except:
        bot.reply_to(message, "❌ Ошибка! Формат: ru СЛОВО")

@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.message_id in [g.message_id for g in active_games.values() if hasattr(g, 'message_id')])
def handle_guess(message):
    user_id = message.from_user.id
    
    if user_id not in active_games or not active_games[user_id].active:
        bot.send_message(message.chat.id, "Игра не активна. Начните новую командой /start")
        return
    
    game = active_games[user_id]
    guess_text = message.text.strip().upper()
    result, msg = game.guess_letter(guess_text)
    
    if not game.active:
        bot.edit_message_text(msg, message.chat.id, game.message_id)
        del active_games[user_id]
        user = get_user(user_id)
        menu_text = f"🎮 УГАДАЙ СЛОВО\n\n💰 Кристаллов: {user['crystals']}\n🏆 Побед: {user['wins']}"
        bot.send_message(message.chat.id, menu_text, reply_markup=main_menu_kb())
    else:
        display = game.get_display_word()
        wrong = ", ".join(game.wrong_letters) if game.wrong_letters else "—"
        text = f"""⏱️ УГАДАЙ СЛОВО — {game.get_time_left()} сек

Слово: {display}
Попыток: {game.attempts}
❌ Уже называли: {wrong}
💎 За победу: +50

{msg}

Напишите букву или слово целиком:"""
        
        bot.edit_message_text(text, message.chat.id, game.message_id, reply_markup=types.ForceReply(selective=True))
    
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

if __name__ == "__main__":
    print("🤖 Guess Word Bot запущен")
    print("Бот работает...")
    print("Команды: /start, /stats, /top, /shop, /lang, /help, /admin")
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")