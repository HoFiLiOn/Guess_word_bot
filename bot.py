try:
    import telebot
    from telebot import types
except ImportError:
    print("Ошибка: telebot не установлен. pip install pyTelegramBotAPI")
    exit(1)

import random
import json
import os
from collections import defaultdict, Counter
from datetime import datetime

TOKEN = "7766594100:AAH7j4yGEW5Tqoiu8IguYh0Mn3g7lMbPwj8"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 8388843828

# ========== ФАЙЛЫ ==========
USERS_FILE = "guess_users.json"
DONATIONS_FILE = "donations.json"
SETTINGS_FILE = "bot_settings.json"
NEURAL_DATA_FILE = "neural_data.json"

# ========== КАРТИНКИ (ВАШИ) ==========
DEFAULT_IMAGES = {
    "main": "https://s10.iimage.su/s/24/gyiVYQqxC4FhKIyY4GD47Mvv1YfJ3KFWNkUAbyKQN.png",
    "game": "https://s10.iimage.su/s/24/gFsXdz1x7sCnEVQMjpFfzw2t2qzT0lMS8Bz4zJGpU.jpg",
    "shop": "https://s10.iimage.su/s/24/g0Sj1dDxuKC84sMhP8q3DDK6Q7MDgBRam1v0lyP8H.jpg",
    "top": "https://s10.iimage.su/s/24/ggZ4ONmxr0bk39GQvB3ODh3cJbSU2XFLlrPstj5cp.jpg",
    "stats": "https://s10.iimage.su/s/24/gDyJ0rdxDzMm1NngFnHePE7MB5uz3oQphOMwXKCtu.jpg",
    "donate": "https://s10.iimage.su/s/24/gsqCZaQxs8sp4aoo0dGKbiNKWzrP6Dg5bEnSjvv9f.jpg"
}

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С JSON ==========
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

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                # Убеждаемся, что картинки есть
                if "images" not in saved:
                    saved["images"] = DEFAULT_IMAGES.copy()
                else:
                    for key in DEFAULT_IMAGES:
                        if key not in saved["images"]:
                            saved["images"][key] = DEFAULT_IMAGES[key]
                return saved
        except:
            return {"images": DEFAULT_IMAGES.copy()}
    return {"images": DEFAULT_IMAGES.copy()}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except:
        pass

