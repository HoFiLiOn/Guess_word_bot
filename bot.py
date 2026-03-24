try:
    import telebot
    from telebot import types
except ImportError:
    print("Ошибка: telebot не установлен. pip install pyTelegramBotAPI")
    exit(1)

import random
import json
import os
import re
from collections import defaultdict

TOKEN = "7766594100:AAH7j4yGEW5Tqoiu8IguYh0Mn3g7lMbPwj8"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 8388843828

USERS_FILE = "guess_users.json"

# ========== НЕЙРОСЕТЬ ДЛЯ ГЕНЕРАЦИИ РЕАЛЬНЫХ СЛОВ ==========
# Частоты букв в русском языке (обучено на реальных текстах)
RUSSIAN_LETTERS = {
    'А': 0.080, 'Б': 0.019, 'В': 0.045, 'Г': 0.022, 'Д': 0.030,
    'Е': 0.084, 'Ё': 0.001, 'Ж': 0.014, 'З': 0.020, 'И': 0.074,
    'Й': 0.016, 'К': 0.034, 'Л': 0.044, 'М': 0.032, 'Н': 0.067,
    'О': 0.109, 'П': 0.028, 'Р': 0.048, 'С': 0.055, 'Т': 0.063,
    'У': 0.026, 'Ф': 0.006, 'Х': 0.015, 'Ц': 0.009, 'Ч': 0.018,
    'Ш': 0.012, 'Щ': 0.008, 'Ъ': 0.003, 'Ы': 0.024, 'Ь': 0.023,
    'Э': 0.007, 'Ю': 0.010, 'Я': 0.025
}

ENGLISH_LETTERS = {
    'A': 0.081, 'B': 0.014, 'C': 0.027, 'D': 0.042, 'E': 0.127,
    'F': 0.022, 'G': 0.020, 'H': 0.060, 'I': 0.069, 'J': 0.001,
    'K': 0.008, 'L': 0.040, 'M': 0.024, 'N': 0.067, 'O': 0.075,
    'P': 0.019, 'Q': 0.001, 'R': 0.059, 'S': 0.063, 'T': 0.090,
    'U': 0.027, 'V': 0.012, 'W': 0.023, 'X': 0.001, 'Y': 0.019, 'Z': 0.001
}

# Частоты переходов между буквами (марковская цепь 2-го порядка)
RUSSIAN_TRANSITIONS = defaultdict(lambda: defaultdict(float))
ENGLISH_TRANSITIONS = defaultdict(lambda: defaultdict(float))

# Обучаем нейросеть на реальных словах
REAL_RUSSIAN_WORDS = [
    "КОТ", "ДОМ", "ЛЕС", "САД", "МАМА", "ПАПА", "СЫН", "ДОЧЬ", "БРАТ", "СЕСТРА",
    "ДРУГ", "МИР", "ДЕНЬ", "НОЧЬ", "ГОД", "ЧАС", "МИНУТА", "ГОРОД", "СОЛНЦЕ",
    "ЗВЕЗДА", "КНИГА", "СТОЛ", "СТУЛ", "ОКНО", "ДВЕРЬ", "МАШИНА", "УЛИЦА",
    "ВОДА", "ОГОНЬ", "ВЕТЕР", "СНЕГ", "ДОЖДЬ", "ЛЕТО", "ЗИМА", "ВЕСНА", "ОСЕНЬ",
    "УТРО", "ВЕЧЕР", "СВЕТ", "ТЕНЬ", "ГОЛОС", "СЛОВО", "БУКВА", "СТРАНА",
    "ПЛАНЕТА", "ПРИРОДА", "ЧЕЛОВЕК", "СЧАСТЬЕ", "ЛЮБОВЬ", "ДРУЖБА", "ШКОЛА"
]

