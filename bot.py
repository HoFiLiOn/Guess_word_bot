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
import io

TOKEN = "7766594100:AAH7j4yGEW5Tqoiu8IguYh0Mn3g7lMbPwj8"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 8388843828

# ========== ФАЙЛЫ ==========
USERS_FILE = "guess_users.json"
DONATIONS_FILE = "donations.json"
SETTINGS_FILE = "bot_settings.json"

# ========== НАСТРОЙКИ ПО УМОЛЧАНИЮ ==========
DEFAULT_SETTINGS = {
    "use_custom_neural": True,
    "neural_power": 95,
    "images": {
        "main": "https://s10.iimage.su/s/24/gyiVYQqxC4FhKIyY4GD47Mvv1YfJ3KFWNkUAbyKQN.png",
        "game": "https://s10.iimage.su/s/24/gFsXdz1x7sCnEVQMjpFfzw2t2qzT0lMS8Bz4zJGpU.jpg",
        "shop": "https://s10.iimage.su/s/24/g0Sj1dDxuKC84sMhP8q3DDK6Q7MDgBRam1v0lyP8H.jpg",
        "top": "https://s10.iimage.su/s/24/ggZ4ONmxr0bk39GQvB3ODh3cJbSU2XFLlrPstj5cp.jpg",
        "stats": "https://s10.iimage.su/s/24/gDyJ0rdxDzMm1NngFnHePE7MB5uz3oQphOMwXKCtu.jpg",
        "donate": "https://s10.iimage.su/s/24/gsqCZaQxs8sp4aoo0dGKbiNKWzrP6Dg5bEnSjvv9f.jpg"
    },
    "texts": {
        "main_title": "<b>УГАДАЙ СЛОВО</b>\n\nДобро пожаловать, {username}!",
        "main_stats": "<b>Кристаллов:</b> {crystals}\n<b>Побед:</b> {wins}\n<b>Игр:</b> {games}",
        "main_buttons": {
            "start": "🎮 Начать игру",
            "donate": "💰 Поддержать",
            "shop": "🛒 Магазин",
            "top": "🏆 Топ игроков",
            "stats": "📊 Статистика",
            "lang": "🌐 Язык",
            "help": "❓ Помощь"
        },
        "game_title": "<b>УГАДАЙ СЛОВО</b>\n<i>Ваша игра</i>",
        "game_word": "<b>Слово:</b> {display}",
        "game_attempts": "<b>Попыток:</b> {attempts}",
        "game_wrong": "<b>Ошибки:</b> {wrong}",
        "game_reward": "<b>За победу:</b> +50",
        "game_enter": "\n\nВведите букву или слово:",
        "game_win": "<b>ПОБЕДА!</b>\n\nСлово: {word}\n+{reward}",
        "game_lose": "<b>ПОРАЖЕНИЕ!</b>\n\nСлово: {word}",
        "game_wrong_word": "<b>Неправильно!</b> Осталось попыток: {attempts}",
        "game_yes_letter": "<b>Есть такая буква!</b>",
        "game_no_letter": "<b>Нет такой буквы!</b> Осталось попыток: {attempts}",
        "game_already_used": "<b>Эта буква уже называлась</b>",
        "game_hint": "<b>Подсказка:</b> буква {letter} есть в слове!",
        "game_all_letters": "<b>Все буквы уже открыты!</b>",
        "game_reroll": "<b>Слово заменено!</b>",
        "shop_title": "<b>🛒 МАГАЗИН</b>\n\nВыбери товар:",
        "shop_hint": "🔍 Подсказка — 50💎",
        "shop_reroll": "🔄 Сменить слово — 100💎",
        "shop_shield": "🛡️ Защита — 150💎",
        "shop_double": "💎 Кристалл x2 — 500💎",
        "shop_back": "◀️ Назад",
        "top_title": "<b>🏆 ТАБЛИЦА ЛИДЕРОВ</b>\n\nВыбери категорию:",
        "top_crystals": "<b>💰 ТОП ПО КРИСТАЛЛАМ</b>",
        "top_wins": "<b>🏆 ТОП ПО ПОБЕДАМ</b>",
        "top_streak": "<b>🔥 ТОП ПО СЕРИИ</b>",
        "top_donations": "<b>💰 ТОП ПО ДОНАТАМ</b>",
        "stats_title": "<b>📊 ТВОЯ СТАТИСТИКА</b>",
        "stats_crystals": "<b>Кристаллов:</b> {crystals}",
        "stats_wins": "<b>Побед:</b> {wins}",
        "stats_games": "<b>Игр:</b> {games}",
        "stats_streak": "<b>Текущая серия:</b> {streak}",
        "stats_best_streak": "<b>Лучшая серия:</b> {best_streak}",
        "stats_donated": "<b>Поддержал проект:</b> {donated}",
        "donate_title": "<b>ПОДДЕРЖАТЬ ПРОЕКТ</b>\n\nВыбери способ поддержки:",
        "donate_stars_title": "<b>TELEGRAM STARS</b>\n\n1 Star = 50 кристаллов + бонусы!",
        "donate_crypto_title": "<b>КРИПТОВАЛЮТА</b>\n\nПоддержать через:",
        "donate_stars_1": "1 Star → 50 +0 бонус",
        "donate_stars_2": "2 Stars → 100 +10 бонус",
        "donate_stars_5": "5 Stars → 250 +30 бонус",
        "donate_stars_10": "10 Stars → 500 +75 бонус",
        "donate_stars_20": "20 Stars → 1000 +200 бонус",
        "donate_stars_50": "50 Stars → 2500 +750 бонус",
        "donate_usdt": "USDT (TRC20): TXXXXXXXXXXXX",
        "donate_btc": "Bitcoin: bc1xxxxxxxxxxxx",
        "donate_ton": "TON: EQDxxxxxxxxxxxx",
        "donate_back": "◀️ Назад",
        "lang_title": "<b>🌐 Выбери язык игры:</b>",
        "lang_ru": "🇷🇺 Русский",
        "lang_en": "🇬🇧 English",
        "help_title": "<b>📚 ПОМОЩЬ</b>",
        "help_text": "<b>Как играть:</b>\n1️⃣ Нажми «Начать игру»\n2️⃣ Введи букву или слово\n3️⃣ Угадай слово\n\n<b>Советы:</b>\n• Нейросеть генерирует уникальные слова\n• Буквы отображаются на своих местах\n• Можно использовать подсказки в магазине\n• За победу дают кристаллы\n\n<b>Команды:</b>\n/start — Лобби\n/stats — Статистика\n/top — Таблица лидеров\n/shop — Магазин\n/lang — Язык\n/donate — Поддержать\n/help — Помощь"
    }
}

