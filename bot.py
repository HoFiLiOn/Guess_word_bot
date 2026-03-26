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
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter

TOKEN = "7766594100:AAH7j4yGEW5Tqoiu8IguYh0Mn3g7lMbPwj8"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 8388843828

# ========== ФАЙЛЫ ==========
USERS_FILE = "guess_users.json"
DONATIONS_FILE = "donations.json"
PROMO_FILE = "promocodes.json"
SETTINGS_FILE = "bot_settings.json"
LOGS_FILE = "admin_logs.json"

# ========== КАРТИНКИ ==========
IMAGES = {
    "main": "https://s10.iimage.su/s/24/gyiVYQqxC4FhKIyY4GD47Mvv1YfJ3KFWNkUAbyKQN.png",
    "game": "https://s10.iimage.su/s/24/gFsXdz1x7sCnEVQMjpFfzw2t2qzT0lMS8Bz4zJGpU.jpg",
    "shop": "https://s10.iimage.su/s/24/g0Sj1dDxuKC84sMhP8q3DDK6Q7MDgBRam1v0lyP8H.jpg",
    "top": "https://s10.iimage.su/s/24/ggZ4ONmxr0bk39GQvB3ODh3cJbSU2XFLlrPstj5cp.jpg",
    "stats": "https://s10.iimage.su/s/24/gDyJ0rdxDzMm1NngFnHePE7MB5uz3oQphOMwXKCtu.jpg",
    "donate": "https://s10.iimage.su/s/24/gsqCZaQxs8sp4aoo0dGKbiNKWzrP6Dg5bEnSjvv9f.jpg",
    "casino": "https://s10.iimage.su/s/25/gLrLE2wxqrLnIgQY85Yr6yGU1egcG5RhzafURnbcN.png",
    "daily": "https://s10.iimage.su/s/25/ge71HnYxjSBitBBeitRhrZjN4XAb57ug9RQOUG27G.jpg",
    "wheel": "https://s10.iimage.su/s/25/gbDCZmqxCKzgIVyU6vq9hC8upJb0GOOyy38EGQa6H.png",
    "promo": "https://s10.iimage.su/s/25/gFlt3kqxmkHEJJF5AyWC2bKzV9zUQZLTSE96FWt2g.jpg",
    "inventory": "https://s10.iimage.su/s/25/gwUW3mYxhzzGTEbYaA1wvVL7ma1MaSFzlUIsjoARf.jpg"
}

# ========== КАЗИНО ==========
CASINO_GAMES = {
    "coin": {"name": "Орёл/Решка", "multiplier": 2},
    "dice": {"name": "Кости", "multiplier": 6},
    "slot": {"name": "Слоты", "multiplier": 5},
    "blackjack": {"name": "Блэкджек", "multiplier": 2}
}

# ========== СЛОЖНОСТЬ ==========
DIFFICULTY = {
    "easy": {"name": "🍃 Лёгкая", "min_len": 3, "max_len": 5, "reward": 30},
    "medium": {"name": "⚡ Средняя", "min_len": 5, "max_len": 7, "reward": 50},
    "hard": {"name": "🔥 Сложная", "min_len": 7, "max_len": 9, "reward": 100}
}

# ========== ЛЮТАЯ НЕЙРОСЕТЬ ==========
class MegaNeuralNetwork:
    def __init__(self, lang):
        self.lang = lang
        if lang == "ru":
            self.vowels = "АЕЁИОУЫЭЮЯ"
            self.consonants = "БВГДЖЗЙКЛМНПРСТФХЦЧШЩ"
            self.soft_sign = "Ь"
            self.hard_sign = "Ъ"
            self.corpus = [
                "КОТ", "ДОМ", "ЛЕС", "САД", "РОЗА", "МАМА", "ПАПА", "СЫН", "ДОЧЬ", "БРАТ",
                "СЕСТРА", "ДРУГ", "МИР", "ДЕНЬ", "НОЧЬ", "ГОРОД", "СОЛНЦЕ", "ЗВЕЗДА", "КНИГА",
                "СТОЛ", "СТУЛ", "ОКНО", "ДВЕРЬ", "РУЧКА", "МАШИНА", "УЛИЦА", "ПАРК", "ЛУНА",
                "ЗЕМЛЯ", "ВОДА", "ОГОНЬ", "ВЕТЕР", "СНЕГ", "ДОЖДЬ", "ЛЕТО", "ЗИМА", "ВЕСНА",
                "ОСЕНЬ", "УТРО", "ВЕЧЕР", "СВЕТ", "ТЕНЬ", "ГОЛОС", "СЛОВО", "БУКВА", "СТРАНА",
                "ПЛАНЕТА", "ПРИРОДА", "ЧЕЛОВЕК", "СЧАСТЬЕ", "ЛЮБОВЬ", "ДРУЖБА", "ШКОЛА",
                "УЧИТЕЛЬ", "РАБОТА", "ДЕНЬГИ", "ВРЕМЯ", "МЫСЛЬ", "ИДЕЯ", "МЕЧТА", "НАДЕЖДА",
                "КОНЬ", "МЕЛЬ", "СТАЛЬ", "РУЛЬ", "БОЛЬ", "ПЫЛЬ", "ЦЕЛЬ", "СОЛЬ", "МОЛЬ", "ТОЛЬ"
            ]
        else:
            self.vowels = "AEIOUY"
            self.consonants = "BCDFGHJKLMNPQRSTVWXZ"
            self.soft_sign = ""
            self.hard_sign = ""
            self.corpus = [
                "CAT", "DOG", "SUN", "MOON", "STAR", "TREE", "FLOWER", "BIRD", "FISH",
                "HOUSE", "CAR", "MOM", "DAD", "SON", "DAUGHTER", "BROTHER", "SISTER",
                "FRIEND", "LOVE", "HOPE", "WATER", "FIRE", "EARTH", "WIND", "CLOUD",
                "RAIN", "SNOW", "SUMMER", "WINTER", "SPRING", "AUTUMN", "DAY", "NIGHT",
                "CITY", "TOWN", "STREET", "PARK", "RIVER", "LAKE", "SEA", "OCEAN",
                "MOUNTAIN", "FOREST", "DESERT", "ISLAND", "SKY", "UNIVERSE", "GALAXY"
            ]
        
        self.letter_freq = self._calc_freq()
        self.bigrams = self._calc_bigrams()
        self.trigrams = self._calc_trigrams()
    
    def _calc_freq(self):
        freq = defaultdict(int)
        for word in self.corpus:
            for letter in word:
                freq[letter] += 1
        total = sum(freq.values())
        return {k: v/total for k, v in freq.items()}
    
    def _calc_bigrams(self):
        bigrams = defaultdict(int)
        for word in self.corpus:
            for i in range(len(word)-1):
                bigrams[word[i:i+2]] += 1
        total = sum(bigrams.values())
        return {k: v/total for k, v in bigrams.items()}
    
    def _calc_trigrams(self):
        trigrams = defaultdict(int)
        for word in self.corpus:
            for i in range(len(word)-2):
                trigrams[word[i:i+3]] += 1
        total = sum(trigrams.values())
        return {k: v/total for k, v in trigrams.items()}
    
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
        if self.lang == "ru":
            for i in range(len(word) - 1):
                if word[i+1] == self.soft_sign and word[i] not in self.consonants:
                    return False
        return True
    
    def generate_word(self, min_len=3, max_len=8):
        for _ in range(100):
            length = random.randint(min_len, max_len)
            word = [random.choice(list(self.letter_freq.keys()))]
            for i in range(1, length):
                if len(word) >= 2:
                    trigram = ''.join(word[-2:])
                    candidates = [t for t in self.trigrams if t.startswith(trigram)]
                    if candidates:
                        next_char = random.choice(candidates)[-1]
                        word.append(next_char)
                        continue
                if len(word) >= 1:
                    bigram = word[-1]
                    candidates = [b for b in self.bigrams if b.startswith(bigram)]
                    if candidates:
                        next_char = random.choice(candidates)[-1]
                        word.append(next_char)
                        continue
                word.append(random.choice(list(self.letter_freq.keys())))
            result = ''.join(word)
            if self._is_readable(result):
                return result
        return random.choice(self.corpus)