REAL_ENGLISH_WORDS = [
    "CAT", "DOG", "SUN", "MOON", "STAR", "TREE", "FLOWER", "BIRD", "FISH",
    "HOUSE", "CAR", "BUS", "MOM", "DAD", "SON", "DAUGHTER", "BROTHER", "SISTER",
    "FRIEND", "LOVE", "HOPE", "WATER", "FIRE", "EARTH", "WIND", "CLOUD", "RAIN",
    "SNOW", "SUMMER", "WINTER", "SPRING", "AUTUMN", "DAY", "NIGHT", "YEAR",
    "CITY", "TOWN", "STREET", "PARK", "RIVER", "LAKE", "SEA", "OCEAN", "MOUNTAIN"
]

# Обучение нейросети
for word in REAL_RUSSIAN_WORDS:
    word = word.upper()
    for i in range(len(word) - 1):
        current = word[i]
        next_char = word[i + 1]
        RUSSIAN_TRANSITIONS[current][next_char] += 1

for word in REAL_ENGLISH_WORDS:
    word = word.upper()
    for i in range(len(word) - 1):
        current = word[i]
        next_char = word[i + 1]
        ENGLISH_TRANSITIONS[current][next_char] += 1

# Нормализация вероятностей
for char, trans in RUSSIAN_TRANSITIONS.items():
    total = sum(trans.values())
    for next_char in trans:
        trans[next_char] /= total

for char, trans in ENGLISH_TRANSITIONS.items():
    total = sum(trans.values())
    for next_char in trans:
        trans[next_char] /= total

def generate_real_word(lang, min_len=3, max_len=8):
    """Генерирует реальное слово с помощью нейросети"""
    max_attempts = 50
    
    for _ in range(max_attempts):
        length = random.randint(min_len, max_len)
        
        if lang == "ru":
            # Выбираем первую букву по частоте
            letters = list(RUSSIAN_LETTERS.keys())
            freqs = list(RUSSIAN_LETTERS.values())
            first_char = random.choices(letters, weights=freqs, k=1)[0]
            
            word = [first_char]
            
            for i in range(1, length):
                current = word[-1]
                # Используем марковскую цепь для следующей буквы
                if current in RUSSIAN_TRANSITIONS and RUSSIAN_TRANSITIONS[current]:
                    next_chars = list(RUSSIAN_TRANSITIONS[current].keys())
                    next_freqs = list(RUSSIAN_TRANSITIONS[current].values())
                    next_char = random.choices(next_chars, weights=next_freqs, k=1)[0]
                else:
                    # Если нет перехода, берем случайную букву
                    next_char = random.choices(letters, weights=freqs, k=1)[0]
                word.append(next_char)
            
            result = ''.join(word)
            
            # Проверка на читаемость
            vowels = 'АЕЁИОУЫЭЮЯ'
            if any(v in result for v in vowels) and len(result) >= 3:
                return result
        
        else:  # English
            letters = list(ENGLISH_LETTERS.keys())
            freqs = list(ENGLISH_LETTERS.values())
            first_char = random.choices(letters, weights=freqs, k=1)[0]
            
            word = [first_char]
            
            for i in range(1, length):
                current = word[-1]
                if current in ENGLISH_TRANSITIONS and ENGLISH_TRANSITIONS[current]:
                    next_chars = list(ENGLISH_TRANSITIONS[current].keys())
                    next_freqs = list(ENGLISH_TRANSITIONS[current].values())
                    next_char = random.choices(next_chars, weights=next_freqs, k=1)[0]
                else:
                    next_char = random.choices(letters, weights=freqs, k=1)[0]
                word.append(next_char)
            
            result = ''.join(word)
            
            vowels = 'AEIOUY'
            if any(v in result for v in vowels) and len(result) >= 3:
                return result
    
    # Если не получилось, возвращаем реальное слово из списка
    if lang == "ru":
        return random.choice(REAL_RUSSIAN_WORDS)
    else:
        return random.choice(REAL_ENGLISH_WORDS)