# ========== САМООБУЧАЮЩАЯСЯ НЕЙРОСЕТЬ ==========
class SelfLearningNeuralNetwork:
    def __init__(self, lang):
        self.lang = lang
        self.ngrams = defaultdict(Counter)
        self.word_freq = Counter()
        self.letter_freq = Counter()
        self.bigram_freq = Counter()
        self.trigram_freq = Counter()
        self.vowels = "АЕЁИОУЫЭЮЯ" if lang == "ru" else "AEIOUY"
        self.consonants = "БВГДЖЗЙКЛМНОПРСТУФХЦЧШЩ" if lang == "ru" else "BCDFGHJKLMNPQRSTVWXZ"
        
        self._load_or_create_base()
    
    def _load_or_create_base(self):
        """Загружает сохранённые данные нейросети или создаёт новые"""
        data = load_json(NEURAL_DATA_FILE)
        
        if self.lang in data:
            self.ngrams = defaultdict(Counter, data[self.lang]["ngrams"])
            self.word_freq = Counter(data[self.lang]["word_freq"])
            self.letter_freq = Counter(data[self.lang]["letter_freq"])
            self.bigram_freq = Counter(data[self.lang]["bigram_freq"])
            self.trigram_freq = Counter(data[self.lang]["trigram_freq"])
            print(f"🧠 Нейросеть {self.lang} загружена, обучена на {len(self.word_freq)} словах")
        else:
            # Начальная база реальных слов
            if self.lang == "ru":
                base_words = [
                    "КОТ", "ДОМ", "ЛЕС", "САД", "РОЗА", "МАМА", "ПАПА", "СЫН", "ДОЧЬ", "БРАТ",
                    "СЕСТРА", "ДРУГ", "МИР", "ДЕНЬ", "НОЧЬ", "ГОРОД", "СОЛНЦЕ", "ЗВЕЗДА", "КНИГА",
                    "СТОЛ", "СТУЛ", "ОКНО", "ДВЕРЬ", "РУЧКА", "МАШИНА", "УЛИЦА", "ПАРК", "ЛУНА",
                    "ЗЕМЛЯ", "ВОДА", "ОГОНЬ", "ВЕТЕР", "СНЕГ", "ДОЖДЬ", "ЛЕТО", "ЗИМА", "ВЕСНА",
                    "ОСЕНЬ", "УТРО", "ВЕЧЕР", "СВЕТ", "ТЕНЬ", "ГОЛОС", "СЛОВО", "БУКВА", "СТРАНА",
                    "ПЛАНЕТА", "ПРИРОДА", "ЧЕЛОВЕК", "СЧАСТЬЕ", "ЛЮБОВЬ", "ДРУЖБА", "ШКОЛА"
                ]
            else:
                base_words = [
                    "CAT", "DOG", "SUN", "MOON", "STAR", "TREE", "FLOWER", "BIRD", "FISH",
                    "HOUSE", "CAR", "MOM", "DAD", "SON", "DAUGHTER", "BROTHER", "SISTER",
                    "FRIEND", "LOVE", "HOPE", "WATER", "FIRE", "EARTH", "WIND", "CLOUD",
                    "RAIN", "SNOW", "SUMMER", "WINTER", "SPRING", "AUTUMN", "DAY", "NIGHT"
                ]
            
            for word in base_words:
                self.learn_word(word.upper())
            
            self._save()
            print(f"🧠 Нейросеть {self.lang} создана, обучена на {len(self.word_freq)} словах")
    
    def learn_word(self, word):
        """Обучает нейросеть на новом слове"""
        word = word.upper()
        if word in self.word_freq:
            self.word_freq[word] += 1
            return
        
        self.word_freq[word] = 1
        
        for letter in word:
            self.letter_freq[letter] += 1
        
        for i in range(len(word) - 1):
            bigram = word[i:i+2]
            self.bigram_freq[bigram] += 1
        
        for i in range(len(word) - 2):
            trigram = word[i:i+3]
            self.trigram_freq[trigram] += 1
        
        for n in range(1, min(5, len(word))):
            for i in range(len(word) - n):
                context = word[i:i+n]
                next_char = word[i+n]
                self.ngrams[f"{n}_{context}"][next_char] += 1
        
        self._save()
    
    def _save(self):
        """Сохраняет данные нейросети"""
        data = load_json(NEURAL_DATA_FILE)
        data[self.lang] = {
            "ngrams": dict(self.ngrams),
            "word_freq": dict(self.word_freq),
            "letter_freq": dict(self.letter_freq),
            "bigram_freq": dict(self.bigram_freq),
            "trigram_freq": dict(self.trigram_freq)
        }
        save_json(NEURAL_DATA_FILE, data)
    
    def _get_weighted_letter(self):
        """Возвращает букву с учётом частоты"""
        if self.letter_freq:
            letters = list(self.letter_freq.keys())
            weights = list(self.letter_freq.values())
            return random.choices(letters, weights=weights, k=1)[0]
        return random.choice(list(self.vowels + self.consonants))
    
    def _get_next_char(self, context, n):
        """Предсказывает следующую букву на основе контекста"""
        key = f"{n}_{context}"
        if key in self.ngrams and self.ngrams[key]:
            chars = list(self.ngrams[key].keys())
            weights = list(self.ngrams[key].values())
            return random.choices(chars, weights=weights, k=1)[0]
        return None
    
    def _is_readable(self, word):
        """Проверяет, что слово похоже на реальное"""
        if len(word) < 3:
            return False
        if not any(c in self.vowels for c in word):
            return False
        cons_seq = 0
        for c in word:
            if c in self.consonants:
                cons_seq += 1
                if cons_seq >= 3:
                    return False
            else:
                cons_seq = 0
        for i in range(len(word) - 2):
            if word[i] == word[i+1] == word[i+2]:
                return False
        return True
    
    def generate_word(self, min_len=3, max_len=8):
        """Генерирует новое слово на основе обученных данных"""
        max_attempts = 100
        
        for _ in range(max_attempts):
            length = random.randint(min_len, max_len)
            word = []
            
            word.append(self._get_weighted_letter())
            
            for i in range(1, length):
                r = random.random()
                
                if r < 0.6 and i >= 3:
                    context = ''.join(word[-3:])
                    next_char = self._get_next_char(context, 4)
                elif r < 0.8 and i >= 2:
                    context = ''.join(word[-2:])
                    next_char = self._get_next_char(context, 3)
                elif r < 0.95 and i >= 1:
                    context = word[-1]
                    next_char = self._get_next_char(context, 2)
                else:
                    next_char = None
                
                if next_char is None:
                    next_char = self._get_weighted_letter()
                
                word.append(next_char)
            
            result = ''.join(word)
            
            if self._is_readable(result):
                return result
        
        if self.word_freq:
            return random.choice(list(self.word_freq.keys()))
        return "КОТ" if self.lang == "ru" else "CAT"

