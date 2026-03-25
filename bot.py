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
    "coin": {"name": "🪙 Орёл/Решка", "multiplier": 2},
    "dice": {"name": "🎲 Кости (1-6)", "multiplier": 6},
    "slot": {"name": "🎰 Слоты", "multiplier": 5},
    "blackjack": {"name": "🃏 Блэкджек", "multiplier": 2}
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
        
        # ========== РУССКИЙ ЯЗЫК ==========
        if lang == "ru":
            self.vowels = "АЕЁИОУЫЭЮЯ"
            self.consonants = "БВГДЖЗЙКЛМНПРСТФХЦЧШЩ"
            self.soft_sign = "Ь"
            self.hard_sign = "Ъ"
            self.all_letters = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
            
            # Частоты букв
            self.letter_freq = {
                'О': 0.109, 'Е': 0.084, 'А': 0.075, 'И': 0.074, 'Н': 0.067,
                'Т': 0.063, 'С': 0.055, 'Р': 0.048, 'В': 0.045, 'Л': 0.044,
                'К': 0.034, 'М': 0.032, 'Д': 0.030, 'П': 0.028, 'У': 0.026,
                'Я': 0.025, 'Ы': 0.024, 'Ь': 0.023, 'Г': 0.022, 'З': 0.020,
                'Б': 0.019, 'Ч': 0.018, 'Й': 0.016, 'Х': 0.015, 'Ж': 0.014,
                'Ш': 0.012, 'Ю': 0.010, 'Ц': 0.009, 'Щ': 0.008, 'Э': 0.007,
                'Ф': 0.006, 'Ъ': 0.003, 'Ё': 0.001
            }
            
            # Реальные слова для обучения
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
        
        # ========== АНГЛИЙСКИЙ ЯЗЫК ==========
        else:
            self.vowels = "AEIOUY"
            self.consonants = "BCDFGHJKLMNPQRSTVWXZ"
            self.soft_sign = ""
            self.hard_sign = ""
            self.all_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            
            self.letter_freq = {
                'E': 0.127, 'T': 0.090, 'A': 0.081, 'O': 0.075, 'I': 0.069,
                'N': 0.067, 'S': 0.063, 'H': 0.060, 'R': 0.059, 'D': 0.042,
                'L': 0.040, 'C': 0.027, 'U': 0.027, 'M': 0.024, 'W': 0.023,
                'F': 0.022, 'G': 0.020, 'Y': 0.019, 'P': 0.019, 'B': 0.014,
                'V': 0.012, 'K': 0.008, 'J': 0.001, 'X': 0.001, 'Q': 0.001, 'Z': 0.001
            }
            
            self.corpus = [
                "CAT", "DOG", "SUN", "MOON", "STAR", "TREE", "FLOWER", "BIRD", "FISH",
                "HOUSE", "CAR", "MOM", "DAD", "SON", "DAUGHTER", "BROTHER", "SISTER",
                "FRIEND", "LOVE", "HOPE", "WATER", "FIRE", "EARTH", "WIND", "CLOUD",
                "RAIN", "SNOW", "SUMMER", "WINTER", "SPRING", "AUTUMN", "DAY", "NIGHT",
                "CITY", "TOWN", "STREET", "PARK", "RIVER", "LAKE", "SEA", "OCEAN",
                "MOUNTAIN", "FOREST", "DESERT", "ISLAND", "SKY", "UNIVERSE", "GALAXY"
            ]
        
        # Строим n-граммы (1, 2, 3, 4 порядка)
        self.ngrams_1 = defaultdict(Counter)
        self.ngrams_2 = defaultdict(Counter)
        self.ngrams_3 = defaultdict(Counter)
        self.ngrams_4 = defaultdict(Counter)
        
        self._train()
    
    def _train(self):
        """Обучение нейросети на реальных словах"""
        for word in self.corpus:
            word = word.upper()
            if len(word) < 2:
                continue
            
            # 1-gram (частоты букв)
            for letter in word:
                self.ngrams_1[letter][letter] += 1
            
            # 2-gram (пары букв)
            for i in range(len(word) - 1):
                self.ngrams_2[word[i]][word[i+1]] += 1
            
            # 3-gram (тройки букв)
            for i in range(len(word) - 2):
                context = word[i:i+2]
                self.ngrams_3[context][word[i+2]] += 1
            
            # 4-gram (четвёрки букв)
            for i in range(len(word) - 3):
                context = word[i:i+3]
                self.ngrams_4[context][word[i+3]] += 1
        
        # Нормализация
        for ngram in [self.ngrams_1, self.ngrams_2, self.ngrams_3, self.ngrams_4]:
            for key in ngram:
                total = sum(ngram[key].values())
                for subkey in ngram[key]:
                    ngram[key][subkey] /= total
    
    def _get_weighted_letter(self):
        """Возвращает букву с учётом частоты"""
        letters = list(self.letter_freq.keys())
        weights = list(self.letter_freq.values())
        return random.choices(letters, weights=weights, k=1)[0]
    
    def _get_next_char(self, context, order):
        """Предсказывает следующую букву на основе контекста"""
        if order == 1:
            ngram = self.ngrams_1
        elif order == 2:
            ngram = self.ngrams_2
        elif order == 3:
            ngram = self.ngrams_3
        else:
            ngram = self.ngrams_4
        
        if context in ngram and ngram[context]:
            chars = list(ngram[context].keys())
            weights = list(ngram[context].values())
            return random.choices(chars, weights=weights, k=1)[0]
        return None
    
    def _is_readable(self, word):
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
        
        # Проверка на мягкий знак (русский)
        if self.lang == "ru":
            for i in range(len(word) - 1):
                if word[i+1] == self.soft_sign:
                    if word[i] not in self.consonants:
                        return False
                if word[i+1] == self.hard_sign:
                    if i == 0 or word[i-1] not in self.consonants:
                        return False
        
        return True
    
    def generate_word(self, min_len=3, max_len=8):
        """Генерирует новое слово на основе обученных данных"""
        max_attempts = 100
        
        for _ in range(max_attempts):
            length = random.randint(min_len, max_len)
            word = []
            
            # Начинаем с частотной буквы
            word.append(self._get_weighted_letter())
            
            for i in range(1, length):
                r = random.random()
                
                # Выбираем порядок n-граммы (чем больше, тем реалистичнее)
                if r < 0.5 and i >= 3:
                    context = ''.join(word[-3:])
                    next_char = self._get_next_char(context, 4)
                elif r < 0.7 and i >= 2:
                    context = ''.join(word[-2:])
                    next_char = self._get_next_char(context, 3)
                elif r < 0.85 and i >= 1:
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
        
        # Если не получилось, возвращаем реальное слово из корпуса
        return random.choice(self.corpus)

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
    """Логирует действия администратора"""
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
            'inventory': {
                'hint': 0,
                'reroll': 0,
                'shield': 0,
                'double': 0
            },
            'blocked': False,
            'gift_limit_today': 0,
            'last_gift_date': None
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

