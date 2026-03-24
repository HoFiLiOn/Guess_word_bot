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
from collections import defaultdict, Counter
from datetime import datetime

TOKEN = "7766594100:AAH7j4yGEW5Tqoiu8IguYh0Mn3g7lMbPwj8"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 8388843828

USERS_FILE = "guess_users.json"
DONATIONS_FILE = "donations.json"

# ========== УЛУЧШЕННАЯ НЕЙРОСЕТЬ ДЛЯ ГЕНЕРАЦИИ СЛОВ ==========
# Большой корпус реальных слов для обучения
RUSSIAN_WORDS_CORPUS = [
    "КОТ", "ДОМ", "ЛЕС", "САД", "РОЗА", "МАМА", "ПАПА", "СЫН", "ДОЧЬ", "БРАТ",
    "СЕСТРА", "ДРУГ", "МИР", "ДЕНЬ", "НОЧЬ", "ГОРОД", "СОЛНЦЕ", "ЗВЕЗДА", "КНИГА",
    "СТОЛ", "СТУЛ", "ОКНО", "ДВЕРЬ", "РУЧКА", "МАШИНА", "УЛИЦА", "ПАРК", "ЛУНА",
    "ЗЕМЛЯ", "ВОДА", "ОГОНЬ", "ВЕТЕР", "СНЕГ", "ДОЖДЬ", "ЛЕТО", "ЗИМА", "ВЕСНА",
    "ОСЕНЬ", "УТРО", "ВЕЧЕР", "СВЕТ", "ТЕНЬ", "ГОЛОС", "СЛОВО", "БУКВА", "СТРАНА",
    "ПЛАНЕТА", "ПРИРОДА", "ЧЕЛОВЕК", "СЧАСТЬЕ", "ЛЮБОВЬ", "ДРУЖБА", "ШКОЛА",
    "УЧИТЕЛЬ", "РАБОТА", "ДЕНЬГИ", "ВРЕМЯ", "МЫСЛЬ", "ИДЕЯ", "МЕЧТА", "НАДЕЖДА",
    "ВЕРА", "СИЛА", "ЭНЕРГИЯ", "КОСМОС", "ГАЛАКТИКА", "ВСЕЛЕННАЯ", "БЕСКОНЕЧНОСТЬ"
]

ENGLISH_WORDS_CORPUS = [
    "CAT", "DOG", "SUN", "MOON", "STAR", "TREE", "FLOWER", "BIRD", "FISH",
    "HOUSE", "CAR", "MOM", "DAD", "SON", "DAUGHTER", "BROTHER", "SISTER",
    "FRIEND", "LOVE", "HOPE", "WATER", "FIRE", "EARTH", "WIND", "CLOUD",
    "RAIN", "SNOW", "SUMMER", "WINTER", "SPRING", "AUTUMN", "DAY", "NIGHT",
    "CITY", "TOWN", "STREET", "PARK", "RIVER", "LAKE", "SEA", "OCEAN",
    "MOUNTAIN", "FOREST", "DESERT", "ISLAND", "SKY", "UNIVERSE", "GALAXY",
    "INFINITY", "ETERNITY", "DREAM", "HAPPINESS", "FREEDOM", "JUSTICE"
]

