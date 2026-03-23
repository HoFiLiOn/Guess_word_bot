import telebot
from telebot import types
import random
import json
import os
import time
import threading
import string
from datetime import datetime
import re

TOKEN = "7766594100:AAH7j4yGEW5Tqoiu8IguYh0Mn3g7lMbPwj8"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 8388843828

USERS_FILE = "guess_users.json"
WORDS_FILE = "guess_words.json"

DEFAULT_WORDS = {
    "ru": ["КОТ", "ДОМ", "ЛЕС", "ГОРОД", "МАШИНА", "СОЛНЦЕ", "ЗВЕЗДА", "КНИГА", "СТОЛ", "ДРУГ"],
    "en": ["CAT", "DOG", "HOUSE", "CAR", "COMPUTER", "SUN", "STAR", "BOOK", "TABLE", "FRIEND"]
}

SHOP_ITEMS = {
    "hint": {"name": "🔍 Подсказка", "price": 50, "emoji": "🔍", "desc": "Открывает одну случайную букву"},
    "time": {"name": "⏱️ +15 секунд", "price": 75, "emoji": "⏱️", "desc": "Добавляет 15 секунд к таймеру"},
    "reroll": {"name": "🔄 Сменить слово", "price": 100, "emoji": "🔄", "desc": "Заменяет текущее слово"},
    "shield": {"name": "🛡️ Защита", "price": 150, "emoji": "🛡️", "desc": "Не теряешь кристаллы при проигрыше"},
    "double": {"name": "💎 Кристалл x2", "price": 500, "emoji": "💎", "desc": "Удваивает выигрыш"}
}

# Хранилище активных игр
active_games = {}

