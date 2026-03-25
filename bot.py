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
from datetime import datetime, timedelta

TOKEN = "7766594100:AAH7j4yGEW5Tqoiu8IguYh0Mn3g7lMbPwj8"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 8388843828

# ========== ФАЙЛЫ ==========
USERS_FILE = "guess_users.json"
DONATIONS_FILE = "donations.json"
SETTINGS_FILE = "bot_settings.json"
DAILY_FILE = "daily_bonus.json"

# ========== КАРТИНКИ ==========
IMAGES = {
    "main": "https://s10.iimage.su/s/24/gyiVYQqxC4FhKIyY4GD47Mvv1YfJ3KFWNkUAbyKQN.png",
    "game": "https://s10.iimage.su/s/24/gFsXdz1x7sCnEVQMjpFfzw2t2qzT0lMS8Bz4zJGpU.jpg",
    "shop": "https://s10.iimage.su/s/24/g0Sj1dDxuKC84sMhP8q3DDK6Q7MDgBRam1v0lyP8H.jpg",
    "top": "https://s10.iimage.su/s/24/ggZ4ONmxr0bk39GQvB3ODh3cJbSU2XFLlrPstj5cp.jpg",
    "stats": "https://s10.iimage.su/s/24/gDyJ0rdxDzMm1NngFnHePE7MB5uz3oQphOMwXKCtu.jpg",
    "donate": "https://s10.iimage.su/s/24/gsqCZaQxs8sp4aoo0dGKbiNKWzrP6Dg5bEnSjvv9f.jpg"
}