class AdvancedNeuralNetwork:
    """Улучшенная нейросеть для генерации реалистичных слов"""
    
    def __init__(self, lang):
        self.lang = lang
        self.ngram_order = 3  # Марковская цепь 3-го порядка
        self.ngrams = defaultdict(Counter)
        self.starts = Counter()
        self.ends = Counter()
        self.vowels = "АЕЁИОУЫЭЮЯ" if lang == "ru" else "AEIOUY"
        self.consonants = "БВГДЖЗЙКЛМНПРСТФХЦЧШЩ" if lang == "ru" else "BCDFGHJKLMNPQRSTVWXZ"
        
        # Обучаем на корпусе слов
        corpus = RUSSIAN_WORDS_CORPUS if lang == "ru" else ENGLISH_WORDS_CORPUS
        self._train(corpus)
    
    def _train(self, corpus):
        """Обучение на реальных словах"""
        for word in corpus:
            word = word.upper()
            if len(word) < 2:
                continue
            
            # Запоминаем начало слов
            prefix = word[:self.ngram_order]
            self.starts[prefix] += 1
            
            # Запоминаем конец слов
            suffix = word[-self.ngram_order:]
            self.ends[suffix] += 1
            
            # Собираем n-граммы
            for i in range(len(word) - self.ngram_order):
                context = word[i:i + self.ngram_order]
                next_char = word[i + self.ngram_order]
                self.ngrams[context][next_char] += 1
    
    def get_next_char(self, context):
        """Предсказывает следующую букву на основе контекста"""
        if context in self.ngrams and self.ngrams[context]:
            chars = list(self.ngrams[context].keys())
            weights = list(self.ngrams[context].values())
            return random.choices(chars, weights=weights, k=1)[0]
        return None
    
    def is_readable(self, word):
        """Проверяет, что слово читаемое"""
        if len(word) < 3:
            return False
        
        # Должна быть хотя бы одна гласная
        if not any(c in self.vowels for c in word):
            return False
        
        # Не должно быть 3+ согласных подряд
        cons_seq = 0
        for c in word:
            if c in self.consonants:
                cons_seq += 1
                if cons_seq >= 3:
                    return False
            else:
                cons_seq = 0
        
        # Не должно быть 3+ одинаковых букв подряд
        for i in range(len(word) - 2):
            if word[i] == word[i+1] == word[i+2]:
                return False
        
        return True
    
    def generate_word(self, min_len=3, max_len=10):
        """Генерирует новое слово"""
        max_attempts = 100
        
        for _ in range(max_attempts):
            length = random.randint(min_len, max_len)
            
            # Выбираем начало из частотных начал
            if self.starts:
                starts_list = list(self.starts.keys())
                starts_weights = list(self.starts.values())
                start = random.choices(starts_list, weights=starts_weights, k=1)[0]
            else:
                # Случайное начало
                letters = list(RUSSIAN_LETTERS.keys()) if self.lang == "ru" else list(ENGLISH_LETTERS.keys())
                start = random.choice(letters) * self.ngram_order
            
            word = list(start[:self.ngram_order])
            
            # Генерируем слово
            for i in range(length - self.ngram_order):
                context = ''.join(word[-self.ngram_order:])
                next_char = self.get_next_char(context)
                
                if next_char is None:
                    # Если нет предсказания, берем случайную букву
                    if self.lang == "ru":
                        letters = list(RUSSIAN_LETTERS.keys())
                        weights = list(RUSSIAN_LETTERS.values())
                        next_char = random.choices(letters, weights=weights, k=1)[0]
                    else:
                        letters = list(ENGLISH_LETTERS.keys())
                        weights = list(ENGLISH_LETTERS.values())
                        next_char = random.choices(letters, weights=weights, k=1)[0]
                
                word.append(next_char)
            
            result = ''.join(word)
            
            # Проверяем читаемость
            if self.is_readable(result):
                return result
        
        # Если не получилось, возвращаем реальное слово из корпуса
        corpus = RUSSIAN_WORDS_CORPUS if self.lang == "ru" else ENGLISH_WORDS_CORPUS
        return random.choice(corpus)

# Создаем нейросети
neural_networks = {
    "ru": AdvancedNeuralNetwork("ru"),
    "en": AdvancedNeuralNetwork("en")
}

# ========== ДОНАТ ЧЕРЕЗ TELEGRAM STARS ==========
# Цены: 1 Star = 50 кристаллов
DONATE_OPTIONS = {
    1: {"stars": 1, "crystals": 50, "bonus": 0, "emoji": "⭐"},
    2: {"stars": 2, "crystals": 100, "bonus": 10, "emoji": "⭐⭐"},
    5: {"stars": 5, "crystals": 250, "bonus": 30, "emoji": "⭐⭐⭐⭐⭐"},
    10: {"stars": 10, "crystals": 500, "bonus": 75, "emoji": "🔟⭐"},
    20: {"stars": 20, "crystals": 1000, "bonus": 200, "emoji": "💎⭐"},
    50: {"stars": 50, "crystals": 2500, "bonus": 750, "emoji": "👑⭐⭐⭐"}
}