def add_win(user_id, difficulty):
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
    
    prizes = [
        {"name": "30 кристаллов", "crystals": 30, "type": "crystals", "weight": 15},
        {"name": "50 кристаллов", "crystals": 50, "type": "crystals", "weight": 15},
        {"name": "100 кристаллов", "crystals": 100, "type": "crystals", "weight": 12},
        {"name": "200 кристаллов", "crystals": 200, "type": "crystals", "weight": 10},
        {"name": "500 кристаллов", "crystals": 500, "type": "crystals", "weight": 8},
        {"name": "1000 кристаллов", "crystals": 1000, "type": "crystals", "weight": 5},
        {"name": "Подсказка", "crystals": 0, "type": "item", "item": "hint", "weight": 10},
        {"name": "Сменить слово", "crystals": 0, "type": "item", "item": "reroll", "weight": 8},
        {"name": "Защита", "crystals": 0, "type": "item", "item": "shield", "weight": 7},
        {"name": "Кристалл x2", "crystals": 0, "type": "item", "item": "double", "weight": 5},
        {"name": "0 кристаллов", "crystals": 0, "type": "crystals", "weight": 5}
    ]
    
    total_weight = sum(p["weight"] for p in prizes)
    r = random.randint(1, total_weight)
    cumulative = 0
    prize = None
    
    for p in prizes:
        cumulative += p["weight"]
        if r <= cumulative:
            prize = p
            break
    
    if prize["type"] == "crystals":
        user['crystals'] += prize["crystals"]
        update_user(user_id, user)
        return prize["crystals"], price
    else:
        user['inventory'][prize["item"]] = user['inventory'].get(prize["item"], 0) + 1
        update_user(user_id, user)
        return prize["name"], price

def play_casino(user_id, game_type, bet, choice=None):
    user = get_user(user_id)
    game = CASINO_GAMES[game_type]
    
    if user['crystals'] < bet:
        return None, f"❌ Не хватает кристаллов! Нужно {bet}💎"
    
    user['crystals'] -= bet
    update_user(user_id, user)
    
    if game_type == "coin":
        result = random.choice(["Орёл", "Решка"])
        if choice == result:
            win = bet * game["multiplier"]
            user['crystals'] += win
            update_user(user_id, user)
            return win, f"🎉 ПОБЕДА! 🎉\n\n🪙 Выпал: {result}\n💰 Ваша ставка: {bet}💎\n🏆 Вы выиграли: {win}💎\n\n💰 Новый баланс: {user['crystals']}💎"
        else:
            update_user(user_id, user)
            return 0, f"😢 ПОРАЖЕНИЕ! 😢\n\n🪙 Выпал: {result}\n💰 Ваша ставка: {bet}💎\n💸 Вы проиграли: {bet}💎\n\n💰 Новый баланс: {user['crystals']}💎"
    
    elif game_type == "dice":
        result = random.randint(1, 6)
        if choice == result:
            win = bet * game["multiplier"]
            user['crystals'] += win
            update_user(user_id, user)
            return win, f"🎉 ПОБЕДА! 🎉\n\n🎲 Выпало число: {result}\n💰 Ваша ставка: {bet}💎\n🏆 Вы выиграли: {win}💎\n\n💰 Новый баланс: {user['crystals']}💎"
        else:
            update_user(user_id, user)
            return 0, f"😢 ПОРАЖЕНИЕ! 😢\n\n🎲 Выпало число: {result}\n💰 Ваша ставка: {bet}💎\n💸 Вы проиграли: {bet}💎\n\n💰 Новый баланс: {user['crystals']}💎"
    
    elif game_type == "slot":
        symbols = ["🍒", "🍋", "🔔", "💎", "7️⃣"]
        slot1 = random.choice(symbols)
        slot2 = random.choice(symbols)
        slot3 = random.choice(symbols)
        
        result = f"{slot1} {slot2} {slot3}"
        
        if slot1 == slot2 == slot3:
            win = bet * game["multiplier"]
            if slot1 == "7️⃣":
                win = bet * 10  # Супер-джекпот для 7️⃣
            user['crystals'] += win
            update_user(user_id, user)
            return win, f"🎉 ДЖЕКПОТ! 🎉\n\n🎰 {result}\n💰 Ваша ставка: {bet}💎\n🏆 Вы выиграли: {win}💎\n\n💰 Новый баланс: {user['crystals']}💎"
        else:
            update_user(user_id, user)
            return 0, f"😢 ПОРАЖЕНИЕ! 😢\n\n🎰 {result}\n💰 Ваша ставка: {bet}💎\n💸 Вы проиграли: {bet}💎\n\n💰 Новый баланс: {user['crystals']}💎"
    
    elif game_type == "blackjack":
        player = random.randint(1, 21)
        dealer = random.randint(1, 21)
        
        if player > 21:
            player = 21 - (player - 21)
        if dealer > 21:
            dealer = 21 - (dealer - 21)
        
        if player > dealer:
            win = bet * game["multiplier"]
            user['crystals'] += win
            update_user(user_id, user)
            return win, f"🎉 ПОБЕДА! 🎉\n\n🃏 Ваши карты: {player}\n🃏 Карты дилера: {dealer}\n💰 Ваша ставка: {bet}💎\n🏆 Вы выиграли: {win}💎\n\n💰 Новый баланс: {user['crystals']}💎"
        elif player == dealer:
            user['crystals'] += bet
            update_user(user_id, user)
            return bet, f"🤝 НИЧЬЯ! 🤝\n\n🃏 Ваши карты: {player}\n🃏 Карты дилера: {dealer}\n💰 Ваша ставка возвращена: {bet}💎\n\n💰 Новый баланс: {user['crystals']}💎"
        else:
            update_user(user_id, user)
            return 0, f"😢 ПОРАЖЕНИЕ! 😢\n\n🃏 Ваши карты: {player}\n🃏 Карты дилера: {dealer}\n💰 Ваша ставка: {bet}💎\n💸 Вы проиграли: {bet}💎\n\n💰 Новый баланс: {user['crystals']}💎"

def send_gift(from_user_id, to_user_id, amount):
    """Отправляет подарок"""
    settings = load_settings()
    gift_settings = settings.get("gift_settings", {
        "enabled": True,
        "min_amount": 10,
        "max_amount": 1000,
        "daily_limit": 10
    })
    
    if not gift_settings["enabled"]:
        return False, "❌ Подарки временно отключены"
    
    if amount < gift_settings["min_amount"] or amount > gift_settings["max_amount"]:
        return False, f"❌ Сумма должна быть от {gift_settings['min_amount']} до {gift_settings['max_amount']}💎"
    
    from_user = get_user(from_user_id)
    
    # Проверка дневного лимита
    today = datetime.now().date().isoformat()
    if from_user.get('last_gift_date') != today:
        from_user['gift_limit_today'] = 0
        from_user['last_gift_date'] = today
    
    if from_user['gift_limit_today'] >= gift_settings["daily_limit"]:
        return False, f"❌ Вы достигли лимита подарков на сегодня ({gift_settings['daily_limit']})"
    
    if from_user['crystals'] < amount:
        return False, f"❌ Не хватает кристаллов! Нужно {amount}💎"
    
    from_user['crystals'] -= amount
    from_user['gift_limit_today'] += 1
    update_user(from_user_id, from_user)
    
    to_user = get_user(to_user_id)
    to_user['crystals'] += amount
    update_user(to_user_id, to_user)
    
    return True, f"✅ Подарок отправлен!\n\n👤 Получатель: {to_user.get('username', to_user_id)}\n🎁 Сумма: {amount}💎"