# ========== ПОЛНЫЙ ПЕРЕВОД ==========
TEXTS = {
    "ru": {
        "game_title": "🎮 УГАДАЙ СЛОВО",
        "your_game": "👤 Ваша игра",
        "word": "📖 Слово: {display}",
        "attempts": "💪 Попыток: {attempts}",
        "wrong": "❌ Ошибки: {wrong}",
        "reward": "💎 За победу: +50",
        "enter": "\n\n✍️ Введите букву или слово:",
        "win": "🏆 ПОБЕДА! 🏆\n\n📖 Слово: {word}\n💎 +{reward}",
        "lose": "💀 ПОРАЖЕНИЕ! 💀\n\n📖 Слово: {word}",
        "wrong_word": "❌ Неправильно! 💪 Осталось попыток: {attempts}",
        "yes_letter": "✅ Есть такая буква!",
        "no_letter": "❌ Нет такой буквы! 💪 Осталось попыток: {attempts}",
        "already_used": "⚠️ Эта буква уже называлась",
        "hint": "🔍 Подсказка: буква {letter} есть в слове!",
        "all_letters": "🔓 Все буквы уже открыты!",
        "reroll": "🔄 Слово заменено!",
        "shop_title": "🛒 МАГАЗИН",
        "shop_hint": "🔍 Подсказка — 50💎",
        "shop_reroll": "🔄 Сменить слово — 100💎",
        "shop_shield": "🛡️ Защита — 150💎",
        "shop_double": "💎 Кристалл x2 — 500💎",
        "shop_back": "◀️ Назад",
        "top_title": "🏆 ТАБЛИЦА ЛИДЕРОВ",
        "top_crystals": "💰 ТОП ПО КРИСТАЛЛАМ",
        "top_wins": "🏆 ТОП ПО ПОБЕДАМ",
        "top_streak": "🔥 ТОП ПО СЕРИИ",
        "top_donations": "⭐ ТОП ПО ДОНАТАМ",
        "stats_title": "📊 ТВОЯ СТАТИСТИКА",
        "stats_crystals": "💰 Кристаллов: {crystals}",
        "stats_wins": "🏆 Побед: {wins}",
        "stats_games": "🎮 Игр: {games}",
        "stats_streak": "🔥 Текущая серия: {streak}",
        "stats_best_streak": "🏅 Лучшая серия: {best_streak}",
        "stats_donated": "⭐ Поддержал проект: {donated}",
        "donate_title": "⭐ ПОДДЕРЖАТЬ ПРОЕКТ",
        "donate_stars_title": "TELEGRAM STARS",
        "donate_desc": "✨ 1 Star = 50 кристаллов + бонусы!",
        "donate_stars_1": "1 Star → 50 +0 бонус",
        "donate_stars_2": "2 Stars → 100 +10 бонус",
        "donate_stars_5": "5 Stars → 250 +30 бонус",
        "donate_stars_10": "10 Stars → 500 +75 бонус",
        "donate_stars_20": "20 Stars → 1000 +200 бонус",
        "donate_stars_50": "50 Stars → 2500 +750 бонус",
        "donate_back": "◀️ Назад",
        "daily_title": "🎁 ЕЖЕДНЕВНЫЙ БОНУС",
        "daily_reward": "🎉 Вы получили {crystals} кристаллов!",
        "daily_already": "⏰ Вы уже получали бонус сегодня! Приходите завтра.",
        "daily_streak": "🔥 Серия: {streak} дней!",
        "wheel_title": "🎡 КОЛЕСО ФОРТУНЫ",
        "wheel_price": "💎 Стоимость вращения: {price}",
        "wheel_win": "🎉 ПОЗДРАВЛЯЕМ! 🎉\n\n💰 Вы выиграли {prize} кристаллов!",
        "wheel_lose": "😢 Вам выпало {prize} кристаллов...\n\n💪 В следующий раз повезёт!",
        "wheel_no_money": "❌ Не хватает кристаллов! Нужно {price}",
        "lang_title": "🌐 ВЫБЕРИ ЯЗЫК",
        "lang_ru": "🇷🇺 Русский",
        "lang_en": "🇬🇧 English",
        "help_title": "❓ ПОМОЩЬ",
        "help_text": "🎮 КАК ИГРАТЬ:\n\n1️⃣ Нажми «Начать игру»\n2️⃣ Введи букву или слово\n3️⃣ Угадай слово\n\n💡 СОВЕТЫ:\n• Буквы отображаются на своих местах\n• Используй подсказки в магазине\n• За победу дают кристаллы\n• Ежедневный бонус и колесо фортуны ждут тебя!\n\n📊 КОМАНДЫ:\n/start — главное меню\n/stats — статистика\n/top — таблица лидеров\n/shop — магазин\n/daily — ежедневный бонус\n/wheel — колесо фортуны\n/lang — язык\n/donate — поддержать\n/help — помощь",
        "buttons": {
            "start": "🎮 Начать игру",
            "donate": "⭐ Поддержать",
            "shop": "🛒 Магазин",
            "top": "🏆 Топ игроков",
            "stats": "📊 Статистика",
            "lang": "🌐 Язык",
            "daily": "🎁 Ежедневный бонус",
            "wheel": "🎡 Колесо фортуны",
            "help": "❓ Помощь",
            "back": "◀️ Назад",
            "spin": "🌀 Крутить!"
        }
    },
    "en": {
        "game_title": "🎮 GUESS THE WORD",
        "your_game": "👤 Your game",
        "word": "📖 Word: {display}",
        "attempts": "💪 Attempts: {attempts}",
        "wrong": "❌ Wrong: {wrong}",
        "reward": "💎 Reward: +50",
        "enter": "\n\n✍️ Enter a letter or word:",
        "win": "🏆 VICTORY! 🏆\n\n📖 Word: {word}\n💎 +{reward}",
        "lose": "💀 DEFEAT! 💀\n\n📖 Word: {word}",
        "wrong_word": "❌ Wrong! 💪 Attempts left: {attempts}",
        "yes_letter": "✅ Letter found!",
        "no_letter": "❌ Letter not found! 💪 Attempts left: {attempts}",
        "already_used": "⚠️ This letter was already used",
        "hint": "🔍 Hint: letter {letter} is in the word!",
        "all_letters": "🔓 All letters are already open!",
        "reroll": "🔄 Word changed!",
        "shop_title": "🛒 SHOP",
        "shop_hint": "🔍 Hint — 50💎",
        "shop_reroll": "🔄 Change word — 100💎",
        "shop_shield": "🛡️ Shield — 150💎",
        "shop_double": "💎 Crystal x2 — 500💎",
        "shop_back": "◀️ Back",
        "top_title": "🏆 LEADERBOARD",
        "top_crystals": "💰 TOP BY CRYSTALS",
        "top_wins": "🏆 TOP BY WINS",
        "top_streak": "🔥 TOP BY STREAK",
        "top_donations": "⭐ TOP BY DONATIONS",
        "stats_title": "📊 YOUR STATISTICS",
        "stats_crystals": "💰 Crystals: {crystals}",
        "stats_wins": "🏆 Wins: {wins}",
        "stats_games": "🎮 Games: {games}",
        "stats_streak": "🔥 Current streak: {streak}",
        "stats_best_streak": "🏅 Best streak: {best_streak}",
        "stats_donated": "⭐ Donated: {donated}",
        "donate_title": "⭐ SUPPORT THE PROJECT",
        "donate_stars_title": "TELEGRAM STARS",
        "donate_desc": "✨ 1 Star = 50 crystals + bonuses!",
        "donate_stars_1": "1 Star → 50 +0 bonus",
        "donate_stars_2": "2 Stars → 100 +10 bonus",
        "donate_stars_5": "5 Stars → 250 +30 bonus",
        "donate_stars_10": "10 Stars → 500 +75 bonus",
        "donate_stars_20": "20 Stars → 1000 +200 bonus",
        "donate_stars_50": "50 Stars → 2500 +750 bonus",
        "donate_back": "◀️ Back",
        "daily_title": "🎁 DAILY BONUS",
        "daily_reward": "🎉 You received {crystals} crystals!",
        "daily_already": "⏰ You already received today's bonus! Come back tomorrow.",
        "daily_streak": "🔥 Streak: {streak} days!",
        "wheel_title": "🎡 WHEEL OF FORTUNE",
        "wheel_price": "💎 Spin cost: {price}",
        "wheel_win": "🎉 CONGRATULATIONS! 🎉\n\n💰 You won {prize} crystals!",
        "wheel_lose": "😢 You got {prize} crystals...\n\n💪 Better luck next time!",
        "wheel_no_money": "❌ Not enough crystals! Need {price}",
        "lang_title": "🌐 CHOOSE LANGUAGE",
        "lang_ru": "🇷🇺 Russian",
        "lang_en": "🇬🇧 English",
        "help_title": "❓ HELP",
        "help_text": "🎮 HOW TO PLAY:\n\n1️⃣ Press «Start Game»\n2️⃣ Enter a letter or word\n3️⃣ Guess the word\n\n💡 TIPS:\n• Letters appear in their places\n• Use hints from the shop\n• Get crystals for wins\n• Daily bonus and wheel of fortune are waiting!\n\n📊 COMMANDS:\n/start — main menu\n/stats — statistics\n/top — leaderboard\n/shop — shop\n/daily — daily bonus\n/wheel — wheel of fortune\n/lang — language\n/donate — support\n/help — help",
        "buttons": {
            "start": "🎮 Start Game",
            "donate": "⭐ Support",
            "shop": "🛒 Shop",
            "top": "🏆 Leaderboard",
            "stats": "📊 Statistics",
            "lang": "🌐 Language",
            "daily": "🎁 Daily bonus",
            "wheel": "🎡 Wheel of Fortune",
            "help": "❓ Help",
            "back": "◀️ Back",
            "spin": "🌀 Spin!"
        }
    }
}

