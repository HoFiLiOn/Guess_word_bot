import telebot
from telebot import types
import random
import json
import os
import time
import threading
import string
from datetime import datetime

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
    "hint": {"name": "🔍 Подсказка", "price": 50, "emoji": "🔍"},
    "time": {"name": "⏱️ +15 секунд", "price": 75, "emoji": "⏱️"},
    "reroll": {"name": "🔄 Сменить слово", "price": 100, "emoji": "🔄"},
    "theme": {"name": "🎭 Своя тема", "price": 200, "emoji": "🎭"},
    "shield": {"name": "🛡️ Защита", "price": 150, "emoji": "🛡️"},
    "double": {"name": "💎 Кристалл x2", "price": 500, "emoji": "💎"}
}

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
            'lang': 'en'
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

# Игровое состояние
game_active = False
game_word = ""
game_lang = "en"
game_start_time = 0
game_message_id = None
game_chat_id = None
game_guessed_letters = []
game_wrong_letters = []
game_attempts = 6
game_effects = {}

def reset_game():
    global game_active, game_word, game_lang, game_start_time, game_message_id, game_chat_id, game_guessed_letters, game_wrong_letters, game_attempts, game_effects
    game_active = False
    game_word = ""
    game_lang = "en"
    game_start_time = 0
    game_message_id = None
    game_chat_id = None
    game_guessed_letters = []
    game_wrong_letters = []
    game_attempts = 6
    game_effects = {}

def start_game(chat_id, lang="en", user_id=None):
    global game_active, game_word, game_lang, game_start_time, game_message_id, game_chat_id, game_guessed_letters, game_wrong_letters, game_attempts, game_effects
    
    if game_active:
        return False, "Игра уже идёт!"
    
    game_word = get_word(lang).upper()
    game_lang = lang
    game_start_time = time.time()
    game_chat_id = chat_id
    game_guessed_letters = []
    game_wrong_letters = []
    game_attempts = 6
    game_effects = {}
    game_active = True
    
    return True, game_word

def get_display_word():
    display = []
    for letter in game_word:
        if letter in game_guessed_letters:
            display.append(letter)
        else:
            display.append("_")
    return " ".join(display)

def guess_letter(letter, user_id):
    global game_attempts
    
    if not game_active:
        return False, "Игра уже закончена"
    
    letter = letter.upper()
    
    if len(letter) > 1:
        if letter == game_word:
            time_taken = int(time.time() - game_start_time)
            reward = 50
            if game_effects.get(user_id, {}).get("double"):
                reward *= 2
                del game_effects[user_id]["double"]
            add_crystals(user_id, reward)
            add_win(user_id, time_taken)
            if game_effects.get(user_id, {}).get("shield"):
                del game_effects[user_id]["shield"]
            return True, f"🏆 Победа! Слово: {game_word}\n+{reward} 💎\n⏱️ {time_taken} сек"
        
        game_attempts -= 1
        if game_attempts <= 0:
            add_loss(user_id)
            return False, f"💀 Поражение! Слово: {game_word}"
        return False, f"❌ Неправильно! Осталось попыток: {game_attempts}"
    
    if letter in game_guessed_letters or letter in game_wrong_letters:
        return False, "❌ Эта буква уже называлась"
    
    if letter in game_word:
        game_guessed_letters.append(letter)
        if all(l in game_guessed_letters for l in game_word):
            time_taken = int(time.time() - game_start_time)
            reward = 50
            if game_effects.get(user_id, {}).get("double"):
                reward *= 2
                del game_effects[user_id]["double"]
            add_crystals(user_id, reward)
            add_win(user_id, time_taken)
            if game_effects.get(user_id, {}).get("shield"):
                del game_effects[user_id]["shield"]
            return True, f"🏆 Победа! Слово: {game_word}\n+{reward} 💎\n⏱️ {time_taken} сек"
        return True, "✅ Есть такая буква!"
    else:
        game_wrong_letters.append(letter)
        game_attempts -= 1
        if game_attempts <= 0:
            add_loss(user_id)
            return False, f"💀 Поражение! Слово: {game_word}"
        return False, f"❌ Нет такой буквы! Осталось попыток: {game_attempts}"