# ========== СОЗДАЁМ НЕЙРОСЕТИ ==========
neural_networks = {
    "ru": SelfLearningNeuralNetwork("ru"),
    "en": SelfLearningNeuralNetwork("en")
}

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ==========
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
            'donated_stars': 0
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

def add_win(user_id, word):
    user = get_user(user_id)
    user['wins'] += 1
    user['games'] += 1
    user['streak'] += 1
    if user['streak'] > user['best_streak']:
        user['best_streak'] = user['streak']
    update_user(user_id, user)
    
    lang = user.get('lang', 'ru')
    neural_networks[lang].learn_word(word)

def add_loss(user_id):
    user = get_user(user_id)
    user['games'] += 1
    user['streak'] = 0
    update_user(user_id, user)

def save_donation(user_id, username, stars, crystals_given):
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
    if 'stats' not in donations:
        donations['stats'] = {}
    donations['stats']['total_stars'] = donations['stats'].get('total_stars', 0) + stars
    donations['stats']['total_crystals'] = donations['stats'].get('total_crystals', 0) + crystals_given
    donations['stats']['total_donations'] = donations['stats'].get('total_donations', 0) + 1
    save_json(DONATIONS_FILE, donations)

def get_word(lang):
    """Генерирует слово с помощью нейросети"""
    return neural_networks[lang].generate_word()

