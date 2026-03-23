try:
    import telebot
    from telebot import types
except ImportError:
    print("Ошибка: telebot не установлен. pip install pyTelegramBotAPI")
    exit(1)

import random
import json
import os
import string

TOKEN = "7766594100:AAH7j4yGEW5Tqoiu8IguYh0Mn3g7lMbPwj8"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 8388843828

USERS_FILE = "guess_users.json"
WORDS_FILE = "guess_words.json"

# Реальные слова из словаря
DEFAULT_WORDS = {
    "ru": [
        "КОТ", "ДОМ", "ЛЕС", "ГОРОД", "МАШИНА", "СОЛНЦЕ", "ЗВЕЗДА", "КНИГА", "СТОЛ", "ДРУГ",
        "МАМА", "ПАПА", "СЫН", "ДОЧЬ", "БРАТ", "СЕСТРА", "ДЕДУШКА", "БАБУШКА", "УЧИТЕЛЬ", "ШКОЛА",
        "УНИВЕРСИТЕТ", "РАБОТА", "ДЕНЬГИ", "СЧАСТЬЕ", "ЛЮБОВЬ", "ДРУЖБА", "ПРИРОДА", "ЦВЕТОК", "ДЕРЕВО",
        "РЕКА", "МОРЕ", "ОКЕАН", "ГОРА", "НЕБО", "ЗЕМЛЯ", "ОГОНЬ", "ВОДА", "ВОЗДУХ", "ВРЕМЯ",
        "КОМПЬЮТЕР", "ТЕЛЕФОН", "ИНТЕРНЕТ", "САЙТ", "ПРОГРАММА", "ИГРА", "КИНО", "МУЗЫКА", "КНИГА"
    ],
    "en": [
        "CAT", "DOG", "HOUSE", "CAR", "COMPUTER", "SUN", "STAR", "BOOK", "TABLE", "FRIEND",
        "MOTHER", "FATHER", "SON", "DAUGHTER", "BROTHER", "SISTER", "GRANDFATHER", "GRANDMOTHER", "TEACHER", "SCHOOL",
        "UNIVERSITY", "WORK", "MONEY", "HAPPINESS", "LOVE", "FRIENDSHIP", "NATURE", "FLOWER", "TREE",
        "RIVER", "SEA", "OCEAN", "MOUNTAIN", "SKY", "EARTH", "FIRE", "WATER", "AIR", "TIME",
        "COMPUTER", "PHONE", "INTERNET", "WEBSITE", "PROGRAM", "GAME", "MOVIE", "MUSIC", "BOOK"
    ]
}