# ========== ЛЮТАЯ НЕЙРОСЕТЬ ==========
class MegaNeuralNetwork:
    def __init__(self, lang):
        self.lang = lang
        self.ngrams_1 = defaultdict(Counter)
        self.ngrams_2 = defaultdict(Counter)
        self.ngrams_3 = defaultdict(Counter)
        self.ngrams_4 = defaultdict(Counter)
        
        self.vowels = "АЕЁИОУЫЭЮЯ" if lang == "ru" else "AEIOUY"
        self.consonants = "БВГДЖЗЙКЛМНОПРСТУФХЦЧШЩ" if lang == "ru" else "BCDFGHJKLMNPQRSTVWXZ"
        
        self.corpus = self._load_corpus()
        self._train()
    
    def _load_corpus(self):
        if self.lang == "ru":
            return [
                "КОТ", "ДОМ", "ЛЕС", "САД", "РОЗА", "МАМА", "ПАПА", "СЫН", "ДОЧЬ", "БРАТ",
                "СЕСТРА", "ДРУГ", "МИР", "ДЕНЬ", "НОЧЬ", "ГОРОД", "СОЛНЦЕ", "ЗВЕЗДА", "КНИГА",
                "СТОЛ", "СТУЛ", "ОКНО", "ДВЕРЬ", "РУЧКА", "МАШИНА", "УЛИЦА", "ПАРК", "ЛУНА",
                "ЗЕМЛЯ", "ВОДА", "ОГОНЬ", "ВЕТЕР", "СНЕГ", "ДОЖДЬ", "ЛЕТО", "ЗИМА", "ВЕСНА",
                "ОСЕНЬ", "УТРО", "ВЕЧЕР", "СВЕТ", "ТЕНЬ", "ГОЛОС", "СЛОВО", "БУКВА", "СТРАНА",
                "ПЛАНЕТА", "ПРИРОДА", "ЧЕЛОВЕК", "СЧАСТЬЕ", "ЛЮБОВЬ", "ДРУЖБА", "ШКОЛА",
                "УЧИТЕЛЬ", "РАБОТА", "ДЕНЬГИ", "ВРЕМЯ", "МЫСЛЬ", "ИДЕЯ", "МЕЧТА", "НАДЕЖДА"
            ]
        else:
            return [
                "CAT", "DOG", "SUN", "MOON", "STAR", "TREE", "FLOWER", "BIRD", "FISH",
                "HOUSE", "CAR", "MOM", "DAD", "SON", "DAUGHTER", "BROTHER", "SISTER",
                "FRIEND", "LOVE", "HOPE", "WATER", "FIRE", "EARTH", "WIND", "CLOUD",
                "RAIN", "SNOW", "SUMMER", "WINTER", "SPRING", "AUTUMN", "DAY", "NIGHT"
            ]
    
    def _train(self):
        for word in self.corpus:
            word = word.upper()
            if len(word) < 2:
                continue
            
            for i in range(len(word)):
                self.ngrams_1[word[i]][word[i]] += 1
            
            for i in range(len(word) - 1):
                self.ngrams_2[word[i]][word[i+1]] += 1
            
            for i in range(len(word) - 2):
                context = word[i:i+2]
                self.ngrams_3[context][word[i+2]] += 1
            
            for i in range(len(word) - 3):
                context = word[i:i+3]
                self.ngrams_4[context][word[i+3]] += 1
        
        for ngram in [self.ngrams_1, self.ngrams_2, self.ngrams_3, self.ngrams_4]:
            for key in ngram:
                total = sum(ngram[key].values())
                for subkey in ngram[key]:
                    ngram[key][subkey] /= total
    
    def _get_freq_letter(self):
        if self.lang == "ru":
            letters = list("АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
            freqs = [0.080, 0.019, 0.045, 0.022, 0.030, 0.084, 0.014, 0.020, 0.074,
                     0.016, 0.034, 0.044, 0.032, 0.067, 0.109, 0.028, 0.048, 0.055,
                     0.063, 0.026, 0.006, 0.015, 0.009, 0.018, 0.012, 0.008, 0.003,
                     0.024, 0.023, 0.007, 0.010, 0.025]
            return random.choices(letters, weights=freqs, k=1)[0]
        else:
            letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            freqs = [0.081, 0.014, 0.027, 0.042, 0.127, 0.022, 0.020, 0.060, 0.069,
                     0.001, 0.008, 0.040, 0.024, 0.067, 0.075, 0.019, 0.001, 0.059,
                     0.063, 0.090, 0.027, 0.012, 0.023, 0.001, 0.019, 0.001]
            return random.choices(letters, weights=freqs, k=1)[0]
    
    def _get_next_char(self, context, ngram_dict):
        if context in ngram_dict and ngram_dict[context]:
            chars = list(ngram_dict[context].keys())
            weights = list(ngram_dict[context].values())
            return random.choices(chars, weights=weights, k=1)[0]
        return None
    
    def _is_readable(self, word):
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
    
    def generate_word(self, min_len=3, max_len=10):
        settings = load_settings()
        power = settings.get("neural_power", 95)
        
        for _ in range(100):
            length = random.randint(min_len, max_len)
            word = []
            
            word.append(self._get_freq_letter())
            
            for i in range(1, length):
                r = random.randint(1, 100)
                
                if r <= power and len(word) >= 3:
                    context = ''.join(word[-3:])
                    next_char = self._get_next_char(context, self.ngrams_4)
                elif r <= power + 5 and len(word) >= 2:
                    context = ''.join(word[-2:])
                    next_char = self._get_next_char(context, self.ngrams_3)
                elif r <= power + 15 and len(word) >= 1:
                    context = word[-1]
                    next_char = self._get_next_char(context, self.ngrams_2)
                else:
                    next_char = self._get_freq_letter()
                
                if next_char is None:
                    next_char = self._get_freq_letter()
                
                word.append(next_char)
            
            result = ''.join(word)
            if self._is_readable(result):
                return result
        
        return random.choice(self.corpus)

# ========== ФУНКЦИИ ==========
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                for key in DEFAULT_SETTINGS:
                    if key not in saved:
                        saved[key] = DEFAULT_SETTINGS[key]
                return saved
        except:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except:
        pass

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

neural_networks = {
    "ru": MegaNeuralNetwork("ru"),
    "en": MegaNeuralNetwork("en")
}

def get_word(lang):
    settings = load_settings()
    if settings.get("use_custom_neural", True):
        return neural_networks[lang].generate_word()
    else:
        if lang == "ru":
            words = ["КОТ", "ДОМ", "ЛЕС", "САД", "РОЗА", "МАМА", "ПАПА", "СЫН", "ДОЧЬ", "БРАТ"]
        else:
            words = ["CAT", "DOG", "SUN", "MOON", "STAR", "TREE", "FLOWER", "BIRD", "FISH", "HOUSE"]
        return random.choice(words)

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
        settings = load_settings()
        texts = settings["texts"]
        display = self.get_display_word()
        wrong = ", ".join(self.wrong_letters) if self.wrong_letters else "—"
        
        text = f"""{texts["game_title"]}

{texts["game_word"].format(display=display)}
{texts["game_attempts"].format(attempts=self.attempts)}
{texts["game_wrong"].format(wrong=wrong)}
{texts["game_reward"]}

{message}

{texts["game_enter"]}"""
        return text
    
    def guess_letter(self, letter):
        settings = load_settings()
        texts = settings["texts"]
        letter = letter.upper()
        
        if len(letter) > 1:
            if letter == self.word:
                reward = 50
                if self.effects.get("double"):
                    reward *= 2
                add_crystals(self.user_id, reward)
                add_win(self.user_id)
                self.active = False
                return True, texts["game_win"].format(word=self.word, reward=reward)
            
            self.attempts -= 1
            if self.attempts <= 0:
                if not self.effects.get("shield"):
                    add_loss(self.user_id)
                self.active = False
                return False, texts["game_lose"].format(word=self.word)
            return False, texts["game_wrong_word"].format(attempts=self.attempts)
        
        if letter in self.guessed_letters or letter in self.wrong_letters:
            return False, texts["game_already_used"]
        
        if letter in self.word:
            self.guessed_letters.append(letter)
            
            if all(l in self.guessed_letters for l in self.word):
                reward = 50
                if self.effects.get("double"):
                    reward *= 2
                add_crystals(self.user_id, reward)
                add_win(self.user_id)
                self.active = False
                return True, texts["game_win"].format(word=self.word, reward=reward)
            
            return True, texts["game_yes_letter"]
        else:
            self.wrong_letters.append(letter)
            self.attempts -= 1
            
            if self.attempts <= 0:
                if not self.effects.get("shield"):
                    add_loss(self.user_id)
                self.active = False
                return False, texts["game_lose"].format(word=self.word)
            
            return False, texts["game_no_letter"].format(attempts=self.attempts)
    
    def use_hint(self):
        settings = load_settings()
        texts = settings["texts"]
        not_guessed = [l for l in self.word if l not in self.guessed_letters]
        if not_guessed:
            hint_letter = random.choice(not_guessed)
            self.guessed_letters.append(hint_letter)
            return texts["game_hint"].format(letter=hint_letter)
        return texts["game_all_letters"]
    
    def reroll_word(self):
        settings = load_settings()
        texts = settings["texts"]
        self.word = get_word(self.lang)
        self.guessed_letters = []
        self.wrong_letters = []
        self.attempts = 6
        return texts["game_reroll"]

# ========== КЛАВИАТУРЫ ==========
def send_with_image(chat_id, image_key, text, reply_markup=None):
    settings = load_settings()
    image_url = settings["images"].get(image_key, "")
    if image_url:
        try:
            bot.send_photo(chat_id=chat_id, photo=image_url, caption=text, reply_markup=reply_markup, parse_mode="HTML")
        except:
            bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode="HTML")