SHOP_ITEMS = {
    "hint": {"price": 50, "emoji": "🔍", "name": "Подсказка"},
    "reroll": {"price": 100, "emoji": "🔄", "name": "Сменить слово"},
    "shield": {"price": 150, "emoji": "🛡️", "name": "Защита"},
    "double": {"price": 500, "emoji": "💎", "name": "Кристалл x2"}
}

active_games = {}

# ========== ФУНКЦИИ РАБОТЫ С ДАННЫМИ ==========
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

def save_donation(user_id, username, stars, crystals_given):
    """Сохраняет информацию о донате"""
    donations = load_json(DONATIONS_FILE)
    
    if 'donations' not in donations:
        donations['donations'] = []
    
    donation = {
        'user_id': user_id,
        'username': username,
        'stars': stars,
        'crystals': crystals_given,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    donations['donations'].append(donation)
    
    # Считаем общую статистику донатов
    if 'stats' not in donations:
        donations['stats'] = {}
    
    donations['stats']['total_stars'] = donations['stats'].get('total_stars', 0) + stars
    donations['stats']['total_crystals'] = donations['stats'].get('total_crystals', 0) + crystals_given
    donations['stats']['total_donations'] = donations['stats'].get('total_donations', 0) + 1
    
    save_json(DONATIONS_FILE, donations)

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
            'lang': 'ru',
            'donated_stars': 0,
            'donated_crystals': 0
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
        self.word = neural_networks[lang].generate_word()
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
        
        text = f"""🎮 УГАДАЙ СЛОВО (Нейросеть)
👤 Ваша игра

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
            return f"🔍 Подсказка: буква {hint_letter} есть в слове!\n\nСлово: {self.get_display_word()}"
        return "❌ Все буквы уже открыты!"
    
    def reroll_word(self):
        self.word = neural_networks[self.lang].generate_word()
        self.guessed_letters = []
        self.wrong_letters = []
        self.attempts = 6
        return f"🔄 Слово заменено на: {self.get_display_word()}"

# ========== КЛАВИАТУРЫ ==========
def lobby_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎮 Начать игру", callback_data="start_game"),
        types.InlineKeyboardButton("⭐ Поддержать (Донат)", callback_data="donate"),
        types.InlineKeyboardButton("🛒 Магазин", callback_data="shop"),
        types.InlineKeyboardButton("🏆 Топ игроков", callback_data="top"),
        types.InlineKeyboardButton("📊 Моя статистика", callback_data="stats"),
        types.InlineKeyboardButton("🌐 Выбрать язык", callback_data="lang"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="help")
    )
    return markup

def donate_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for stars, info in DONATE_OPTIONS.items():
        markup.add(types.InlineKeyboardButton(
            f"{info['emoji']} {stars} Star → {info['crystals'] + info['bonus']} 💎 (+{info['bonus']} бонус)",
            callback_data=f"donate_{stars}"
        ))
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
    return markup

def game_kb(user_id):
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
        types.InlineKeyboardButton("⭐ Статистика донатов", callback_data="admin_donations"),
        types.InlineKeyboardButton("💎 Выдать кристаллы", callback_data="admin_give"),
        types.InlineKeyboardButton("📝 Добавить слово в нейросеть", callback_data="admin_addword"),
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
        types.InlineKeyboardButton("⭐ По донатам", callback_data="top_donations"),
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

✨ Нейросеть генерирует уникальные слова!
⭐ Поддержи проект через Telegram Stars!

Нажми «Начать игру», чтобы играть!"""
    
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
🏅 Лучшая серия: {user['best_streak']}
⭐ Поддержал проект: {user.get('donated_stars', 0)} Stars"""
    
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

@bot.message_handler(commands=['donate'])
def donate_command(message):
    text = """⭐ ПОДДЕРЖАТЬ ПРОЕКТ

Поддержите разработку бота через Telegram Stars!

✨ 1 Star = 50 кристаллов + бонусы!

Выберите сумму доната:"""
    bot.send_message(message.chat.id, text, reply_markup=donate_kb())

@bot.message_handler(commands=['help'])
def help_command(message):
    text = """📚 ПОМОЩЬ

Команды:
/start — Лобби
/stats — Моя статистика
/top — Таблица лидеров
/shop — Магазин
/lang — Выбрать язык
/donate — Поддержать проект
/help — Помощь

Как играть:
1. Нажми /start
2. Нажми «Начать игру»
3. Введи букву или слово
4. Угадай слово

✨ Нейросеть генерирует уникальные слова!
⭐ Донат помогает развитию бота!

🏆 За победу: +50 кристаллов
🔤 Попыток: 6 ошибок"""

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
    
    if user_id in active_games and active_games[user_id].active:
        game = active_games[user_id]
        guess_text = message.text.strip()
        
        if guess_text:
            result, msg = game.guess_letter(guess_text)
            
            if not game.active:
                bot.edit_message_text(msg, game.chat_id, game.message_id)
                del active_games[user_id]
                user = get_user(user_id)
                menu_text = f"""🎮 УГАДАЙ СЛОВО - ЛОББИ

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}