def get_word(lang, difficulty):
    """Генерирует слово с помощью нейросети"""
    neural = neural_networks[lang]
    diff = DIFFICULTY[difficulty]
    return neural.generate_word(diff["min_len"], diff["max_len"])

# ========== НЕЙРОСЕТИ ==========
neural_networks = {
    "ru": MegaNeuralNetwork("ru"),
    "en": MegaNeuralNetwork("en")
}

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
        display = []
        for letter in self.word:
            if letter in self.guessed_letters:
                display.append(letter)
            else:
                display.append("_")
        return " ".join(display)
    
    def get_game_text(self, message=""):
        reward = DIFFICULTY[self.difficulty]["reward"]
        display = self.get_display_word()
        wrong = ", ".join(self.wrong_letters) if self.wrong_letters else "—"
        
        text = f"""<b>🎮 УГАДАЙ СЛОВО</b>
<i>Общая игра в чате</i>

<b>📖 Слово:</b> {display}
<b>💎 За победу:</b> +{reward}
<b>❌ Ошибки:</b> {wrong}

{message}

<i>✍️ Введите букву или слово:</i>"""
        return text
    
    def guess_letter(self, letter, user_id, username):
        letter = letter.upper()
        reward = DIFFICULTY[self.difficulty]["reward"]
        
        if len(letter) > 1:
            if letter == self.word:
                final_reward = reward
                if self.effects.get("double"):
                    final_reward *= 2
                add_crystals(user_id, final_reward)
                add_win(user_id, self.difficulty)
                self.active = False
                return True, f"<b>🏆 ПОБЕДА! 🏆</b>\n\n📖 Слово: {self.word}\n💎 +{final_reward}\n\n👤 Победитель: {username}"
            return False, f"<b>❌ Неправильно!</b> Попробуйте снова."
        
        if letter in self.guessed_letters or letter in self.wrong_letters:
            return False, f"<b>⚠️ Эта буква уже называлась</b>"
        
        if letter in self.word:
            self.guessed_letters.append(letter)
            
            if all(l in self.guessed_letters for l in self.word):
                final_reward = reward
                if self.effects.get("double"):
                    final_reward *= 2
                add_crystals(user_id, final_reward)
                add_win(user_id, self.difficulty)
                self.active = False
                return True, f"<b>🏆 ПОБЕДА! 🏆</b>\n\n📖 Слово: {self.word}\n💎 +{final_reward}\n\n👤 Победитель: {username}"
            
            return True, f"<b>✅ Есть такая буква!</b>"
        else:
            self.wrong_letters.append(letter)
            return False, f"<b>❌ Нет такой буквы!</b>"
    
    def use_hint(self, user_id):
        """Подсказка — может купить любой игрок"""
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
        else:
            return f"<b>❌ У вас нет подсказок! Купите в магазине.</b>"
    
    def reroll_word(self, user_id):
        """Сменить слово — только создатель игры"""
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
        else:
            return f"<b>❌ У вас нет предмета «Сменить слово»! Купите в магазине.</b>"
    
    def use_shield(self, user_id):
        """Защита — можно купить в магазине"""
        user = get_user(user_id)
        if user['inventory'].get('shield', 0) > 0:
            user['inventory']['shield'] -= 1
            update_user(user_id, user)
            self.effects['shield'] = True
            return f"<b>🛡️ Защита активирована! При поражении вы не потеряете серию.</b>"
        else:
            return f"<b>❌ У вас нет защиты! Купите в магазине.</b>"
    
    def use_double(self, user_id):
        """Удвоение кристаллов — можно купить в магазине"""
        user = get_user(user_id)
        if user['inventory'].get('double', 0) > 0:
            user['inventory']['double'] -= 1
            update_user(user_id, user)
            self.effects['double'] = True
            return f"<b>⚡ Кристалл x2 активирован! Следующая победа принесёт вдвое больше кристаллов.</b>"
        else:
            return f"<b>❌ У вас нет кристалла x2! Купите в магазине.</b>"

# ========== КАЗИНО СЕССИИ ==========
class CasinoSession:
    def __init__(self, user_id, chat_id, message_id):
        self.user_id = user_id
        self.chat_id = chat_id
        self.message_id = message_id
        self.game = None
        self.bet = None
        self.state = "menu"  # menu, game, bet
    
    def get_menu_text(self):
        user = get_user(self.user_id)
        return f"""<b>🎰 КАЗИНО</b>

💰 Ваш баланс: {user['crystals']}💎

Выберите игру:

🪙 <b>Орёл/Решка</b> — угадай сторону (x2)
🎲 <b>Кости</b> — угадай число 1-6 (x6)
🎰 <b>Слоты</b> — собери 3 одинаковых (x5, за 7️⃣ x10)
🃏 <b>Блэкджек</b> — обыграй дилера (x2)"""
    
    def get_bet_text(self):
        user = get_user(self.user_id)
        game_names = {
            "coin": "🪙 Орёл/Решка",
            "dice": "🎲 Кости",
            "slot": "🎰 Слоты",
            "blackjack": "🃏 Блэкджек"
        }
        return f"""<b>{game_names[self.game]}</b>

💰 Ваш баланс: {user['crystals']}💎

Введите сумму ставки (от 10 до 1000💎):

10💎 | 50💎 | 100💎 | 250💎 | 500💎 | 1000💎"""
    
    def get_game_text(self):
        if self.game == "coin":
            return f"""<b>🪙 Орёл/Решка</b>

💰 Ваша ставка: {self.bet}💎

Выберите сторону:"""
        elif self.game == "dice":
            return f"""<b>🎲 Кости</b>

💰 Ваша ставка: {self.bet}💎

Выберите число от 1 до 6:"""
        elif self.game == "slot":
            return f"""<b>🎰 Слоты</b>

💰 Ваша ставка: {self.bet}💎

🌀 Нажмите «Крутить», чтобы начать!"""
        elif self.game == "blackjack":
            return f"""<b>🃏 Блэкджек</b>

💰 Ваша ставка: {self.bet}💎

🌀 Нажмите «Играть», чтобы начать!"""
        return ""