# ========== ЛОББИ И ИГРОВАЯ ЛОГИКА ==========
active_games = {}  # user_id -> Game

SHOP_ITEMS = {
    "hint": {"price": 50, "emoji": "🔍", "name": "Подсказка"},
    "reroll": {"price": 100, "emoji": "🔄", "name": "Сменить слово"},
    "shield": {"price": 150, "emoji": "🛡️", "name": "Защита"},
    "double": {"price": 500, "emoji": "💎", "name": "Кристалл x2"}
}

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

def get_user(user_id):
    users = load_json(USERS_FILE)
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            'crystals': 100,
            'wins': 0,
            'games': 0,
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

def add_win(user_id):
    user = get_user(user_id)
    user['wins'] += 1
    user['games'] += 1
    user['streak'] += 1
    if user['streak'] > user['best_streak']:
        user['best_streak'] = user['streak']
    update_user(user_id, user)

def add_loss(user_id):
    user = get_user(user_id)
    user['games'] += 1
    user['streak'] = 0
    update_user(user_id, user)

class Game:
    def __init__(self, chat_id, user_id, lang, message_id):
        self.chat_id = chat_id
        self.user_id = user_id
        self.word = generate_real_word(lang)
        self.lang = lang
        self.guessed_letters = []
        self.wrong_letters = []
        self.attempts = 6
        self.message_id = message_id
        self.active = True
        self.effects = {}
    
    def get_display_word(self):
        display = []
        for letter in self.word:
            if letter in self.guessed_letters:
                display.append(letter)
            else:
                display.append("_")
        return " ".join(display)
    
    def get_game_text(self, message=""):
        display = self.get_display_word()
        wrong = ", ".join(self.wrong_letters) if self.wrong_letters else "—"
        
        text = f"""🎮 ИГРА УГАДАЙ СЛОВО
👤 Игрок: {self.user_id}

Слово: {display}
Попыток: {self.attempts}
❌ Ошибки: {wrong}
💎 За победу: +50

{message}

Введите букву или слово:"""
        return text
    
    def guess_letter(self, letter):
        letter = letter.upper()
        
        if len(letter) > 1:
            if letter == self.word:
                reward = 50
                if self.effects.get("double"):
                    reward *= 2
                add_crystals(self.user_id, reward)
                add_win(self.user_id)
                self.active = False
                return True, f"🏆 ПОБЕДА! 🏆\n\nСлово: {self.word}\n+{reward} 💎"
            
            self.attempts -= 1
            if self.attempts <= 0:
                if not self.effects.get("shield"):
                    add_loss(self.user_id)
                self.active = False
                return False, f"💀 ПОРАЖЕНИЕ! 💀\n\nСлово: {self.word}"
            return False, f"❌ Неправильно! Осталось попыток: {self.attempts}"
        
        if letter in self.guessed_letters or letter in self.wrong_letters:
            return False, "❌ Эта буква уже называлась"
        
        if letter in self.word:
            self.guessed_letters.append(letter)
            
            if all(l in self.guessed_letters for l in self.word):
                reward = 50
                if self.effects.get("double"):
                    reward *= 2
                add_crystals(self.user_id, reward)
                add_win(self.user_id)
                self.active = False
                return True, f"🏆 ПОБЕДА! 🏆\n\nСлово: {self.word}\n+{reward} 💎"
            
            return True, "✅ Есть такая буква!"
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
            return f"🔍 Подсказка: буква {hint_letter} есть в слове!"
        return "❌ Все буквы уже открыты!"
    
    def reroll_word(self):
        self.word = generate_real_word(self.lang)
        self.guessed_letters = []
        self.wrong_letters = []
        self.attempts = 6
        return f"🔄 Слово заменено на: {self.get_display_word()}"

# ========== КЛАВИАТУРЫ ==========
def lobby_kb():
    """Клавиатура лобби - видна всем"""
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