Игра завершена! Нажмите «Начать игру» для новой игры!"""
                bot.send_message(message.chat.id, menu_text, reply_markup=lobby_kb())
            else:
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
    
    # Проверка для игровых кнопок
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
    
    elif data == "donate":
        text = """⭐ ПОДДЕРЖАТЬ ПРОЕКТ

Поддержите разработку бота через Telegram Stars!

✨ 1 Star = 50 кристаллов + бонусы!

Выберите сумму доната:"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=donate_kb())
        bot.answer_callback_query(call.id)
    
    elif data.startswith("donate_"):
        stars = int(data.split("_")[1])
        option = DONATE_OPTIONS[stars]
        
        total_crystals = option['crystals'] + option['bonus']
        
        prices = [types.LabeledPrice(label=f"{stars} Stars", amount=stars)]
        
        bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Поддержка бота",
            description=f"⭐ {stars} Stars\n✨ +{option['crystals']} кристаллов\n🎁 Бонус: +{option['bonus']} кристаллов\n💰 Итого: {total_crystals} кристаллов",
            invoice_payload=f"donate_{stars}_{total_crystals}_{user_id}",
            provider_token="",
            currency="XTR",
            prices=prices,
            start_parameter="donate"
        )
        bot.answer_callback_query(call.id)
    
    elif data == "help":
        text = """📚 КАК ИГРАТЬ

1️⃣ Нажми «Начать игру»
2️⃣ Введи букву или слово
3️⃣ Угадай слово

💡 Советы:
- Нейросеть генерирует уникальные слова
- Буквы отображаются на своих местах
- Можно использовать подсказки в магазине
- За победу дают кристаллы
- Поддержи проект через донат!

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
        
        text = "🎮 НАЧИНАЕМ ИГРУ...\n\n✨ Нейросеть генерирует слово..."
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
    
    elif data == "top_donations":
        donations = load_json(DONATIONS_FILE)
        users = load_json(USERS_FILE)
        
        # Собираем статистику донатов по пользователям
        user_donations = defaultdict(int)
        for d in donations.get('donations', []):
            user_donations[d['user_id']] += d['stars']
        
        top = []
        for uid, stars in user_donations.items():
            username = users.get(str(uid), {}).get('username', f"User_{uid}")
            top.append({'username': username, 'stars': stars})
        
        top.sort(key=lambda x: x['stars'], reverse=True)
        
        text = "⭐ ТОП ПО ДОНАТАМ\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['stars']} Stars\n"
        
        if not top:
            text += "Пока нет донатов. Будь первым! ⭐"
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "stats":
        text = f"""📊 ТВОЯ СТАТИСТИКА

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}
🎮 Игр: {user['games']}
🔥 Текущая серия: {user['streak']}
🏅 Лучшая серия: {user['best_streak']}
⭐ Поддержал проект: {user.get('donated_stars', 0)} Stars"""
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
        donations = load_json(DONATIONS_FILE)
        
        total_users = len(users)
        total_games = sum(u.get('games', 0) for u in users.values())
        total_wins = sum(u.get('wins', 0) for u in users.values())
        total_crystals = sum(u.get('crystals', 0) for u in users.values())
        total_stars = donations.get('stats', {}).get('total_stars', 0)
        total_donations = donations.get('stats', {}).get('total_donations', 0)
        
        text = f"""📊 ОБЩАЯ СТАТИСТИКА

👥 Всего игроков: {total_users}
🎮 Всего игр: {total_games}
🏆 Всего побед: {total_wins}
💰 Всего кристаллов: {total_crystals}
⭐ Всего донатов: {total_donations}
⭐ Получено Stars: {total_stars}