neural_networks = {
    "ru": MegaNeuralNetwork("ru"),
    "en": MegaNeuralNetwork("en")
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

def log_admin_action(admin_id, action, details):
    logs = load_json(LOGS_FILE)
    if 'logs' not in logs:
        logs['logs'] = []
    logs['logs'].append({
        'admin_id': admin_id,
        'action': action,
        'details': details,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_json(LOGS_FILE, logs)

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
            'daily_streak': 0,
            'inventory': {'hint': 0, 'reroll': 0, 'shield': 0, 'double': 0},
            'blocked': False
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

def get_daily_bonus(user_id):
    user = get_user(user_id)
    today = datetime.now().date().isoformat()
    if user.get('last_daily') == today:
        return None, user.get('daily_streak', 0)
    if user.get('last_daily'):
        last_date = datetime.fromisoformat(user['last_daily']).date()
        if (datetime.now().date() - last_date).days == 1:
            user['daily_streak'] = user.get('daily_streak', 0) + 1
        else:
            user['daily_streak'] = 1
    else:
        user['daily_streak'] = 1
    streak = user['daily_streak']
    bonus = min(50 + (streak - 1) * 10, 500)
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
    prizes = [30, 50, 100, 200, 500, 1000, "Подсказка", "Сменить слово", "Защита", "Кристалл x2", 0]
    weights = [15, 15, 12, 10, 8, 5, 10, 8, 7, 5, 5]
    prize = random.choices(prizes, weights=weights, k=1)[0]
    if isinstance(prize, int):
        user['crystals'] += prize
        update_user(user_id, user)
        return prize, price
    else:
        item_map = {"Подсказка": "hint", "Сменить слово": "reroll", "Защита": "shield", "Кристалл x2": "double"}
        user['inventory'][item_map[prize]] += 1
        update_user(user_id, user)
        return prize, price

def play_casino(user_id, game_type, bet, choice=None):
    user = get_user(user_id)
    if user['crystals'] < bet:
        return None, f"❌ Не хватает кристаллов! Нужно {bet}💎"
    user['crystals'] -= bet
    
    if game_type == "coin":
        result = random.choice(["Орёл", "Решка"])
        if choice == result:
            win = bet * 2
            user['crystals'] += win
            update_user(user_id, user)
            return win, f"🎉 ПОБЕДА! 🎉\n\n🪙 Выпал: {result}\n💰 Ставка: {bet}💎\n🏆 Выигрыш: {win}💎\n\n💰 Баланс: {user['crystals']}💎"
        else:
            update_user(user_id, user)
            return 0, f"😢 ПОРАЖЕНИЕ! 😢\n\n🪙 Выпал: {result}\n💰 Ставка: {bet}💎\n💸 Проигрыш: {bet}💎\n\n💰 Баланс: {user['crystals']}💎"
    
    elif game_type == "dice":
        result = random.randint(1, 6)
        if choice == result:
            win = bet * 6
            user['crystals'] += win
            update_user(user_id, user)
            return win, f"🎉 ПОБЕДА! 🎉\n\n🎲 Выпало: {result}\n💰 Ставка: {bet}💎\n🏆 Выигрыш: {win}💎\n\n💰 Баланс: {user['crystals']}💎"
        else:
            update_user(user_id, user)
            return 0, f"😢 ПОРАЖЕНИЕ! 😢\n\n🎲 Выпало: {result}\n💰 Ставка: {bet}💎\n💸 Проигрыш: {bet}💎\n\n💰 Баланс: {user['crystals']}💎"
    
    elif game_type == "slot":
        symbols = ["🍒", "🍋", "🔔", "💎", "7️⃣"]
        s1, s2, s3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)
        result = f"{s1} {s2} {s3}"
        if s1 == s2 == s3:
            mult = 10 if s1 == "7️⃣" else 5
            win = bet * mult
            user['crystals'] += win
            update_user(user_id, user)
            return win, f"🎉 ДЖЕКПОТ! 🎉\n\n🎰 {result}\n💰 Ставка: {bet}💎\n🏆 Выигрыш: {win}💎\n\n💰 Баланс: {user['crystals']}💎"
        else:
            update_user(user_id, user)
            return 0, f"😢 ПОРАЖЕНИЕ! 😢\n\n🎰 {result}\n💰 Ставка: {bet}💎\n💸 Проигрыш: {bet}💎\n\n💰 Баланс: {user['crystals']}💎"
    
    elif game_type == "blackjack":
        player = random.randint(1, 21)
        dealer = random.randint(1, 21)
        if player > 21: player = 21 - (player - 21)
        if dealer > 21: dealer = 21 - (dealer - 21)
        if player > dealer:
            win = bet * 2
            user['crystals'] += win
            update_user(user_id, user)
            return win, f"🎉 ПОБЕДА! 🎉\n\n🃏 Вы: {player}, Дилер: {dealer}\n💰 Ставка: {bet}💎\n🏆 Выигрыш: {win}💎\n\n💰 Баланс: {user['crystals']}💎"
        elif player == dealer:
            user['crystals'] += bet
            update_user(user_id, user)
            return bet, f"🤝 НИЧЬЯ! 🤝\n\n🃏 Вы: {player}, Дилер: {dealer}\n💰 Ставка возвращена: {bet}💎\n\n💰 Баланс: {user['crystals']}💎"
        else:
            update_user(user_id, user)
            return 0, f"😢 ПОРАЖЕНИЕ! 😢\n\n🃏 Вы: {player}, Дилер: {dealer}\n💰 Ставка: {bet}💎\n💸 Проигрыш: {bet}💎\n\n💰 Баланс: {user['crystals']}💎"

def send_gift(from_id, to_id, amount):
    from_user = get_user(from_id)
    if from_user['crystals'] < amount:
        return False, f"❌ Не хватает кристаллов! Нужно {amount}💎"
    if amount < 10 or amount > 1000:
        return False, "❌ Сумма от 10 до 1000💎"
    from_user['crystals'] -= amount
    to_user = get_user(to_id)
    to_user['crystals'] += amount
    update_user(from_id, from_user)
    update_user(to_id, to_user)
    return True, f"✅ Подарок отправлен!\n\n👤 Получатель: {to_user.get('username', to_id)}\n🎁 Сумма: {amount}💎"

def get_word(lang, difficulty):
    diff = DIFFICULTY[difficulty]
    return neural_networks[lang].generate_word(diff["min_len"], diff["max_len"])

# ========== КЛАСС ИГРЫ ==========
class Game:
    def __init__(self, chat_id, creator_id, lang, message_id, difficulty):
        self.chat_id = chat_id
        self.creator_id = creator_id
        self.word = get_word(lang, difficulty)
        self.lang = lang
        self.difficulty = difficulty
        self.guessed_letters = []
        self.wrong_letters = []
        self.message_id = message_id
        self.active = True
        self.effects = {}
    
    def get_display_word(self):
        return " ".join([l if l in self.guessed_letters else "_" for l in self.word])
    
    def get_game_text(self, message=""):
        reward = DIFFICULTY[self.difficulty]["reward"]
        wrong = ", ".join(self.wrong_letters) if self.wrong_letters else "—"
        return f"""<b>🎮 УГАДАЙ СЛОВО</b>
<i>Общая игра в чате</i>

<b>📖 Слово:</b> {self.get_display_word()}
<b>💎 За победу:</b> +{reward}
<b>❌ Ошибки:</b> {wrong}

{message}

<i>✍️ Введите букву или слово:</i>"""
    
    def guess_letter(self, letter, user_id, username):
        letter = letter.upper()
        reward = DIFFICULTY[self.difficulty]["reward"]
        if len(letter) > 1:
            if letter == self.word:
                final_reward = reward * (2 if self.effects.get("double") else 1)
                add_crystals(user_id, final_reward)
                add_win(user_id)
                self.active = False
                return True, f"<b>🏆 ПОБЕДА! 🏆</b>\n\n📖 Слово: {self.word}\n💎 +{final_reward}\n\n👤 Победитель: {username}"
            return False, f"<b>❌ Неправильно!</b>"
        if letter in self.guessed_letters or letter in self.wrong_letters:
            return False, f"<b>⚠️ Эта буква уже называлась</b>"
        if letter in self.word:
            self.guessed_letters.append(letter)
            if all(l in self.guessed_letters for l in self.word):
                final_reward = reward * (2 if self.effects.get("double") else 1)
                add_crystals(user_id, final_reward)
                add_win(user_id)
                self.active = False
                return True, f"<b>🏆 ПОБЕДА! 🏆</b>\n\n📖 Слово: {self.word}\n💎 +{final_reward}\n\n👤 Победитель: {username}"
            return True, f"<b>✅ Есть такая буква!</b>"
        else:
            self.wrong_letters.append(letter)
            return False, f"<b>❌ Нет такой буквы!</b>"
    
    def use_hint(self, user_id):
        user = get_user(user_id)
        if user['inventory'].get('hint', 0) > 0:
            user['inventory']['hint'] -= 1
            update_user(user_id, user)
            not_guessed = [l for l in self.word if l not in self.guessed_letters]
            if not_guessed:
                hint_letter = random.choice(not_guessed)
                self.guessed_letters.append(hint_letter)
                return f"<b>🔍 Подсказка:</b> буква {hint_letter} есть в слове!"
            return f"<b>🔓 Все буквы уже открыты!</b>"
        return f"<b>❌ У вас нет подсказок! Купите в магазине.</b>"
    
    def reroll_word(self, user_id):
        if user_id != self.creator_id:
            return f"<b>❌ Сменить слово может только создатель игры!</b>"
        user = get_user(user_id)
        if user['inventory'].get('reroll', 0) > 0:
            user['inventory']['reroll'] -= 1
            update_user(user_id, user)
            self.word = get_word(self.lang, self.difficulty)
            self.guessed_letters = []
            self.wrong_letters = []
            return f"<b>🔄 Слово заменено!</b>"
        return f"<b>❌ У вас нет предмета «Сменить слово»!</b>"
    
    def use_shield(self, user_id):
        user = get_user(user_id)
        if user['inventory'].get('shield', 0) > 0:
            user['inventory']['shield'] -= 1
            update_user(user_id, user)
            self.effects['shield'] = True
            return f"<b>🛡️ Защита активирована!</b>"
        return f"<b>❌ У вас нет защиты!</b>"
    
    def use_double(self, user_id):
        user = get_user(user_id)
        if user['inventory'].get('double', 0) > 0:
            user['inventory']['double'] -= 1
            update_user(user_id, user)
            self.effects['double'] = True
            return f"<b>⚡ Кристалл x2 активирован!</b>"
        return f"<b>❌ У вас нет кристалла x2!</b>"

# ========== КЛАСС КАЗИНО ==========
class CasinoSession:
    def __init__(self, user_id, chat_id, message_id):
        self.user_id = user_id
        self.chat_id = chat_id
        self.message_id = message_id
        self.game = None
        self.bet = None
    
    def get_menu_text(self):
        user = get_user(self.user_id)
        return f"""<b>🎰 КАЗИНО</b>

💰 Ваш баланс: {user['crystals']}💎

Выберите игру:

🪙 Орёл/Решка — угадай сторону (x2)
🎲 Кости — угадай число 1-6 (x6)
🎰 Слоты — собери 3 одинаковых (x5, за 7️⃣ x10)
🃏 Блэкджек — обыграй дилера (x2)"""
    
    def get_bet_text(self):
        user = get_user(self.user_id)
        names = {"coin": "🪙 Орёл/Решка", "dice": "🎲 Кости", "slot": "🎰 Слоты", "blackjack": "🃏 Блэкджек"}
        return f"""<b>{names[self.game]}</b>

💰 Ваш баланс: {user['crystals']}💎

Введите сумму ставки (от 10 до 1000💎):

10💎 | 50💎 | 100💎 | 250💎 | 500💎 | 1000💎"""
    
    def get_coin_text(self):
        return f"""<b>🪙 Орёл/Решка</b>

💰 Ваша ставка: {self.bet}💎

Выберите сторону:"""
    
    def get_dice_text(self):
        return f"""<b>🎲 Кости</b>

💰 Ваша ставка: {self.bet}💎

Выберите число от 1 до 6:"""
    
    def get_slot_text(self):
        return f"""<b>🎰 Слоты</b>

💰 Ваша ставка: {self.bet}💎

🌀 Нажмите «Крутить», чтобы начать!"""
    
    def get_blackjack_text(self):
        return f"""<b>🃏 Блэкджек</b>

💰 Ваша ставка: {self.bet}💎

🌀 Нажмите «Играть», чтобы начать!"""

# ========== ТЕКСТЫ ==========
TEXTS = {
    "ru": {
        "game_title": "🎮 УГАДАЙ СЛОВО",
        "shop_title": "🛒 МАГАЗИН",
        "shop_hint": "🔍 Подсказка — 50💎",
        "shop_reroll": "🔄 Сменить слово — 100💎",
        "shop_shield": "🛡️ Защита — 150💎",
        "shop_double": "💎 Кристалл x2 — 500💎",
        "top_title": "🏆 ТАБЛИЦА ЛИДЕРОВ",
        "top_crystals": "💰 ТОП ПО КРИСТАЛЛАМ",
        "stats_title": "📊 ТВОЯ СТАТИСТИКА",
        "stats_crystals": "💰 Кристаллов: {crystals}",
        "stats_wins": "🏆 Побед: {wins}",
        "stats_games": "🎮 Игр: {games}",
        "stats_streak": "🔥 Текущая серия: {streak}",
        "stats_best_streak": "🏅 Лучшая серия: {best_streak}",
        "stats_donated": "⭐ Поддержал проект: {donated}",
        "difficulty_title": "🎯 ВЫБЕРИ СЛОЖНОСТЬ",
        "difficulty_easy": "🍃 Лёгкая (3-5 букв) — 30💎",
        "difficulty_medium": "⚡ Средняя (5-7 букв) — 50💎",
        "difficulty_hard": "🔥 Сложная (7-9 букв) — 100💎",
        "daily_title": "🎁 ЕЖЕДНЕВНЫЙ БОНУС",
        "daily_reward": "🎉 Вы получили {crystals} кристаллов!",
        "daily_already": "⏰ Вы уже получали бонус сегодня! Приходите завтра.",
        "daily_streak": "🔥 Серия: {streak} дней!",
        "wheel_title": "🎡 КОЛЕСО ФОРТУНЫ",
        "wheel_price": "💎 Стоимость вращения: {price}",
        "wheel_win": "🎉 ПОЗДРАВЛЯЕМ! 🎉\n\n💰 Вы выиграли {prize}!",
        "wheel_no_money": "❌ Не хватает кристаллов! Нужно {price}",
        "inventory_title": "📦 ИНВЕНТАРЬ",
        "inventory_empty": "📦 У вас нет предметов.\n\nКупить их можно в магазине: /shop",
        "inventory_hint": "🔍 Подсказка: {count} шт.",
        "inventory_reroll": "🔄 Сменить слово: {count} шт.",
        "inventory_shield": "🛡️ Защита: {count} шт.",
        "inventory_double": "💎 Кристалл x2: {count} шт.",
        "lang_title": "🌐 ВЫБЕРИ ЯЗЫК",
        "lang_ru": "🇷🇺 Русский",
        "lang_en": "🇬🇧 English",
        "promo_title": "🎫 ПРОМОКОДЫ",
        "promo_enter": "Введите промокод командой:\n/promo КОД\n\nПример: /promo WELCOME100",
        "gift_title": "🎁 ПОДАРКИ",
        "gift_usage": "Используйте команду:\n/gift @username сумма\n\nПример: /gift @friend 100\n\nСумма от 10 до 1000💎",
        "help_title": "❓ ПОМОЩЬ",
        "help_text": """<b>📚 ПОМОЩЬ</b>

<b>🎮 КАК ИГРАТЬ:</b>

1️⃣ Нажми <i>«Начать игру»</i> и выбери сложность
2️⃣ В чате появится слово (_ _ _ _)
3️⃣ Все игроки могут отвечать буквами или словами
4️⃣ Кто первый угадает — получает кристаллы!

<b>💡 СОВЕТЫ:</b>
• Буквы отображаются на своих местах
• Используй подсказки в магазине <i>(50💎)</i>
• За победу дают <b>30-100💎</b> (зависит от сложности)
• Ежедневный бонус увеличивается с каждым днём
• В казино можно рискнуть и умножить кристаллы

<b>🛒 МАГАЗИН ПРЕДМЕТОВ:</b>
🔍 Подсказка — 50💎
🔄 Сменить слово — 100💎
🛡️ Защита — 150💎
💎 Кристалл x2 — 500💎

<b>🎁 ПОДАРКИ:</b>
/gift @username сумма — подарить кристаллы

<b>🎫 ПРОМОКОДЫ:</b>
/promo КОД — активировать промокод

<b>📊 КОМАНДЫ:</b>
/start — главное меню
/stats — статистика
/top — таблица лидеров
/shop — магазин
/inventory — инвентарь
/daily — ежедневный бонус
/wheel — колесо фортуны
/casino — казино
/gift — подарки
/promo — промокод
/lang — язык
/donate — поддержать
/help — помощь""",
        "buttons": {
            "start": "🎮 Начать игру",
            "casino": "🎰 Казино",
            "shop": "🛒 Магазин",
            "top": "🏆 Топ игроков",
            "stats": "📊 Статистика",
            "daily": "🎁 Ежедневный бонус",
            "more": "📋 Ещё",
            "wheel": "🎡 Колесо фортуны",
            "lang": "🌐 Язык",
            "promo": "🎫 Промокоды",
            "donate": "⭐ Поддержать",
            "gift": "🎁 Подарки",
            "inventory": "📦 Инвентарь",
            "help": "❓ Помощь",
            "back": "◀️ Назад",
            "spin": "🌀 Крутить",
            "play": "🎲 Играть",
            "easy": "🍃 Лёгкая",
            "medium": "⚡ Средняя",
            "hard": "🔥 Сложная"
        }
    },
    "en": {
        "game_title": "🎮 GUESS THE WORD",
        "shop_title": "🛒 SHOP",
        "shop_hint": "🔍 Hint — 50💎",
        "shop_reroll": "🔄 Change word — 100💎",
        "shop_shield": "🛡️ Shield — 150💎",
        "shop_double": "💎 Crystal x2 — 500💎",
        "top_title": "🏆 LEADERBOARD",
        "top_crystals": "💰 TOP BY CRYSTALS",
        "stats_title": "📊 YOUR STATISTICS",
        "stats_crystals": "💰 Crystals: {crystals}",
        "stats_wins": "🏆 Wins: {wins}",
        "stats_games": "🎮 Games: {games}",
        "stats_streak": "🔥 Current streak: {streak}",
        "stats_best_streak": "🏅 Best streak: {best_streak}",
        "stats_donated": "⭐ Donated: {donated}",
        "difficulty_title": "🎯 CHOOSE DIFFICULTY",
        "difficulty_easy": "🍃 Easy (3-5 letters) — 30💎",
        "difficulty_medium": "⚡ Medium (5-7 letters) — 50💎",
        "difficulty_hard": "🔥 Hard (7-9 letters) — 100💎",
        "daily_title": "🎁 DAILY BONUS",
        "daily_reward": "🎉 You received {crystals} crystals!",
        "daily_already": "⏰ You already received today's bonus! Come back tomorrow.",
        "daily_streak": "🔥 Streak: {streak} days!",
        "wheel_title": "🎡 WHEEL OF FORTUNE",
        "wheel_price": "💎 Spin cost: {price}",
        "wheel_win": "🎉 CONGRATULATIONS! 🎉\n\n💰 You won {prize}!",
        "wheel_no_money": "❌ Not enough crystals! Need {price}",
        "inventory_title": "📦 INVENTORY",
        "inventory_empty": "📦 You have no items.\n\nBuy them in the shop: /shop",
        "inventory_hint": "🔍 Hint: {count} pcs.",
        "inventory_reroll": "🔄 Change word: {count} pcs.",
        "inventory_shield": "🛡️ Shield: {count} pcs.",
        "inventory_double": "💎 Crystal x2: {count} pcs.",
        "lang_title": "🌐 CHOOSE LANGUAGE",
        "lang_ru": "🇷🇺 Russian",
        "lang_en": "🇬🇧 English",
        "promo_title": "🎫 PROMO CODES",
        "promo_enter": "Enter promo code:\n/promo CODE\n\nExample: /promo WELCOME100",
        "gift_title": "🎁 GIFTS",
        "gift_usage": "Use command:\n/gift @username amount\n\nExample: /gift @friend 100\n\nAmount from 10 to 1000💎",
        "help_title": "❓ HELP",
        "help_text": """<b>📚 HELP</b>

<b>🎮 HOW TO PLAY:</b>

1️⃣ Press <i>«Start Game»</i> and choose difficulty
2️⃣ A word appears in chat (_ _ _ _)
3️⃣ Everyone can answer with letters or words
4️⃣ First to guess gets crystals!

<b>💡 TIPS:</b>
• Letters appear in their places
• Use hints from the shop <i>(50💎)</i>
• Win <b>30-100💎</b> (depends on difficulty)
• Daily bonus increases every day
• Casino can multiply your crystals

<b>🛒 SHOP ITEMS:</b>
🔍 Hint — 50💎
🔄 Change word — 100💎
🛡️ Shield — 150💎
💎 Crystal x2 — 500💎

<b>🎁 GIFTS:</b>
/gift @username amount — gift crystals

<b>🎫 PROMO CODES:</b>
/promo CODE — activate promo code

<b>📊 COMMANDS:</b>
/start — main menu
/stats — statistics
/top — leaderboard
/shop — shop
/inventory — inventory
/daily — daily bonus
/wheel — wheel of fortune
/casino — casino
/gift — gifts
/promo — promo code
/lang — language
/donate — support
/help — help""",
        "buttons": {
            "start": "🎮 Start Game",
            "casino": "🎰 Casino",
            "shop": "🛒 Shop",
            "top": "🏆 Leaderboard",
            "stats": "📊 Statistics",
            "daily": "🎁 Daily bonus",
            "more": "📋 More",
            "wheel": "🎡 Wheel of Fortune",
            "lang": "🌐 Language",
            "promo": "🎫 Promo codes",
            "donate": "⭐ Support",
            "gift": "🎁 Gifts",
            "inventory": "📦 Inventory",
            "help": "❓ Help",
            "back": "◀️ Back",
            "spin": "🌀 Spin",
            "play": "🎲 Play",
            "easy": "🍃 Easy",
            "medium": "⚡ Medium",
            "hard": "🔥 Hard"
        }
    }
}

# ========== КЛАВИАТУРЫ ==========
def get_user_lang(user_id):
    return get_user(user_id).get('lang', 'ru')

def send_with_image(chat_id, image_key, text, reply_markup=None):
    url = IMAGES.get(image_key)
    if url:
        try:
            bot.send_photo(chat_id, photo=url, caption=text, reply_markup=reply_markup, parse_mode="HTML")
        except:
            bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode="HTML")

def edit_with_image(chat_id, msg_id, image_key, text, reply_markup=None):
    url = IMAGES.get(image_key)
    if url:
        try:
            bot.edit_message_media(types.InputMediaPhoto(url, caption=text, parse_mode="HTML"), chat_id, msg_id, reply_markup=reply_markup)
        except:
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=reply_markup, parse_mode="HTML")
    else:
        bot.edit_message_text(text, chat_id, msg_id, reply_markup=reply_markup, parse_mode="HTML")