def edit_with_image(chat_id, message_id, image_key, text, reply_markup=None):
    settings = load_settings()
    image_url = settings["images"].get(image_key, "")
    if image_url:
        try:
            bot.edit_message_media(media=types.InputMediaPhoto(media=image_url, caption=text, parse_mode="HTML"), chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
        except:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup, parse_mode="HTML")
    else:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup, parse_mode="HTML")

def lobby_kb():
    settings = load_settings()
    texts = settings["texts"]["main_buttons"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(texts["start"], callback_data="start_game"),
        types.InlineKeyboardButton(texts["donate"], callback_data="donate"),
        types.InlineKeyboardButton(texts["shop"], callback_data="shop"),
        types.InlineKeyboardButton(texts["top"], callback_data="top"),
        types.InlineKeyboardButton(texts["stats"], callback_data="stats"),
        types.InlineKeyboardButton(texts["lang"], callback_data="lang"),
        types.InlineKeyboardButton(texts["help"], callback_data="help")
    )
    return markup

def donate_kb():
    settings = load_settings()
    texts = settings["texts"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("TELEGRAM STARS", callback_data="donate_stars_menu"),
        types.InlineKeyboardButton("КРИПТОВАЛЮТА", callback_data="donate_crypto_menu"),
        types.InlineKeyboardButton(texts["donate_back"], callback_data="back_to_main")
    )
    return markup