⚡ Средний выигрыш: {total_wins/total_users if total_users > 0 else 0:.1f} на игрока"""
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "admin_donations":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        
        donations = load_json(DONATIONS_FILE)
        text = "⭐ ПОСЛЕДНИЕ ДОНАТЫ\n\n"
        
        for d in donations.get('donations', [])[-20:]:
            text += f"👤 {d.get('username', d['user_id'])}\n"
            text += f"⭐ {d['stars']} Stars → {d['crystals']} 💎\n"
            text += f"📅 {d['date']}\n\n"
        
        if not donations.get('donations'):
            text += "Пока нет донатов"
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "admin_users":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        
        users = load_json(USERS_FILE)
        text = "👥 СПИСОК ПОЛЬЗОВАТЕЛЕЙ\n\n"
        for uid, u in list(users.items())[:20]:
            text += f"ID: {uid}\n👤 {u.get('username', 'Без имени')}\n💰 {u.get('crystals', 0)}💎 | 🏆 {u.get('wins', 0)}\n⭐ Донат: {u.get('donated_stars', 0)} Stars\n\n"
        
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

# ========== ОБРАБОТКА ПЛАТЕЖЕЙ ==========
@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout(query):
    """Подтверждение платежа"""
    bot.answer_pre_checkout_query(query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    """Успешная оплата"""
    payment = message.successful_payment
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Разбираем payload
    payload = payment.invoice_payload
    parts = payload.split('_')
    stars = int(parts[1])
    crystals = int(parts[2])
    
    # Начисляем кристаллы
    add_crystals(user_id, crystals)
    
    # Обновляем информацию о донатах пользователя
    user = get_user(user_id)
    user['donated_stars'] = user.get('donated_stars', 0) + stars
    user['donated_crystals'] = user.get('donated_crystals', 0) + crystals
    update_user(user_id, user)
    
    # Сохраняем донат
    save_donation(user_id, username, stars, crystals)
    
    # Отправляем сообщение
    text = f"""✅ СПАСИБО ЗА ПОДДЕРЖКУ! 🙏

⭐ Stars: {stars}
💎 Получено кристаллов: {crystals}
💰 Ваш баланс: {user['crystals']} кристаллов

Спасибо, что поддерживаете проект! ❤️"""
    
    bot.send_message(message.chat.id, text, reply_markup=lobby_kb())

# ========== АДМИН ФУНКЦИИ ==========
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
    try:
        parts = message.text.split()
        lang = parts[0].lower()
        word = parts[1].upper()
        
        # Добавляем слово в корпус и переобучаем нейросеть
        if lang == "ru":
            if word not in RUSSIAN_WORDS_CORPUS:
                RUSSIAN_WORDS_CORPUS.append(word)
                # Пересоздаем нейросеть с новыми данными
                neural_networks["ru"] = AdvancedNeuralNetwork("ru")
                bot.reply_to(message, f"✅ Слово {word} добавлено в нейросеть! Теперь она будет генерировать похожие слова.")
            else:
                bot.reply_to(message, f"❌ Слово {word} уже есть в словаре")
        elif lang == "en":
            if word not in ENGLISH_WORDS_CORPUS:
                ENGLISH_WORDS_CORPUS.append(word)
                neural_networks["en"] = AdvancedNeuralNetwork("en")
                bot.reply_to(message, f"✅ Word {word} added to neural network!")
            else:
                bot.reply_to(message, f"❌ Word {word} already exists")
        else:
            bot.reply_to(message, "❌ Ошибка! Формат: ru СЛОВО или en WORD")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🤖 Guess Word Bot с УЛУЧШЕННОЙ НЕЙРОСЕТЬЮ запущен")
    print(f"🧠 Нейросеть обучена на {len(RUSSIAN_WORDS_CORPUS)} русских словах")
    print(f"🧠 Нейросеть обучена на {len(ENGLISH_WORDS_CORPUS)} английских словах")
    print(f"⭐ Донат: 1 Star = 50 кристаллов + бонусы")
    print("👥 Лобби активна - каждый игрок играет в свою игру!")
    print("Команды: /start, /stats, /top, /shop, /lang, /donate, /help, /admin")
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")