# ========== ФУНКЦИИ ==========
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
            'lang': 'ru',
            'donated_stars': 0,
            'last_daily': None,
            'daily_streak': 0
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

def get_daily_bonus(user_id):
    user = get_user(user_id)
    today = datetime.now().date().isoformat()
    
    if user.get('last_daily') == today:
        return None, user.get('daily_streak', 0)
    
    last_daily = user.get('last_daily')
    if last_daily:
        last_date = datetime.fromisoformat(last_daily).date()
        if (datetime.now().date() - last_date).days == 1:
            user['daily_streak'] = user.get('daily_streak', 0) + 1
        else:
            user['daily_streak'] = 1
    else:
        user['daily_streak'] = 1
    
    streak = user['daily_streak']
    bonus = 50 + (streak - 1) * 10
    bonus = min(bonus, 500)
    
    user['last_daily'] = today
    user['crystals'] += bonus
    update_user(user_id, user)
    
    return bonus, streak

def spin_wheel(user_id):
    user = get_user(user_id)
    price = 50
    
    if user['crystals'] < price:
        return None, price
    
    user['crystals'] -= price
    
    prizes = [0, 10, 20, 30, 50, 100, 150, 200, 300, 500]
    weights = [0.15, 0.15, 0.15, 0.12, 0.10, 0.08, 0.07, 0.06, 0.05, 0.07]
    
    prize = random.choices(prizes, weights=weights, k=1)[0]
    user['crystals'] += prize
    update_user(user_id, user)
    
    return prize, price