# ========== ТЕКСТЫ ==========
TEXTS = {
    "ru": {
        "game_title": "🎮 УГАДАЙ СЛОВО",
        "your_game": "👤 Ваша игра",
        "word": "📖 Слово: {display}",
        "reward": "💎 За победу: +{reward}",
        "enter": "\n\n✍️ Введите букву или слово:",
        "win": "🏆 ПОБЕДА! 🏆\n\n📖 Слово: {word}\n💎 +{reward}\n\nПобедитель: {winner}",
        "lose": "💀 ПОРАЖЕНИЕ! 💀\n\n📖 Слово: {word}",
        "wrong_word": "❌ Неправильно! Попробуйте снова.",
        "yes_letter": "✅ Есть такая буква!",
        "no_letter": "❌ Нет такой буквы!",
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
        "donate_title": "⭐ ПОДДЕРЖАТЬ ПРОЕКТ",
        "donate_stars_title": "TELEGRAM STARS",
        "donate_desc": "✨ 1 Star = 50 кристаллов + бонусы!",
        "donate_stars_1": "1 Star → 50 +0",
        "donate_stars_2": "2 Stars → 100 +10",
        "donate_stars_5": "5 Stars → 250 +30",
        "donate_stars_10": "10 Stars → 500 +75",
        "donate_stars_20": "20 Stars → 1000 +200",
        "donate_stars_50": "50 Stars → 2500 +750",
        "donate_stars_100": "100 Stars → 5000 +2000",
        "donate_stars_150": "150 Stars → 7500 +3750",
        "donate_stars_200": "200 Stars → 10000 +6000",
        "donate_stars_250": "250 Stars → 12500 +8750",
        "donate_stars_300": "300 Stars → 15000 +12000",
        "donate_stars_400": "400 Stars → 20000 +18000",
        "donate_stars_500": "500 Stars → 25000 +25000",
        "donate_stars_750": "750 Stars → 37500 +41250",
        "donate_stars_1000": "1000 Stars → 50000 +60000",
        "donate_back": "◀️ Назад",
        "daily_title": "🎁 ЕЖЕДНЕВНЫЙ БОНУС",
        "daily_reward": "🎉 Вы получили {crystals} кристаллов!",
        "daily_already": "⏰ Вы уже получали бонус сегодня! Приходите завтра.",
        "daily_streak": "🔥 Серия: {streak} дней!",
        "wheel_title": "🎡 КОЛЕСО ФОРТУНЫ",
        "wheel_price": "💎 Стоимость вращения: {price}",
        "wheel_win": "🎉 ПОЗДРАВЛЯЕМ! 🎉\n\n💰 Вы выиграли {prize}!",
        "wheel_no_money": "❌ Не хватает кристаллов! Нужно {price}",
        "casino_title": "🎰 КАЗИНО",
        "casino_games": "🎲 Выбери игру:",
        "casino_coin": "🪙 Орёл/Решка — выбери сторону (x2)",
        "casino_dice": "🎲 Кости — угадай число 1-6 (x6)",
        "casino_slot": "🎰 Слоты — собери 3 одинаковых (x5, за 7️⃣ x10)",
        "casino_blackjack": "🃏 Блэкджек — обыграй дилера (x2)",
        "casino_back": "◀️ Назад",
        "inventory_title": "📦 ИНВЕНТАРЬ",
        "inventory_empty": "📦 У вас нет предметов.\n\nКупить их можно в магазине: /shop",
        "inventory_hint": "🔍 Подсказка: {count} шт.",
        "inventory_reroll": "🔄 Сменить слово: {count} шт.",
        "inventory_shield": "🛡️ Защита: {count} шт.",
        "inventory_double": "💎 Кристалл x2: {count} шт.",
        "gift_title": "🎁 ПОДАРКИ",
        "gift_select_user": "🎁 Выберите друга:",
        "gift_amount": "🎁 Введите сумму подарка (от {min} до {max}💎):",
        "gift_sent": "✅ Подарок отправлен!\n\n👤 Получатель: {to}\n🎁 Сумма: {amount}💎",
        "gift_received": "🎁 ВАМ ПОДАРОК!\n\n👤 От: {from}\n🎁 Сумма: {amount}💎\n💰 Ваш новый баланс: {balance}💎",
        "gift_no_users": "❌ Нет других пользователей",
        "gift_limit_reached": "❌ Вы достигли лимита подарков на сегодня",
        "lang_title": "🌐 ВЫБЕРИ ЯЗЫК",
        "lang_ru": "🇷🇺 Русский",
        "lang_en": "🇬🇧 English",
        "help_title": "❓ ПОМОЩЬ",
        "help_text": """<b>📚 ПОМОЩЬ</b>

<b>🎮 КАК ИГРАТЬ:</b>

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

<b>🛒 МАГАЗИН ПРЕДМЕТОВ:</b>
🔍 Подсказка — 50💎
🔄 Сменить слово — 100💎
🛡️ Защита — 150💎
💎 Кристалл x2 — 500💎

<b>🎁 ПОДАРКИ:</b>
/donate — поддержать проект
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
        "your_game": "👤 Your game",
        "word": "📖 Word: {display}",
        "reward": "💎 Reward: +{reward}",
        "enter": "\n\n✍️ Enter a letter or word:",
        "win": "🏆 VICTORY! 🏆\n\n📖 Word: {word}\n💎 +{reward}\n\nWinner: {winner}",
        "lose": "💀 DEFEAT! 💀\n\n📖 Word: {word}",
        "wrong_word": "❌ Wrong! Try again.",
        "yes_letter": "✅ Letter found!",
        "no_letter": "❌ Letter not found!",
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
        "donate_title": "⭐ SUPPORT THE PROJECT",
        "donate_stars_title": "TELEGRAM STARS",
        "donate_desc": "✨ 1 Star = 50 crystals + bonuses!",
        "donate_stars_1": "1 Star → 50 +0",
        "donate_stars_2": "2 Stars → 100 +10",
        "donate_stars_5": "5 Stars → 250 +30",
        "donate_stars_10": "10 Stars → 500 +75",
        "donate_stars_20": "20 Stars → 1000 +200",
        "donate_stars_50": "50 Stars → 2500 +750",
        "donate_stars_100": "100 Stars → 5000 +2000",
        "donate_stars_150": "150 Stars → 7500 +3750",
        "donate_stars_200": "200 Stars → 10000 +6000",
        "donate_stars_250": "250 Stars → 12500 +8750",
        "donate_stars_300": "300 Stars → 15000 +12000",
        "donate_stars_400": "400 Stars → 20000 +18000",
        "donate_stars_500": "500 Stars → 25000 +25000",
        "donate_stars_750": "750 Stars → 37500 +41250",
        "donate_stars_1000": "1000 Stars → 50000 +60000",
        "donate_back": "◀️ Back",
        "daily_title": "🎁 DAILY BONUS",
        "daily_reward": "🎉 You received {crystals} crystals!",
        "daily_already": "⏰ You already received today's bonus! Come back tomorrow.",
        "daily_streak": "🔥 Streak: {streak} days!",
        "wheel_title": "🎡 WHEEL OF FORTUNE",
        "wheel_price": "💎 Spin cost: {price}",
        "wheel_win": "🎉 CONGRATULATIONS! 🎉\n\n💰 You won {prize}!",
        "wheel_no_money": "❌ Not enough crystals! Need {price}",
        "casino_title": "🎰 CASINO",
        "casino_games": "🎲 Choose a game:",
        "casino_coin": "🪙 Heads/Tails — choose side (x2)",
        "casino_dice": "🎲 Dice — guess number 1-6 (x6)",
        "casino_slot": "🎰 Slots — match 3 symbols (x5, for 7️⃣ x10)",
        "casino_blackjack": "🃏 Blackjack — beat the dealer (x2)",
        "casino_back": "◀️ Back",
        "inventory_title": "📦 INVENTORY",
        "inventory_empty": "📦 You have no items.\n\nBuy them in the shop: /shop",
        "inventory_hint": "🔍 Hint: {count} pcs.",
        "inventory_reroll": "🔄 Change word: {count} pcs.",
        "inventory_shield": "🛡️ Shield: {count} pcs.",
        "inventory_double": "💎 Crystal x2: {count} pcs.",
        "gift_title": "🎁 GIFTS",
        "gift_select_user": "🎁 Select a friend:",
        "gift_amount": "🎁 Enter gift amount (from {min} to {max}💎):",
        "gift_sent": "✅ Gift sent!\n\n👤 Recipient: {to}\n🎁 Amount: {amount}💎",
        "gift_received": "🎁 YOU GOT A GIFT!\n\n👤 From: {from}\n🎁 Amount: {amount}💎\n💰 Your new balance: {balance}💎",
        "gift_no_users": "❌ No other users",
        "gift_limit_reached": "❌ You have reached the daily gift limit",
        "lang_title": "🌐 CHOOSE LANGUAGE",
        "lang_ru": "🇷🇺 Russian",
        "lang_en": "🇬🇧 English",
        "help_title": "❓ HELP",
        "help_text": """<b>📚 HELP</b>

<b>🎮 HOW TO PLAY:</b>

1️⃣ Press <i>«Start Game»</i> and choose difficulty
2️⃣ A word appears in chat <code>_ _ _ _</code>
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
/donate — support the project
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

# ========== НАСТРОЙКИ ==========
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except:
        pass

# ========== КЛАВИАТУРЫ ==========
def get_user_lang(user_id):
    user = get_user(user_id)
    return user.get('lang', 'ru')

def main_menu_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]["buttons"]
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton(texts["start"], callback_data="start_game"),
        types.InlineKeyboardButton(texts["casino"], callback_data="casino"),
        types.InlineKeyboardButton(texts["shop"], callback_data="shop"),
        types.InlineKeyboardButton(texts["top"], callback_data="top"),
        types.InlineKeyboardButton(texts["stats"], callback_data="stats"),
        types.InlineKeyboardButton(texts["daily"], callback_data="daily"),
        types.InlineKeyboardButton(texts["more"], callback_data="more_menu")
    )
    return markup