def donate_stars_kb():
    settings = load_settings()
    texts = settings["texts"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(texts["donate_stars_1"], callback_data="donate_1"),
        types.InlineKeyboardButton(texts["donate_stars_2"], callback_data="donate_2"),
        types.InlineKeyboardButton(texts["donate_stars_5"], callback_data="donate_5"),
        types.InlineKeyboardButton(texts["donate_stars_10"], callback_data="donate_10"),
        types.InlineKeyboardButton(texts["donate_stars_20"], callback_data="donate_20"),
        types.InlineKeyboardButton(texts["donate_stars_50"], callback_data="donate_50"),
        types.InlineKeyboardButton(texts["donate_back"], callback_data="donate")
    )
    return markup

def donate_crypto_kb():
    settings = load_settings()
    texts = settings["texts"]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(texts["donate_usdt"], callback_data="no"),
        types.InlineKeyboardButton(texts["donate_btc"], callback_data="no"),
        types.InlineKeyboardButton(texts["donate_ton"], callback_data="no"),
        types.InlineKeyboardButton(texts["donate_back"], callback_data="donate")
    )
    return markup

def shop_kb():
    settings = load_settings()
    texts = settings["texts"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(texts["shop_hint"], callback_data="buy_hint"),
        types.InlineKeyboardButton(texts["shop_reroll"], callback_data="buy_reroll"),
        types.InlineKeyboardButton(texts["shop_shield"], callback_data="buy_shield"),
        types.InlineKeyboardButton(texts["shop_double"], callback_data="buy_double"),
        types.InlineKeyboardButton(texts["shop_back"], callback_data="back_to_main")
    )
    return markup