# ========== СЛОВАРЬ СЛОВ ==========
RUSSIAN_WORDS = [
    "КОТ", "ДОМ", "ЛЕС", "САД", "РОЗА", "МАМА", "ПАПА", "СЫН", "ДОЧЬ", "БРАТ",
    "СЕСТРА", "ДРУГ", "МИР", "ДЕНЬ", "НОЧЬ", "ГОРОД", "СОЛНЦЕ", "ЗВЕЗДА", "КНИГА",
    "СТОЛ", "СТУЛ", "ОКНО", "ДВЕРЬ", "РУЧКА", "МАШИНА", "УЛИЦА", "ПАРК", "ЛУНА",
    "ЗЕМЛЯ", "ВОДА", "ОГОНЬ", "ВЕТЕР", "СНЕГ", "ДОЖДЬ", "ЛЕТО", "ЗИМА", "ВЕСНА",
    "ОСЕНЬ", "УТРО", "ВЕЧЕР", "СВЕТ", "ТЕНЬ", "ГОЛОС", "СЛОВО", "БУКВА", "СТРАНА",
    "ПЛАНЕТА", "ПРИРОДА", "ЧЕЛОВЕК", "СЧАСТЬЕ", "ЛЮБОВЬ", "ДРУЖБА", "ШКОЛА"
]

ENGLISH_WORDS = [
    "CAT", "DOG", "SUN", "MOON", "STAR", "TREE", "FLOWER", "BIRD", "FISH",
    "HOUSE", "CAR", "MOM", "DAD", "SON", "DAUGHTER", "BROTHER", "SISTER",
    "FRIEND", "LOVE", "HOPE", "WATER", "FIRE", "EARTH", "WIND", "CLOUD",
    "RAIN", "SNOW", "SUMMER", "WINTER", "SPRING", "AUTUMN", "DAY", "NIGHT",
    "CITY", "TOWN", "STREET", "PARK", "RIVER", "LAKE", "SEA", "OCEAN"
]