def main_menu_kb(user_id):
    lang = get_user_lang(user_id)
    btns = TEXTS[lang]["buttons"]
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton(btns["start"], callback_data="start_game"),
        types.InlineKeyboardButton(btns["casino"], callback_data="casino"),
        types.InlineKeyboardButton(btns["shop"], callback_data="shop"),
        types.InlineKeyboardButton(btns["top"], callback_data="top"),
        types.InlineKeyboardButton(btns["stats"], callback_data="stats"),
        types.InlineKeyboardButton(btns["daily"], callback_data="daily"),
        types.InlineKeyboardButton(btns["more"], callback_data="more_menu")
    )
    return markup

def more_menu_kb(user_id):
    lang = get_user_lang(user_id)
    btns = TEXTS[lang]["buttons"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(btns["wheel"], callback_data="wheel"),
        types.InlineKeyboardButton(btns["lang"], callback_data="lang"),
        types.InlineKeyboardButton(btns["promo"], callback_data="promo"),
        types.InlineKeyboardButton(btns["gift"], callback_data="gift"),
        types.InlineKeyboardButton(btns["inventory"], callback_data="inventory"),
        types.InlineKeyboardButton(btns["donate"], callback_data="donate"),
        types.InlineKeyboardButton(btns["help"], callback_data="help"),
        types.InlineKeyboardButton(btns["back"], callback_data="back_to_main")
    )
    return markup