# Тексты для разных языков
TEXTS = {
    "ru": {
        "menu_title": "🎮 УГАДАЙ СЛОВО",
        "game_title": "🎮 УГАДАЙ СЛОВО",
        "word_label": "Слово",
        "attempts_label": "Попыток",
        "wrong_label": "Ошибки",
        "reward_label": "За победу",
        "enter_letter": "Введите букву или слово:",
        "win": "🏆 ПОБЕДА! 🏆",
        "lose": "💀 ПОРАЖЕНИЕ! 💀",
        "yes_letter": "✅ Есть такая буква!",
        "no_letter": "❌ Нет такой буквы!",
        "already_used": "❌ Эта буква уже называлась",
        "wrong_word": "❌ Неправильно!",
        "remaining_attempts": "Осталось попыток",
        "hint_used": "🔍 Подсказка: буква {} есть в слове!",
        "reroll_used": "🔄 Слово заменено!",
        "game_start": "Игра началась!",
        "start_game": "🎮 Начать игру",
        "shop": "🛒 Магазин",
        "top": "🏆 Топ игроков",
        "stats": "📊 Моя статистика",
        "language": "🌐 Выбрать язык",
        "help": "❓ Помощь",
        "back": "◀️ Назад",
        "hint_item": "🔍 Подсказка",
        "reroll_item": "🔄 Сменить слово",
        "shield_item": "🛡️ Защита",
        "double_item": "💎 Кристалл x2",
        "exit_game": "🏠 Выйти из игры",
        "admin_panel": "🔧 АДМИН ПАНЕЛЬ",
        "total_stats": "📊 ОБЩАЯ СТАТИСТИКА",
        "total_players": "👥 Всего игроков",
        "total_games": "🎮 Всего игр",
        "total_wins": "🏆 Всего побед",
        "total_crystals": "💰 Всего кристаллов",
        "avg_win": "⚡ Средний выигрыш",
        "user_list": "👥 СПИСОК ПОЛЬЗОВАТЕЛЕЙ",
        "word_list": "📚 СПИСОК СЛОВ",
        "give_crystals": "💎 ВЫДАЧА КРИСТАЛЛОВ",
        "add_word": "📝 ДОБАВЛЕНИЕ СЛОВА",
        "no_game": "У вас нет активной игры!",
        "not_enough": "❌ Не хватает! Нужно",
        "bought": "✅ Куплено:",
        "hint_bought": "🔍 Подсказка использована! -50💎",
        "reroll_bought": "🔄 Слово заменено! -100💎",
        "all_letters": "❌ Все буквы уже открыты!",
        "top_crystals": "💰 ТОП ПО КРИСТАЛЛАМ",
        "top_wins": "🏆 ТОП ПО ПОБЕДАМ",
        "top_streak": "🔥 ТОП ПО СЕРИИ",
        "your_stats": "📊 ТВОЯ СТАТИСТИКА",
        "crystals": "💰 Кристаллов",
        "wins": "🏆 Побед",
        "games": "🎮 Игр",
        "current_streak": "🔥 Текущая серия",
        "best_streak": "🏅 Лучшая серия",
        "how_to_play": "📚 КАК ИГРАТЬ",
        "help_text": """Как играть:

1️⃣ Нажми «Начать игру»
2️⃣ Введи букву или слово
3️⃣ Угадай слово

Советы:
- Буквы отображаются на своих местах
- Можно использовать подсказки в магазине
- За победу дают кристаллы

За победу: +50 кристаллов
Попыток: 6 ошибок"""
    },
    "en": {
        "menu_title": "🎮 GUESS THE WORD",
        "game_title": "🎮 GUESS THE WORD",
        "word_label": "Word",
        "attempts_label": "Attempts",
        "wrong_label": "Wrong",
        "reward_label": "Reward",
        "enter_letter": "Enter a letter or word:",
        "win": "🏆 VICTORY! 🏆",
        "lose": "💀 DEFEAT! 💀",
        "yes_letter": "✅ Letter found!",
        "no_letter": "❌ Letter not found!",
        "already_used": "❌ This letter was already used",
        "wrong_word": "❌ Wrong!",
        "remaining_attempts": "Attempts left",
        "hint_used": "🔍 Hint: letter {} is in the word!",
        "reroll_used": "🔄 Word changed!",
        "game_start": "Game started!",
        "start_game": "🎮 Start Game",
        "shop": "🛒 Shop",
        "top": "🏆 Leaderboard",
        "stats": "📊 My Stats",
        "language": "🌐 Language",
        "help": "❓ Help",
        "back": "◀️ Back",
        "hint_item": "🔍 Hint",
        "reroll_item": "🔄 Change word",
        "shield_item": "🛡️ Shield",
        "double_item": "💎 Crystal x2",
        "exit_game": "🏠 Exit Game",
        "admin_panel": "🔧 ADMIN PANEL",
        "total_stats": "📊 TOTAL STATISTICS",
        "total_players": "👥 Total players",
        "total_games": "🎮 Total games",
        "total_wins": "🏆 Total wins",
        "total_crystals": "💰 Total crystals",
        "avg_win": "⚡ Average wins",
        "user_list": "👥 USER LIST",
        "word_list": "📚 WORD LIST",
        "give_crystals": "💎 GIVE CRYSTALS",
        "add_word": "📝 ADD WORD",
        "no_game": "You don't have an active game!",
        "not_enough": "❌ Not enough! Need",
        "bought": "✅ Purchased:",
        "hint_bought": "🔍 Hint used! -50💎",
        "reroll_bought": "🔄 Word changed! -100💎",
        "all_letters": "❌ All letters are already open!",
        "top_crystals": "💰 TOP BY CRYSTALS",
        "top_wins": "🏆 TOP BY WINS",
        "top_streak": "🔥 TOP BY STREAK",
        "your_stats": "📊 YOUR STATISTICS",
        "crystals": "💰 Crystals",
        "wins": "🏆 Wins",
        "games": "🎮 Games",
        "current_streak": "🔥 Current streak",
        "best_streak": "🏅 Best streak",
        "how_to_play": "📚 HOW TO PLAY",
        "help_text": """How to play:

1️⃣ Press «Start Game»
2️⃣ Enter a letter or word
3️⃣ Guess the word

Tips:
- Letters are shown in their places
- Use hints from the shop
- Get crystals for winning

Reward: +50 crystals
Attempts: 6 mistakes"""
    }
}