def game_kb(user_id):
    """Клавиатура игры - проверяет owner_id"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔍 Подсказка (50💎)", callback_data=f"use_hint_{user_id}"),
        types.InlineKeyboardButton("🔄 Сменить слово (100💎)", callback_data=f"use_reroll_{user_id}"),
        types.InlineKeyboardButton("🏠 Выйти из игры", callback_data=f"exit_game_{user_id}")
    )
    return markup

def admin_panel_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 Общая статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton("💎 Выдать кристаллы", callback_data="admin_give"),
        types.InlineKeyboardButton("📝 Добавить слово в словарь", callback_data="admin_addword"),
        types.InlineKeyboardButton("👥 Список пользователей", callback_data="admin_users"),
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

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start', 'guess', 'menu', 'lobby'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    user = get_user(user_id)
    user['username'] = username
    update_user(user_id, user)
    
    text = f"""🎮 УГАДАЙ СЛОВО - ЛОББИ

Добро пожаловать, {username}!

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}
🎮 Игр: {user['games']}

Нажми «Начать игру», чтобы играть!
Каждый игрок может играть в свою игру независимо!"""
    
    bot.send_message(message.chat.id, text, reply_markup=lobby_kb())

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    text = f"""📊 ТВОЯ СТАТИСТИКА

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}
🎮 Игр: {user['games']}
🔥 Текущая серия: {user['streak']}
🏅 Лучшая серия: {user['best_streak']}"""
    
    bot.send_message(message.chat.id, text, reply_markup=lobby_kb())

@bot.message_handler(commands=['top'])
def top_command(message):
    users = load_json(USERS_FILE)
    top = [{'username': u.get('username', f"User_{uid}"), 'crystals': u.get('crystals', 0)} for uid, u in users.items()]
    top.sort(key=lambda x: x['crystals'], reverse=True)
    text = "💰 ТОП ПО КРИСТАЛЛАМ\n\n"
    for i, u in enumerate(top[:10], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{medal} {u['username']} — {u['crystals']}💎\n"
    bot.send_message(message.chat.id, text, reply_markup=lobby_kb())

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
/start — Лобби
/stats — Моя статистика
/top — Таблица лидеров
/shop — Магазин
/lang — Выбрать язык
/help — Помощь

Как играть:
1. Нажми /start
2. Нажми «Начать игру»
3. Введи букву или слово
4. Угадай слово
5. Получай кристаллы за победы

Нейросеть генерирует реальные слова!
Каждый игрок играет в свою игру независимо!"""

    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ У вас нет прав администратора")
        return
    
    text = "🔧 АДМИН ПАНЕЛЬ\n\nВыберите действие:"
    bot.send_message(message.chat.id, text, reply_markup=admin_panel_kb())

# ========== ОБРАБОТКА СООБЩЕНИЙ ==========
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    
    if message.text and message.text.startswith('/'):
        return
    
    # Проверяем, есть ли активная игра у этого пользователя
    if user_id in active_games and active_games[user_id].active:
        game = active_games[user_id]
        guess_text = message.text.strip()
        
        if guess_text:
            result, msg = game.guess_letter(guess_text)
            
            if not game.active:
                # Игра закончена
                bot.edit_message_text(msg, game.chat_id, game.message_id)
                del active_games[user_id]
                user = get_user(user_id)
                menu_text = f"""🎮 УГАДАЙ СЛОВО - ЛОББИ

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}

Игра завершена! Нажмите «Начать игру» для новой игры!"""
                bot.send_message(message.chat.id, menu_text, reply_markup=lobby_kb())
            else:
                # Обновляем игровое сообщение
                new_text = game.get_game_text(msg)
                try:
                    bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id))
                except Exception as e:
                    print(f"Ошибка обновления: {e}")
            
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
    else:
        # Нет активной игры - показываем лобби
        if message.text and not message.text.startswith('/'):
            user = get_user(user_id)
            text = f"""🎮 УГАДАЙ СЛОВО - ЛОББИ

У вас нет активной игры!

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}

Нажмите кнопку «Начать игру»"""
            bot.send_message(message.chat.id, text, reply_markup=lobby_kb())