def get_word(lang):
    if lang == "ru":
        return random.choice(RUSSIAN_WORDS)
    else:
        return random.choice(ENGLISH_WORDS)

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
        texts = TEXTS[self.lang]
        display = self.get_display_word()
        wrong = ", ".join(self.wrong_letters) if self.wrong_letters else "—"
        
        text = f"""{texts["game_title"]}
{texts["your_game"]}

{texts["word"].format(display=display)}
{texts["attempts"].format(attempts=self.attempts)}
{texts["wrong"].format(wrong=wrong)}
{texts["reward"]}

{message}

{texts["enter"]}"""
        return text
    
    def guess_letter(self, letter):
        texts = TEXTS[self.lang]
        letter = letter.upper()
        
        if len(letter) > 1:
            if letter == self.word:
                reward = 50
                if self.effects.get("double"):
                    reward *= 2
                add_crystals(self.user_id, reward)
                add_win(self.user_id, self.word)
                self.active = False
                return True, texts["win"].format(word=self.word, reward=reward)
            
            self.attempts -= 1
            if self.attempts <= 0:
                if not self.effects.get("shield"):
                    add_loss(self.user_id)
                self.active = False
                return False, texts["lose"].format(word=self.word)
            return False, texts["wrong_word"].format(attempts=self.attempts)
        
        if letter in self.guessed_letters or letter in self.wrong_letters:
            return False, texts["already_used"]
        
        if letter in self.word:
            self.guessed_letters.append(letter)
            
            if all(l in self.guessed_letters for l in self.word):
                reward = 50
                if self.effects.get("double"):
                    reward *= 2
                add_crystals(self.user_id, reward)
                add_win(self.user_id, self.word)
                self.active = False
                return True, texts["win"].format(word=self.word, reward=reward)
            
            return True, texts["yes_letter"]
        else:
            self.wrong_letters.append(letter)
            self.attempts -= 1
            
            if self.attempts <= 0:
                if not self.effects.get("shield"):
                    add_loss(self.user_id)
                self.active = False
                return False, texts["lose"].format(word=self.word)
            
            return False, texts["no_letter"].format(attempts=self.attempts)
    
    def use_hint(self):
        texts = TEXTS[self.lang]
        not_guessed = [l for l in self.word if l not in self.guessed_letters]
        if not_guessed:
            hint_letter = random.choice(not_guessed)
            self.guessed_letters.append(hint_letter)
            return texts["hint"].format(letter=hint_letter)
        return texts["all_letters"]
    
    def reroll_word(self):
        texts = TEXTS[self.lang]
        self.word = get_word(self.lang)
        self.guessed_letters = []
        self.wrong_letters = []
        self.attempts = 6
        return texts["reroll"]

# ========== КЛАВИАТУРЫ ==========
def get_user_lang(user_id):
    user = get_user(user_id)
    return user.get('lang', 'ru')

def lobby_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]["buttons"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(texts["start"], callback_data="start_game"),
        types.InlineKeyboardButton(texts["donate"], callback_data="donate"),
        types.InlineKeyboardButton(texts["shop"], callback_data="shop"),
        types.InlineKeyboardButton(texts["top"], callback_data="top"),
        types.InlineKeyboardButton(texts["stats"], callback_data="stats"),
        types.InlineKeyboardButton(texts["daily"], callback_data="daily"),
        types.InlineKeyboardButton(texts["wheel"], callback_data="wheel"),
        types.InlineKeyboardButton(texts["lang"], callback_data="lang"),
        types.InlineKeyboardButton(texts["help"], callback_data="help")
    )
    return markup

def donate_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("TELEGRAM STARS", callback_data="donate_stars_menu"),
        types.InlineKeyboardButton(texts["buttons"]["back"], callback_data="back_to_main")
    )
    return markup

def donate_stars_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
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

def shop_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(texts["shop_hint"], callback_data="buy_hint"),
        types.InlineKeyboardButton(texts["shop_reroll"], callback_data="buy_reroll"),
        types.InlineKeyboardButton(texts["shop_shield"], callback_data="buy_shield"),
        types.InlineKeyboardButton(texts["shop_double"], callback_data="buy_double"),
        types.InlineKeyboardButton(texts["shop_back"], callback_data="back_to_main")
    )
    return markup

def top_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(texts["top_crystals"], callback_data="top_crystals"),
        types.InlineKeyboardButton(texts["top_wins"], callback_data="top_wins"),
        types.InlineKeyboardButton(texts["top_streak"], callback_data="top_streak"),
        types.InlineKeyboardButton(texts["top_donations"], callback_data="top_donations"),
        types.InlineKeyboardButton(texts["shop_back"], callback_data="back_to_main")
    )
    return markup

def lang_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(texts["lang_ru"], callback_data="lang_ru"),
        types.InlineKeyboardButton(texts["lang_en"], callback_data="lang_en"),
        types.InlineKeyboardButton(texts["buttons"]["back"], callback_data="back_to_main")
    )
    return markup

def game_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔍 Подсказка (50)", callback_data=f"use_hint_{user_id}"),
        types.InlineKeyboardButton("🔄 Сменить слово (100)", callback_data=f"use_reroll_{user_id}"),
        types.InlineKeyboardButton("🏠 Выйти", callback_data=f"exit_game_{user_id}")
    )
    return markup