SHOP_ITEMS = {
    "hint": {"price": 50, "emoji": "🔍"},
    "reroll": {"price": 100, "emoji": "🔄"},
    "shield": {"price": 150, "emoji": "🛡️"},
    "double": {"price": 500, "emoji": "💎"}
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

def get_word(lang):
    words_dict = load_json(WORDS_FILE)
    if lang not in words_dict or not words_dict[lang]:
        words_dict[lang] = DEFAULT_WORDS[lang].copy()
        save_json(WORDS_FILE, words_dict)
    return random.choice(words_dict[lang])

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
        self.word = get_word(lang).upper()
        self.lang = lang
        self.guessed_letters = []
        self.wrong_letters = []
        self.attempts = 6
        self.message_id = message_id
        self.active = True
        self.effects = {}
        self.texts = TEXTS[lang]
    
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
        
        text = f"""{self.texts['game_title']}

{self.texts['word_label']}: {display}
{self.texts['attempts_label']}: {self.attempts}
{self.texts['wrong_label']}: {wrong}
{self.texts['reward_label']}: +50💎

{message}

{self.texts['enter_letter']}"""
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
                return True, f"{self.texts['win']}\n\n{self.texts['word_label']}: {self.word}\n+{reward}💎"
            
            self.attempts -= 1
            if self.attempts <= 0:
                if not self.effects.get("shield"):
                    add_loss(self.user_id)
                self.active = False
                return False, f"{self.texts['lose']}\n\n{self.texts['word_label']}: {self.word}"
            return False, f"{self.texts['wrong_word']} {self.texts['remaining_attempts']}: {self.attempts}"
        
        if letter in self.guessed_letters or letter in self.wrong_letters:
            return False, self.texts['already_used']
        
        if letter in self.word:
            self.guessed_letters.append(letter)
            
            if all(l in self.guessed_letters for l in self.word):
                reward = 50
                if self.effects.get("double"):
                    reward *= 2
                add_crystals(self.user_id, reward)
                add_win(self.user_id)
                self.active = False
                return True, f"{self.texts['win']}\n\n{self.texts['word_label']}: {self.word}\n+{reward}💎"
            
            return True, self.texts['yes_letter']
        else:
            self.wrong_letters.append(letter)
            self.attempts -= 1
            
            if self.attempts <= 0:
                if not self.effects.get("shield"):
                    add_loss(self.user_id)
                self.active = False
                return False, f"{self.texts['lose']}\n\n{self.texts['word_label']}: {self.word}"
            
            return False, f"{self.texts['no_letter']} {self.texts['remaining_attempts']}: {self.attempts}"
    
    def use_hint(self):
        not_guessed = [l for l in self.word if l not in self.guessed_letters]
        if not_guessed:
            hint_letter = random.choice(not_guessed)
            self.guessed_letters.append(hint_letter)
            return self.texts['hint_used'].format(hint_letter)
        return self.texts['all_letters']
    
    def reroll_word(self):
        self.word = get_word(self.lang).upper()
        self.guessed_letters = []
        self.wrong_letters = []
        self.attempts = 6
        return self.texts['reroll_used']

def main_menu_kb(lang):
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(texts['start_game'], callback_data="start_game"),
        types.InlineKeyboardButton(texts['shop'], callback_data="shop"),
        types.InlineKeyboardButton(texts['top'], callback_data="top"),
        types.InlineKeyboardButton(texts['stats'], callback_data="stats"),
        types.InlineKeyboardButton(texts['language'], callback_data="lang"),
        types.InlineKeyboardButton(texts['help'], callback_data="help")
    )
    return markup

def admin_panel_kb(lang):
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(texts['total_stats'], callback_data="admin_stats"),
        types.InlineKeyboardButton(texts['give_crystals'], callback_data="admin_give"),
        types.InlineKeyboardButton(texts['add_word'], callback_data="admin_addword"),
        types.InlineKeyboardButton(texts['word_list'], callback_data="admin_words"),
        types.InlineKeyboardButton(texts['user_list'], callback_data="admin_users"),
        types.InlineKeyboardButton(texts['back'], callback_data="back_to_main")
    )
    return markup

def shop_kb(lang):
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=2)
    for item_id, item in SHOP_ITEMS.items():
        name = texts[f"{item_id}_item"]
        markup.add(types.InlineKeyboardButton(
            f"{item['emoji']} {name} — {item['price']}💎",
            callback_data=f"buy_{item_id}"
        ))
    markup.add(types.InlineKeyboardButton(texts['back'], callback_data="back_to_main"))
    return markup