def difficulty_kb(user_id):
    lang = get_user_lang(user_id)
    btns = TEXTS[lang]["buttons"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(btns["easy"], callback_data="difficulty_easy"),
        types.InlineKeyboardButton(btns["medium"], callback_data="difficulty_medium"),
        types.InlineKeyboardButton(btns["hard"], callback_data="difficulty_hard"),
        types.InlineKeyboardButton(btns["back"], callback_data="back_to_main")
    )
    return markup

def casino_menu_kb(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🪙 Орёл/Решка", callback_data="casino_coin"),
        types.InlineKeyboardButton("🎲 Кости", callback_data="casino_dice"),
        types.InlineKeyboardButton("🎰 Слоты", callback_data="casino_slot"),
        types.InlineKeyboardButton("🃏 Блэкджек", callback_data="casino_blackjack"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
    )
    return markup

def casino_bet_kb():
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("10💎", callback_data="casino_bet_10"),
        types.InlineKeyboardButton("50💎", callback_data="casino_bet_50"),
        types.InlineKeyboardButton("100💎", callback_data="casino_bet_100"),
        types.InlineKeyboardButton("250💎", callback_data="casino_bet_250"),
        types.InlineKeyboardButton("500💎", callback_data="casino_bet_500"),
        types.InlineKeyboardButton("1000💎", callback_data="casino_bet_1000"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="casino")
    )
    return markup