# ========== КЛАСС ИГРЫ ==========
class Game:
    def __init__(self, chat_id, user_id, lang, message_id):
        self.chat_id = chat_id
        self.user_id = user_id
        self.word = get_word(lang)
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
        
        text = f"""<b>УГАДАЙ СЛОВО</b>
<i>Ваша игра</i>

<b>Слово:</b> {display}
<b>Попыток:</b> {self.attempts}
<b>Ошибки:</b> {wrong}
<b>За победу:</b> +50

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
                add_win(self.user_id, self.word)
                self.active = False
                return True, f"<b>ПОБЕДА!</b>\n\nСлово: {self.word}\n+{reward}"
            
            self.attempts -= 1
            if self.attempts <= 0:
                if not self.effects.get("shield"):
                    add_loss(self.user_id)
                self.active = False
                return False, f"<b>ПОРАЖЕНИЕ!</b>\n\nСлово: {self.word}"
            return False, f"<b>Неправильно!</b> Осталось попыток: {self.attempts}"
        
        if letter in self.guessed_letters or letter in self.wrong_letters:
            return False, "<b>Эта буква уже называлась</b>"
        
        if letter in self.word:
            self.guessed_letters.append(letter)
            
            if all(l in self.guessed_letters for l in self.word):
                reward = 50
                if self.effects.get("double"):
                    reward *= 2
                add_crystals(self.user_id, reward)
                add_win(self.user_id, self.word)
                self.active = False
                return True, f"<b>ПОБЕДА!</b>\n\nСлово: {self.word}\n+{reward}"
            
            return True, "<b>Есть такая буква!</b>"
        else:
            self.wrong_letters.append(letter)
            self.attempts -= 1
            
            if self.attempts <= 0:
                if not self.effects.get("shield"):
                    add_loss(self.user_id)
                self.active = False
                return False, f"<b>ПОРАЖЕНИЕ!</b>\n\nСлово: {self.word}"
            
            return False, f"<b>Нет такой буквы!</b> Осталось попыток: {self.attempts}"
    
    def use_hint(self):
        not_guessed = [l for l in self.word if l not in self.guessed_letters]
        if not_guessed:
            hint_letter = random.choice(not_guessed)
            self.guessed_letters.append(hint_letter)
            return f"<b>Подсказка:</b> буква {hint_letter} есть в слове!"
        return "<b>Все буквы уже открыты!</b>"
    
    def reroll_word(self):
        self.word = get_word(self.lang)
        self.guessed_letters = []
        self.wrong_letters = []
        self.attempts = 6
        return f"<b>Слово заменено!</b>"

# ========== КЛАВИАТУРЫ ==========
def get_image(key):
    settings = load_settings()
    images = settings.get("images", DEFAULT_IMAGES)
    return images.get(key, DEFAULT_IMAGES.get(key, ""))

def send_with_image(chat_id, image_key, text, reply_markup=None):
    image_url = get_image(image_key)
    if image_url:
        try:
            bot.send_photo(chat_id=chat_id, photo=image_url, caption=text, reply_markup=reply_markup, parse_mode="HTML")
        except:
            bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode="HTML")

def edit_with_image(chat_id, message_id, image_key, text, reply_markup=None):
    image_url = get_image(image_key)
    if image_url:
        try:
            bot.edit_message_media(media=types.InputMediaPhoto(media=image_url, caption=text, parse_mode="HTML"), chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
        except:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup, parse_mode="HTML")
    else:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup, parse_mode="HTML")

def lobby_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎮 Начать игру", callback_data="start_game"),
        types.InlineKeyboardButton("⭐ Поддержать", callback_data="donate"),
        types.InlineKeyboardButton("🛒 Магазин", callback_data="shop"),
        types.InlineKeyboardButton("🏆 Топ игроков", callback_data="top"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="stats"),
        types.InlineKeyboardButton("🌐 Язык", callback_data="lang"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="help")
    )
    return markup

def donate_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("TELEGRAM STARS", callback_data="donate_stars_menu"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
    )
    return markup

def donate_stars_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("1 Star → 50 +0 бонус", callback_data="donate_1"),
        types.InlineKeyboardButton("2 Stars → 100 +10 бонус", callback_data="donate_2"),
        types.InlineKeyboardButton("5 Stars → 250 +30 бонус", callback_data="donate_5"),
        types.InlineKeyboardButton("10 Stars → 500 +75 бонус", callback_data="donate_10"),
        types.InlineKeyboardButton("20 Stars → 1000 +200 бонус", callback_data="donate_20"),
        types.InlineKeyboardButton("50 Stars → 2500 +750 бонус", callback_data="donate_50"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="donate")
    )
    return markup

def shop_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔍 Подсказка — 50💎", callback_data="buy_hint"),
        types.InlineKeyboardButton("🔄 Сменить слово — 100💎", callback_data="buy_reroll"),
        types.InlineKeyboardButton("🛡️ Защита — 150💎", callback_data="buy_shield"),
        types.InlineKeyboardButton("💎 Кристалл x2 — 500💎", callback_data="buy_double"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
    )
    return markup

def top_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💰 ТОП ПО КРИСТАЛЛАМ", callback_data="top_crystals"),
        types.InlineKeyboardButton("🏆 ТОП ПО ПОБЕДАМ", callback_data="top_wins"),
        types.InlineKeyboardButton("🔥 ТОП ПО СЕРИИ", callback_data="top_streak"),
        types.InlineKeyboardButton("⭐ ТОП ПО ДОНАТАМ", callback_data="top_donations"),
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

def game_kb(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Подсказка (50)", callback_data=f"use_hint_{user_id}"),
        types.InlineKeyboardButton("Сменить слово (100)", callback_data=f"use_reroll_{user_id}"),
        types.InlineKeyboardButton("Выйти", callback_data=f"exit_game_{user_id}")
    )
    return markup

def admin_panel_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton("⭐ Донаты", callback_data="admin_donations"),
        types.InlineKeyboardButton("💎 Выдать кристаллы", callback_data="admin_give"),
        types.InlineKeyboardButton("🧠 Нейросеть", callback_data="admin_neural"),
        types.InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
    )
    return markup

# ========== КОМАНДЫ ==========
active_games = {}

@bot.message_handler(commands=['start', 'guess', 'menu'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    user = get_user(user_id)
    user['username'] = username
    update_user(user_id, user)
    
    text = f"""<b>УГАДАЙ СЛОВО</b>