def top_kb(lang):
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(texts['top_crystals'], callback_data="top_crystals"),
        types.InlineKeyboardButton(texts['top_wins'], callback_data="top_wins"),
        types.InlineKeyboardButton(texts['top_streak'], callback_data="top_streak"),
        types.InlineKeyboardButton(texts['back'], callback_data="back_to_main")
    )
    return markup

def lang_kb(lang):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        types.InlineKeyboardButton(TEXTS[lang]['back'], callback_data="back_to_main")
    )
    return markup

def game_kb(lang):
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"{texts['hint_item']} (50💎)", callback_data="use_hint"),
        types.InlineKeyboardButton(f"{texts['reroll_item']} (100💎)", callback_data="use_reroll"),
        types.InlineKeyboardButton(texts['exit_game'], callback_data="exit_game")
    )
    return markup

@bot.message_handler(commands=['start', 'guess', 'menu'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    user = get_user(user_id)
    user['username'] = username
    update_user(user_id, user)
    
    lang = user.get('lang', 'ru')
    texts = TEXTS[lang]
    
    text = f"""{texts['menu_title']}

Добро пожаловать, {username}!

{texts['crystals']}: {user['crystals']}
{texts['wins']}: {user['wins']}
{texts['games']}: {user['games']}

Нажми «{texts['start_game']}», чтобы играть!"""
    
    bot.send_message(message.chat.id, text, reply_markup=main_menu_kb(lang))

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user.get('lang', 'ru')
    texts = TEXTS[lang]
    
    text = f"""{texts['your_stats']}

{texts['crystals']}: {user['crystals']}
{texts['wins']}: {user['wins']}
{texts['games']}: {user['games']}
{texts['current_streak']}: {user['streak']}
{texts['best_streak']}: {user['best_streak']}"""
    
    bot.send_message(message.chat.id, text, reply_markup=main_menu_kb(lang))

@bot.message_handler(commands=['top'])
def top_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user.get('lang', 'ru')
    texts = TEXTS[lang]
    
    users = load_json(USERS_FILE)
    top = [{'username': u.get('username', f"User_{uid}"), 'crystals': u.get('crystals', 0)} for uid, u in users.items()]
    top.sort(key=lambda x: x['crystals'], reverse=True)
    text = f"{texts['top_crystals']}\n\n"
    for i, u in enumerate(top[:10], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{medal} {u['username']} — {u['crystals']}💎\n"
    bot.send_message(message.chat.id, text, reply_markup=main_menu_kb(lang))

@bot.message_handler(commands=['shop'])
def shop_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user.get('lang', 'ru')
    texts = TEXTS[lang]
    
    text = f"{texts['shop']}\n\nВыбери товар в меню ниже:"
    bot.send_message(message.chat.id, text, reply_markup=shop_kb(lang))

@bot.message_handler(commands=['lang'])
def lang_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user.get('lang', 'ru')
    
    text = TEXTS[lang]['language']
    bot.send_message(message.chat.id, text, reply_markup=lang_kb(lang))

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user.get('lang', 'ru')
    texts = TEXTS[lang]
    
    bot.send_message(message.chat.id, texts['help_text'])

@bot.message_handler(commands=['admin'])
def admin_command(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.reply_to(message, "❌ У вас нет прав администратора")
        return
    
    user = get_user(user_id)
    lang = user.get('lang', 'ru')
    texts = TEXTS[lang]
    
    text = texts['admin_panel']
    bot.send_message(message.chat.id, text, reply_markup=admin_panel_kb(lang))

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
                menu_text = f"""{texts['menu_title']}

{texts['crystals']}: {user['crystals']}
{texts['wins']}: {user['wins']}"""
                bot.send_message(message.chat.id, menu_text, reply_markup=main_menu_kb(lang))
            else:
                new_text = game.get_game_text(msg)
                try:
                    bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb(game.lang))
                except Exception as e:
                    print(f"Ошибка обновления: {e}")
            
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
    else:
        if message.text and not message.text.startswith('/'):
            user = get_user(user_id)
            lang = user.get('lang', 'ru')
            texts = TEXTS[lang]
            text = f"""{texts['menu_title']}

{texts['no_game']}

{texts['crystals']}: {user['crystals']}
{texts['wins']}: {user['wins']}

Нажмите кнопку «{texts['start_game']}»"""
            bot.send_message(message.chat.id, text, reply_markup=main_menu_kb(lang))

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    user = get_user(user_id)
    lang = user.get('lang', 'ru')
    texts = TEXTS[lang]
    
    if data == "back_to_main":
        text = f"""{texts['menu_title']}

{texts['crystals']}: {user['crystals']}
{texts['wins']}: {user['wins']}"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb(lang))
        bot.answer_callback_query(call.id)
    
    elif data == "help":
        bot.edit_message_text(texts['help_text'], call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb(lang))
        bot.answer_callback_query(call.id)
    
    elif data == "lang":
        bot.edit_message_text(texts['language'], call.message.chat.id, call.message.message_id, reply_markup=lang_kb(lang))
        bot.answer_callback_query(call.id)
    
    elif data == "lang_ru":
        user['lang'] = 'ru'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "🇷🇺 Язык: русский")
        texts = TEXTS['ru']
        text = f"""{texts['menu_title']}

{texts['crystals']}: {user['crystals']}
{texts['wins']}: {user['wins']}"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb('ru'))
    
    elif data == "lang_en":
        user['lang'] = 'en'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "🇬🇧 Language: English")
        texts = TEXTS['en']
        text = f"""{texts['menu_title']}

{texts['crystals']}: {user['crystals']}
{texts['wins']}: {user['wins']}"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb('en'))
    
    elif data == "start_game":
        lang = user.get('lang', 'ru')
        
        if user_id in active_games and active_games[user_id].active:
            bot.answer_callback_query(call.id, texts['no_game'], show_alert=True)
            return
        
        text = texts['game_start']
        sent = bot.send_message(call.message.chat.id, text)
        
        game = Game(call.message.chat.id, user_id, lang, sent.message_id)
        active_games[user_id] = game
        
        game_text = game.get_game_text(texts['game_start'])
        bot.edit_message_text(game_text, game.chat_id, game.message_id, reply_markup=game_kb(lang))
        bot.answer_callback_query(call.id)
    
    elif data == "shop":
        bot.edit_message_text(f"{texts['shop']}\n\nВыбери товар:", call.message.chat.id, call.message.message_id, reply_markup=shop_kb(lang))
        bot.answer_callback_query(call.id)
    
    elif data.startswith("buy_"):
        item_id = data[4:]
        item = SHOP_ITEMS.get(item_id)
        if not item:
            bot.answer_callback_query(call.id, "❌ Товар не найден")
            return
        
        if user['crystals'] < item['price']:
            bot.answer_callback_query(call.id, f"{texts['not_enough']} {item['price']}💎", show_alert=True)
            return
        
        user['crystals'] -= item['price']
        update_user(user_id, user)
        
        if user_id in active_games and active_games[user_id].active:
            active_games[user_id].effects[item_id] = True
        
        bot.answer_callback_query(call.id, f"{texts['bought']} {texts[f'{item_id}_item']}!", show_alert=True)
        bot.edit_message_text(f"{texts['shop']}\n\nВыбери товар:", call.message.chat.id, call.message.message_id, reply_markup=shop_kb(lang))
    
    elif data == "top":
        bot.edit_message_text(texts['top'], call.message.chat.id, call.message.message_id, reply_markup=top_kb(lang))
        bot.answer_callback_query(call.id)
    
    elif data == "top_crystals":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'crystals': u.get('crystals', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['crystals'], reverse=True)
        text = f"{texts['top_crystals']}\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['crystals']}💎\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb(lang))
        bot.answer_callback_query(call.id)
    
    elif data == "top_wins":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'wins': u.get('wins', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['wins'], reverse=True)
        text = f"{texts['top_wins']}\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['wins']}🏆\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb(lang))
        bot.answer_callback_query(call.id)
    
    elif data == "top_streak":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'streak': u.get('best_streak', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['streak'], reverse=True)
        text = f"{texts['top_streak']}\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['streak']}🏆\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=top_kb(lang))
        bot.answer_callback_query(call.id)
    
    elif data == "stats":
        text = f"""{texts['your_stats']}

{texts['crystals']}: {user['crystals']}
{texts['wins']}: {user['wins']}
{texts['games']}: {user['games']}
{texts['current_streak']}: {user['streak']}
{texts['best_streak']}: {user['best_streak']}"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb(lang))
        bot.answer_callback_query(call.id)
    
    elif data == "use_hint":
        if user_id not in active_games or not active_games[user_id].active:
            bot.answer_callback_query(call.id, texts['no_game'], show_alert=True)
            return
        
        if user['crystals'] < 50:
            bot.answer_callback_query(call.id, f"{texts['not_enough']} 50💎", show_alert=True)
            return
        
        user['crystals'] -= 50
        update_user(user_id, user)
        
        game = active_games[user_id]
        hint_msg = game.use_hint()
        
        new_text = game.get_game_text(hint_msg)
        bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb(game.lang))
        bot.answer_callback_query(call.id, texts['hint_bought'])
    
    elif data == "use_reroll":
        if user_id not in active_games or not active_games[user_id].active:
            bot.answer_callback_query(call.id, texts['no_game'], show_alert=True)
            return
        
        if user['crystals'] < 100:
            bot.answer_callback_query(call.id, f"{texts['not_enough']} 100💎", show_alert=True)
            return
        
        user['crystals'] -= 100
        update_user(user_id, user)
        
        game = active_games[user_id]
        reroll_msg = game.reroll_word()
        
        new_text = game.get_game_text(reroll_msg)
        bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb(game.lang))
        bot.answer_callback_query(call.id, texts['reroll_bought'])
    
    elif data == "exit_game":
        if user_id in active_games:
            del active_games[user_id]
        bot.answer_callback_query(call.id, texts['exit_game'])
        text = f"""{texts['menu_title']}

{texts['crystals']}: {user['crystals']}
{texts['wins']}: {user['wins']}"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb(lang))
    
    elif data == "admin_stats":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        
        users = load_json(USERS_FILE)
        total_users = len(users)
        total_games = sum(u.get('games', 0) for u in users.values())
        total_wins = sum(u.get('wins', 0) for u in users.values())
        total_crystals = sum(u.get('crystals', 0) for u in users.values())
        
        text = f"""{texts['total_stats']}