def top_kb():
    settings = load_settings()
    texts = settings["texts"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(texts["top_crystals"], callback_data="top_crystals"),
        types.InlineKeyboardButton(texts["top_wins"], callback_data="top_wins"),
        types.InlineKeyboardButton(texts["top_streak"], callback_data="top_streak"),
        types.InlineKeyboardButton(texts["top_donations"], callback_data="top_donations"),
        types.InlineKeyboardButton(texts["shop_back"], callback_data="back_to_main")
    )
    return markup

def lang_kb():
    settings = load_settings()
    texts = settings["texts"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(texts["lang_ru"], callback_data="lang_ru"),
        types.InlineKeyboardButton(texts["lang_en"], callback_data="lang_en"),
        types.InlineKeyboardButton(texts["shop_back"], callback_data="back_to_main")
    )
    return markup

def game_kb(user_id):
    settings = load_settings()
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
        types.InlineKeyboardButton("✏️ Изменить текст", callback_data="admin_edit_text"),
        types.InlineKeyboardButton("🖼️ Изменить картинку", callback_data="admin_edit_image"),
        types.InlineKeyboardButton("🧠 Нейросеть", callback_data="admin_neural"),
        types.InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
    )
    return markup

def admin_edit_text_kb():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("Главное меню", callback_data="admin_text_main"),
        types.InlineKeyboardButton("Игра", callback_data="admin_text_game"),
        types.InlineKeyboardButton("Магазин", callback_data="admin_text_shop"),
        types.InlineKeyboardButton("Топ", callback_data="admin_text_top"),
        types.InlineKeyboardButton("Статистика", callback_data="admin_text_stats"),
        types.InlineKeyboardButton("Донат", callback_data="admin_text_donate"),
        types.InlineKeyboardButton("Язык", callback_data="admin_text_lang"),
        types.InlineKeyboardButton("Помощь", callback_data="admin_text_help"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="admin_panel")
    )
    return markup

# ========== КОМАНДЫ ==========
active_games = {}