def casino_coin_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🪙 Орёл", callback_data="casino_choice_Орёл"),
        types.InlineKeyboardButton("🪙 Решка", callback_data="casino_choice_Решка"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="casino")
    )
    return markup

def casino_dice_kb():
    markup = types.InlineKeyboardMarkup(row_width=3)
    btns = [types.InlineKeyboardButton(str(i), callback_data=f"casino_choice_{i}") for i in range(1, 7)]
    markup.add(*btns)
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="casino"))
    return markup

def casino_slot_kb():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🌀 Крутить", callback_data="casino_slot_spin"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="casino")
    )
    return markup

def casino_blackjack_kb():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎲 Играть", callback_data="casino_blackjack_play"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="casino")
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
        types.InlineKeyboardButton(texts["buttons"]["back"], callback_data="back_to_main")
    )
    return markup

def top_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(texts["top_crystals"], callback_data="top_crystals"),
        types.InlineKeyboardButton(texts["buttons"]["back"], callback_data="back_to_main")
    )
    return markup

def stats_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(texts["buttons"]["back"], callback_data="back_to_main"))
    return markup

def daily_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(texts["buttons"]["back"], callback_data="back_to_main"))
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

def promo_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(texts["buttons"]["back"], callback_data="back_to_main"))
    return markup

def gift_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(texts["buttons"]["back"], callback_data="back_to_main"))
    return markup