{texts['total_players']}: {total_users}
{texts['total_games']}: {total_games}
{texts['total_wins']}: {total_wins}
{texts['total_crystals']}: {total_crystals}
{texts['avg_win']}: {total_wins/total_users if total_users > 0 else 0:.1f}"""
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb(lang))
        bot.answer_callback_query(call.id)
    
    elif data == "admin_users":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        
        users = load_json(USERS_FILE)
        text = f"{texts['user_list']}\n\n"
        for uid, u in list(users.items())[:20]:
            text += f"ID: {uid}\n👤 {u.get('username', 'Без имени')}\n💰 {u.get('crystals', 0)}💎 | 🏆 {u.get('wins', 0)}\n\n"
        
        if len(users) > 20:
            text += f"... и еще {len(users)-20} пользователей"
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb(lang))
        bot.answer_callback_query(call.id)
    
    elif data == "admin_give":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        
        bot.edit_message_text(f"{texts['give_crystals']}\n\nВведите ID пользователя и сумму через пробел:\nПример: 123456789 100", 
                            call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb(lang))
        bot.answer_callback_query(call.id)
        bot.register_next_step_handler(call.message, admin_give_crystals)
    
    elif data == "admin_addword":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        
        bot.edit_message_text(f"{texts['add_word']}\n\nВведите язык и слово через пробел:\nПример: ru КОТ\nили: en CAT", 
                            call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb(lang))
        bot.answer_callback_query(call.id)
        bot.register_next_step_handler(call.message, admin_add_word)
    
    elif data == "admin_words":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Доступ запрещен")
            return
        
        words = load_json(WORDS_FILE)
        text = f"{texts['word_list']}\n\n"
        for lang_key, word_list in words.items():
            text += f"{lang_key}: {', '.join(word_list[:15])}\n"
            if len(word_list) > 15:
                text += f"... и еще {len(word_list)-15} слов\n"
            text += "\n"
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb(lang))
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
        
        words = load_json(WORDS_FILE)
        if lang not in words:
            words[lang] = []
        if word not in words[lang]:
            words[lang].append(word)
            save_json(WORDS_FILE, words)
            bot.reply_to(message, f"✅ Слово {word} добавлено в словарь {lang}")
        else:
            bot.reply_to(message, f"❌ Слово {word} уже есть")
    except:
        bot.reply_to(message, "❌ Ошибка! Формат: ru СЛОВО")

if __name__ == "__main__":
    print("🤖 Guess Word Bot запущен")
    print("Бот работает...")
    print("Команды: /start, /stats, /top, /shop, /lang, /help, /admin")
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")