@bot.message_handler(commands=['start', 'guess', 'menu', 'lobby'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    user = get_user(user_id)
    user['username'] = username
    update_user(user_id, user)
    
    settings = load_settings()
    texts = settings["texts"]
    
    text = texts["main_title"].format(username=username) + "\n\n" + texts["main_stats"].format(
        crystals=user['crystals'], wins=user['wins'], games=user['games']
    )
    
    send_with_image(message.chat.id, "main", text, lobby_kb())

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    settings = load_settings()
    texts = settings["texts"]
    
    text = f"""{texts["stats_title"]}

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}
{texts["stats_games"].format(games=user['games'])}
{texts["stats_streak"].format(streak=user['streak'])}
{texts["stats_best_streak"].format(best_streak=user['best_streak'])}
{texts["stats_donated"].format(donated=user.get('donated_stars', 0))}"""
    
    send_with_image(message.chat.id, "stats", text, lobby_kb())

@bot.message_handler(commands=['top'])
def top_command(message):
    settings = load_settings()
    texts = settings["texts"]
    send_with_image(message.chat.id, "top", texts["top_title"], top_kb())

@bot.message_handler(commands=['shop'])
def shop_command(message):
    settings = load_settings()
    texts = settings["texts"]
    send_with_image(message.chat.id, "shop", texts["shop_title"], shop_kb())

@bot.message_handler(commands=['lang'])
def lang_command(message):
    settings = load_settings()
    texts = settings["texts"]
    send_with_image(message.chat.id, "main", texts["lang_title"], lang_kb())

@bot.message_handler(commands=['donate'])
def donate_command(message):
    settings = load_settings()
    texts = settings["texts"]
    send_with_image(message.chat.id, "donate", texts["donate_title"], donate_kb())

@bot.message_handler(commands=['help'])
def help_command(message):
    settings = load_settings()
    texts = settings["texts"]
    text = f"""{texts["help_title"]}

{texts["help_text"]}"""
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
                settings = load_settings()
                texts = settings["texts"]
                menu_text = texts["main_title"].format(username=user['username']) + "\n\n" + texts["main_stats"].format(
                    crystals=user['crystals'], wins=user['wins'], games=user['games']
                )
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
            settings = load_settings()
            texts = settings["texts"]
            text = texts["main_title"].format(username=user['username']) + "\n\n" + texts["main_stats"].format(
                crystals=user['crystals'], wins=user['wins'], games=user['games']
            ) + "\n\nНет активной игры. Нажми «Начать игру»"
            send_with_image(message.chat.id, "main", text, lobby_kb())

# ========== ОБРАБОТКА КНОПОК ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    user = get_user(user_id)
    settings = load_settings()
    texts = settings["texts"]
    
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
        text = texts["main_title"].format(username=user['username']) + "\n\n" + texts["main_stats"].format(
            crystals=user['crystals'], wins=user['wins'], games=user['games']
        )
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, lobby_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "donate":
        edit_with_image(call.message.chat.id, call.message.message_id, "donate", texts["donate_title"], donate_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "donate_stars_menu":
        text = texts["donate_stars_title"]
        edit_with_image(call.message.chat.id, call.message.message_id, "donate", text, donate_stars_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "donate_crypto_menu":
        text = texts["donate_crypto_title"]
        edit_with_image(call.message.chat.id, call.message.message_id, "donate", text, donate_crypto_kb())
        bot.answer_callback_query(call.id)
    
    elif data.startswith("donate_") and data not in ["donate_stars_menu", "donate_crypto_menu"]:
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
        edit_with_image(call.message.chat.id, call.message.message_id, "shop", texts["shop_title"], shop_kb())
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
        edit_with_image(call.message.chat.id, call.message.message_id, "shop", texts["shop_title"], shop_kb())
    
    elif data == "top":
        edit_with_image(call.message.chat.id, call.message.message_id, "top", texts["top_title"], top_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "top_crystals":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'crystals': u.get('crystals', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['crystals'], reverse=True)
        text = f"{texts['top_crystals']}\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['crystals']}💎\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb(), parse_mode="HTML")
        bot.answer_callback_query(call.id)
    
    elif data == "top_wins":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'wins': u.get('wins', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['wins'], reverse=True)
        text = f"{texts['top_wins']}\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['wins']}🏆\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb(), parse_mode="HTML")
        bot.answer_callback_query(call.id)
    
    elif data == "top_streak":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'streak': u.get('best_streak', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['streak'], reverse=True)
        text = f"{texts['top_streak']}\n\n"
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
        text = f"{texts['top_donations']}\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['stars']}⭐\n"
        if not top:
            text += "Пока нет донатов"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb(), parse_mode="HTML")
        bot.answer_callback_query(call.id)
    
    elif data == "stats":
        text = f"""{texts["stats_title"]}

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}
{texts["stats_games"].format(games=user['games'])}
{texts["stats_streak"].format(streak=user['streak'])}
{texts["stats_best_streak"].format(best_streak=user['best_streak'])}
{texts["stats_donated"].format(donated=user.get('donated_stars', 0))}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "stats", text, lobby_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "lang":
        edit_with_image(call.message.chat.id, call.message.message_id, "main", texts["lang_title"], lang_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "lang_ru":
        user['lang'] = 'ru'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "Язык: русский")
        text = texts["main_title"].format(username=user['username']) + "\n\n" + texts["main_stats"].format(
            crystals=user['crystals'], wins=user['wins'], games=user['games']
        )
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, lobby_kb())
    
    elif data == "lang_en":
        user['lang'] = 'en'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "Language: English")
        text = texts["main_title"].format(username=user['username']) + "\n\n" + texts["main_stats"].format(
            crystals=user['crystals'], wins=user['wins'], games=user['games']
        )
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, lobby_kb())
    
    elif data == "help":
        text = f"""{texts["help_title"]}

{texts["help_text"]}"""
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
        text = texts["main_title"].format(username=user['username']) + "\n\n" + texts["main_stats"].format(
            crystals=user['crystals'], wins=user['wins'], games=user['games']
        )
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, lobby_kb())
    
    elif data == "admin_panel":
        bot.edit_message_text("🔧 АДМИН ПАНЕЛЬ", call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
        bot.answer_callback_query(call.id)
    
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
    
    elif data == "admin_edit_text":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        bot.edit_message_text("✏️ РЕДАКТИРОВАНИЕ ТЕКСТОВ\n\nВыбери раздел:", call.message.chat.id, call.message.message_id, reply_markup=admin_edit_text_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "admin_edit_image":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for img in ["main", "game", "shop", "top", "stats", "donate"]:
            markup.add(types.InlineKeyboardButton(img.upper(), callback_data=f"admin_img_{img}"))
        markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="admin_panel"))
        bot.edit_message_text("🖼️ ВЫБЕРИ КАРТИНКУ ДЛЯ ИЗМЕНЕНИЯ\n\nОтправь новую ссылку или фото:", call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    elif data.startswith("admin_img_"):
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        img_key = data.split("_")[2]
        msg = bot.send_message(call.message.chat.id, f"Отправь новую ссылку или фото для {img_key}:")
        bot.register_next_step_handler(msg, lambda m: admin_set_image(m, img_key, call.message.chat.id, call.message.message_id))
        bot.answer_callback_query(call.id)
    
    elif data.startswith("admin_text_"):
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        section = data.split("_")[2]
        show_current_texts(call.message.chat.id, section, call.message.message_id)
        bot.answer_callback_query(call.id)
    
    elif data == "admin_neural":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        settings = load_settings()
        status = "ВКЛЮЧЕНА" if settings.get("use_custom_neural") else "ВЫКЛЮЧЕНА"
        power = settings.get("neural_power", 95)
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("Включить свою нейросеть" if not settings.get("use_custom_neural") else "Выключить свою нейросеть", callback_data="admin_neural_toggle"),
            types.InlineKeyboardButton(f"Мощность: {power}%", callback_data="admin_neural_power"),
            types.InlineKeyboardButton("◀️ Назад", callback_data="admin_panel")
        )
        text = f"🧠 НЕЙРОСЕТЬ\n\nРежим: {status}\nМощность: {power}%\n\nСвоя нейросеть генерирует более реалистичные слова"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    elif data == "admin_neural_toggle":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        settings = load_settings()
        settings["use_custom_neural"] = not settings.get("use_custom_neural", True)
        save_settings(settings)
        bot.answer_callback_query(call.id, f"Нейросеть {'включена' if settings['use_custom_neural'] else 'выключена'}")
        callback_handler(call)
    
    elif data == "admin_neural_power":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        msg = bot.send_message(call.message.chat.id, "Введите мощность нейросети (1-100):\nЧем выше, тем умнее слова")
        bot.register_next_step_handler(msg, admin_set_neural_power)
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

def admin_set_image(message, img_key, chat_id, msg_id):
    if message.from_user.id != ADMIN_ID:
        return
    settings = load_settings()
    if message.photo:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        settings["images"][img_key] = file_url
    else:
        settings["images"][img_key] = message.text.strip()
    save_settings(settings)
    bot.send_message(chat_id, f"✅ Картинка {img_key} обновлена!")
    bot.edit_message_text("🔧 АДМИН ПАНЕЛЬ", chat_id, msg_id, reply_markup=admin_panel_kb())

def admin_set_neural_power(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        power = int(message.text.strip())
        if 1 <= power <= 100:
            settings = load_settings()
            settings["neural_power"] = power
            save_settings(settings)
            bot.reply_to(message, f"✅ Мощность нейросети: {power}%")
        else:
            bot.reply_to(message, "❌ Число от 1 до 100")
    except:
        bot.reply_to(message, "❌ Введите число от 1 до 100")

def show_current_texts(chat_id, section, msg_id):
    settings = load_settings()
    texts = settings["texts"]
    
    if section == "main":
        text = f"""✏️ ГЛАВНОЕ МЕНЮ

Текущие тексты:
main_title: {texts["main_title"]}
main_stats: {texts["main_stats"]}

Кнопки:
start: {texts["main_buttons"]["start"]}
donate: {texts["main_buttons"]["donate"]}
shop: {texts["main_buttons"]["shop"]}
top: {texts["main_buttons"]["top"]}
stats: {texts["main_buttons"]["stats"]}
lang: {texts["main_buttons"]["lang"]}
help: {texts["main_buttons"]["help"]}

Введи новое значение в формате:
ключ = значение

Пример: main_title = <b>НОВЫЙ ЗАГОЛОВОК</b>"""
        bot.edit_message_text(text, chat_id, msg_id, reply_markup=admin_edit_text_kb())
        msg = bot.send_message(chat_id, "Введите изменения:")
        bot.register_next_step_handler(msg, lambda m: admin_edit_text(m, "main", chat_id, msg_id))
    
    elif section == "game":
        text = f"""✏️ ИГРА

Текущие тексты:
game_title: {texts["game_title"]}
game_word: {texts["game_word"]}
game_attempts: {texts["game_attempts"]}
game_wrong: {texts["game_wrong"]}
game_reward: {texts["game_reward"]}
game_enter: {texts["game_enter"]}
game_win: {texts["game_win"]}
game_lose: {texts["game_lose"]}
game_wrong_word: {texts["game_wrong_word"]}
game_yes_letter: {texts["game_yes_letter"]}
game_no_letter: {texts["game_no_letter"]}
game_already_used: {texts["game_already_used"]}
game_hint: {texts["game_hint"]}
game_all_letters: {texts["game_all_letters"]}
game_reroll: {texts["game_reroll"]}

Введи новое значение в формате:
ключ = значение

Пример: game_win = <b>ТЫ ПОБЕДИЛ!</b> {word}"""
        bot.edit_message_text(text, chat_id, msg_id, reply_markup=admin_edit_text_kb())
        msg = bot.send_message(chat_id, "Введите изменения:")
        bot.register_next_step_handler(msg, lambda m: admin_edit_text(m, "game", chat_id, msg_id))

def admin_edit_text(message, section, chat_id, msg_id):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        text = message.text.strip()
        if "=" not in text:
            bot.reply_to(message, "❌ Формат: ключ = значение")
            return
        key, value = text.split("=", 1)
        key = key.strip()
        value = value.strip()
        
        settings = load_settings()
        if section == "main":
            if key in settings["texts"]:
                settings["texts"][key] = value
            elif key in settings["texts"]["main_buttons"]:
                settings["texts"]["main_buttons"][key] = value
            else:
                bot.reply_to(message, f"❌ Ключ {key} не найден")
                return
        else:
            if key in settings["texts"]:
                settings["texts"][key] = value
            else:
                bot.reply_to(message, f"❌ Ключ {key} не найден")
                return
        
        save_settings(settings)
        bot.reply_to(message, f"✅ Обновлено: {key} = {value}")
        bot.send_message(chat_id, "🔧 АДМИН ПАНЕЛЬ", reply_markup=admin_panel_kb())
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

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
    print("🤖 Бот с лютой нейросетью запущен")
    print("⭐ Донат: Telegram Stars + Криптовалюта (без эмодзи на кнопках доната)")
    print("🔧 Админ-панель: /admin")
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")