def more_menu_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]["buttons"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(texts["wheel"], callback_data="wheel"),
        types.InlineKeyboardButton(texts["lang"], callback_data="lang"),
        types.InlineKeyboardButton(texts["promo"], callback_data="promo"),
        types.InlineKeyboardButton(texts["gift"], callback_data="gift"),
        types.InlineKeyboardButton(texts["inventory"], callback_data="inventory"),
        types.InlineKeyboardButton(texts["donate"], callback_data="donate"),
        types.InlineKeyboardButton(texts["help"], callback_data="help"),
        types.InlineKeyboardButton(texts["back"], callback_data="back_to_main")
    )
    return markup

def difficulty_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]["buttons"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(texts["easy"], callback_data="difficulty_easy"),
        types.InlineKeyboardButton(texts["medium"], callback_data="difficulty_medium"),
        types.InlineKeyboardButton(texts["hard"], callback_data="difficulty_hard"),
        types.InlineKeyboardButton(texts["back"], callback_data="back_to_main")
    )
    return markup

def casino_menu_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(texts["casino_coin"], callback_data="casino_coin"),
        types.InlineKeyboardButton(texts["casino_dice"], callback_data="casino_dice"),
        types.InlineKeyboardButton(texts["casino_slot"], callback_data="casino_slot"),
        types.InlineKeyboardButton(texts["casino_blackjack"], callback_data="casino_blackjack"),
        types.InlineKeyboardButton(texts["casino_back"], callback_data="back_to_main")
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
        types.InlineKeyboardButton("◀️ Назад", callback_data="casino_back")
    )
    return markup

def casino_coin_kb():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🪙 Орёл", callback_data="casino_choice_Орёл"),
        types.InlineKeyboardButton("🪙 Решка", callback_data="casino_choice_Решка"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="casino_back")
    )
    return markup

def casino_dice_kb():
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    for i in range(1, 7):
        buttons.append(types.InlineKeyboardButton(str(i), callback_data=f"casino_choice_{i}"))
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="casino_back"))
    return markup

def casino_slot_kb():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🌀 Крутить", callback_data="casino_slot_spin"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="casino_back")
    )
    return markup

def casino_blackjack_kb():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎲 Играть", callback_data="casino_blackjack_play"),
        types.InlineKeyboardButton("◀️ Назад", callback_data="casino_back")
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
    markup.add(
        types.InlineKeyboardButton(texts["buttons"]["back"], callback_data="back_to_main")
    )
    return markup

def daily_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(texts["buttons"]["back"], callback_data="back_to_main")
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
    markup.add(
        types.InlineKeyboardButton(texts["buttons"]["back"], callback_data="back_to_main")
    )
    return markup

def gift_kb(user_id, page=0):
    users = load_json(USERS_FILE)
    user_list = []
    for uid, u in users.items():
        if int(uid) != user_id:
            user_list.append((uid, u.get('username', f"User_{uid}")))
    
    if not user_list:
        return None
    
    per_page = 10
    start = page * per_page
    end = start + per_page
    page_users = user_list[start:end]
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for uid, username in page_users:
        markup.add(types.InlineKeyboardButton(f"👤 {username}", callback_data=f"gift_user_{uid}"))
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton("⬅️", callback_data=f"gift_page_{page-1}"))
    if end < len(user_list):
        nav_buttons.append(types.InlineKeyboardButton("➡️", callback_data=f"gift_page_{page+1}"))
    if nav_buttons:
        markup.add(*nav_buttons)
    
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
    return markup

def inventory_kb(user_id):
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(texts["buttons"]["back"], callback_data="back_to_main")
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
        types.InlineKeyboardButton(texts["donate_stars_100"], callback_data="donate_100"),
        types.InlineKeyboardButton(texts["donate_stars_150"], callback_data="donate_150"),
        types.InlineKeyboardButton(texts["donate_stars_200"], callback_data="donate_200"),
        types.InlineKeyboardButton(texts["donate_stars_250"], callback_data="donate_250"),
        types.InlineKeyboardButton(texts["donate_stars_300"], callback_data="donate_300"),
        types.InlineKeyboardButton(texts["donate_stars_400"], callback_data="donate_400"),
        types.InlineKeyboardButton(texts["donate_stars_500"], callback_data="donate_500"),
        types.InlineKeyboardButton(texts["donate_stars_750"], callback_data="donate_750"),
        types.InlineKeyboardButton(texts["donate_stars_1000"], callback_data="donate_1000"),
        types.InlineKeyboardButton(texts["donate_back"], callback_data="donate")
    )
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

def send_with_image(chat_id, image_key, text, reply_markup=None):
    image_url = IMAGES.get(image_key)
    if image_url:
        try:
            bot.send_photo(chat_id=chat_id, photo=image_url, caption=text, reply_markup=reply_markup, parse_mode="HTML")
        except:
            bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode="HTML")

def edit_with_image(chat_id, message_id, image_key, text, reply_markup=None):
    image_url = IMAGES.get(image_key)
    if image_url:
        try:
            bot.edit_message_media(media=types.InputMediaPhoto(media=image_url, caption=text, parse_mode="HTML"), chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
        except:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup, parse_mode="HTML")
    else:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup, parse_mode="HTML")