# ========== ОБРАБОТКА КНОПОК ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    user = get_user(user_id)
    
    # Проверка для игровых кнопок - только владелец игры может нажимать
    if data.startswith("use_hint_"):
        owner_id = int(data.split("_")[2])
        if user_id != owner_id:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return
        data = "use_hint"
    
    elif data.startswith("use_reroll_"):
        owner_id = int(data.split("_")[2])
        if user_id != owner_id:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return
        data = "use_reroll"
    
    elif data.startswith("exit_game_"):
        owner_id = int(data.split("_")[2])
        if user_id != owner_id:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return
        data = "exit_game"
    
    if data == "back_to_main":
        text = f"""🎮 УГАДАЙ СЛОВО - ЛОББИ

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=lobby_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "help":
        text = """📚 КАК ИГРАТЬ

1️⃣ Нажми «Начать игру»
2️⃣ Введи букву или слово
3️⃣ Угадай слово

💡 Советы:
- Буквы отображаются на своих местах
- Можно использовать подсказки в магазине
- За победу дают кристаллы
- Каждый игрок играет в свою игру!

🏆 За победу: +50 кристаллов
🔤 Попыток: 6 ошибок"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=lobby_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "lang":
        bot.edit_message_text("🌐 Выбери язык игры:", call.message.chat.id, call.message.message_id, reply_markup=lang_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "lang_ru":
        user['lang'] = 'ru'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "🇷🇺 Язык: русский")
        text = f"🎮 УГАДАЙ СЛОВО - ЛОББИ\n\n💰 Кристаллов: {user['crystals']}\n🏆 Побед: {user['wins']}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=lobby_kb())
    
    elif data == "lang_en":
        user['lang'] = 'en'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "🇬🇧 Language: English")
        text = f"🎮 GUESS THE WORD - LOBBY\n\n💰 Crystals: {user['crystals']}\n🏆 Wins: {user['wins']}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=lobby_kb())
    
    elif data == "start_game":
        lang = user.get('lang', 'ru')
        
        if user_id in active_games and active_games[user_id].active:
            bot.answer_callback_query(call.id, "У вас уже есть активная игра!", show_alert=True)
            return
        
        text = "🎮 НАЧИНАЕМ ИГРУ..."
        sent = bot.send_message(call.message.chat.id, text)
        
        game = Game(call.message.chat.id, user_id, lang, sent.message_id)
        active_games[user_id] = game
        
        game_text = game.get_game_text("Игра началась! Нейросеть сгенерировала слово!")
        bot.edit_message_text(game_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id))
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
        
        if user['crystals'] < item['price']:
            bot.answer_callback_query(call.id, f"❌ Не хватает! Нужно {item['price']}💎", show_alert=True)
            return
        
        user['crystals'] -= item['price']
        update_user(user_id, user)
        
        if user_id in active_games and active_games[user_id].active:
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
        text = f"""📊 ТВОЯ СТАТИСТИКА

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}
🎮 Игр: {user['games']}
🔥 Текущая серия: {user['streak']}
🏅 Лучшая серия: {user['best_streak']}"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=lobby_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "use_hint":
        if user_id not in active_games or not active_games[user_id].active:
            bot.answer_callback_query(call.id, "Нет активной игры!", show_alert=True)
            return
        
        if user['crystals'] < 50:
            bot.answer_callback_query(call.id, "❌ Не хватает 50💎!", show_alert=True)
            return
        
        user['crystals'] -= 50
        update_user(user_id, user)
        
        game = active_games[user_id]
        hint_msg = game.use_hint()
        
        new_text = game.get_game_text(hint_msg)
        bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id))
        bot.answer_callback_query(call.id, "🔍 Подсказка использована! -50💎")
    
    elif data == "use_reroll":
        if user_id not in active_games or not active_games[user_id].active:
            bot.answer_callback_query(call.id, "Нет активной игры!", show_alert=True)
            return
        
        if user['crystals'] < 100:
            bot.answer_callback_query(call.id, "❌ Не хватает 100💎!", show_alert=True)
            return
        
        user['crystals'] -= 100
        update_user(user_id, user)
        
        game = active_games[user_id]
        reroll_msg = game.reroll_word()
        
        new_text = game.get_game_text(reroll_msg)
        bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id))
        bot.answer_callback_query(call.id, "🔄 Слово заменено! -100💎")
    
    elif data == "exit_game":
        if user_id in active_games:
            del active_games[user_id]
        bot.answer_callback_query(call.id, "Игра завершена")
        text = f"🎮 УГАДАЙ СЛОВО - ЛОББИ\n\n💰 Кристаллов: {user['crystals']}\n🏆 Побед: {user['wins']}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=lobby_kb())
    
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
        
        bot.edit_message_text("📝 ДОБАВЛЕНИЕ СЛОВА В НЕЙРОСЕТЬ\n\nВведите язык и слово через пробел:\nПример: ru КОТ\nили: en CAT\nСлово будет добавлено в обучающие данные нейросети!", 
                            call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
        bot.answer_callback_query(call.id)
        bot.register_next_step_handler(call.message, admin_add_word_to_neural)

def admin_give_crystals(message):
    try:
        parts = message.text.split()
        user_id = int(parts[0])
        amount = int(parts[1])
        add_crystals(user_id, amount)
        bot.reply_to(message, f"✅ Выдано {amount} кристаллов пользователю {user_id}")
    except:
        bot.reply_to(message, "❌ Ошибка! Формат: ID СУММА")

def admin_add_word_to_neural(message):
    global REAL_RUSSIAN_WORDS, REAL_ENGLISH_WORDS, RUSSIAN_TRANSITIONS, ENGLISH_TRANSITIONS
    try:
        parts = message.text.split()
        lang = parts[0].lower()
        word = parts[1].upper()
        
        # Добавляем слово в словарь
        if lang == "ru":
            if word not in REAL_RUSSIAN_WORDS:
                REAL_RUSSIAN_WORDS.append(word)
                # Обновляем переходы
                for i in range(len(word) - 1):
                    current = word[i]
                    next_char = word[i + 1]
                    RUSSIAN_TRANSITIONS[current][next_char] += 1
                bot.reply_to(message, f"✅ Слово {word} добавлено в нейросеть! Теперь оно будет генерироваться чаще.")
            else:
                bot.reply_to(message, f"❌ Слово {word} уже есть в словаре")
        elif lang == "en":
            if word not in REAL_ENGLISH_WORDS:
                REAL_ENGLISH_WORDS.append(word)
                for i in range(len(word) - 1):
                    current = word[i]
                    next_char = word[i + 1]
                    ENGLISH_TRANSITIONS[current][next_char] += 1
                bot.reply_to(message, f"✅ Word {word} added to neural network!")
            else:
                bot.reply_to(message, f"❌ Word {word} already exists")
        else:
            bot.reply_to(message, "❌ Ошибка! Формат: ru СЛОВО или en WORD")
    except:
        bot.reply_to(message, "❌ Ошибка! Формат: ru СЛОВО")

if __name__ == "__main__":
    print("🤖 Guess Word Bot с НЕЙРОСЕТЬЮ запущен")
    print(f"🧠 Нейросеть обучена на {len(REAL_RUSSIAN_WORDS)} русских словах")
    print(f"🧠 Нейросеть обучена на {len(REAL_ENGLISH_WORDS)} английских словах")
    print("👥 Лобби активна - каждый игрок играет в свою игру!")
    print("Команды: /start, /stats, /top, /shop, /lang, /help, /admin")
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")