try:
    import telebot
    from telebot import types
except ImportError:
    print("Ошибка: telebot не установлен. pip install pyTelebotAPI")
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

DEFAULT_WORDS = {
    "ru": ["КОТ", "ДОМ", "ЛЕС", "ГОРОД", "МАШИНА", "СОЛНЦЕ", "ЗВЕЗДА", "КНИГА", "СТОЛ", "ДРУГ"],
    "en": ["CAT", "DOG", "HOUSE", "CAR", "SUN", "STAR", "BOOK", "TABLE", "FRIEND"]
}

SHOP_ITEMS = {
    "hint": {"name": "🔍 Подсказка", "price": 50, "emoji": "🔍"},
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
    words_dict = load_json(WORDS_FILE)
    if lang not in words_dict or not words_dict[lang]:
        words_dict[lang] = DEFAULT_WORDS[lang].copy()
        save_json(WORDS_FILE, words_dict)
    
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
        
        text = f"""🎮 УГАДАЙ СЛОВО

Слово: {display}
Попыток: {self.attempts}
❌ Ошибки: {wrong}
💎 За победу: +50

{message}

Введите букву или слово:"""
        return text
    
    def guess_letter(self, letter):
        letter = letter.upper()
        
        # Если ввели целое слово
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
        
        # Проверка буквы
        if letter in self.guessed_letters or letter in self.wrong_letters:
            return False, "❌ Эта буква уже называлась"
        
        # Проверяем, есть ли буква в слове
        if letter in self.word:
            self.guessed_letters.append(letter)
            
            # Проверяем, все ли буквы угаданы
            if all(l in self.guessed_letters for l in self.word):
                reward = 50
                if self.effects.get("double"):
                    reward *= 2
                add_crystals(self.user_id, reward)
                add_win(self.user_id)
                self.active = False
                return True, f"🏆 ПОБЕДА! 🏆\n\nСлово: {self.word}\n+{reward} 💎"
            
            return True, f"✅ Есть такая буква!"
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
        self.word = get_word(self.lang).upper()
        self.guessed_letters = []
        self.wrong_letters = []
        self.attempts = 6
        return f"🔄 Слово заменено!"

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

def game_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔍 Подсказка (50💎)", callback_data="use_hint"),
        types.InlineKeyboardButton("🔄 Сменить слово (100💎)", callback_data="use_reroll"),
        types.InlineKeyboardButton("🏠 Выйти из игры", callback_data="exit_game")
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
3. Введи букву или слово
4. Угадай слово
5. Получай кристаллы за победы

Магазин:
🔍 Подсказка — открывает букву (50💎)
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

# Обработка всех текстовых сообщений для игры
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    
    # Пропускаем команды
    if message.text and message.text.startswith('/'):
        return
    
    # Проверяем, есть ли активная игра у пользователя
    if user_id in active_games and active_games[user_id].active:
        game = active_games[user_id]
        guess_text = message.text.strip()
        
        if guess_text:
            result, msg = game.guess_letter(guess_text)
            
            if not game.active:
                # Игра закончена, отправляем результат и меню
                bot.edit_message_text(msg, game.chat_id, game.message_id)
                del active_games[user_id]
                user = get_user(user_id)
                menu_text = f"🎮 УГАДАЙ СЛОВО\n\n💰 Кристаллов: {user['crystals']}\n🏆 Побед: {user['wins']}"
                bot.send_message(message.chat.id, menu_text, reply_markup=main_menu_kb())
            else:
                # Обновляем игровое сообщение
                new_text = game.get_game_text(msg)
                try:
                    bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb())
                except Exception as e:
                    print(f"Ошибка обновления: {e}")
            
            # Удаляем сообщение пользователя, чтобы не засорять чат
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
    else:
        # Если нет активной игры, показываем главное меню
        if message.text and not message.text.startswith('/'):
            user = get_user(user_id)
            text = f"""🎮 УГАДАЙ СЛОВО

У вас нет активной игры!

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}

Нажмите кнопку «Начать игру»"""
            bot.send_message(message.chat.id, text, reply_markup=main_menu_kb())

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
3️⃣ Угадай слово

💡 Советы:
- Буквы отображаются на своих местах
- Можно использовать подсказки в магазине
- За победу дают кристаллы

🏆 За победу: +50 кристаллов
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
        
        # Создаем новое сообщение с игрой
        text = "🎮 НАЧИНАЕМ ИГРУ...\n\nЗагрузка..."
        sent = bot.send_message(call.message.chat.id, text)
        
        game = Game(call.message.chat.id, user_id, lang, sent.message_id)
        active_games[user_id] = game
        
        # Обновляем сообщение с игрой
        game_text = game.get_game_text("Игра началась!")
        bot.edit_message_text(game_text, game.chat_id, game.message_id, reply_markup=game_kb())
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
        
        # Добавляем эффект если есть активная игра
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
        user = get_user(user_id)
        text = f"""📊 ТВОЯ СТАТИСТИКА

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}
🎮 Игр: {user['games']}
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
        
        new_text = game.get_game_text(hint_msg)
        bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb())
        bot.answer_callback_query(call.id, "🔍 Подсказка использована! -50💎")
    
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
        
        new_text = game.get_game_text(reroll_msg)
        bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb())
        bot.answer_callback_query(call.id, "🔄 Слово заменено! -100💎")
    
    elif data == "exit_game":
        if user_id in active_games:
            del active_games[user_id]
        bot.answer_callback_query(call.id, "Игра завершена")
        user = get_user(user_id)
        text = f"🎮 УГАДАЙ СЛОВО\n\n💰 Кристаллов: {user['crystals']}\n🏆 Побед: {user['wins']}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb())
    
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
        
        words = load_json(WORDS_FILE)
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