# ========== КОМАНДЫ ==========
active_games = {}  # chat_id -> Game
casino_sessions = {}  # user_id -> CasinoSession
gift_pages = {}  # user_id -> page
reset_confirm = {}  # user_id -> step

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
    top = []
    for uid, u in users.items():
        username = u.get('username', f"User_{uid}")
        top.append({'username': username, 'crystals': u.get('crystals', 0)})
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
    
    inventory = user.get('inventory', {})
    items = []
    
    if inventory.get('hint', 0) > 0:
        items.append(texts["inventory_hint"].format(count=inventory['hint']))
    if inventory.get('reroll', 0) > 0:
        items.append(texts["inventory_reroll"].format(count=inventory['reroll']))
    if inventory.get('shield', 0) > 0:
        items.append(texts["inventory_shield"].format(count=inventory['shield']))
    if inventory.get('double', 0) > 0:
        items.append(texts["inventory_double"].format(count=inventory['double']))
    
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

{texts["casino_games"]}"""
    
    send_with_image(message.chat.id, "casino", text, casino_menu_kb(user_id))

@bot.message_handler(commands=['gift'])
def gift_command(message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if len(args) >= 3:
        # Формат: /gift @username 100
        username = args[1].replace('@', '')
        try:
            amount = int(args[2])
        except:
            bot.reply_to(message, "❌ Неверная сумма")
            return
        
        # Ищем пользователя по username
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
        # Показываем выбор пользователя
        lang = get_user_lang(user_id)
        texts = TEXTS[lang]
        markup = gift_kb(user_id)
        if markup:
            send_with_image(message.chat.id, "inventory", f"<b>{texts['gift_title']}</b>\n\n{texts['gift_select_user']}", markup)
        else:
            bot.reply_to(message, texts['gift_no_users'])

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
    
    # Проверка срока действия
    if promo.get('expires'):
        expires = datetime.fromisoformat(promo['expires'])
        if datetime.now() > expires:
            bot.reply_to(message, "❌ Промокод истёк")
            return
    
    # Проверка лимита использований
    if promo.get('uses', 0) >= promo.get('max_uses', float('inf')):
        bot.reply_to(message, "❌ Промокод больше не активен")
        return
    
    # Проверка, использовал ли пользователь
    if user_id in promo.get('used_by', []):
        bot.reply_to(message, "❌ Вы уже использовали этот промокод")
        return
    
    # Активация
    add_crystals(user_id, promo['crystals'])
    
    if 'used_by' not in promo:
        promo['used_by'] = []
    promo['used_by'].append(user_id)
    promo['uses'] = promo.get('uses', 0) + 1
    promos[code] = promo
    save_json(PROMO_FILE, promos)
    
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

{texts["donate_desc"]}"""
    send_with_image(message.chat.id, "donate", text, donate_kb(user_id))

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    texts = TEXTS[lang]
    
    text = texts["help_text"]
    bot.send_message(message.chat.id, text, parse_mode="HTML")

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
    
    # Проверяем, есть ли активная игра в этом чате
    if chat_id in active_games and active_games[chat_id].active:
        game = active_games[chat_id]
        guess_text = message.text.strip()
        
        if guess_text:
            username = message.from_user.username or message.from_user.first_name
            result, msg = game.guess_letter(guess_text, user_id, username)
            
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
    
    # ========== ИГРОВЫЕ КНОПКИ ==========
    if data.startswith("use_hint_"):
        owner_id = int(data.split("_")[2])
        if user_id != owner_id:
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
        owner_id = int(data.split("_")[2])
        if user_id != owner_id:
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
        owner_id = int(data.split("_")[2])
        if user_id != owner_id:
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
        owner_id = int(data.split("_")[2])
        if user_id != owner_id:
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
        owner_id = int(data.split("_")[2])
        if user_id != owner_id:
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
    
    # ========== КОЛЕСО ФОРТУНЫ ==========
    elif data.startswith("wheel_spin_"):
        owner_id = int(data.split("_")[2])
        if user_id != owner_id:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return
        
        prize, price = spin_wheel(user_id)
        
        if prize is None:
            text = f"""<b>{texts["wheel_title"]}</b>

{texts["wheel_no_money"].format(price=price)}"""
        else:
            if isinstance(prize, int):
                text = f"""<b>{texts["wheel_title"]}</b>

{texts["wheel_win"].format(prize=f"{prize} кристаллов")}"""
            else:
                text = f"""<b>{texts["wheel_title"]}</b>

{texts["wheel_win"].format(prize=prize)}"""
        
        bot.send_message(chat_id, text, parse_mode="HTML")
        bot.answer_callback_query(call.id)
        
        # Возвращаем в меню колеса
        wheel_text = f"""<b>{texts["wheel_title"]}</b>

{texts["wheel_price"].format(price=50)}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "wheel", wheel_text, wheel_kb(user_id))
        return
    
    # ========== КАЗИНО ==========
    elif data == "casino":
        sent = bot.send_message(chat_id, "🎰 Загрузка казино...")
        casino = CasinoSession(user_id, chat_id, sent.message_id)
        casino_sessions[user_id] = casino
        text = casino.get_menu_text()
        bot.edit_message_text(text, chat_id, sent.message_id, reply_markup=casino_menu_kb(user_id), parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return
    
    elif data == "casino_back":
        if user_id in casino_sessions:
            del casino_sessions[user_id]
        text = f"""<b>{texts["casino_title"]}</b>