Добро пожаловать, {username}!

<b>Кристаллов:</b> {user['crystals']}
<b>Побед:</b> {user['wins']}
<b>Игр:</b> {user['games']}

Нажми «Начать игру», чтобы играть!"""
    
    send_with_image(message.chat.id, "main", text, lobby_kb())

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    text = f"""<b>ТВОЯ СТАТИСТИКА</b>

<b>Кристаллов:</b> {user['crystals']}
<b>Побед:</b> {user['wins']}
<b>Игр:</b> {user['games']}
<b>Текущая серия:</b> {user['streak']}
<b>Лучшая серия:</b> {user['best_streak']}
<b>Поддержал проект:</b> {user.get('donated_stars', 0)} ⭐"""
    
    send_with_image(message.chat.id, "stats", text, lobby_kb())

@bot.message_handler(commands=['top'])
def top_command(message):
    text = "<b>🏆 ТАБЛИЦА ЛИДЕРОВ</b>\n\nВыбери категорию:"
    send_with_image(message.chat.id, "top", text, top_kb())

@bot.message_handler(commands=['shop'])
def shop_command(message):
    text = "<b>🛒 МАГАЗИН</b>\n\nВыбери товар:"
    send_with_image(message.chat.id, "shop", text, shop_kb())

@bot.message_handler(commands=['lang'])
def lang_command(message):
    text = "<b>🌐 Выбери язык игры:</b>"
    send_with_image(message.chat.id, "main", text, lang_kb())

@bot.message_handler(commands=['donate'])
def donate_command(message):
    text = "<b>⭐ ПОДДЕРЖАТЬ ПРОЕКТ</b>\n\nВыбери сумму доната:"
    send_with_image(message.chat.id, "donate", text, donate_kb())

@bot.message_handler(commands=['help'])
def help_command(message):
    text = """<b>📚 ПОМОЩЬ</b>

<b>Как играть:</b>
1️⃣ Нажми «Начать игру»
2️⃣ Введи букву или слово
3️⃣ Угадай слово

<b>Советы:</b>
• Нейросеть генерирует уникальные слова
• Буквы отображаются на своих местах
• Можно использовать подсказки в магазине
• За победу дают кристаллы

<b>Команды:</b>
/start — Лобби
/stats — Статистика
/top — Таблица лидеров
/shop — Магазин
/lang — Язык
/donate — Поддержать
/help — Помощь"""
    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Нет прав")
        return
    bot.send_message(message.chat.id, "🔧 АДМИН ПАНЕЛЬ", reply_markup=admin_panel_kb())

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
                bot.edit_message_text(msg, game.chat_id, game.message_id, parse_mode="HTML")
                del active_games[user_id]
                user = get_user(user_id)
                menu_text = f"""<b>УГАДАЙ СЛОВО</b>

<b>Кристаллов:</b> {user['crystals']}
<b>Побед:</b> {user['wins']}

Игра завершена! Нажми «Начать игру» для новой игры!"""
                send_with_image(message.chat.id, "main", menu_text, lobby_kb())
            else:
                new_text = game.get_game_text(msg)
                try:
                    bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id), parse_mode="HTML")
                except:
                    pass
            
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
    else:
        if message.text and not message.text.startswith('/'):
            user = get_user(user_id)
            text = f"""<b>УГАДАЙ СЛОВО</b>

<b>Кристаллов:</b> {user['crystals']}
<b>Побед:</b> {user['wins']}

Нет активной игры. Нажми «Начать игру»"""
            send_with_image(message.chat.id, "main", text, lobby_kb())

# ========== ОБРАБОТКА КНОПОК ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    user = get_user(user_id)
    
    if data.startswith("use_hint_"):
        owner_id = int(data.split("_")[2])
        if user_id != owner_id:
            bot.answer_callback_query(call.id, "Это не ваша игра!", show_alert=True)
            return
        data = "use_hint"
    elif data.startswith("use_reroll_"):
        owner_id = int(data.split("_")[2])
        if user_id != owner_id:
            bot.answer_callback_query(call.id, "Это не ваша игра!", show_alert=True)
            return
        data = "use_reroll"
    elif data.startswith("exit_game_"):
        owner_id = int(data.split("_")[2])
        if user_id != owner_id:
            bot.answer_callback_query(call.id, "Это не ваша игра!", show_alert=True)
            return
        data = "exit_game"
    
    if data == "back_to_main":
        text = f"""<b>УГАДАЙ СЛОВО</b>