def load_json(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_random_word(lang, length=6):
    if lang == "en":
        letters = string.ascii_uppercase
    else:
        letters = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    return ''.join(random.choices(letters, k=length))

def is_playable(word):
    for i in range(len(word)-2):
        if word[i] == word[i+1] == word[i+2]:
            return False
    return True

def get_word(lang):
    words_dict = load_json(WORDS_FILE)
    if lang not in words_dict or not words_dict[lang]:
        words_dict[lang] = DEFAULT_WORDS[lang].copy()
        save_json(WORDS_FILE, words_dict)
    
    if random.random() < 0.3:
        while True:
            word = generate_random_word(lang)
            if is_playable(word):
                return word
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

def deduct_crystals(user_id, amount):
    user = get_user(user_id)
    if user['crystals'] >= amount:
        user['crystals'] -= amount
        update_user(user_id, user)
        return True
    return False

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
        
        if len(letter) > 1:
            if letter == self.word:
                time_taken = int(time.time() - self.start_time)
                reward = 50
                if self.effects.get("double"):
                    reward *= 2
                    del self.effects["double"]
                add_crystals(self.user_id, reward)
                add_win(self.user_id, time_taken)
                self.active = False
                return True, f"🏆 ПОБЕДА! 🏆\n\nСлово: {self.word}\n⏱️ Время: {time_taken} сек\n+{reward} 💎"
            
            self.attempts -= 1
            if self.attempts <= 0:
                if not self.effects.get("shield"):
                    add_loss(self.user_id)
                else:
                    del self.effects["shield"]
                self.active = False
                return False, f"💀 ПОРАЖЕНИЕ! 💀\n\nСлово: {self.word}"
            return False, f"❌ Неправильно! Осталось попыток: {self.attempts}"
        
        if letter in self.guessed_letters or letter in self.wrong_letters:
            return False, "❌ Эта буква уже называлась"
        
        if letter in self.word:
            self.guessed_letters.append(letter)
            if all(l in self.guessed_letters for l in self.word):
                time_taken = int(time.time() - self.start_time)
                reward = 50
                if self.effects.get("double"):
                    reward *= 2
                    del self.effects["double"]
                add_crystals(self.user_id, reward)
                add_win(self.user_id, time_taken)
                self.active = False
                return True, f"🏆 ПОБЕДА! 🏆\n\nСлово: {self.word}\n⏱️ Время: {time_taken} сек\n+{reward} 💎"
            return True, "✅ Есть такая буква!"
        else:
            self.wrong_letters.append(letter)
            self.attempts -= 1
            if self.attempts <= 0:
                if not self.effects.get("shield"):
                    add_loss(self.user_id)
                else:
                    del self.effects["shield"]
                self.active = False
                return False, f"💀 ПОРАЖЕНИЕ! 💀\n\nСлово: {self.word}"
            return False, f"❌ Нет такой буквы! Осталось попыток: {self.attempts}"
    
    def use_hint(self):
        not_guessed = [l for l in self.word if l not in self.guessed_letters]
        if not_guessed:
            hint_letter = random.choice(not_guessed)
            self.guessed_letters.append(hint_letter)
            return f"🔍 Подсказка: буква {hint_letter} есть в слове!"
        return "❌ Все буквы уже открыты!"
    
    def add_time(self):
        self.time_extension += 15
        return f"⏱️ Добавлено 15 секунд! Осталось: {self.get_time_left()} сек"
    
    def reroll_word(self):
        self.word = get_word(self.lang).upper()
        self.guessed_letters = []
        self.wrong_letters = []
        self.attempts = 6
        return f"🔄 Слово заменено! Новое слово: {self.get_display_word()}"

def main_menu_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎮 Начать игру", callback_data="start_game"),
        types.InlineKeyboardButton("🛒 Магазин", callback_data="shop"),
        types.InlineKeyboardButton("🏆 Топ", callback_data="top"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        types.InlineKeyboardButton("🌐 Язык", callback_data="lang")
    )
    return markup

def game_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔍 Подсказка (50💎)", callback_data="use_hint"),
        types.InlineKeyboardButton("⏱️ +15 сек (75💎)", callback_data="use_time"),
        types.InlineKeyboardButton("🔄 Сменить слово (100💎)", callback_data="use_reroll"),
        types.InlineKeyboardButton("🏠 Выход", callback_data="exit_game")
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

@bot.message_handler(commands=['start', 'guess', 'stats', 'top', 'shop', 'lang', 'help', 'menu'])
def handle_commands(message):
    cmd = message.text.split()[0].replace('/', '').lower()
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    user = get_user(user_id)
    user['username'] = username
    update_user(user_id, user)
    
    if cmd in ['start', 'guess', 'menu']:
        text = f"""🎮 УГАДАЙ СЛОВО

Добро пожаловать, {username}!

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}
🎮 Игр: {user['games']}

Нажми «Начать игру», чтобы играть!"""
        bot.send_message(message.chat.id, text, reply_markup=main_menu_kb())
    
    elif cmd == 'stats':
        text = f"""📊 ТВОЯ СТАТИСТИКА

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}
🎮 Игр: {user['games']}
⚡ Лучшее время: {user['fastest_win'] or '—'} сек
🔥 Текущая серия: {user['streak']}
🏅 Лучшая серия: {user['best_streak']}"""
        bot.send_message(message.chat.id, text, reply_markup=main_menu_kb())
    
    elif cmd == 'top':
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'crystals': u.get('crystals', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['crystals'], reverse=True)
        text = "💰 ТОП ПО КРИСТАЛЛАМ\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['crystals']}💎\n"
        bot.send_message(message.chat.id, text, reply_markup=main_menu_kb())
    
    elif cmd == 'shop':
        text = "🛒 МАГАЗИН\n\nВыбери товар в меню ниже:"
        bot.send_message(message.chat.id, text, reply_markup=shop_kb())
    
    elif cmd == 'lang':
        text = "🌐 Выбери язык игры:"
        bot.send_message(message.chat.id, text, reply_markup=lang_kb())
    
    elif cmd == 'help':
        text = """📚 ПОМОЩЬ

Команды:
/start — главное меню
/guess — главное меню
/stats — моя статистика
/top — таблица лидеров
/shop — магазин
/lang — выбрать язык

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

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    
    if data == "back_to_main":
        user = get_user(user_id)
        text = f"""🎮 УГАДАЙ СЛОВО

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}"""
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
        text = f"""🎮 УГАДАЙ СЛОВО

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb())
    
    elif data == "lang_en":
        user = get_user(user_id)
        user['lang'] = 'en'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "🇬🇧 Language: English")
        text = f"""🎮 GUESS THE WORD

💰 Crystals: {user['crystals']}
🏆 Wins: {user['wins']}"""
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

Отвечай на это сообщение"""
        
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
    
    elif data == "use_hint":
        if user_id not in active_games or not active_games[user_id].active:
            bot.answer_callback_query(call.id, "Нет активной игры!", show_alert=True)
            return
        
        user = get_user(user_id)
        if user['crystals'] < 50:
            bot.answer_callback_query(call.id, "❌ Не хватает 50💎!", show_alert=True)
            return
        
        user['crystals'] -= 50
        update_user(user_id, user)
        
        game = active_games[user_id]
        hint_msg = game.use_hint()
        
        display = game.get_display_word()
        wrong = ", ".join(game.wrong_letters) if game.wrong_letters else "—"
        text = f"""⏱️ УГАДАЙ СЛОВО — {game.get_time_left()} сек

Слово: {display}
Попыток: {game.attempts}
❌ Уже называли: {wrong}
💎 За победу: +50

{hint_msg}