{texts["casino_games"]}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "casino", text, casino_menu_kb(user_id))
        bot.answer_callback_query(call.id)
        return
    
    elif data in ["casino_coin", "casino_dice", "casino_slot", "casino_blackjack"]:
        game_type = data.split("_")[1]
        if user_id not in casino_sessions:
            bot.answer_callback_query(call.id, "❌ Сессия не найдена", show_alert=True)
            return
        casino = casino_sessions[user_id]
        casino.game = game_type
        casino.state = "bet"
        text = casino.get_bet_text()
        bot.edit_message_text(text, casino.chat_id, casino.message_id, reply_markup=casino_bet_kb(), parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return
    
    elif data.startswith("casino_bet_"):
        bet = int(data.split("_")[2])
        if user_id not in casino_sessions:
            bot.answer_callback_query(call.id, "❌ Сессия не найдена", show_alert=True)
            return
        casino = casino_sessions[user_id]
        casino.bet = bet
        casino.state = "game"
        
        if casino.game == "coin":
            text = casino.get_game_text()
            bot.edit_message_text(text, casino.chat_id, casino.message_id, reply_markup=casino_coin_kb(), parse_mode="HTML")
        elif casino.game == "dice":
            text = casino.get_game_text()
            bot.edit_message_text(text, casino.chat_id, casino.message_id, reply_markup=casino_dice_kb(), parse_mode="HTML")
        elif casino.game == "slot":
            text = casino.get_game_text()
            bot.edit_message_text(text, casino.chat_id, casino.message_id, reply_markup=casino_slot_kb(), parse_mode="HTML")
        elif casino.game == "blackjack":
            text = casino.get_game_text()
            bot.edit_message_text(text, casino.chat_id, casino.message_id, reply_markup=casino_blackjack_kb(), parse_mode="HTML")
        
        bot.answer_callback_query(call.id)
        return
    
    elif data.startswith("casino_choice_"):
        choice = data.split("_")[2]
        if user_id not in casino_sessions:
            bot.answer_callback_query(call.id, "❌ Сессия не найдена", show_alert=True)
            return
        casino = casino_sessions[user_id]
        
        if casino.game == "coin":
            if choice in ["Орёл", "Решка"]:
                win, result_text = play_casino(user_id, "coin", casino.bet, choice)
            else:
                bot.answer_callback_query(call.id, "❌ Неверный выбор", show_alert=True)
                return
        elif casino.game == "dice":
            try:
                num = int(choice)
                if 1 <= num <= 6:
                    win, result_text = play_casino(user_id, "dice", casino.bet, num)
                else:
                    bot.answer_callback_query(call.id, "❌ Число от 1 до 6", show_alert=True)
                    return
            except:
                bot.answer_callback_query(call.id, "❌ Неверный выбор", show_alert=True)
                return
        else:
            bot.answer_callback_query(call.id, "❌ Неизвестная игра", show_alert=True)
            return
        
        bot.send_message(chat_id, result_text, parse_mode="HTML")
        bot.answer_callback_query(call.id)
        
        # Возвращаем в меню казино
        del casino_sessions[user_id]
        text = f"""<b>{texts["casino_title"]}</b>

{texts["casino_games"]}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "casino", text, casino_menu_kb(user_id))
        return
    
    elif data == "casino_slot_spin":
        if user_id not in casino_sessions:
            bot.answer_callback_query(call.id, "❌ Сессия не найдена", show_alert=True)
            return
        casino = casino_sessions[user_id]
        
        # Визуальное вращение слотов
        symbols = ["🍒", "🍋", "🔔", "💎", "7️⃣"]
        
        for _ in range(5):
            slot1 = random.choice(symbols)
            slot2 = random.choice(symbols)
            slot3 = random.choice(symbols)
            spin_text = f"""<b>🎰 Слоты</b>

💰 Ваша ставка: {casino.bet}💎

🌀 КРУТИМ...

[ {slot1} {slot2} {slot3} ]"""
            bot.edit_message_text(spin_text, casino.chat_id, casino.message_id, parse_mode="HTML")
            time.sleep(0.3)
        
        win, result_text = play_casino(user_id, "slot", casino.bet)
        bot.send_message(chat_id, result_text, parse_mode="HTML")
        bot.answer_callback_query(call.id)
        
        del casino_sessions[user_id]
        text = f"""<b>{texts["casino_title"]}</b>

{texts["casino_games"]}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "casino", text, casino_menu_kb(user_id))
        return
    
    elif data == "casino_blackjack_play":
        if user_id not in casino_sessions:
            bot.answer_callback_query(call.id, "❌ Сессия не найдена", show_alert=True)
            return
        casino = casino_sessions[user_id]
        
        win, result_text = play_casino(user_id, "blackjack", casino.bet)
        bot.send_message(chat_id, result_text, parse_mode="HTML")
        bot.answer_callback_query(call.id)
        
        del casino_sessions[user_id]
        text = f"""<b>{texts["casino_title"]}</b>

{texts["casino_games"]}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "casino", text, casino_menu_kb(user_id))
        return
    
    # ========== ОСНОВНЫЕ КНОПКИ ==========
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
        difficulty = data.split("_")[1]
        
        if chat_id in active_games and active_games[chat_id].active:
            bot.answer_callback_query(call.id, "❌ В этом чате уже есть активная игра!", show_alert=True)
            return
        
        sent = bot.send_message(chat_id, "🎮 Генерация слова...")
        game = Game(chat_id, user_id, lang, sent.message_id, difficulty)
        active_games[chat_id] = game
        game_text = game.get_game_text("✨ Игра началась! Все могут угадывать!")
        bot.edit_message_text(game_text, game.chat_id, game.message_id, reply_markup=game_kb(user_id), parse_mode="HTML")
        bot.answer_callback_query(call.id)
    
    elif data == "shop":
        edit_with_image(call.message.chat.id, call.message.message_id, "shop", f"<b>{texts['shop_title']}</b>", shop_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data.startswith("buy_"):
        item_id = data[4:]
        prices = {"hint": 50, "reroll": 100, "shield": 150, "double": 500}
        if user['crystals'] < prices[item_id]:
            bot.answer_callback_query(call.id, f"❌ Не хватает! Нужно {prices[item_id]}💎", show_alert=True)
            return
        user['crystals'] -= prices[item_id]
        user['inventory'][item_id] = user['inventory'].get(item_id, 0) + 1
        update_user(user_id, user)
        bot.answer_callback_query(call.id, f"✅ Куплено! -{prices[item_id]}💎", show_alert=True)
        bot.send_message(chat_id, f"✅ Вы купили {texts[f'shop_{item_id}']} за {prices[item_id]}💎!", parse_mode="HTML")
        edit_with_image(call.message.chat.id, call.message.message_id, "shop", f"<b>{texts['shop_title']}</b>", shop_kb(user_id))
    
    elif data == "top":
        users = load_json(USERS_FILE)
        top = []
        for uid, u in users.items():
            username = u.get('username', f"User_{uid}")
            top.append({'username': username, 'crystals': u.get('crystals', 0)})
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
        text = f"""<b>🎫 ПРОМОКОДЫ</b>

Введите промокод командой:
/promo КОД

Пример: /promo WELCOME100"""
        edit_with_image(call.message.chat.id, call.message.message_id, "promo", text, promo_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "gift":
        markup = gift_kb(user_id)
        if markup:
            edit_with_image(call.message.chat.id, call.message.message_id, "inventory", f"<b>{texts['gift_title']}</b>\n\n{texts['gift_select_user']}", markup)
        else:
            bot.send_message(chat_id, texts['gift_no_users'])
        bot.answer_callback_query(call.id)
    
    elif data.startswith("gift_page_"):
        page = int(data.split("_")[2])
        gift_pages[user_id] = page
        markup = gift_kb(user_id, page)
        if markup:
            edit_with_image(call.message.chat.id, call.message.message_id, "inventory", f"<b>{texts['gift_title']}</b>\n\n{texts['gift_select_user']}", markup)
        bot.answer_callback_query(call.id)
    
    elif data.startswith("gift_user_"):
        target_id = int(data.split("_")[2])
        # Сохраняем в сессию
        bot.answer_callback_query(call.id)
        msg = bot.send_message(chat_id, texts["gift_amount"].format(min=10, max=1000))
        bot.register_next_step_handler(msg, lambda m: process_gift_amount(m, target_id))
    
    elif data == "inventory":
        inventory = user.get('inventory', {})
        items = []
        
        if inventory.get('hint', 0) > 0:
            items.append(texts["inventory_hint"].format(count=inventory['hint']))
        if inventory.get('reroll', 0) > 0:
            items.append(texts["inventory_reroll"].format(count=inventory['reroll']))
        if inventory.get('shield', 0) > 0:
            items.append(texts["inventory_shield"].format(count=inventory['shield']))
        if inventory.get('double', 0) > 0:
            items.append(texts["inventory_double"].format(count=inventory['double']))
        
        if items:
            text = f"<b>{texts['inventory_title']}</b>\n\n" + "\n".join(items)
        else:
            text = f"<b>{texts['inventory_title']}</b>\n\n{texts['inventory_empty']}"
        
        edit_with_image(call.message.chat.id, call.message.message_id, "inventory", text, inventory_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "donate":
        text = f"""<b>{texts["donate_title"]}</b>