<b>Кристаллов:</b> {user['crystals']}
<b>Побед:</b> {user['wins']}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, lobby_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "donate":
        text = "<b>⭐ ПОДДЕРЖАТЬ ПРОЕКТ</b>\n\nВыбери сумму доната:"
        edit_with_image(call.message.chat.id, call.message.message_id, "donate", text, donate_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "donate_stars_menu":
        text = "<b>TELEGRAM STARS</b>\n\n1 Star = 50 кристаллов + бонусы!"
        edit_with_image(call.message.chat.id, call.message.message_id, "donate", text, donate_stars_kb())
        bot.answer_callback_query(call.id)
    
    elif data.startswith("donate_") and data != "donate_stars_menu":
        stars = int(data.split("_")[1])
        if stars == 1: bonus = 0
        elif stars == 2: bonus = 10
        elif stars == 5: bonus = 30
        elif stars == 10: bonus = 75
        elif stars == 20: bonus = 200
        elif stars == 50: bonus = 750
        else: bonus = 0
        total = stars * 50 + bonus
        
        prices = [types.LabeledPrice(label=f"{stars} Stars", amount=stars)]
        bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Поддержка",
            description=f"{stars} Stars\n+{stars*50} кристаллов\nБонус: +{bonus}\nИтого: {total}",
            invoice_payload=f"donate_{stars}_{total}_{user_id}",
            provider_token="",
            currency="XTR",
            prices=prices,
            start_parameter="donate"
        )
        bot.answer_callback_query(call.id)
    
    elif data == "shop":
        text = "<b>🛒 МАГАЗИН</b>\n\nВыбери товар:"
        edit_with_image(call.message.chat.id, call.message.message_id, "shop", text, shop_kb())
        bot.answer_callback_query(call.id)
    
    elif data.startswith("buy_"):
        item_id = data[4:]
        prices = {"hint": 50, "reroll": 100, "shield": 150, "double": 500}
        if user['crystals'] < prices[item_id]:
            bot.answer_callback_query(call.id, f"Не хватает! Нужно {prices[item_id]}", show_alert=True)
            return
        user['crystals'] -= prices[item_id]
        update_user(user_id, user)
        if user_id in active_games and active_games[user_id].active:
            active_games[user_id].effects[item_id] = True
        bot.answer_callback_query(call.id, f"Куплено! -{prices[item_id]}", show_alert=True)
        text = "<b>🛒 МАГАЗИН</b>\n\nВыбери товар:"
        edit_with_image(call.message.chat.id, call.message.message_id, "shop", text, shop_kb())
    
    elif data == "top":
        text = "<b>🏆 ТАБЛИЦА ЛИДЕРОВ</b>\n\nВыбери категорию:"
        edit_with_image(call.message.chat.id, call.message.message_id, "top", text, top_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "top_crystals":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'crystals': u.get('crystals', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['crystals'], reverse=True)
        text = "<b>💰 ТОП ПО КРИСТАЛЛАМ</b>\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['crystals']}💎\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb(), parse_mode="HTML")
        bot.answer_callback_query(call.id)
    
    elif data == "top_wins":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'wins': u.get('wins', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['wins'], reverse=True)
        text = "<b>🏆 ТОП ПО ПОБЕДАМ</b>\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['wins']}🏆\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb(), parse_mode="HTML")
        bot.answer_callback_query(call.id)
    
    elif data == "top_streak":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'streak': u.get('best_streak', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['streak'], reverse=True)
        text = "<b>🔥 ТОП ПО СЕРИИ</b>\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['streak']}🔥\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb(), parse_mode="HTML")
        bot.answer_callback_query(call.id)
    
    elif data == "top_donations":
        donations = load_json(DONATIONS_FILE)
        user_donations = {}
        for d in donations.get('donations', []):
            user_donations[d['user_id']] = user_donations.get(d['user_id'], 0) + d['stars']
        users = load_json(USERS_FILE)
        top = []
        for uid, stars in user_donations.items():
            username = users.get(str(uid), {}).get('username', f"User_{uid}")
            top.append({'username': username, 'stars': stars})
        top.sort(key=lambda x: x['stars'], reverse=True)
        text = "<b>⭐ ТОП ПО ДОНАТАМ</b>\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['stars']}⭐\n"
        if not top:
            text += "Пока нет донатов"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb(), parse_mode="HTML")
        bot.answer_callback_query(call.id)
    
    elif data == "stats":
        text = f"""<b>ТВОЯ СТАТИСТИКА</b>

<b>Кристаллов:</b> {user['crystals']}
<b>Побед:</b> {user['wins']}
<b>Игр:</b> {user['games']}
<b>Текущая серия:</b> {user['streak']}
<b>Лучшая серия:</b> {user['best_streak']}
<b>Поддержал проект:</b> {user.get('donated_stars', 0)} ⭐"""
        edit_with_image(call.message.chat.id, call.message.message_id, "stats", text, lobby_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "lang":
        text = "<b>🌐 Выбери язык игры:</b>"
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, lang_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "lang_ru":
        user['lang'] = 'ru'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "Язык: русский")
        text = f"""<b>УГАДАЙ СЛОВО</b>

<b>Кристаллов:</b> {user['crystals']}
<b>Побед:</b> {user['wins']}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, lobby_kb())
    
    elif data == "lang_en":
        user['lang'] = 'en'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "Language: English")
        text = f"""<b>GUESS THE WORD</b>