Отвечай на это сообщение"""
        
        bot.edit_message_text(text, call.message.chat.id, game.message_id, reply_markup=types.ForceReply(selective=True))
        bot.answer_callback_query(call.id, "🔍 Подсказка использована! -50💎")
    
    elif data == "use_time":
        if user_id not in active_games or not active_games[user_id].active:
            bot.answer_callback_query(call.id, "Нет активной игры!", show_alert=True)
            return
        
        user = get_user(user_id)
        if user['crystals'] < 75:
            bot.answer_callback_query(call.id, "❌ Не хватает 75💎!", show_alert=True)
            return
        
        user['crystals'] -= 75
        update_user(user_id, user)
        
        game = active_games[user_id]
        time_msg = game.add_time()
        
        display = game.get_display_word()
        wrong = ", ".join(game.wrong_letters) if game.wrong_letters else "—"
        text = f"""⏱️ УГАДАЙ СЛОВО — {game.get_time_left()} сек

Слово: {display}
Попыток: {game.attempts}
❌ Уже называли: {wrong}
💎 За победу: +50

{time_msg}

Отвечай на это сообщение"""
        
        bot.edit_message_text(text, call.message.chat.id, game.message_id, reply_markup=types.ForceReply(selective=True))
        bot.answer_callback_query(call.id, "⏱️ +15 секунд! -75💎")
    
    elif data == "use_reroll":
        if user_id not in active_games or not active_games[user_id].active:
            bot.answer_callback_query(call.id, "Нет активной игры!", show_alert=True)
            return
        
        user = get_user(user_id)
        if user['crystals'] < 100:
            bot.answer_callback_query(call.id, "❌ Не хватает 100💎!", show_alert=True)
            return
        
        user['crystals'] -= 100
        update_user(user_id, user)
        
        game = active_games[user_id]
        reroll_msg = game.reroll_word()
        
        display = game.get_display_word()
        wrong = ", ".join(game.wrong_letters) if game.wrong_letters else "—"
        text = f"""⏱️ УГАДАЙ СЛОВО — {game.get_time_left()} сек

Слово: {display}
Попыток: {game.attempts}
❌ Уже называли: {wrong}
💎 За победу: +50

{reroll_msg}

Отвечай на это сообщение"""
        
        bot.edit_message_text(text, call.message.chat.id, game.message_id, reply_markup=types.ForceReply(selective=True))
        bot.answer_callback_query(call.id, "🔄 Слово заменено! -100💎")
    
    elif data == "exit_game":
        if user_id in active_games:
            del active_games[user_id]
        bot.answer_callback_query(call.id, "Игра завершена")
        user = get_user(user_id)
        text = f"""🎮 УГАДАЙ СЛОВО

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb())

@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.message_id in [g.message_id for g in active_games.values() if g.message_id])
def handle_guess(message):
    user_id = message.from_user.id
    
    if user_id not in active_games or not active_games[user_id].active:
        bot.send_message(message.chat.id, "Игра не активна. Начните новую командой /start")
        return
    
    game = active_games[user_id]
    guess_text = message.text.strip().upper()
    result, msg = game.guess_letter(guess_text)
    
    if not game.active:
        # Игра закончена
        bot.edit_message_text(msg, message.chat.id, game.message_id)
        del active_games[user_id]
        user = get_user(user_id)
        menu_text = f"""🎮 УГАДАЙ СЛОВО

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}"""
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

Отвечай на это сообщение"""
        bot.edit_message_text(text, message.chat.id, game.message_id, reply_markup=types.ForceReply(selective=True))
    
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

@bot.message_handler(commands=['addword'])
def add_word_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ У вас нет прав администратора")
        return
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ /addword ru/en СЛОВО")
            return
        lang = parts[1].lower()
        word = parts[2].upper()
        words = load_json(WORDS_FILE)
        if lang not in words:
            words[lang] = []
        if word not in words[lang]:
            words[lang].append(word)
            save_json(WORDS_FILE, words)
            bot.reply_to(message, f"✅ Слово {word} добавлено в словарь {lang}")
        else:
            bot.reply_to(message, f"❌ Слово {word} уже есть в словаре")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['addcrystals'])
def add_crystals_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ У вас нет прав администратора")
        return
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "❌ /addcrystals ID СУММА")
            return
        user_id = int(parts[1])
        amount = int(parts[2])
        add_crystals(user_id, amount)
        bot.reply_to(message, f"✅ Добавлено {amount} кристаллов пользователю {user_id}")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['words'])
def words_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    words = load_json(WORDS_FILE)
    text = "📚 СЛОВАРЬ\n\n"
    for lang, word_list in words.items():
        text += f"{lang}: {', '.join(word_list[:20])}\n"
        if len(word_list) > 20:
            text += f"... и еще {len(word_list)-20} слов\n"
        text += "\n"
    bot.reply_to(message, text)

if __name__ == "__main__":
    print("🤖 Guess Word Bot запущен")
    print("Доступные команды:")
    print("/start - Главное меню")
    print("/guess - Главное меню")
    print("/stats - Статистика")
    print("/top - Таблица лидеров")
    print("/shop - Магазин")
    print("/lang - Выбор языка")
    print("/help - Помощь")
    bot.infinity_polling()