{texts["donate_desc"]}"""
        edit_with_image(call.message.chat.id, call.message.message_id, "donate", text, donate_kb(user_id))
        bot.answer_callback_query(call.id)
    
    elif data == "donate_stars_menu":
        text = f"<b>{texts['donate_stars_title']}</b>\n\n{texts['donate_desc']}"
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
        elif stars == 100: bonus = 2000
        elif stars == 150: bonus = 3750
        elif stars == 200: bonus = 6000
        elif stars == 250: bonus = 8750
        elif stars == 300: bonus = 12000
        elif stars == 400: bonus = 18000
        elif stars == 500: bonus = 25000
        elif stars == 750: bonus = 41250
        elif stars == 1000: bonus = 60000
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
    
    elif data == "help":
        text = texts["help_text"]
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML")
        bot.answer_callback_query(call.id)
    
    # ========== АДМИН-ПАНЕЛЬ ==========
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
    
    elif data == "admin_reset":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Доступ запрещен")
            return
        
        step = reset_confirm.get(user_id, 0)
        
        if step == 0:
            reset_confirm[user_id] = 1
            text = """⚠️ ВНИМАНИЕ! ⚠️

Вы собираетесь СБРОСИТЬ статистику ВСЕХ пользователей.
Это действие НЕОБРАТИМО!

Все кристаллы, победы, серии будут обнулены.

Подтвердите, что вы уверены:

[✅ ДА, Я УВЕРЕН]  [❌ НЕТ, ОТМЕНА]"""
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("✅ ДА, Я УВЕРЕН", callback_data="admin_reset_confirm"),
                types.InlineKeyboardButton("❌ НЕТ, ОТМЕНА", callback_data="admin_reset_cancel")
            )
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id)
        
        elif step == 1:
            bot.answer_callback_query(call.id)
        
        elif step == 2:
            reset_confirm[user_id] = 0
            users = load_json(USERS_FILE)
            for uid in users:
                users[uid]['crystals'] = 100
                users[uid]['wins'] = 0
                users[uid]['games'] = 0
                users[uid]['streak'] = 0
                users[uid]['best_streak'] = 0
            save_json(USERS_FILE, users)
            bot.answer_callback_query(call.id, "✅ Статистика сброшена!", show_alert=True)
            bot.edit_message_text("🔧 АДМИН ПАНЕЛЬ\n\nСтатистика сброшена", call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
    
    elif data == "admin_reset_confirm":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Доступ запрещен")
            return
        reset_confirm[user_id] = 2
        text = """🔐 Введите код подтверждения: СБРОС123

Введите этот код в чат для подтверждения сброса."""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        bot.register_next_step_handler(call.message, admin_reset_code)
    
    elif data == "admin_reset_cancel":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Доступ запрещен")
            return
        reset_confirm[user_id] = 0
        bot.answer_callback_query(call.id, "❌ Сброс отменён")
        bot.edit_message_text("🔧 АДМИН ПАНЕЛЬ", call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
    
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
    
    elif data == "admin_gifts":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Доступ запрещен")
            return
        settings = load_settings()
        gift_settings = settings.get("gift_settings", {
            "enabled": True,
            "min_amount": 10,
            "max_amount": 1000,
            "daily_limit": 10
        })
        text = f"""🎁 УПРАВЛЕНИЕ ПОДАРКАМИ

Статус: {'✅ Включены' if gift_settings['enabled'] else '❌ Отключены'}
Минимальная сумма: {gift_settings['min_amount']}💎
Максимальная сумма: {gift_settings['max_amount']}💎
Лимит в день: {gift_settings['daily_limit']}

Изменить настройки можно командами:
/admin_gift_enable — включить
/admin_gift_disable — отключить
/admin_gift_min 10 — установить минимум
/admin_gift_max 1000 — установить максимум
/admin_gift_limit 10 — установить лимит"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
        bot.answer_callback_query(call.id)
    
    elif data == "admin_neural":
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "❌ Доступ запрещен")
            return
        text = """🧠 НЕЙРОСЕТЬ

Нейросеть генерирует реалистичные слова на основе:
• Частот букв в русском и английском
• Сочетаний букв (биграммы, триграммы)
• Правил чередования гласных и согласных
• Ь и Ъ знаков

Настройка через команды:
/neural_on — включить нейросеть
/neural_off — отключить нейросеть
/neural_power 95 — установить мощность (1-100)"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel_kb())
        bot.answer_callback_query(call.id)

def process_gift_amount(message, target_id):
    user_id = message.from_user.id
    try:
        amount = int(message.text.strip())
        success, msg = send_gift(user_id, target_id, amount)
        bot.reply_to(message, msg)
    except:
        bot.reply_to(message, "❌ Неверная сумма")

def admin_reset_code(message):
    if message.from_user.id != ADMIN_ID:
        return
    if message.text.strip() == "СБРОС123":
        reset_confirm[ADMIN_ID] = 3
        text = """⚠️ ПОСЛЕДНЕЕ ПРЕДУПРЕЖДЕНИЕ! ⚠️

Вы точно хотите сбросить статистику ВСЕХ пользователей?

Это действие НЕЛЬЗЯ будет отменить!

[💀 ДА, СБРОСИТЬ ВСЁ]  [❌ НЕТ, НАЗАД]"""
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("💀 ДА, СБРОСИТЬ ВСЁ", callback_data="admin_reset_final"),
            types.InlineKeyboardButton("❌ НЕТ, НАЗАД", callback_data="admin_reset_cancel")
        )
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        bot.reply_to(message, "❌ Неверный код. Сброс отменён.")
        reset_confirm[ADMIN_ID] = 0

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
    print(f"📚 Русских слов: {len(neural_networks['ru'].corpus)}")
    print(f"📚 Английских слов: {len(neural_networks['en'].corpus)}")
    print("🧠 ЛЮТАЯ НЕЙРОСЕТЬ — полное знание языков")
    print("🎮 УГАДАЙ СЛОВО — общая игра в чате")
    print("🎰 КАЗИНО — 4 игры с визуальными эффектами")
    print("🎁 ПОДАРКИ — дари кристаллы друзьям")
    print("📦 ИНВЕНТАРЬ — используй предметы")
    print("⭐ ДОНАТ — 15 вариантов до 1000 Stars")
    print("🎡 КОЛЕСО ФОРТУНЫ — минимальный выигрыш 30💎")
    print("🔧 АДМИН-ПАНЕЛЬ — 12 разделов")
    print("🔒 СБРОС СТАТИСТИКИ — 3 подтверждения")
    print("🖼️ ВСЕ КАРТИНКИ — 11 штук")
    print("📢 РАССЫЛКА — текст, фото, видео")
    print("📋 ЛОГИ — все действия админов")
    print("🎫 ПРОМОКОДЫ — создавай и удаляй")
    print("")
    print("Команды: /start, /stats, /top, /shop, /inventory, /daily, /wheel, /casino, /gift, /promo, /lang, /donate, /help, /admin")
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")