<b>Crystals:</b> {user['crystals']}
<b>Wins:</b> {user['wins']}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, lobby_kb())
    
    elif data == "help":
        text = """<b>📚 ПОМОЩЬ</b>

<b>Как играть:</b>
1️⃣ Нажми «Начать игру»
2️⃣ Введи букву или слово
3️⃣ Угадай слово

<b>Советы:</b>
• Нейросеть генерирует уникальные слова
• Буквы отображаются на своих местах
• Можно использовать подсказки в магазине
• За победу дают кристаллы

<b>Команды:</b>
/start — Лобби
/stats — Статистика
/top — Таблица лидеров
/shop — Магазин
/lang — Язык
/donate — Поддержать
/help — Помощь"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML")
        bot.answer_callback_query(call.id)
    
    elif data == "start_game":
        lang = user.get('lang', 'ru')
        if user_id in active_games and active_games[user_id].active:
            bot.answer_callback_query(call.id, "У вас уже есть игра!", show_alert=True)
            return
        sent = bot.send_message(call.message.chat.id, "Генерация слова...")
        game = Game(call.message.chat.id, user_id, lang, sent.message_id)
        active_games[user_id] = game
        game_text = game.get_game_text("Игра началась!")
        bot.edit_message_text(game_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id), parse_mode="HTML")
        bot.answer_callback_query(call.id)
    
    elif data == "use_hint":
        if user_id not in active_games or not active_games[user_id].active:
            bot.answer_callback_query(call.id, "Нет активной игры!", show_alert=True)
            return
        if user['crystals'] < 50:
            bot.answer_callback_query(call.id, "Не хватает 50!", show_alert=True)
            return
        user['crystals'] -= 50
        update_user(user_id, user)
        game = active_games[user_id]
        hint_msg = game.use_hint()
        new_text = game.get_game_text(hint_msg)
        bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id), parse_mode="HTML")
        bot.answer_callback_query(call.id, "Подсказка! -50")
    
    elif data == "use_reroll":
        if user_id not in active_games or not active_games[user_id].active:
            bot.answer_callback_query(call.id, "Нет активной игры!", show_alert=True)
            return
        if user['crystals'] < 100:
            bot.answer_callback_query(call.id, "Не хватает 100!", show_alert=True)
            return
        user['crystals'] -= 100
        update_user(user_id, user)
        game = active_games[user_id]
        reroll_msg = game.reroll_word()
        new_text = game.get_game_text(reroll_msg)
        bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id), parse_mode="HTML")
        bot.answer_callback_query(call.id, "Слово заменено! -100")
    
    elif data == "exit_game":
        if user_id in active_games:
            del active_games[user_id]
        bot.answer_callback_query(call.id, "Игра завершена")
        text = f"""<b>УГАДАЙ СЛОВО</b>