def wheel_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(texts["buttons"]["spin"], callback_data=f"wheel_spin_{user_id}"),
        types.InlineKeyboardButton(texts["buttons"]["back"], callback_data="back_to_main")
    )
    return markup

def admin_panel_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton("⭐ Донаты", callback_data="admin_donations"),
        types.InlineKeyboardButton("💎 Выдать кристаллы", callback_data="admin_give"),
        types.InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
    )
    return markup

def send_with_image(chat_id, image_key, text, reply_markup=None):
    image_url = IMAGES.get(image_key)
    if image_url:
        try:
            bot.send_photo(chat_id=chat_id, photo=image_url, caption=text, reply_markup=reply_markup)
        except:
            bot.send_message(chat_id, text, reply_markup=reply_markup)
    else:
        bot.send_message(chat_id, text, reply_markup=reply_markup)

def edit_with_image(chat_id, message_id, image_key, text, reply_markup=None):
    image_url = IMAGES.get(image_key)
    if image_url:
        try:
            bot.edit_message_media(media=types.InputMediaPhoto(media=image_url, caption=text), chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
        except:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup)
    else:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup)

# ========== КОМАНДЫ ==========
active_games = {}

@bot.message_handler(commands=['start', 'guess', 'menu'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    user = get_user(user_id)
    user['username'] = username
    update_user(user_id, user)
    
    lang = user.get('lang', 'ru')
    texts = TEXTS[lang]
    
    text = f"""{texts["game_title"]}

Добро пожаловать, {username}!

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}
{texts["stats_games"].format(games=user['games'])}"""
    
    send_with_image(message.chat.id, "main", text, lobby_kb(user_id))

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user.get('lang', 'ru')
    texts = TEXTS[lang]
    
    text = f"""{texts["stats_title"]}

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}
{texts["stats_games"].format(games=user['games'])}
{texts["stats_streak"].format(streak=user['streak'])}
{texts["stats_best_streak"].format(best_streak=user['best_streak'])}
{texts["stats_donated"].format(donated=user.get('donated_stars', 0))}"""
    
    send_with_image(message.chat.id, "stats", text, lobby_kb(user_id))

@bot.message_handler(commands=['top'])
def top_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    send_with_image(message.chat.id, "top", texts["top_title"], top_kb(user_id))

@bot.message_handler(commands=['shop'])
def shop_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    send_with_image(message.chat.id, "shop", texts["shop_title"], shop_kb(user_id))

@bot.message_handler(commands=['lang'])
def lang_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    send_with_image(message.chat.id, "main", texts["lang_title"], lang_kb(user_id))

@bot.message_handler(commands=['donate'])
def donate_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    text = f"""{texts["donate_title"]}

{texts["donate_desc"]}"""
    send_with_image(message.chat.id, "donate", text, donate_kb(user_id))

@bot.message_handler(commands=['daily'])
def daily_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    
    bonus, streak = get_daily_bonus(user_id)
    
    if bonus is None:
        text = f"""{texts["daily_title"]}

{texts["daily_already"]}
{texts["daily_streak"].format(streak=streak)}"""
    else:
        text = f"""{texts["daily_title"]}

{texts["daily_reward"].format(crystals=bonus)}
{texts["daily_streak"].format(streak=streak)}"""
    
    send_with_image(message.chat.id, "stats", text, lobby_kb(user_id))

@bot.message_handler(commands=['wheel'])
def wheel_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    
    text = f"""{texts["wheel_title"]}

{texts["wheel_price"].format(price=50)}"""
    
    send_with_image(message.chat.id, "stats", text, wheel_kb(user_id))

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    
    text = f"""{texts["help_title"]}

{texts["help_text"]}"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Нет прав")
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
                bot.edit_message_text(msg, game.chat_id, game.message_id)
                del active_games[user_id]
                user = get_user(user_id)
                lang = user.get('lang', 'ru')
                texts = TEXTS[lang]
                menu_text = f"""{texts["game_title"]}

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}"""
                send_with_image(message.chat.id, "main", menu_text, lobby_kb(user_id))
            else:
                new_text = game.get_game_text(msg)
                try:
                    bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id))
                except:
                    pass
            
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
    else:
        if message.text and not message.text.startswith('/'):
            user = get_user(user_id)
            lang = user.get('lang', 'ru')
            texts = TEXTS[lang]
            text = f"""{texts["game_title"]}

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}