# ========== КНОПКИ ==========
def main_menu_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎮 Начать игру", callback_data="start_game"),
        types.InlineKeyboardButton("🛒 Магазин", callback_data="shop"),
        types.InlineKeyboardButton("🏆 Топ", callback_data="top"),
        types.InlineKeyboardButton("📊 Моя статистика", callback_data="stats"),
        types.InlineKeyboardButton("⚙️ Выбор языка", callback_data="lang")
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

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start', 'guess', 'stats', 'top', 'shop', 'lang', 'help'])
def handle_commands(message):
    cmd = message.text.split()[0].replace('/', '')
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    # Обновляем юзернейм
    user = get_user(user_id)
    user['username'] = username
    update_user(user_id, user)
    
    if cmd == 'start' or cmd == 'guess':
        # Начинаем игру
        lang = user.get('lang', 'en')
        success, word = start_game(message.chat.id, lang, user_id)
        if not success:
            bot.reply_to(message, word)
            return
        
        display = get_display_word()
        wrong = ", ".join(game_wrong_letters) if game_wrong_letters else "—"
        text = f"⏱️ **УГАДАЙ СЛОВО** — 60 сек\n\nСлово: `{display}`\nПопыток: {game_attempts}\n❌ Уже называли: {wrong}\n💎 За победу: +50\n\n_Отвечай на это сообщение_"
        sent = bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=types.ForceReply(selective=True))
        
        global game_message_id
        game_message_id = sent.message_id
        
        def end_game():
            global game_active
            time.sleep(60)
            if game_active and game_message_id:
                game_active = False
                try:
                    bot.edit_message_text(f"⏰ Время вышло! Слово: {game_word}", game_chat_id, game_message_id)
                except:
                    pass
        threading.Thread(target=end_game, daemon=True).start()
    
    elif cmd == 'stats':
        text = f"📊 **ТВОЯ СТАТИСТИКА**\n\n💰 Кристаллов: {user['crystals']}\n🏆 Побед: {user['wins']}\n🎮 Игр: {user['games']}\n⚡ Лучшее время: {user['fastest_win'] or '—'} сек\n🔥 Текущая серия: {user['streak']}\n🏅 Лучшая серия: {user['best_streak']}"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu_kb())
    
    elif cmd == 'top':
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'crystals': u.get('crystals', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['crystals'], reverse=True)
        text = "💰 **ТОП ПО КРИСТАЛЛАМ**\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['crystals']}💎\n"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=main_menu_kb())
    
    elif cmd == 'shop':
        text = "🛒 **МАГАЗИН**\n\nВыбери товар в меню ниже:"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=shop_kb())
    
    elif cmd == 'lang':
        text = "🌐 **Выбери язык игры:**"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=lang_kb())
    
    elif cmd == 'help':
        text = """
📚 **ПОМОЩЬ**

**Команды:**
/start — начать игру
/guess — то же самое
/stats — моя статистика
/top — таблица лидеров
/shop — магазин
/lang — выбрать язык

**Как играть:**
1. Нажми /start
2. Отвечай на сообщение бота буквой или словом
3. Угадай слово за 60 секунд
4. Получай кристаллы за победы

**Магазин:**
🔍 Подсказка — открывает букву (50💎)
⏱️ +15 секунд — добавляет время (75💎)
🔄 Сменить слово — новое слово (100💎)
🎭 Своя тема — выбор темы (200💎)
🛡️ Защита — не теряешь кристаллы (150💎)
💎 Кристалл x2 — удваивает выигрыш (500💎)
        """
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    
    if data == "back_to_main":
        user = get_user(user_id)
        text = f"🎮 **УГАДАЙ СЛОВО**\n\n💰 Кристаллов: {user['crystals']}\n🏆 Побед: {user['wins']}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=main_menu_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "lang":
        bot.edit_message_text("🌐 **Выбери язык игры:**", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=lang_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "lang_ru":
        user = get_user(user_id)
        user['lang'] = 'ru'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "🇷🇺 Язык: русский")
        text = f"🎮 **УГАДАЙ СЛОВО**\n\n💰 Кристаллов: {user['crystals']}\n🏆 Побед: {user['wins']}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=main_menu_kb())
    
    elif data == "lang_en":
        user = get_user(user_id)
        user['lang'] = 'en'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "🇬🇧 Language: English")
        text = f"🎮 **GUESS THE WORD**\n\n💰 Crystals: {user['crystals']}\n🏆 Wins: {user['wins']}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=main_menu_kb())
    
    elif data == "start_game":
        user = get_user(user_id)
        lang = user.get('lang', 'en')
        success, word = start_game(call.message.chat.id, lang, user_id)
        if not success:
            bot.answer_callback_query(call.id, word, show_alert=True)
            return
        
        display = get_display_word()
        wrong = ", ".join(game_wrong_letters) if game_wrong_letters else "—"
        text = f"⏱️ **УГАДАЙ СЛОВО** — 60 сек\n\nСлово: `{display}`\nПопыток: {game_attempts}\n❌ Уже называли: {wrong}\n💎 За победу: +50\n\n_Отвечай на это сообщение_"
        sent = bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=types.ForceReply(selective=True))
        
        global game_message_id
        game_message_id = sent.message_id
        
        def end_game():
            global game_active
            time.sleep(60)
            if game_active and game_message_id:
                game_active = False
                try:
                    bot.edit_message_text(f"⏰ Время вышло! Слово: {game_word}", game_chat_id, game_message_id)
                except:
                    pass
        threading.Thread(target=end_game, daemon=True).start()
        bot.answer_callback_query(call.id)
    
    elif data == "shop":
        bot.edit_message_text("🛒 **МАГАЗИН**\n\nВыбери товар:", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=shop_kb())
        bot.answer_callback_query(call.id)
    
    elif data.startswith("buy_"):
        item_id = data[4:]
        item = SHOP_ITEMS.get(item_id)
        if not item:
            bot.answer_callback_query(call.id, "❌ Товар не найден")
            return
        user = get_user(user_id)
        if user['crystals'] < item['price']:
            bot.answer_callback_query(call.id, f"❌ Не хватает! Нужно {item['price']}", show_alert=True)
            return
        user['crystals'] -= item['price']
        update_user(user_id, user)
        if item_id not in game_effects:
            game_effects[user_id] = {}
        game_effects[user_id][item_id] = True
        bot.answer_callback_query(call.id, f"✅ Куплено: {item['name']}!", show_alert=True)
        bot.edit_message_text("🛒 **МАГАЗИН**\n\nВыбери товар:", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=shop_kb())
    
    elif data == "top":
        bot.edit_message_text("🏆 **ТАБЛИЦА ЛИДЕРОВ**\n\nВыбери категорию:", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=top_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "top_crystals":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'crystals': u.get('crystals', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['crystals'], reverse=True)
        text = "💰 **ТОП ПО КРИСТАЛЛАМ**\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['crystals']}💎\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=top_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "top_wins":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'wins': u.get('wins', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['wins'], reverse=True)
        text = "🏆 **ТОП ПО ПОБЕДАМ**\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['wins']}🏆\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=top_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "top_speed":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'speed': u['fastest_win']} for uid, u in users.items() if u.get('fastest_win')]
        top.sort(key=lambda x: x['speed'])
        text = "⚡ **ТОП ПО СКОРОСТИ**\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['speed']} сек\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=top_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "top_streak":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'streak': u.get('best_streak', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['streak'], reverse=True)
        text = "🔥 **ТОП ПО СЕРИИ**\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['streak']}🏆\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=top_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "stats":
        user = get_user(user_id)
        text = f"📊 **ТВОЯ СТАТИСТИКА**\n\n💰 Кристаллов: {user['crystals']}\n🏆 Побед: {user['wins']}\n🎮 Игр: {user['games']}\n⚡ Лучшее время: {user['fastest_win'] or '—'} сек\n🔥 Текущая серия: {user['streak']}\n🏅 Лучшая серия: {user['best_streak']}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=main_menu_kb())
        bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.reply_to_message and game_active and message.reply_to_message.message_id == game_message_id)