def inventory_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(texts["buttons"]["back"], callback_data="back_to_main"))
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
    stars_list = [1, 2, 5, 10, 20, 50, 100, 150, 200, 250, 300, 400, 500, 750, 1000]
    for s in stars_list:
        bonus = 0 if s == 1 else (10 if s == 2 else (30 if s == 5 else (75 if s == 10 else (200 if s == 20 else (750 if s == 50 else (2000 if s == 100 else (3750 if s == 150 else (6000 if s == 200 else (8750 if s == 250 else (12000 if s == 300 else (18000 if s == 400 else (25000 if s == 500 else (41250 if s == 750 else 60000))))))))))))
        total = s * 50 + bonus
        markup.add(types.InlineKeyboardButton(f"{s} Star → {total}", callback_data=f"donate_{s}"))
    markup.add(types.InlineKeyboardButton(texts["buttons"]["back"], callback_data="donate"))
    return markup

def game_kb(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔍 Подсказка", callback_data=f"use_hint_{user_id}"),
        types.InlineKeyboardButton("🔄 Сменить слово", callback_data=f"use_reroll_{user_id}"),
        types.InlineKeyboardButton("🛡️ Защита", callback_data=f"use_shield_{user_id}"),
        types.InlineKeyboardButton("💎 Кристалл x2", callback_data=f"use_double_{user_id}"),
        types.InlineKeyboardButton("🏠 Выйти", callback_data=f"exit_game_{user_id}")
    )
    return markup

# ========== АДМИН-ПАНЕЛЬ ==========
def admin_panel_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
        types.InlineKeyboardButton("🎫 Промокоды", callback_data="admin_promocodes"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton("🎮 Управление игрой", callback_data="admin_game"),
        types.InlineKeyboardButton("📝 Тексты", callback_data="admin_texts"),
        types.InlineKeyboardButton("🖼️ Картинки", callback_data="admin_images"),
        types.InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast"),
        types.InlineKeyboardButton("📋 Логи", callback_data="admin_logs"),
        types.InlineKeyboardButton("🎁 Подарки", callback_data="admin_gifts"),
        types.InlineKeyboardButton("🔔 Уведомления", callback_data="admin_notifications"),
        types.InlineKeyboardButton("🧠 Нейросеть", callback_data="admin_neural"),
        types.InlineKeyboardButton("🔄 Сброс статистики", callback_data="admin_reset"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
    )
    return markup

# ========== КОМАНДЫ ==========
active_games = {}
casino_sessions = {}
reset_confirm = {}

@bot.message_handler(commands=['start', 'guess', 'menu'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    user = get_user(user_id)
    user['username'] = username
    update_user(user_id, user)
    lang = user.get('lang', 'ru')
    texts = TEXTS[lang]
    
    text = f"""<b>🌟 ДОБРО ПОЖАЛОВАТЬ В ИГРУ «УГАДАЙ СЛОВО»!</b> 🌟

Привет, {username}! 👋

<b>🎮 ЧТО ТЕБЯ ЖДЁТ:</b>

✨ Уникальные слова, созданные нейросетью
💎 Кристаллы за каждую победу
🏆 Соревнования с друзьями в чате
🎰 Казино для умножения кристаллов
🎁 Ежедневные бонусы
🎡 Колесо фортуны с крутыми призами

<b>🎯 КАК ИГРАТЬ:</b>

1️⃣ Нажми <i>«Начать игру»</i> и выбери сложность
2️⃣ В чате появится слово <code>_ _ _ _</code>
3️⃣ Все игроки могут отвечать буквами или словами
4️⃣ Кто первый угадает — получает кристаллы!

<b>💡 СОВЕТЫ:</b>

• Буквы отображаются на своих местах
• Используй подсказки в магазине <i>(50💎)</i>
• За победу дают <b>30-100💎</b> (зависит от сложности)
• Ежедневный бонус увеличивается с каждым днём
• В казино можно рискнуть и умножить кристаллы

<b>🎯 ИГРАЙ, ПОБЕЖДАЙ, СОРЕВНУЙСЯ!</b>

<i>❤️ Бот создан с любовью для твоего чата</i>"""
    
    send_with_image(message.chat.id, "main", text, main_menu_kb(user_id))

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user.get('lang', 'ru')
    texts = TEXTS[lang]
    text = f"""<b>{texts["stats_title"]}</b>

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}
{texts["stats_games"].format(games=user['games'])}
{texts["stats_streak"].format(streak=user['streak'])}
{texts["stats_best_streak"].format(best_streak=user['best_streak'])}
{texts["stats_donated"].format(donated=user.get('donated_stars', 0))}"""
    send_with_image(message.chat.id, "stats", text, stats_kb(user_id))

@bot.message_handler(commands=['top'])
def top_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    users = load_json(USERS_FILE)
    top = [{'username': u.get('username', f"User_{uid}"), 'crystals': u.get('crystals', 0)} for uid, u in users.items()]
    top.sort(key=lambda x: x['crystals'], reverse=True)
    text = f"<b>{texts['top_crystals']}</b>\n\n"
    for i, u in enumerate(top[:10], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{medal} {u['username']} — {u['crystals']}💎\n"
    send_with_image(message.chat.id, "top", text, top_kb(user_id))

@bot.message_handler(commands=['shop'])
def shop_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    send_with_image(message.chat.id, "shop", f"<b>{texts['shop_title']}</b>", shop_kb(user_id))

@bot.message_handler(commands=['inventory'])
def inventory_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    lang = user.get('lang', 'ru')
    texts = TEXTS[lang]
    inv = user.get('inventory', {})
    items = []
    if inv.get('hint', 0): items.append(texts["inventory_hint"].format(count=inv['hint']))
    if inv.get('reroll', 0): items.append(texts["inventory_reroll"].format(count=inv['reroll']))
    if inv.get('shield', 0): items.append(texts["inventory_shield"].format(count=inv['shield']))
    if inv.get('double', 0): items.append(texts["inventory_double"].format(count=inv['double']))
    if items:
        text = f"<b>{texts['inventory_title']}</b>\n\n" + "\n".join(items)
    else:
        text = f"<b>{texts['inventory_title']}</b>\n\n{texts['inventory_empty']}"
    send_with_image(message.chat.id, "inventory", text, inventory_kb(user_id))

@bot.message_handler(commands=['daily'])
def daily_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    bonus, streak = get_daily_bonus(user_id)
    if bonus is None:
        text = f"""<b>{texts["daily_title"]}</b>

{texts["daily_already"]}
{texts["daily_streak"].format(streak=streak)}"""
    else:
        text = f"""<b>{texts["daily_title"]}</b>

{texts["daily_reward"].format(crystals=bonus)}
{texts["daily_streak"].format(streak=streak)}"""
    send_with_image(message.chat.id, "daily", text, daily_kb(user_id))

@bot.message_handler(commands=['wheel'])
def wheel_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    text = f"""<b>{texts["wheel_title"]}</b>

{texts["wheel_price"].format(price=50)}"""
    send_with_image(message.chat.id, "wheel", text, wheel_kb(user_id))

@bot.message_handler(commands=['casino'])
def casino_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    text = f"""<b>{texts["casino_title"]}</b>

💰 Ваш баланс: {get_user(user_id)['crystals']}💎

Выберите игру:

🪙 Орёл/Решка — угадай сторону (x2)
🎲 Кости — угадай число 1-6 (x6)
🎰 Слоты — собери 3 одинаковых (x5, за 7️⃣ x10)
🃏 Блэкджек — обыграй дилера (x2)"""
    send_with_image(message.chat.id, "casino", text, casino_menu_kb(user_id))

@bot.message_handler(commands=['gift'])
def gift_command(message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) >= 3:
        username = args[1].replace('@', '')
        try:
            amount = int(args[2])
        except:
            bot.reply_to(message, "❌ Неверная сумма")
            return
        users = load_json(USERS_FILE)
        target_id = None
        for uid, u in users.items():
            if u.get('username') == username:
                target_id = int(uid)
                break
        if not target_id:
            bot.reply_to(message, "❌ Пользователь не найден")
            return
        success, msg = send_gift(user_id, target_id, amount)
        bot.reply_to(message, msg)
    else:
        lang = get_user_lang(user_id)
        texts = TEXTS[lang]
        send_with_image(message.chat.id, "inventory", f"<b>{texts['gift_title']}</b>\n\n{texts['gift_usage']}", gift_kb(user_id))

@bot.message_handler(commands=['promo'])
def promo_command(message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "❌ Используйте: /promo КОД")
        return
    code = args[1].upper()
    promos = load_json(PROMO_FILE)
    if code not in promos:
        bot.reply_to(message, "❌ Промокод не найден")
        return
    promo = promos[code]
    if user_id in promo.get('used_by', []):
        bot.reply_to(message, "❌ Вы уже использовали этот промокод")
        return
    if 'used_by' not in promo:
        promo['used_by'] = []
    promo['used_by'].append(user_id)
    promos[code] = promo
    save_json(PROMO_FILE, promos)
    add_crystals(user_id, promo['crystals'])
    bot.reply_to(message, f"✅ Промокод активирован! Вы получили {promo['crystals']} кристаллов!")

@bot.message_handler(commands=['lang'])
def lang_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    send_with_image(message.chat.id, "main", f"<b>{texts['lang_title']}</b>", lang_kb(user_id))

@bot.message_handler(commands=['donate'])
def donate_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    text = f"""<b>{texts["donate_title"]}</b>

✨ 1 Star = 50 кристаллов + бонусы!"""
    send_with_image(message.chat.id, "donate", text, donate_kb(user_id))

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    bot.send_message(message.chat.id, texts["help_text"], parse_mode="HTML")

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
    chat_id = message.chat.id
    if message.text and message.text.startswith('/'):
        return
    if chat_id in active_games and active_games[chat_id].active:
        game = active_games[chat_id]
        guess = message.text.strip()
        if guess:
            username = message.from_user.username or message.from_user.first_name
            res, msg = game.guess_letter(guess, user_id, username)
            if not game.active:
                bot.edit_message_text(msg, game.chat_id, game.message_id, parse_mode="HTML")
                del active_games[chat_id]
                user = get_user(user_id)
                lang = user.get('lang', 'ru')
                texts = TEXTS[lang]
                menu_text = f"""<b>{texts["game_title"]}</b>

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}"""
                send_with_image(message.chat.id, "main", menu_text, main_menu_kb(user_id))
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
            lang = user.get('lang', 'ru')
            texts = TEXTS[lang]
            text = f"""<b>{texts["game_title"]}</b>

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}

Нет активной игры. Нажми «Начать игру»"""
            send_with_image(message.chat.id, "main", text, main_menu_kb(user_id))

# ========== ОБРАБОТКА КНОПОК ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    data = call.data
    user = get_user(user_id)
    lang = user.get('lang', 'ru')
    texts = TEXTS[lang]
    
    # Игровые кнопки
    if data.startswith("use_hint_"):
        owner = int(data.split("_")[2])
        if user_id != owner:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return
        if chat_id not in active_games:
            bot.answer_callback_query(call.id, "❌ Нет активной игры!", show_alert=True)
            return
        game = active_games[chat_id]
        msg = game.use_hint(user_id)
        new_text = game.get_game_text(msg)
        bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id), parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return
    
    elif data.startswith("use_reroll_"):
        owner = int(data.split("_")[2])
        if user_id != owner:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return
        if chat_id not in active_games:
            bot.answer_callback_query(call.id, "❌ Нет активной игры!", show_alert=True)
            return
        game = active_games[chat_id]
        msg = game.reroll_word(user_id)
        new_text = game.get_game_text(msg)
        bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id), parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return
    
    elif data.startswith("use_shield_"):
        owner = int(data.split("_")[2])
        if user_id != owner:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return
        if chat_id not in active_games:
            bot.answer_callback_query(call.id, "❌ Нет активной игры!", show_alert=True)
            return
        game = active_games[chat_id]
        msg = game.use_shield(user_id)
        new_text = game.get_game_text(msg)
        bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id), parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return
    
    elif data.startswith("use_double_"):
        owner = int(data.split("_")[2])
        if user_id != owner:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return
        if chat_id not in active_games:
            bot.answer_callback_query(call.id, "❌ Нет активной игры!", show_alert=True)
            return
        game = active_games[chat_id]
        msg = game.use_double(user_id)
        new_text = game.get_game_text(msg)
        bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id), parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return
    
    elif data.startswith("exit_game_"):
        owner = int(data.split("_")[2])
        if user_id != owner:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return
        if chat_id in active_games:
            del active_games[chat_id]
        bot.answer_callback_query(call.id, "🏠 Игра завершена")
        text = f"""<b>{texts["game_title"]}</b>

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, main_menu_kb(user_id))
        return
    
    # Колесо фортуны
    elif data.startswith("wheel_spin_"):
        owner = int(data.split("_")[2])
        if user_id != owner:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return
        prize, price = spin_wheel(user_id)
        if prize is None:
            result = texts["wheel_no_money"].format(price=price)
        else:
            result = texts["wheel_win"].format(prize=f"{prize} кристаллов" if isinstance(prize, int) else prize)
        wheel_text = f"""<b>{texts["wheel_title"]}</b>

{result}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "wheel", wheel_text, wheel_kb(user_id))
        bot.answer_callback_query(call.id)
        return
    
    # Казино
    elif data == "casino":
        casino = CasinoSession(user_id, chat_id, call.message.message_id)
        casino_sessions[user_id] = casino
        text = casino.get_menu_text()
        edit_with_image(chat_id, call.message.message_id, "casino", text, casino_menu_kb(user_id))
        bot.answer_callback_query(call.id)
        return
    
    elif data in ["casino_coin", "casino_dice", "casino_slot", "casino_blackjack"]:
        if user_id not in casino_sessions:
            bot.answer_callback_query(call.id, "❌ Сессия не найдена", show_alert=True)
            return
        casino = casino_sessions[user_id]
        casino.game = data.split("_")[1]
        text = casino.get_bet_text()
        edit_with_image(chat_id, call.message.message_id, "casino", text, casino_bet_kb())
        bot.answer_callback_query(call.id)
        return
    
    elif data.startswith("casino_bet_"):
        bet = int(data.split("_")[2])
        if user_id not in casino_sessions:
            bot.answer_callback_query(call.id, "❌ Сессия не найдена", show_alert=True)
            return
        casino = casino_sessions[user_id]
        casino.bet = bet
        if casino.game == "coin":
            text = casino.get_coin_text()
            markup = casino_coin_kb()
        elif casino.game == "dice":
            text = casino.get_dice_text()
            markup = casino_dice_kb()
        elif casino.game == "slot":
            text = casino.get_slot_text()
            markup = casino_slot_kb()
        else:
            text = casino.get_blackjack_text()
            markup = casino_blackjack_kb()
        edit_with_image(chat_id, call.message.message_id, "casino", text, markup)
        bot.answer_callback_query(call.id)
        return
    
    elif data.startswith("casino_choice_"):
        choice = data.split("_")[2]
        if user_id not in casino_sessions:
            bot.answer_callback_query(call.id, "❌ Сессия не найдена", show_alert=True)
            return
        casino = casino_sessions[user_id]
        try:
            if casino.game == "coin":
                if choice not in ["Орёл", "Решка"]:
                    raise ValueError
                win, result = play_casino(user_id, "coin", casino.bet, choice)
            else:
                num = int(choice)
                if not 1 <= num <= 6:
                    raise ValueError
                win, result = play_casino(user_id, "dice", casino.bet, num)
        except:
            bot.answer_callback_query(call.id, "❌ Неверный выбор", show_alert=True)
            return
        text = f"""<b>{casino.get_bet_text().split('💰')[0]}</b>

{result}"""
        edit_with_image(chat_id, call.message.message_id, "casino", text, casino_menu_kb(user_id))
        del casino_sessions[user_id]
        bot.answer_callback_query(call.id)
        return
    
    elif data == "casino_slot_spin":
        if user_id not in casino_sessions:
            bot.answer_callback_query(call.id, "❌ Сессия не найдена", show_alert=True)
            return
        casino = casino_sessions[user_id]
        symbols = ["🍒", "🍋", "🔔", "💎", "7️⃣"]
        for _ in range(5):
            s1, s2, s3 = random.choice(symbols), random.choice(symbols), random.choice(symbols)
            spin_text = f"""<b>🎰 Слоты</b>

💰 Ваша ставка: {casino.bet}💎

🌀 КРУТИМ...

[ {s1} {s2} {s3} ]"""
            edit_with_image(chat_id, call.message.message_id, "casino", spin_text, casino_slot_kb())
            time.sleep(0.3)
        win, result = play_casino(user_id, "slot", casino.bet)
        text = f"""<b>🎰 Слоты</b>

{result}"""
        edit_with_image(chat_id, call.message.message_id, "casino", text, casino_menu_kb(user_id))
        del casino_sessions[user_id]
        bot.answer_callback_query(call.id)
        return
    
    elif data == "casino_blackjack_play":
        if user_id not in casino_sessions:
            bot.answer_callback_query(call.id, "❌ Сессия не найдена", show_alert=True)
            return
        casino = casino_sessions[user_id]
        win, result = play_casino(user_id, "blackjack", casino.bet)
        text = f"""<b>🃏 Блэкджек</b>

{result}"""
        edit_with_image(chat_id, call.message.message_id, "casino", text, casino_menu_kb(user_id))
        del casino_sessions[user_id]
        bot.answer_callback_query(call.id)
        return
    
    # Основные кнопки
    elif data == "back_to_main":
        text = f"""<b>{texts["game_title"]}</b>

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, main_menu_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "more_menu":
        text = "<b>📋 ДОПОЛНИТЕЛЬНОЕ МЕНЮ</b>\n\nВыберите раздел:"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=more_menu_kb(user_id), parse_mode="HTML")
        bot.answer_callback_query(call.id)
    
    elif data == "start_game":
        text = texts["difficulty_title"]
        edit_with_image(call.message.chat.id, call.message.message_id, "game", text, difficulty_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data in ["difficulty_easy", "difficulty_medium", "difficulty_hard"]:
        diff = data.split("_")[1]
        if chat_id in active_games and active_games[chat_id].active:
            bot.answer_callback_query(call.id, "❌ В этом чате уже есть активная игра!", show_alert=True)
            return
        sent = bot.send_message(chat_id, "🎮 Генерация слова...")
        game = Game(chat_id, user_id, lang, sent.message_id, diff)
        active_games[chat_id] = game
        game_text = game.get_game_text("✨ Игра началась! Все могут угадывать!")
        bot.edit_message_text(game_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id), parse_mode="HTML")
        bot.answer_callback_query(call.id)
    
    elif data == "shop":
        edit_with_image(call.message.chat.id, call.message.message_id, "shop", f"<b>{texts['shop_title']}</b>", shop_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data.startswith("buy_"):
        item = data[4:]
        prices = {"hint": 50, "reroll": 100, "shield": 150, "double": 500}
        if user['crystals'] < prices[item]:
            bot.answer_callback_query(call.id, f"❌ Не хватает! Нужно {prices[item]}💎", show_alert=True)
            return
        user['crystals'] -= prices[item]
        user['inventory'][item] = user['inventory'].get(item, 0) + 1
        update_user(user_id, user)
        bot.answer_callback_query(call.id, f"✅ Куплено! -{prices[item]}💎", show_alert=True)
        edit_with_image(call.message.chat.id, call.message.message_id, "shop", f"<b>{texts['shop_title']}</b>", shop_kb(user_id))
    
    elif data == "top":
        users = load_json(USERS_FILE)
        top = [{'username': u.get('username', f"User_{uid}"), 'crystals': u.get('crystals', 0)} for uid, u in users.items()]
        top.sort(key=lambda x: x['crystals'], reverse=True)
        text = f"<b>{texts['top_crystals']}</b>\n\n"
        for i, u in enumerate(top[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {u['username']} — {u['crystals']}💎\n"
        edit_with_image(call.message.chat.id, call.message.message_id, "top", text, top_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "stats":
        text = f"""<b>{texts["stats_title"]}</b>

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}
{texts["stats_games"].format(games=user['games'])}
{texts["stats_streak"].format(streak=user['streak'])}
{texts["stats_best_streak"].format(best_streak=user['best_streak'])}
{texts["stats_donated"].format(donated=user.get('donated_stars', 0))}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "stats", text, stats_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "daily":
        bonus, streak = get_daily_bonus(user_id)
        if bonus is None:
            text = f"""<b>{texts["daily_title"]}</b>

{texts["daily_already"]}
{texts["daily_streak"].format(streak=streak)}"""
        else:
            text = f"""<b>{texts["daily_title"]}</b>

{texts["daily_reward"].format(crystals=bonus)}
{texts["daily_streak"].format(streak=streak)}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "daily", text, daily_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "wheel":
        text = f"""<b>{texts["wheel_title"]}</b>