Нет активной игры. Нажми «Начать игру»"""
            send_with_image(message.chat.id, "main", text, lobby_kb(user_id))

# ========== ОБРАБОТКА КНОПОК ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    user = get_user(user_id)
    lang = user.get('lang', 'ru')
    texts = TEXTS[lang]
    
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
    elif data.startswith("wheel_spin_"):
        owner_id = int(data.split("_")[2])
        if user_id != owner_id:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return
        data = "wheel_spin"
    
    if data == "back_to_main":
        text = f"""{texts["game_title"]}

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, lobby_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "donate":
        text = f"""{texts["donate_title"]}

{texts["donate_desc"]}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "donate", text, donate_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "donate_stars_menu":
        text = f"{texts['donate_stars_title']}\n\n{texts['donate_desc']}"
        edit_with_image(call.message.chat.id, call.message.message_id, "donate", text, donate_stars_kb(user_id))
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
        edit_with_image(call.message.chat.id, call.message.message_id, "shop", texts["shop_title"], shop_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data.startswith("buy_"):
        item_id = data[4:]
        prices = {"hint": 50, "reroll": 100, "shield": 150, "double": 500}
        if user['crystals'] < prices[item_id]:
            bot.answer_callback_query(call.id, f"❌ Не хватает! Нужно {prices[item_id]}💎", show_alert=True)
            return
        user['crystals'] -= prices[item_id]
        update_user(user_id, user)
        if user_id in active_games and active_games[user_id].active:
            active_games[user_id].effects[item_id] = True
        bot.answer_callback_query(call.id, f"✅ Куплено! -{prices[item_id]}💎", show_alert=True)
        edit_with_image(call.message.chat.id, call.message.message_id, "shop", texts["shop_title"], shop_kb(user_id))
    
    elif data == "top":
        edit_with_image(call.message.chat.id, call.message.message_id, "top", texts["top_title"], top_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "top_crystals":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'crystals': u.get('crystals', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['crystals'], reverse=True)
        text = f"{texts['top_crystals']}\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['crystals']}💎\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "top_wins":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'wins': u.get('wins', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['wins'], reverse=True)
        text = f"{texts['top_wins']}\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['wins']}🏆\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "top_streak":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'streak': u.get('best_streak', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['streak'], reverse=True)
        text = f"{texts['top_streak']}\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['streak']}🔥\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb(user_id))
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
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "stats":
        text = f"""{texts["stats_title"]}

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}
{texts["stats_games"].format(games=user['games'])}
{texts["stats_streak"].format(streak=user['streak'])}
{texts["stats_best_streak"].format(best_streak=user['best_streak'])}
{texts["stats_donated"].format(donated=user.get('donated_stars', 0))}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "stats", text, lobby_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "daily":
        bonus, streak = get_daily_bonus(user_id)
        
        if bonus is None:
            text = f"""{texts["daily_title"]}

{texts["daily_already"]}
{texts["daily_streak"].format(streak=streak)}"""
        else:
            text = f"""{texts["daily_title"]}

{texts["daily_reward"].format(crystals=bonus)}
{texts["daily_streak"].format(streak=streak)}"""
        
        edit_with_image(call.message.chat.id, call.message.message_id, "stats", text, lobby_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "wheel":
        text = f"""{texts["wheel_title"]}

{texts["wheel_price"].format(price=50)}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "stats", text, wheel_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "wheel_spin":
        prize, price = spin_wheel(user_id)
        
        if prize is None:
            text = f"""{texts["wheel_title"]}

{texts["wheel_no_money"].format(price=price)}"""
        else:
            if prize >= 100:
                text = texts["wheel_win"].format(prize=prize)
            else:
                text = texts["wheel_lose"].format(prize=prize)
        
        edit_with_image(call.message.chat.id, call.message.message_id, "stats", text, lobby_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "lang":
        edit_with_image(call.message.chat.id, call.message.message_id, "main", texts["lang_title"], lang_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "lang_ru":
        user['lang'] = 'ru'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "🇷🇺 Язык: русский")
        text = f"""{texts["game_title"]}

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, lobby_kb(user_id))
    
    elif data == "lang_en":
        user['lang'] = 'en'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "🇬🇧 Language: English")
        texts = TEXTS["en"]
        text = f"""{texts["game_title"]}

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, lobby_kb(user_id))
    
    elif data == "help":
        text = f"""{texts["help_title"]}