def handle_guess(message):
    user_id = message.from_user.id
    guess_text = message.text.strip().upper()
    result, msg = guess_letter(guess_text, user_id)
    
    display = get_display_word()
    wrong = ", ".join(game_wrong_letters) if game_wrong_letters else "—"
    
    if "Победа" in msg or "Поражение" in msg:
        bot.edit_message_text(msg, message.chat.id, game_message_id, parse_mode="Markdown")
        reset_game()
        user = get_user(user_id)
        menu_text = f"🎮 **УГАДАЙ СЛОВО**\n\n💰 Кристаллов: {user['crystals']}\n🏆 Побед: {user['wins']}"
        bot.send_message(message.chat.id, menu_text, parse_mode="Markdown", reply_markup=main_menu_kb())
    else:
        time_left = max(0, 60 - int(time.time() - game_start_time))
        text = f"⏱️ **УГАДАЙ СЛОВО** — {time_left} сек\n\nСлово: `{display}`\nПопыток: {game_attempts}\n❌ Уже называли: {wrong}\n💎 За победу: +50\n\n{msg}\n\n_Отвечай на это сообщение_"
        bot.edit_message_text(text, message.chat.id, game_message_id, parse_mode="Markdown", reply_markup=types.ForceReply(selective=True))
    
    bot.delete_message(message.chat.id, message.message_id)

# ========== АДМИН-КОМАНДЫ ==========
@bot.message_handler(commands=['addword'])
def add_word_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split()
        lang = parts[1].lower()
        word = parts[2].upper()
        words = load_json(WORDS_FILE)
        if lang not in words:
            words[lang] = []
        if word not in words[lang]:
            words[lang].append(word)
            save_json(WORDS_FILE, words)
            bot.reply_to(message, f"✅ Слово {word} добавлено")
        else:
            bot.reply_to(message, f"❌ Уже есть")
    except:
        bot.reply_to(message, "❌ /addword ru/en СЛОВО")

@bot.message_handler(commands=['addcrystals'])
def add_crystals_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        parts = message.text.split()
        user_id = int(parts[1])
        amount = int(parts[2])
        add_crystals(user_id, amount)
        bot.reply_to(message, f"✅ Добавлено {amount} кристаллов")
    except:
        bot.reply_to(message, "❌ /addcrystals ID СУММА")

if __name__ == "__main__":
    print("🤖 Guess Word Bot запущен")
    bot.infinity_polling()