<b>Кристаллов:</b> {user['crystals']}
<b>Побед:</b> {user['wins']}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, lobby_kb())
    
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
        text = f"📊 СТАТИСТИКА\n\n👥 Игроков: {total_users}\n🎮 Игр: {total_games}\n🏆 Побед: {total_wins}\n💰 Кристаллов: {total_crystals}\n⭐ Stars: {total_stars}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "admin_donations":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        donations = load_json(DONATIONS_FILE)
        text = "⭐ ПОСЛЕДНИЕ ДОНАТЫ\n\n"
        for d in donations.get('donations', [])[-20:]:
            text += f"👤 {d.get('username', d['user_id'])}\n⭐ {d['stars']} → {d['crystals']}\n📅 {d['date']}\n\n"
        if not donations.get('donations'):
            text += "Пока нет донатов"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "admin_users":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        users = load_json(USERS_FILE)
        text = "👥 ПОЛЬЗОВАТЕЛИ\n\n"
        for uid, u in list(users.items())[:20]:
            text += f"ID: {uid}\n👤 {u.get('username', 'Без имени')}\n💰 {u.get('crystals', 0)} | 🏆 {u.get('wins', 0)}\n⭐ {u.get('donated_stars', 0)}\n\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "admin_give":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        msg = bot.send_message(call.message.chat.id, "Введите ID и сумму:\nПример: 123456789 100")
        bot.register_next_step_handler(msg, admin_give_crystals)
        bot.answer_callback_query(call.id)
    
    elif data == "admin_neural":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        ru_words = len(neural_networks["ru"].word_freq)
        en_words = len(neural_networks["en"].word_freq)
        text = f"🧠 НЕЙРОСЕТЬ\n\nРусская: {ru_words} слов\nАнглийская: {en_words} слов\n\nНейросеть самообучается на каждом угаданном слове!"
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="admin_panel"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)

def admin_give_crystals(message):
    try:
        parts = message.text.split()
        user_id = int(parts[0])
        amount = int(parts[1])
        add_crystals(user_id, amount)
        bot.reply_to(message, f"✅ Выдано {amount} кристаллов")
    except:
        bot.reply_to(message, "❌ Ошибка! Формат: ID СУММА")

# ========== ПЛАТЕЖИ ==========
@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout(query):
    bot.answer_pre_checkout_query(query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    payment = message.successful_payment
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    parts = payment.invoice_payload.split('_')
    stars = int(parts[1])
    crystals = int(parts[2])
    
    add_crystals(user_id, crystals)
    user = get_user(user_id)
    user['donated_stars'] = user.get('donated_stars', 0) + stars
    update_user(user_id, user)
    save_donation(user_id, username, stars, crystals)
    
    bot.send_message(user_id, f"✅ Спасибо за поддержку!\n⭐ {stars} Stars\n💎 +{crystals} кристаллов\n💰 Баланс: {user['crystals']}")

# ========== ПРИВЕТСТВИЕ В ЧАТ ==========
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for member in message.new_chat_members:
        if member.id == bot.get_me().id:
            text = """🎉 Всем привет! Я бот «Угадай слово»!

Нажми /start, чтобы начать играть!

Угадывай слова, получай кристаллы и попадай в топ!

Команды:
/start — начать
/stats — статистика
/top — таблица лидеров
/shop — магазин
/donate — поддержать проект

Играем! 🔥"""
            bot.send_message(message.chat.id, text)
            break

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("🤖 Бот с самообучающейся нейросетью запущен")
    print(f"🧠 Русская нейросеть: {len(neural_networks['ru'].word_freq)} слов")
    print(f"🧠 Английская нейросеть: {len(neural_networks['en'].word_freq)} слов")
    print("⭐ Донат: Telegram Stars (кнопки без эмодзи)")
    print("👥 Лобби: каждый игрок играет в свою игру")
    print("🔧 Админ-панель: /admin")
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")