{texts["help_text"]}"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
    
    elif data == "start_game":
        lang = user.get('lang', 'ru')
        if user_id in active_games and active_games[user_id].active:
            bot.answer_callback_query(call.id, "❌ У вас уже есть игра!", show_alert=True)
            return
        sent = bot.send_message(call.message.chat.id, "🎮 Генерация слова...")
        game = Game(call.message.chat.id, user_id, lang, sent.message_id)
        active_games[user_id] = game
        game_text = game.get_game_text("✨ Игра началась!")
        bot.edit_message_text(game_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "use_hint":
        if user_id not in active_games or not active_games[user_id].active:
            bot.answer_callback_query(call.id, "❌ Нет активной игры!", show_alert=True)
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
        bot.answer_callback_query(call.id, "🔍 Подсказка! -50💎")
    
    elif data == "use_reroll":
        if user_id not in active_games or not active_games[user_id].active:
            bot.answer_callback_query(call.id, "❌ Нет активной игры!", show_alert=True)
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
        bot.answer_callback_query(call.id, "🏠 Игра завершена")
        text = f"""{texts["game_title"]}

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, lobby_kb(user_id))
    
    # Админ-панель
    elif data == "admin_stats":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Доступ запрещен")
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
            bot.answer_callback_query(call.id, "❌ Доступ запрещен")
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
            bot.answer_callback_query(call.id, "❌ Доступ запрещен")
            return
        users = load_json(USERS_FILE)
        text = "👥 ПОЛЬЗОВАТЕЛИ\n\n"
        for uid, u in list(users.items())[:20]:
            text += f"ID: {uid}\n👤 {u.get('username', 'Без имени')}\n💰 {u.get('crystals', 0)} | 🏆 {u.get('wins', 0)}\n⭐ {u.get('donated_stars', 0)}\n\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "admin_give":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Доступ запрещен")
            return
        msg = bot.send_message(call.message.chat.id, "💎 Введите ID и сумму:\nПример: 123456789 100")
        bot.register_next_step_handler(msg, admin_give_crystals)
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
            welcome_text = """🎉 Всем привет! Я - УГАДАЙ СЛОВО БОТ! 🎉

🤖 Что я умею:
✨ → Генерировать слова прямо в этом чате
🎲 → Устраивать игру «Угадай слово»
💎 → Давать кристаллы за победы
🏆 → Показывать топ игроков
🌐 → Работать с русским и английским языком

🎮 Как играть:
1️⃣ → Нажмите /start или кнопку «Начать игру»
2️⃣ → Угадывайте слово по буквам
3️⃣ → Получайте кристаллы и попадайте в топ!

⭐ Поддержать проект:
💰 /donate → поддержать бота Telegram Stars

📊 Команды:
🏠 /start → главное меню
📈 /stats → моя статистика
🏆 /top → таблица лидеров
🛒 /shop → магазин предметов
🌐 /lang → выбрать язык
🎁 /daily → ежедневный бонус
🎡 /wheel → колесо фортуны
❓ /help → помощь
👥 /lobby → кто сейчас играет

🎯 Играйте вместе, соревнуйтесь и побеждайте!

❤️ Бот создан с любовью для вашего чата"""
            
            bot.send_message(message.chat.id, welcome_text)
            break

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("🤖 Бот запущен")
    print("🎮 УГАДАЙ СЛОВО")
    print("🎁 Ежедневный бонус и колесо фортуны")
    print("🔧 Админ-панель: /admin")
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")