{texts["wheel_price"].format(price=50)}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "wheel", text, wheel_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "lang":
        edit_with_image(call.message.chat.id, call.message.message_id, "main", f"<b>{texts['lang_title']}</b>", lang_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "lang_ru":
        user['lang'] = 'ru'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "🇷🇺 Язык: русский")
        text = f"""<b>{texts["game_title"]}</b>

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, main_menu_kb(user_id))
    
    elif data == "lang_en":
        user['lang'] = 'en'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "🇬🇧 Language: English")
        texts = TEXTS["en"]
        text = f"""<b>{texts["game_title"]}</b>

{texts["stats_crystals"].format(crystals=user['crystals'])}
{texts["stats_wins"].format(wins=user['wins'])}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "main", text, main_menu_kb(user_id))
    
    elif data == "promo":
        text = f"""<b>{texts['promo_title']}</b>

{texts['promo_enter']}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "promo", text, promo_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "gift":
        text = f"""<b>{texts['gift_title']}</b>

{texts['gift_usage']}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "inventory", text, gift_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "inventory":
        inv = user.get('inventory', {})
        items = []
        if inv.get('hint', 0): items.append(texts["inventory_hint"].format(count=inv['hint']))
        if inv.get('reroll', 0): items.append(texts["inventory_reroll"].format(count=inv['reroll']))
        if inv.get('shield', 0): items.append(texts["inventory_shield"].format(count=inv['shield']))
        if inv.get('double', 0): items.append(texts["inventory_double"].format(count=inv['double']))
        if items:
            text = f"<b>{texts['inventory_title']}</b>\n\n" + "\n".join(items)
        else:
            text = f"<b>{texts['inventory_title']}</b>\n\n{texts['inventory_empty']}"
        edit_with_image(call.message.chat.id, call.message.message_id, "inventory", text, inventory_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "donate":
        text = f"""<b>{texts["donate_title"]}</b>

✨ 1 Star = 50 кристаллов + бонусы!"""
        edit_with_image(call.message.chat.id, call.message.message_id, "donate", text, donate_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "donate_stars_menu":
        text = f"<b>{texts['donate_stars_title']}</b>\n\n✨ 1 Star = 50 кристаллов + бонусы!"
        edit_with_image(call.message.chat.id, call.message.message_id, "donate", text, donate_stars_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data.startswith("donate_") and data != "donate_stars_menu":
        stars = int(data.split("_")[1])
        bonus_map = {1:0, 2:10, 5:30, 10:75, 20:200, 50:750, 100:2000, 150:3750, 200:6000, 250:8750, 300:12000, 400:18000, 500:25000, 750:41250, 1000:60000}
        bonus = bonus_map.get(stars, 0)
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
    
    elif data == "help":
        text = texts["help_text"]
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML")
        bot.answer_callback_query(call.id)
    
    # Админ-панель (упрощённая для демонстрации)
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
    donations = load_json(DONATIONS_FILE)
    if 'donations' not in donations:
        donations['donations'] = []
    donations['donations'].append({'user_id': user_id, 'username': username, 'stars': stars, 'crystals': crystals, 'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    save_json(DONATIONS_FILE, donations)
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
2️⃣ → Выберите сложность
3️⃣ → В чате появится слово (_ _ _ _)
4️⃣ → Все игроки могут отвечать буквами или словами
5️⃣ → Кто первый угадает — получает кристаллы!

🎰 КАЗИНО:
/casino — поиграть в казино и умножить кристаллы

⭐ Поддержать проект:
💰 /donate → поддержать бота Telegram Stars

📊 Команды:
🏠 /start → главное меню
📈 /stats → моя статистика
🏆 /top → таблица лидеров
🛒 /shop → магазин предметов
📦 /inventory → инвентарь
🌐 /lang → выбрать язык
🎁 /daily → ежедневный бонус
🎡 /wheel → колесо фортуны
🎰 /casino → казино
🎁 /gift → подарки
🎫 /promo → промокоды
❓ /help → помощь

🎯 Играйте вместе, соревнуйтесь и побеждайте!

❤️ Бот создан с любовью для вашего чата"""
            bot.send_message(message.chat.id, welcome_text)
            break

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("🤖 Бот запущен")
    print("🧠 ЛЮТАЯ НЕЙРОСЕТЬ — полное знание языков")
    print("🎮 УГАДАЙ СЛОВО — общая игра в чате")
    print("🎰 КАЗИНО — всё в одном сообщении")
    print("🎡 КОЛЕСО ФОРТУНЫ — всё в одном сообщении")
    print("⭐ ДОНАТ — 15 вариантов до 1000 Stars")
    print("🎁 ПОДАРКИ — дари кристаллы друзьям")
    print("📦 ИНВЕНТАРЬ — используй предметы")
    print("🎫 ПРОМОКОДЫ — активируй бонусы")
    print("🔧 АДМИН-ПАНЕЛЬ — 12 разделов")
    print("")
    print("Команды: /start, /stats, /top, /shop, /inventory, /daily, /wheel, /casino, /gift, /promo, /lang, /donate, /help, /admin")
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")