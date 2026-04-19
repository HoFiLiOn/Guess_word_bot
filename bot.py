import telebot
from telebot import types
import json
import os
import time
import random
from datetime import datetime, timedelta
import threading
import shutil

# ========== ТОКЕН ==========
TOKEN = "8786399001:AAF2GODnsIrCluHiFPH8XYC8uVMuPrDiSss"
bot = telebot.TeleBot(TOKEN)

# ========== АДМИНЫ ==========
MASTER_IDS = [8388843828]
ADMINS_FILE = "data/admins.json"

# ========== ФАЙЛЫ ==========
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = f"{DATA_DIR}/users.json"
PROMO_FILE = f"{DATA_DIR}/promocodes.json"
ROLES_FILE = f"{DATA_DIR}/roles.json"
MARKET_FILE = f"{DATA_DIR}/market.json"
REPORTS_FILE = f"{DATA_DIR}/reports.json"
IDEAS_FILE = f"{DATA_DIR}/ideas.json"
SETTINGS_FILE = f"{DATA_DIR}/settings.json"

# ========== НАСТРОЙКИ ПО УМОЛЧАНИЮ ==========
DEFAULT_SETTINGS = {
    'market_commission_base': 10,
    'market_commission_tiers': [
        {'max_price': 10000, 'commission': 30},
        {'max_price': 30000, 'commission': 15},
        {'max_price': 999999, 'commission': 10}
    ],
    'market_min_prices': {
        'Vip': 8000, 'Pro': 10000, 'Phoenix': 15000, 'Dragon': 25000,
        'Elite': 30000, 'Phantom': 35000, 'Hydra': 45000, 'Overlord': 55000,
        'Apex': 70000, 'Quantum': 80000
    },
    'market_lot_days': 7,
    'workshop_levels': {
        1: {'price': 0, 'bonus': 0, 'max_lots': 1},
        2: {'price': 5000, 'bonus': 5, 'max_lots': 1},
        3: {'price': 10000, 'bonus': 10, 'max_lots': 2},
        4: {'price': 20000, 'bonus': 15, 'max_lots': 2},
        5: {'price': 35000, 'bonus': 20, 'max_lots': 3},
        6: {'price': 55000, 'bonus': 25, 'max_lots': 3},
        7: {'price': 80000, 'bonus': 30, 'max_lots': 4},
        8: {'price': 110000, 'bonus': 35, 'max_lots': 4},
        9: {'price': 150000, 'bonus': 40, 'max_lots': 5},
        10: {'price': 200000, 'bonus': 50, 'max_lots': 5}
    }
}

# ========== ФОТОГРАФИИ ==========
IMAGES = {
    'main': 'https://s10.iimage.su/s/19/gRFZSeMxdaqNHNZYeqDEWNQDnnz80Ja8c63deATA7.jpg',
    'shop': 'https://s10.iimage.su/s/19/gRnaU7sxEU6XWHYbGw78EkVSp5IPw1ddodaUu9mlo.jpg',
    'profile': 'https://s10.iimage.su/s/19/gxUPlX8xJjv31lGZGcI9hvs8AQK0mVHRbfSsnzfpH.jpg',
    'market': 'https://s10.iimage.su/s/19/gdUzQDuxLH6sZWEhDz1uHiXRazGT4HzqG8m54neT9.jpg',
    'workshop': 'https://s10.iimage.su/s/19/gZ6zIWexrV0rmJBQ9FUWeUWvpys7JH6cufMBzMn3h.jpg',
    'bonus': 'https://s10.iimage.su/s/19/gBREkUaxGPGX9MdKMhfjI4pVgCoiBUa15gMSR18DS.jpg',
    'leaders': 'https://s10.iimage.su/s/19/gEYbByAxi9iVwc3cqwidzzARo6yeh6pvlZEcFZy9G.jpg',
    'help': 'https://s10.iimage.su/s/19/gX0g4pSxDRr1P8bhaHjT0KOjsGod9MpHXH0us0gRZ.jpg'
}

# ========== ФУНКЦИИ РАБОТЫ С ДАННЫМИ ==========
def get_moscow_time():
    return datetime.utcnow() + timedelta(hours=3)

def load_json(file_path, default=None):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return default if default is not None else {}

def save_json(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

def get_settings():
    settings = load_json(SETTINGS_FILE)
    if not settings:
        settings = DEFAULT_SETTINGS.copy()
        save_json(SETTINGS_FILE, settings)
    return settings

def is_admin(user_id):
    if user_id in MASTER_IDS:
        return True
    admins = load_json(ADMINS_FILE)
    return str(user_id) in admins.get('admin_list', {})

def is_master(user_id):
    return user_id in MASTER_IDS

# ========== РАБОТА С ПОЛЬЗОВАТЕЛЯМИ ==========
def get_user(user_id):
    users = load_json(USERS_FILE)
    return users.get(str(user_id))

def create_user(user_id, username, first_name):
    users = load_json(USERS_FILE)
    uid = str(user_id)
    if uid not in users:
        users[uid] = {
            'coins': 100, 'role': None, 'username': username, 'first_name': first_name,
            'messages': 0, 'messages_today': 0, 'last_message_reset': None,
            'daily_streak': 0, 'last_daily': None, 'invites': [], 'invited_by': None,
            'referral_earned': 0, 'total_earned': 100, 'total_spent': 0,
            'is_banned': False, 'ban_reason': None,
            'registered_at': get_moscow_time().strftime('%Y-%m-%d %H:%M:%S'),
            'last_active': get_moscow_time().strftime('%Y-%m-%d %H:%M:%S'),
            'workshop_level': 1
        }
        save_json(USERS_FILE, users)
    return users[uid]

def add_coins(user_id, amount):
    users = load_json(USERS_FILE)
    uid = str(user_id)
    if uid in users:
        users[uid]['coins'] += amount
        users[uid]['total_earned'] += amount
        save_json(USERS_FILE, users)
        return True
    return False

def remove_coins(user_id, amount):
    users = load_json(USERS_FILE)
    uid = str(user_id)
    if uid in users:
        users[uid]['coins'] = max(0, users[uid]['coins'] - amount)
        users[uid]['total_spent'] += amount
        save_json(USERS_FILE, users)
        return True
    return False

def is_banned(user_id):
    user = get_user(user_id)
    return user.get('is_banned', False) if user else False

def add_message(user_id):
    if is_banned(user_id): return False
    user = get_user(user_id)
    if not user: return False
    now = get_moscow_time()
    today = now.strftime('%Y-%m-%d')
    if user.get('last_message_reset') != today:
        user['messages_today'] = 0
        user['last_message_reset'] = today
    if user['messages_today'] >= 500: return False
    base = random.randint(1, 5)
    mult = get_multiplier(user_id)
    earn = int(base * mult)
    users = load_json(USERS_FILE)
    uid = str(user_id)
    users[uid]['messages'] += 1
    users[uid]['messages_today'] += 1
    users[uid]['coins'] += earn
    users[uid]['total_earned'] += earn
    users[uid]['last_active'] = now.strftime('%Y-%m-%d %H:%M:%S')
    if users[uid]['messages'] % 100 == 0:
        bonus = 500
        users[uid]['coins'] += bonus
        users[uid]['total_earned'] += bonus
        try:
            bot.send_message(user_id, f"🎉 <b>Бонус!</b>\n\n📊 {users[uid]['messages']} сообщений\n💰 +{bonus} монет", parse_mode='HTML')
        except:
            pass
    save_json(USERS_FILE, users)
    return True

def get_daily(user_id):
    user = get_user(user_id)
    if not user: return 0, "Ошибка"
    today = get_moscow_time().strftime('%Y-%m-%d')
    if user.get('last_daily') == today: return 0, "❌ Бонус уже получен сегодня!"
    streak = user.get('daily_streak', 0) + 1
    if streak >= 15:
        bonus = random.randint(400, 800)
        extra = "✨ Супер бонус! ✨"
    elif streak >= 8:
        bonus = random.randint(200, 400)
        extra = "⭐️ Отлично! ⭐️"
    elif streak >= 4:
        bonus = random.randint(100, 200)
        extra = "👍 Хорошо! 👍"
    else:
        bonus = random.randint(50, 100)
        extra = ""
    mult = get_multiplier(user_id)
    bonus = int(bonus * mult)
    users = load_json(USERS_FILE)
    uid = str(user_id)
    users[uid]['last_daily'] = today
    users[uid]['daily_streak'] = streak
    users[uid]['coins'] += bonus
    users[uid]['total_earned'] += bonus
    save_json(USERS_FILE, users)
    msg = f"🎁 +{bonus}💰\n🔥 Серия: {streak} дн."
    if extra: msg += f"\n{extra}"
    return bonus, msg

def add_invite(inviter, invited):
    users = load_json(USERS_FILE)
    inv_str = str(inviter)
    invd_str = str(invited)
    if invd_str not in users[inv_str].get('invites', []):
        users[inv_str].setdefault('invites', []).append(invd_str)
        users[inv_str]['coins'] += 100
        users[inv_str]['referral_earned'] += 100
        save_json(USERS_FILE, users)
        try:
            bot.send_message(inviter, f"🎉 <b>Новый реферал!</b>\n\n👤 {users[invd_str]['first_name']}\n💰 +100 монет", parse_mode='HTML')
        except:
            pass
        return True
    return False

def check_referral_reward(invited_id):
    invited = get_user(invited_id)
    if not invited: return
    inviter = invited.get('invited_by')
    if not inviter: return
    if invited['messages'] >= 50:
        users = load_json(USERS_FILE)
        inv_str = str(inviter)
        key = f'rewarded_{invited_id}'
        if not users[inv_str].get(key):
            users[inv_str]['coins'] += 200
            users[inv_str]['referral_earned'] += 200
            users[inv_str][key] = True
            save_json(USERS_FILE, users)
            try:
                bot.send_message(int(inviter), f"🎉 <b>Бонус за активность!</b>\n\n👤 {invited['first_name']} написал 50 сообщений\n💰 +200 монет", parse_mode='HTML')
            except:
                pass

# ========== РАБОТА С РОЛЯМИ ==========
def load_roles():
    roles = load_json(ROLES_FILE)
    if not roles:
        roles = {
            'Vip': {'price': 12000, 'mult': 1.1},
            'Pro': {'price': 15000, 'mult': 1.2},
            'Phoenix': {'price': 25000, 'mult': 1.3},
            'Dragon': {'price': 40000, 'mult': 1.4},
            'Elite': {'price': 45000, 'mult': 1.5},
            'Phantom': {'price': 50000, 'mult': 1.6},
            'Hydra': {'price': 60000, 'mult': 1.7},
            'Overlord': {'price': 75000, 'mult': 1.8},
            'Apex': {'price': 90000, 'mult': 1.9},
            'Quantum': {'price': 100000, 'mult': 2.0}
        }
        save_json(ROLES_FILE, roles)
    return roles

def save_roles(roles):
    save_json(ROLES_FILE, roles)

def get_multiplier(user_id):
    user = get_user(user_id)
    if not user: return 1.0
    roles = load_roles()
    role = user.get('role')
    workshop_level = user.get('workshop_level', 1)
    workshop_bonus = get_workshop_bonus(workshop_level)
    role_mult = roles[role]['mult'] if role and role in roles else 1.0
    return role_mult * (1 + workshop_bonus / 100)

def get_workshop_bonus(level):
    settings = get_settings()
    levels = settings.get('workshop_levels', DEFAULT_SETTINGS['workshop_levels'])
    return levels.get(level, {}).get('bonus', 0)

def get_workshop_max_lots(level):
    settings = get_settings()
    levels = settings.get('workshop_levels', DEFAULT_SETTINGS['workshop_levels'])
    return levels.get(level, {}).get('max_lots', 1)

def get_workshop_next_price(level):
    settings = get_settings()
    levels = settings.get('workshop_levels', DEFAULT_SETTINGS['workshop_levels'])
    next_level = level + 1
    return levels.get(next_level, {}).get('price', None)

def upgrade_workshop(user_id):
    user = get_user(user_id)
    if not user: return False, "Ошибка"
    current = user.get('workshop_level', 1)
    next_price = get_workshop_next_price(current)
    if not next_price: return False, "Максимальный уровень достигнут"
    if user['coins'] < next_price: return False, f"Не хватает монет. Нужно {next_price}💰"
    remove_coins(user_id, next_price)
    users = load_json(USERS_FILE)
    users[str(user_id)]['workshop_level'] = current + 1
    save_json(USERS_FILE, users)
    return True, f"Мастерская улучшена до {current + 1} уровня! +{get_workshop_bonus(current + 1)}% к доходу"

def buy_role(user_id, role_name):
    user = get_user(user_id)
    if not user: return False, "Ошибка"
    roles = load_roles()
    if role_name not in roles: return False, "Роль не найдена"
    price = roles[role_name]['price']
    if user['coins'] < price: return False, f"Нужно {price}💰\n💰 У тебя: {user['coins']}💰"
    old_role = user.get('role')
    cashback = 0
    if old_role and old_role in roles and roles[old_role]['price'] > 0:
        cashback = int(roles[old_role]['price'] * 0.1)
    remove_coins(user_id, price)
    if cashback > 0: add_coins(user_id, cashback)
    users = load_json(USERS_FILE)
    users[str(user_id)]['role'] = role_name
    save_json(USERS_FILE, users)
    inviter = user.get('invited_by')
    if inviter:
        bonus = int(price * 0.1)
        add_coins(int(inviter), bonus)
        try:
            bot.send_message(int(inviter), f"🎉 <b>Бонус!</b>\n\n👤 {user['first_name']} купил {role_name}\n💰 +{bonus} монет", parse_mode='HTML')
        except:
            pass
    msg = f"✅ <b>Поздравляю!</b>\n\n🎭 Роль: {role_name}\n💰 Цена: {price}💰\n📈 Множитель: x{roles[role_name]['mult']}"
    if cashback > 0: msg += f"\n💸 Кешбэк: {cashback}💰"
    return True, msg

# ========== РЫНОК ==========
def load_market():
    market = load_json(MARKET_FILE)
    if not market:
        market = {'lots': [], 'next_id': 1}
        save_json(MARKET_FILE, market)
    return market

def save_market(market):
    save_json(MARKET_FILE, market)

def get_market_commission(price):
    settings = get_settings()
    tiers = settings.get('market_commission_tiers', DEFAULT_SETTINGS['market_commission_tiers'])
    for tier in tiers:
        if price <= tier['max_price']: return tier['commission']
    return settings.get('market_commission_base', 10)

def get_market_min_price(role_name):
    settings = get_settings()
    min_prices = settings.get('market_min_prices', DEFAULT_SETTINGS['market_min_prices'])
    return min_prices.get(role_name, 1000)

def add_market_lot(user_id, role_name, price):
    user = get_user(user_id)
    if not user: return False, "Ошибка"
    if user.get('role') != role_name: return False, "Вы можете продавать только свою текущую роль"
    workshop_level = user.get('workshop_level', 1)
    max_lots = get_workshop_max_lots(workshop_level)
    market = load_market()
    user_lots = [lot for lot in market['lots'] if lot['seller_id'] == user_id]
    if len(user_lots) >= max_lots: return False, f"Вы можете выставить только {max_lots} лот(ов). Улучшите Мастерскую"
    min_price = get_market_min_price(role_name)
    if price < min_price: return False, f"Минимальная цена для этой роли: {min_price}💰"
    settings = get_settings()
    lot = {
        'id': market['next_id'], 'seller_id': user_id, 'seller_name': user['first_name'],
        'seller_username': user.get('username'), 'role_name': role_name, 'price': price,
        'created_at': get_moscow_time().isoformat(),
        'expires_at': (get_moscow_time() + timedelta(days=settings.get('market_lot_days', 7))).isoformat()
    }
    market['lots'].append(lot)
    market['next_id'] += 1
    save_market(market)
    users = load_json(USERS_FILE)
    users[str(user_id)]['role'] = None
    save_json(USERS_FILE, users)
    return True, f"Роль {role_name} выставлена на продажу за {price}💰"

def remove_market_lot(lot_id, user_id):
    market = load_market()
    for lot in market['lots']:
        if lot['id'] == lot_id and lot['seller_id'] == user_id:
            users = load_json(USERS_FILE)
            users[str(user_id)]['role'] = lot['role_name']
            save_json(USERS_FILE, users)
            market['lots'].remove(lot)
            save_market(market)
            return True, f"Лот #{lot_id} снят, роль {lot['role_name']} возвращена"
    return False, "Лот не найден"

def buy_market_lot(lot_id, buyer_id):
    market = load_market()
    lot = next((l for l in market['lots'] if l['id'] == lot_id), None)
    if not lot: return False, "Лот не найден"
    if lot['seller_id'] == buyer_id: return False, "Нельзя купить свой лот"
    buyer = get_user(buyer_id)
    if not buyer: return False, "Ошибка"
    price = lot['price']
    if buyer['coins'] < price: return False, f"Не хватает монет. Нужно {price}💰"
    if datetime.fromisoformat(lot['expires_at']) < get_moscow_time():
        users = load_json(USERS_FILE)
        users[str(lot['seller_id'])]['role'] = lot['role_name']
        save_json(USERS_FILE, users)
        market['lots'].remove(lot)
        save_market(market)
        return False, "Лот истёк"
    commission = get_market_commission(price)
    commission_amount = int(price * commission / 100)
    seller_gets = price - commission_amount
    remove_coins(buyer_id, price)
    add_coins(lot['seller_id'], seller_gets)
    users = load_json(USERS_FILE)
    users[str(buyer_id)]['role'] = lot['role_name']
    save_json(USERS_FILE, users)
    market['lots'].remove(lot)
    save_market(market)
    try:
        bot.send_message(lot['seller_id'], f"💰 <b>Ваш лот продан!</b>\n\n🎭 Роль: {lot['role_name']}\n💰 Цена: {price}💰\n💸 Комиссия: {commission_amount}💰\n💵 Вы получили: {seller_gets}💰", parse_mode='HTML')
    except:
        pass
    return True, f"✅ Вы купили роль {lot['role_name']} за {price}💰"

def get_user_lots(user_id):
    market = load_market()
    return [lot for lot in market['lots'] if lot['seller_id'] == user_id]

def get_all_lots():
    market = load_market()
    return market['lots']

def cleanup_expired_lots():
    market = load_market()
    now = get_moscow_time()
    removed = 0
    for lot in market['lots'][:]:
        if datetime.fromisoformat(lot['expires_at']) < now:
            users = load_json(USERS_FILE)
            users[str(lot['seller_id'])]['role'] = lot['role_name']
            save_json(USERS_FILE, users)
            market['lots'].remove(lot)
            removed += 1
    if removed: save_market(market)
    return removed

# ========== ОТЧЁТЫ И ИДЕИ ==========
def save_report(user_id, username, first_name, text, file_id=None):
    reports = load_json(REPORTS_FILE)
    if 'list' not in reports: reports['list'] = []
    report_id = len(reports['list']) + 1
    reports['list'].append({
        'id': report_id, 'user_id': user_id, 'username': username, 'first_name': first_name,
        'text': text, 'file_id': file_id, 'status': 'new', 'created_at': get_moscow_time().isoformat()
    })
    save_json(REPORTS_FILE, reports)
    mention = f"@{username}" if username else first_name
    try:
        bot.send_message(MASTER_IDS[0], f"📝 <b>Новый отчёт</b>\n\nОт: {mention} (ID: {user_id})\n\n{text}", parse_mode='HTML')
    except:
        pass
    return report_id

def save_idea(user_id, username, first_name, text):
    ideas = load_json(IDEAS_FILE)
    if 'list' not in ideas: ideas['list'] = []
    idea_id = len(ideas['list']) + 1
    ideas['list'].append({
        'id': idea_id, 'user_id': user_id, 'username': username, 'first_name': first_name,
        'text': text, 'status': 'new', 'created_at': get_moscow_time().isoformat()
    })
    save_json(IDEAS_FILE, ideas)
    mention = f"@{username}" if username else first_name
    try:
        bot.send_message(MASTER_IDS[0], f"💡 <b>Новая идея</b>\n\nОт: {mention} (ID: {user_id})\n\n{text}", parse_mode='HTML')
    except:
        pass
    return idea_id

def get_reports_list():
    return load_json(REPORTS_FILE).get('list', [])

def get_ideas_list():
    return load_json(IDEAS_FILE).get('list', [])

def update_report_status(report_id, status):
    reports = load_json(REPORTS_FILE)
    for r in reports.get('list', []):
        if r['id'] == report_id:
            r['status'] = status
            save_json(REPORTS_FILE, reports)
            return True
    return False

def update_idea_status(idea_id, status):
    ideas = load_json(IDEAS_FILE)
    for i in ideas.get('list', []):
        if i['id'] == idea_id:
            i['status'] = status
            save_json(IDEAS_FILE, ideas)
            return True
    return False

def delete_report(report_id):
    reports = load_json(REPORTS_FILE)
    reports['list'] = [r for r in reports.get('list', []) if r['id'] != report_id]
    save_json(REPORTS_FILE, reports)
    return True

def delete_idea(idea_id):
    ideas = load_json(IDEAS_FILE)
    ideas['list'] = [i for i in ideas.get('list', []) if i['id'] != idea_id]
    save_json(IDEAS_FILE, ideas)
    return True

def get_stats():
    users = load_json(USERS_FILE)
    total = len(users)
    coins = sum(u.get('coins', 0) for u in users.values())
    msgs = sum(u.get('messages', 0) for u in users.values())
    banned = sum(1 for u in users.values() if u.get('is_banned'))
    with_role = sum(1 for u in users.values() if u.get('role'))
    today = get_moscow_time().strftime('%Y-%m-%d')
    active = sum(1 for u in users.values() if u.get('last_active', '').startswith(today))
    return {'total': total, 'coins': coins, 'messages': msgs, 'banned': banned, 'with_role': with_role, 'active': active}

# ========== КЛАВИАТУРЫ ==========
def get_main_menu(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("🛍️ Магазин", callback_data="shop"),
        types.InlineKeyboardButton("👤 Профиль", callback_data="profile"),
        types.InlineKeyboardButton("🔧 Мастерская", callback_data="workshop"),
        types.InlineKeyboardButton("💰 Рынок", callback_data="market"),
        types.InlineKeyboardButton("🎁 Бонус", callback_data="bonus"),
        types.InlineKeyboardButton("📊 Топ", callback_data="top"),
        types.InlineKeyboardButton("❓ Помощь", callback_data="help"),
        types.InlineKeyboardButton("📝 Обратная связь", callback_data="feedback")
    ]
    markup.add(*buttons)
    if is_admin(user_id):
        markup.add(types.InlineKeyboardButton("🔧 Админ панель", callback_data="admin_panel"))
    return markup

def get_back_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back"))
    return markup

def get_shop_menu(page=1):
    roles = load_roles()
    items = list(roles.items())
    per_page = 3
    total = (len(items) + per_page - 1) // per_page
    page = max(1, min(page, total))
    start = (page-1)*per_page
    markup = types.InlineKeyboardMarkup(row_width=1)
    for name, data in items[start:start+per_page]:
        markup.add(types.InlineKeyboardButton(f"{name} — {data['price']}💰 (x{data['mult']})", callback_data=f"buy_{name}"))
    nav = []
    if page > 1: nav.append(types.InlineKeyboardButton("◀️", callback_data=f"shop_page_{page-1}"))
    if page < total: nav.append(types.InlineKeyboardButton("▶️", callback_data=f"shop_page_{page+1}"))
    if nav: markup.row(*nav)
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back"))
    return markup, page, total

def get_market_menu(page=1):
    lots = get_all_lots()
    per_page = 3
    total = (len(lots) + per_page - 1) // per_page if lots else 1
    page = max(1, min(page, total))
    start = (page-1)*per_page
    markup = types.InlineKeyboardMarkup(row_width=1)
    for lot in lots[start:start+per_page]:
        seller = f"@{lot['seller_username']}" if lot['seller_username'] else lot['seller_name']
        markup.add(types.InlineKeyboardButton(f"#{lot['id']} {lot['role_name']} — {lot['price']}💰 ({seller})", callback_data=f"lot_{lot['id']}"))
    nav = []
    if page > 1: nav.append(types.InlineKeyboardButton("◀️", callback_data=f"market_page_{page-1}"))
    if page < total: nav.append(types.InlineKeyboardButton("▶️", callback_data=f"market_page_{page+1}"))
    if nav: markup.row(*nav)
    markup.add(types.InlineKeyboardButton("💰 Выставить роль", callback_data="market_sell"))
    markup.add(types.InlineKeyboardButton("📦 Мои лоты", callback_data="market_my_lots"))
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back"))
    return markup, page, total

def get_workshop_menu(user_id):
    user = get_user(user_id)
    level = user.get('workshop_level', 1)
    bonus = get_workshop_bonus(level)
    max_lots = get_workshop_max_lots(level)
    next_price = get_workshop_next_price(level)
    markup = types.InlineKeyboardMarkup(row_width=1)
    if next_price:
        markup.add(types.InlineKeyboardButton(f"⚡️ Улучшить — {next_price}💰", callback_data="workshop_upgrade"))
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back"))
    return markup, level, bonus, max_lots, next_price

def get_admin_panel():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton("👥 Пользователи", callback_data="admin_users"),
        types.InlineKeyboardButton("💰 Выдать монеты", callback_data="admin_add_coins"),
        types.InlineKeyboardButton("💸 Забрать монеты", callback_data="admin_remove_coins"),
        types.InlineKeyboardButton("🎭 Выдать роль", callback_data="admin_give_role"),
        types.InlineKeyboardButton("➕ Создать роль", callback_data="admin_add_role"),
        types.InlineKeyboardButton("✏️ Редакт. роль", callback_data="admin_edit_role"),
        types.InlineKeyboardButton("🗑 Удалить роль", callback_data="admin_del_role"),
        types.InlineKeyboardButton("📋 Список ролей", callback_data="admin_list_roles"),
        types.InlineKeyboardButton("🛒 Управление рынком", callback_data="admin_market"),
        types.InlineKeyboardButton("🔧 Настройки мастерской", callback_data="admin_workshop"),
        types.InlineKeyboardButton("📝 Отчёты", callback_data="admin_reports"),
        types.InlineKeyboardButton("💡 Идеи", callback_data="admin_ideas"),
        types.InlineKeyboardButton("🚫 Забанить", callback_data="admin_ban"),
        types.InlineKeyboardButton("✅ Разбанить", callback_data="admin_unban"),
        types.InlineKeyboardButton("👑 Добавить админа", callback_data="admin_add_admin"),
        types.InlineKeyboardButton("🗑 Удалить админа", callback_data="admin_remove_admin"),
        types.InlineKeyboardButton("📢 Рассылка", callback_data="admin_mail"),
        types.InlineKeyboardButton("🎁 Промокоды", callback_data="admin_promo"),
        types.InlineKeyboardButton("📦 Бэкап", callback_data="admin_backup"),
        types.InlineKeyboardButton("🖼️ Сменить фото", callback_data="admin_images")
    ]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back"))
    return markup

def get_users_list_menu(page=1):
    users = load_json(USERS_FILE)
    items = list(users.items())
    per_page = 10
    total = (len(items) + per_page - 1) // per_page if items else 1
    page = max(1, min(page, total))
    start = (page-1)*per_page
    markup = types.InlineKeyboardMarkup(row_width=1)
    for uid, data in items[start:start+per_page]:
        name = data.get('first_name', 'User')
        markup.add(types.InlineKeyboardButton(f"{name} — {data['coins']}💰", callback_data=f"user_{uid}"))
    nav = []
    if page > 1: nav.append(types.InlineKeyboardButton("◀️", callback_data=f"users_page_{page-1}"))
    if page < total: nav.append(types.InlineKeyboardButton("▶️", callback_data=f"users_page_{page+1}"))
    if nav: markup.row(*nav)
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="admin_panel"))
    return markup, page, total

def get_user_actions_menu(target_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("💰 Выдать монеты", callback_data=f"user_add_coins_{target_id}"),
        types.InlineKeyboardButton("💸 Забрать монеты", callback_data=f"user_remove_coins_{target_id}"),
        types.InlineKeyboardButton("🎭 Выдать роль", callback_data=f"user_give_role_{target_id}"),
        types.InlineKeyboardButton("🚫 Забанить", callback_data=f"user_ban_{target_id}"),
        types.InlineKeyboardButton("✅ Разбанить", callback_data=f"user_unban_{target_id}")
    ]
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="admin_users"))
    return markup

def get_reports_list_menu(page=1):
    reports = get_reports_list()
    reports.reverse()
    per_page = 5
    total = (len(reports) + per_page - 1) // per_page if reports else 1
    page = max(1, min(page, total))
    start = (page-1)*per_page
    markup = types.InlineKeyboardMarkup(row_width=1)
    for r in reports[start:start+per_page]:
        status = "🔴" if r['status'] == 'new' else "🟢"
        name = r.get('first_name', f"User_{r['user_id']}")
        markup.add(types.InlineKeyboardButton(f"{status} #{r['id']} — {name}", callback_data=f"report_{r['id']}"))
    nav = []
    if page > 1: nav.append(types.InlineKeyboardButton("◀️", callback_data=f"reports_page_{page-1}"))
    if page < total: nav.append(types.InlineKeyboardButton("▶️", callback_data=f"reports_page_{page+1}"))
    if nav: markup.row(*nav)
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="admin_panel"))
    return markup, page, total

def get_ideas_list_menu(page=1):
    ideas = get_ideas_list()
    ideas.reverse()
    per_page = 5
    total = (len(ideas) + per_page - 1) // per_page if ideas else 1
    page = max(1, min(page, total))
    start = (page-1)*per_page
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i in ideas[start:start+per_page]:
        status = "🔴" if i['status'] == 'new' else "🟢"
        name = i.get('first_name', f"User_{i['user_id']}")
        markup.add(types.InlineKeyboardButton(f"{status} #{i['id']} — {name}", callback_data=f"idea_{i['id']}"))
    nav = []
    if page > 1: nav.append(types.InlineKeyboardButton("◀️", callback_data=f"ideas_page_{page-1}"))
    if page < total: nav.append(types.InlineKeyboardButton("▶️", callback_data=f"ideas_page_{page+1}"))
    if nav: markup.row(*nav)
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="admin_panel"))
    return markup, page, total

def get_market_admin_menu(page=1):
    lots = get_all_lots()
    per_page = 5
    total = (len(lots) + per_page - 1) // per_page if lots else 1
    page = max(1, min(page, total))
    start = (page-1)*per_page
    markup = types.InlineKeyboardMarkup(row_width=1)
    for lot in lots[start:start+per_page]:
        seller = f"@{lot['seller_username']}" if lot['seller_username'] else lot['seller_name']
        markup.add(types.InlineKeyboardButton(f"#{lot['id']} {lot['role_name']} — {lot['price']}💰 ({seller})", callback_data=f"admin_lot_{lot['id']}"))
    nav = []
    if page > 1: nav.append(types.InlineKeyboardButton("◀️", callback_data=f"admin_lots_page_{page-1}"))
    if page < total: nav.append(types.InlineKeyboardButton("▶️", callback_data=f"admin_lots_page_{page+1}"))
    if nav: markup.row(*nav)
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="admin_panel"))
    return markup, page, total

def get_feedback_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("🐞 Сообщить о баге", callback_data="send_report"))
    markup.add(types.InlineKeyboardButton("💡 Предложить идею", callback_data="send_idea"))
    markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back"))
    return markup

# ========== ОБРАБОТЧИКИ КОМАНД ==========
@bot.message_handler(commands=['startrole', 'menu'])
def menu_command(message):
    if message.chat.type != 'private':
        bot.reply_to(message, "Используй команду в личных сообщениях")
        return
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.send_message(user_id, "🚫 <b>Вы забанены</b>", parse_mode='HTML')
        return
    user = create_user(user_id, message.from_user.username, message.from_user.first_name)
    if message.text.startswith('/startrole'):
        args = message.text.split()
        if len(args) > 1:
            try:
                inviter = int(args[1])
                if inviter != user_id and not is_master(inviter):
                    if get_user(inviter):
                        add_invite(inviter, user_id)
                        users = load_json(USERS_FILE)
                        users[str(user_id)]['invited_by'] = inviter
                        save_json(USERS_FILE, users)
            except:
                pass
    role = user.get('role') or "Нет роли"
    mult = get_multiplier(user_id)
    workshop_level = user.get('workshop_level', 1)
    workshop_bonus = get_workshop_bonus(workshop_level)
    text = f"""🌟 <b>Role Shop Bot</b>

Привет! Твой магазин ролей.

💰 <b>Что можно делать:</b>
• Писать в чат → получать монеты
• Покупать роли → увеличивать доход
• Улучшать мастерскую → повышать бонус
• Продавать роли на рынке
• Забирать ежедневный бонус
• Приглашать друзей

┌ 👤 <b>{user['first_name']}</b>
├ 🎭 Роль: {role}
├ 📈 Множитель: x{mult:.1f}
├ 🔧 Мастерская: {workshop_level} ур. (+{workshop_bonus}%)
├ 💰 Баланс: {user['coins']}💰
├ 📊 Сообщений: {user['messages']}
└ 🔥 Серия: {user.get('daily_streak', 0)} дн.

👇 <b>Выбери действие:</b>"""
    try:
        bot.send_photo(user_id, IMAGES['main'], caption=text, parse_mode='HTML', reply_markup=get_main_menu(user_id))
    except:
        bot.send_message(user_id, text, parse_mode='HTML', reply_markup=get_main_menu(user_id))

@bot.message_handler(commands=['daily'])
def daily_command(message):
    if message.chat.type != 'private':
        return
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.send_message(user_id, "🚫 Вы забанены", parse_mode='HTML')
        return
    bonus, msg = get_daily(user_id)
    try:
        bot.send_photo(user_id, IMAGES['bonus'], caption=msg, parse_mode='HTML')
    except:
        bot.send_message(user_id, msg, parse_mode='HTML')

@bot.message_handler(commands=['admin'])
def admin_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "Нет доступа")
        return
    text = f"🔧 <b>Админ панель</b>\n\n👑 <b>{message.from_user.first_name}</b>\n📊 Статус: {'Владелец' if is_master(user_id) else 'Администратор'}\n\n👇 <b>Выбери действие:</b>"
    bot.send_message(user_id, text, parse_mode='HTML', reply_markup=get_admin_panel())

# ========== ОБРАБОТЧИК КОЛБЭКОВ ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    if is_banned(user_id):
        bot.answer_callback_query(call.id, "Вы забанены", show_alert=True)
        return
    user = create_user(user_id, call.from_user.username, call.from_user.first_name)

    # Назад в главное меню
    if data == "back":
        role = user.get('role') or "Нет роли"
        mult = get_multiplier(user_id)
        workshop_level = user.get('workshop_level', 1)
        workshop_bonus = get_workshop_bonus(workshop_level)
        text = f"""🌟 <b>Role Shop Bot</b>

┌ 👤 <b>{user['first_name']}</b>
├ 🎭 Роль: {role}
├ 📈 Множитель: x{mult:.1f}
├ 🔧 Мастерская: {workshop_level} ур. (+{workshop_bonus}%)
├ 💰 Баланс: {user['coins']}💰
├ 📊 Сообщений: {user['messages']}
└ 🔥 Серия: {user.get('daily_streak', 0)} дн.

👇 <b>Выбери действие:</b>"""
        try:
            bot.edit_message_media(types.InputMediaPhoto(IMAGES['main'], caption=text, parse_mode='HTML'), call.message.chat.id, call.message.message_id, reply_markup=get_main_menu(user_id))
        except:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=get_main_menu(user_id))
        bot.answer_callback_query(call.id)
        return

    # Магазин
    if data == "shop":
        markup, page, total = get_shop_menu(1)
        text = f"🛍️ <b>Магазин ролей</b>\n\n💰 Баланс: {user['coins']}💰\n📄 Страница {page}/{total}\n\n👇 <b>Выбери роль:</b>"
        try:
            bot.edit_message_media(types.InputMediaPhoto(IMAGES['shop'], caption=text, parse_mode='HTML'), call.message.chat.id, call.message.message_id, reply_markup=markup)
        except:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("shop_page_"):
        page = int(data.split("_")[-1])
        markup, page, total = get_shop_menu(page)
        text = f"🛍️ <b>Магазин ролей</b>\n\n💰 Баланс: {user['coins']}💰\n📄 Страница {page}/{total}\n\n👇 <b>Выбери роль:</b>"
        try:
            bot.edit_message_media(types.InputMediaPhoto(IMAGES['shop'], caption=text, parse_mode='HTML'), call.message.chat.id, call.message.message_id, reply_markup=markup)
        except:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("buy_"):
        role = data[4:]
        success, msg = buy_role(user_id, role)
        bot.answer_callback_query(call.id, msg, show_alert=True)
        if success:
            role = user.get('role') or "Нет роли"
            mult = get_multiplier(user_id)
            workshop_level = user.get('workshop_level', 1)
            workshop_bonus = get_workshop_bonus(workshop_level)
            text = f"""🌟 <b>Role Shop Bot</b>

┌ 👤 <b>{user['first_name']}</b>
├ 🎭 Роль: {role}
├ 📈 Множитель: x{mult:.1f}
├ 🔧 Мастерская: {workshop_level} ур. (+{workshop_bonus}%)
├ 💰 Баланс: {user['coins']}💰
├ 📊 Сообщений: {user['messages']}
└ 🔥 Серия: {user.get('daily_streak', 0)} дн.

👇 <b>Выбери действие:</b>"""
            try:
                bot.edit_message_media(types.InputMediaPhoto(IMAGES['main'], caption=text, parse_mode='HTML'), call.message.chat.id, call.message.message_id, reply_markup=get_main_menu(user_id))
            except:
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=get_main_menu(user_id))
        return

    # Профиль
    if data == "profile":
        role = user.get('role') or "Нет роли"
        mult = get_multiplier(user_id)
        workshop_level = user.get('workshop_level', 1)
        workshop_bonus = get_workshop_bonus(workshop_level)
        max_lots = get_workshop_max_lots(workshop_level)
        text = f"""👤 <b>Профиль</b>

┌ 📛 Имя: <b>{user['first_name']}</b>
├ 🎭 Роль: {role}
├ 📈 Множитель: x{mult:.1f}
├ 🔧 Мастерская: {workshop_level} ур. (+{workshop_bonus}%)
├ 💰 Монет: {user['coins']}💰
├ 📊 Сообщений: {user['messages']}
├ 📅 Сегодня: {user.get('messages_today', 0)}
├ 🔥 Серия: {user.get('daily_streak', 0)} дн.
├ 👥 Пригласил: {len(user.get('invites', []))}
├ 💸 С рефералов: {user.get('referral_earned', 0)}💰
├ 💵 Заработано: {user.get('total_earned', 0)}💰
├ 💸 Потрачено: {user.get('total_spent', 0)}💰
├ 📦 Лотов на рынке: {len(get_user_lots(user_id))}/{max_lots}
└ 📅 Регистрация: {user.get('registered_at', '-')[:10]}"""
        try:
            bot.edit_message_media(types.InputMediaPhoto(IMAGES['profile'], caption=text, parse_mode='HTML'), call.message.chat.id, call.message.message_id, reply_markup=get_back_button())
        except:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=get_back_button())
        bot.answer_callback_query(call.id)
        return

    # Бонус
    if data == "bonus":
        bonus, msg = get_daily(user_id)
        bot.answer_callback_query(call.id, msg, show_alert=True)
        if bonus:
            role = user.get('role') or "Нет роли"
            mult = get_multiplier(user_id)
            workshop_level = user.get('workshop_level', 1)
            workshop_bonus = get_workshop_bonus(workshop_level)
            text = f"""🌟 <b>Role Shop Bot</b>

┌ 👤 <b>{user['first_name']}</b>
├ 🎭 Роль: {role}
├ 📈 Множитель: x{mult:.1f}
├ 🔧 Мастерская: {workshop_level} ур. (+{workshop_bonus}%)
├ 💰 Баланс: {user['coins']}💰
├ 📊 Сообщений: {user['messages']}
└ 🔥 Серия: {user.get('daily_streak', 0)} дн.

👇 <b>Выбери действие:</b>"""
            try:
                bot.edit_message_media(types.InputMediaPhoto(IMAGES['main'], caption=text, parse_mode='HTML'), call.message.chat.id, call.message.message_id, reply_markup=get_main_menu(user_id))
            except:
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=get_main_menu(user_id))
        return

    # Топ
    if data == "top":
        users = load_json(USERS_FILE)
        top = []
        for uid, u in users.items():
            if int(uid) not in MASTER_IDS and not u.get('is_banned'):
                top.append((u.get('first_name', 'User'), u.get('coins', 0)))
        top.sort(key=lambda x: x[1], reverse=True)
        top = top[:10]
        text = "🏆 <b>Топ по монетам</b>\n\n"
        for i, (name, coins) in enumerate(top, 1):
            if i == 1: text += f"🥇 <b>{name}</b> — {coins}💰\n"
            elif i == 2: text += f"🥈 <b>{name}</b> — {coins}💰\n"
            elif i == 3: text += f"🥉 <b>{name}</b> — {coins}💰\n"
            else: text += f"{i}. {name} — {coins}💰\n"
        try:
            bot.edit_message_media(types.InputMediaPhoto(IMAGES['leaders'], caption=text, parse_mode='HTML'), call.message.chat.id, call.message.message_id, reply_markup=get_back_button())
        except:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=get_back_button())
        bot.answer_callback_query(call.id)
        return

    # Помощь
    if data == "help":
        roles = load_roles()
        text = "📚 <b>Помощь</b>\n\n<b>💰 Как заработать?</b>\n• Писать в чат — 1-5💰 × множитель\n• /daily — ежедневный бонус\n• Приглашать друзей — 100💰\n• Покупать роли — увеличивать множитель\n• Улучшать мастерскую — увеличивать бонус\n• Продавать роли на рынке\n\n<b>🎭 Все роли:</b>\n"
        for name, data in roles.items():
            text += f"• {name}: {data['price']}💰 → x{data['mult']}\n"
        text += "\n<b>🔧 Мастерская</b>\nУлучшай мастерскую за монеты. Каждый уровень даёт +% к доходу и больше слотов на рынке.\n\n<b>💰 Рынок</b>\nПродавай свои роли другим игрокам. Комиссия зависит от цены.\n\n<b>📋 Команды:</b>\n• /startrole — запуск бота\n• /menu — главное меню\n• /daily — бонус"
        try:
            bot.edit_message_media(types.InputMediaPhoto(IMAGES['help'], caption=text, parse_mode='HTML'), call.message.chat.id, call.message.message_id, reply_markup=get_back_button())
        except:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=get_back_button())
        bot.answer_callback_query(call.id)
        return

    # Мастерская
    if data == "workshop":
        markup, level, bonus, max_lots, next_price = get_workshop_menu(user_id)
        text = f"🔧 <b>Мастерская</b>\n\n📊 Уровень: <b>{level}</b>\n📈 Бонус к доходу: +{bonus}%\n📦 Слотов на рынке: {max_lots}\n\n"
        if next_price:
            text += f"💰 Стоимость улучшения до {level+1} уровня: {next_price}💰\n\n🎁 <b>Что даст улучшение:</b>\n• +{get_workshop_bonus(level+1)}% к доходу\n• {get_workshop_max_lots(level+1)} слотов на рынке"
        else:
            text += "✨ <b>Максимальный уровень достигнут!</b>"
        try:
            bot.edit_message_media(types.InputMediaPhoto(IMAGES['workshop'], caption=text, parse_mode='HTML'), call.message.chat.id, call.message.message_id, reply_markup=markup)
        except:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data == "workshop_upgrade":
        success, msg = upgrade_workshop(user_id)
        bot.answer_callback_query(call.id, msg, show_alert=True)
        if success:
            markup, level, bonus, max_lots, next_price = get_workshop_menu(user_id)
            text = f"🔧 <b>Мастерская</b>\n\n📊 Уровень: <b>{level}</b>\n📈 Бонус к доходу: +{bonus}%\n📦 Слотов на рынке: {max_lots}\n\n"
            if next_price:
                text += f"💰 Стоимость улучшения до {level+1} уровня: {next_price}💰\n\n🎁 <b>Что даст улучшение:</b>\n• +{get_workshop_bonus(level+1)}% к доходу\n• {get_workshop_max_lots(level+1)} слотов на рынке"
            else:
                text += "✨ <b>Максимальный уровень достигнут!</b>"
            try:
                bot.edit_message_media(types.InputMediaPhoto(IMAGES['workshop'], caption=text, parse_mode='HTML'), call.message.chat.id, call.message.message_id, reply_markup=markup)
            except:
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return

    # Рынок
    if data == "market":
        cleanup_expired_lots()
        markup, page, total = get_market_menu(1)
        text = f"💰 <b>Рынок ролей</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери лот:</b>"
        try:
            bot.edit_message_media(types.InputMediaPhoto(IMAGES['market'], caption=text, parse_mode='HTML'), call.message.chat.id, call.message.message_id, reply_markup=markup)
        except:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("market_page_"):
        page = int(data.split("_")[-1])
        markup, page, total = get_market_menu(page)
        text = f"💰 <b>Рынок ролей</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери лот:</b>"
        try:
            bot.edit_message_media(types.InputMediaPhoto(IMAGES['market'], caption=text, parse_mode='HTML'), call.message.chat.id, call.message.message_id, reply_markup=markup)
        except:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("lot_"):
        lot_id = int(data.split("_")[1])
        market = load_market()
        lot = next((l for l in market['lots'] if l['id'] == lot_id), None)
        if lot:
            commission = get_market_commission(lot['price'])
            commission_amount = int(lot['price'] * commission / 100)
            text = f"""🔨 <b>Лот #{lot['id']}</b>

🎭 Роль: {lot['role_name']}
💰 Цена: {lot['price']}💰
👤 Продавец: @{lot['seller_username'] if lot['seller_username'] else lot['seller_name']}
📅 Создан: {lot['created_at'][:16].replace('T', ' ')}

💸 Комиссия: {commission}% ({commission_amount}💰)
💰 Продавец получит: {lot['price'] - commission_amount}💰"""
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(types.InlineKeyboardButton("✅ Купить", callback_data=f"buy_lot_{lot_id}"))
            markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="market"))
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("buy_lot_"):
        lot_id = int(data.split("_")[2])
        success, msg = buy_market_lot(lot_id, user_id)
        bot.answer_callback_query(call.id, msg, show_alert=True)
        if success:
            role = user.get('role') or "Нет роли"
            mult = get_multiplier(user_id)
            workshop_level = user.get('workshop_level', 1)
            workshop_bonus = get_workshop_bonus(workshop_level)
            text = f"""🌟 <b>Role Shop Bot</b>

┌ 👤 <b>{user['first_name']}</b>
├ 🎭 Роль: {role}
├ 📈 Множитель: x{mult:.1f}
├ 🔧 Мастерская: {workshop_level} ур. (+{workshop_bonus}%)
├ 💰 Баланс: {user['coins']}💰
├ 📊 Сообщений: {user['messages']}
└ 🔥 Серия: {user.get('daily_streak', 0)} дн.

👇 <b>Выбери действие:</b>"""
            try:
                bot.edit_message_media(types.InputMediaPhoto(IMAGES['main'], caption=text, parse_mode='HTML'), call.message.chat.id, call.message.message_id, reply_markup=get_main_menu(user_id))
            except:
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=get_main_menu(user_id))
        return
    if data == "market_sell":
        user_role = user.get('role')
        if not user_role:
            bot.answer_callback_query(call.id, "У вас нет роли для продажи", show_alert=True)
            return
        msg = bot.send_message(user_id, f"💰 <b>Продажа роли</b>\n\nВаша роль: {user_role}\n\nВведите цену продажи (мин. {get_market_min_price(user_role)}💰):", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_sell_role, user_role, call.message)
        bot.answer_callback_query(call.id)
        return
    if data == "market_my_lots":
        lots = get_user_lots(user_id)
        if not lots:
            bot.answer_callback_query(call.id, "У вас нет активных лотов", show_alert=True)
            return
        text = "📦 <b>Ваши лоты</b>\n\n"
        for lot in lots:
            text += f"┌ #{lot['id']} — {lot['role_name']}\n├ 💰 {lot['price']}💰\n└ 📅 {lot['created_at'][:16].replace('T', ' ')}\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        for lot in lots:
            markup.add(types.InlineKeyboardButton(f"🗑 Снять лот #{lot['id']}", callback_data=f"remove_lot_{lot['id']}"))
        markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="market"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("remove_lot_"):
        lot_id = int(data.split("_")[-1])
        success, msg = remove_market_lot(lot_id, user_id)
        bot.answer_callback_query(call.id, msg, show_alert=True)
        cleanup_expired_lots()
        markup, page, total = get_market_menu(1)
        text = f"💰 <b>Рынок ролей</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери лот:</b>"
        try:
            bot.edit_message_media(types.InputMediaPhoto(IMAGES['market'], caption=text, parse_mode='HTML'), call.message.chat.id, call.message.message_id, reply_markup=markup)
        except:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return

    # Обратная связь
    if data == "feedback":
        bot.edit_message_text("📝 <b>Обратная связь</b>\n\nВыберите тип сообщения:", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=get_feedback_menu())
        bot.answer_callback_query(call.id)
        return
    if data == "send_report":
        bot.edit_message_text("🐞 <b>Отправить отчёт</b>\n\nОпишите проблему. Можно прикрепить фото.\n\nОтправьте сообщение:", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_report, user_id)
        bot.answer_callback_query(call.id)
        return
    if data == "send_idea":
        bot.edit_message_text("💡 <b>Отправить идею</b>\n\nНапишите вашу идею по улучшению бота.\n\nОтправьте сообщение:", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_idea, user_id)
        bot.answer_callback_query(call.id)
        return

    # Админ панель
    if data == "admin_panel":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "Нет доступа", show_alert=True)
            return
        text = f"🔧 <b>Админ панель</b>\n\n👑 <b>{user['first_name']}</b>\n📊 Статус: {'Владелец' if is_master(user_id) else 'Администратор'}\n\n👇 <b>Выбери действие:</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=get_admin_panel())
        bot.answer_callback_query(call.id)
        return

    # Админ: Статистика
    if data == "admin_stats":
        if not is_admin(user_id): return
        s = get_stats()
        market = load_market()
        text = f"📊 <b>Статистика бота</b>\n\n┌ 👥 Пользователей: {s['total']}\n├ 💰 Всего монет: {s['coins']:,}\n├ 💬 Сообщений: {s['messages']:,}\n├ 🎭 С ролью: {s['with_role']}\n├ 🚫 Забанено: {s['banned']}\n├ ✅ Активных сегодня: {s['active']}\n├ 🎯 Доступно ролей: {len(load_roles())}\n├ 🛒 Активных лотов: {len(market['lots'])}\n├ 📝 Отчётов: {len(get_reports_list())}\n└ 💡 Идей: {len(get_ideas_list())}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=get_admin_panel())
        bot.answer_callback_query(call.id)
        return

    # Админ: Пользователи
    if data == "admin_users":
        if not is_admin(user_id): return
        markup, page, total = get_users_list_menu(1)
        text = f"👥 <b>Список пользователей</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери пользователя:</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("users_page_"):
        page = int(data.split("_")[-1])
        markup, page, total = get_users_list_menu(page)
        text = f"👥 <b>Список пользователей</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери пользователя:</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("user_"):
        target_id = int(data.split("_")[1])
        target = get_user(target_id)
        if target:
            name = target.get('first_name', 'User')
            text = f"👤 <b>{name}</b>\n\n💰 Баланс: {target['coins']}💰\n🎭 Роль: {target.get('role') or 'Нет'}\n📊 Сообщений: {target.get('messages', 0)}\n🚫 Бан: {'Да' if target.get('is_banned') else 'Нет'}\n🔧 Мастерская: {target.get('workshop_level', 1)} ур."
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=get_user_actions_menu(target_id))
        bot.answer_callback_query(call.id)
        return

    # Админ: Управление рынком
    if data == "admin_market":
        if not is_admin(user_id): return
        cleanup_expired_lots()
        markup, page, total = get_market_admin_menu(1)
        text = f"🛒 <b>Управление рынком</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери лот для управления:</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("admin_lots_page_"):
        page = int(data.split("_")[-1])
        markup, page, total = get_market_admin_menu(page)
        text = f"🛒 <b>Управление рынком</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери лот для управления:</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("admin_lot_"):
        lot_id = int(data.split("_")[-1])
        market = load_market()
        lot = next((l for l in market['lots'] if l['id'] == lot_id), None)
        if lot:
            text = f"🔨 <b>Лот #{lot['id']}</b>\n\n🎭 Роль: {lot['role_name']}\n💰 Цена: {lot['price']}💰\n👤 Продавец: @{lot['seller_username'] if lot['seller_username'] else lot['seller_name']} (ID: {lot['seller_id']})\n📅 Создан: {lot['created_at'][:16].replace('T', ' ')}\n📅 Истекает: {lot['expires_at'][:16].replace('T', ' ')}"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🗑 Удалить лот", callback_data=f"admin_del_lot_{lot_id}"))
            markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="admin_market"))
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("admin_del_lot_"):
        if not is_admin(user_id): return
        lot_id = int(data.split("_")[-1])
        market = load_market()
        for lot in market['lots']:
            if lot['id'] == lot_id:
                users = load_json(USERS_FILE)
                users[str(lot['seller_id'])]['role'] = lot['role_name']
                save_json(USERS_FILE, users)
                market['lots'].remove(lot)
                save_market(market)
                bot.answer_callback_query(call.id, f"Лот #{lot_id} удалён, роль возвращена", show_alert=True)
                break
        markup, page, total = get_market_admin_menu(1)
        text = f"🛒 <b>Управление рынком</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери лот для управления:</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return

    # Админ: Мастерская (настройки)
    if data == "admin_workshop":
        if not is_admin(user_id): return
        settings = get_settings()
        levels = settings.get('workshop_levels', DEFAULT_SETTINGS['workshop_levels'])
        text = "🔧 <b>Настройки мастерской</b>\n\n"
        for level, info in levels.items():
            text += f"Уровень {level}: {info['price']}💰 → +{info['bonus']}%, {info['max_lots']} лотов\n"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="admin_panel"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    # Админ: Отчёты
    if data == "admin_reports":
        if not is_admin(user_id): return
        markup, page, total = get_reports_list_menu(1)
        text = f"📝 <b>Список отчётов</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери отчёт:</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("reports_page_"):
        page = int(data.split("_")[-1])
        markup, page, total = get_reports_list_menu(page)
        text = f"📝 <b>Список отчётов</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери отчёт:</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("report_"):
        report_id = int(data.split("_")[1])
        reports = get_reports_list()
        report = next((r for r in reports if r['id'] == report_id), None)
        if report:
            status_text = "🔴 Новый" if report['status'] == 'new' else "🟢 Решён"
            text = f"📋 <b>Отчёт #{report['id']}</b>\n\n👤 От: {report.get('first_name', f'User_{report['user_id']}')}\n🆔 ID: {report['user_id']}\n📅 Дата: {report['created_at'][:16].replace('T', ' ')}\n📊 Статус: {status_text}\n\n📝 Сообщение:\n{report['text']}"
            markup = types.InlineKeyboardMarkup(row_width=2)
            if report['status'] == 'new':
                markup.add(types.InlineKeyboardButton("✅ Отметить решённым", callback_data=f"report_resolve_{report_id}"))
            markup.add(types.InlineKeyboardButton("🗑 Удалить", callback_data=f"report_delete_{report_id}"))
            markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="admin_reports"))
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("report_resolve_"):
        if not is_admin(user_id): return
        report_id = int(data.split("_")[-1])
        update_report_status(report_id, 'resolved')
        bot.answer_callback_query(call.id, "Отмечено как решённое", show_alert=True)
        markup, page, total = get_reports_list_menu(1)
        text = f"📝 <b>Список отчётов</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери отчёт:</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    if data.startswith("report_delete_"):
        if not is_admin(user_id): return
        report_id = int(data.split("_")[-1])
        delete_report(report_id)
        bot.answer_callback_query(call.id, "Отчёт удалён", show_alert=True)
        markup, page, total = get_reports_list_menu(1)
        text = f"📝 <b>Список отчётов</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери отчёт:</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return

    # Админ: Идеи
    if data == "admin_ideas":
        if not is_admin(user_id): return
        markup, page, total = get_ideas_list_menu(1)
        text = f"💡 <b>Список идей</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери идею:</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("ideas_page_"):
        page = int(data.split("_")[-1])
        markup, page, total = get_ideas_list_menu(page)
        text = f"💡 <b>Список идей</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери идею:</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("idea_"):
        idea_id = int(data.split("_")[1])
        ideas = get_ideas_list()
        idea = next((i for i in ideas if i['id'] == idea_id), None)
        if idea:
            status_text = "🔴 Новая" if idea['status'] == 'new' else "🟢 Рассмотрена"
            text = f"💡 <b>Идея #{idea['id']}</b>\n\n👤 От: {idea.get('first_name', f'User_{idea['user_id']}')}\n🆔 ID: {idea['user_id']}\n📅 Дата: {idea['created_at'][:16].replace('T', ' ')}\n📊 Статус: {status_text}\n\n📝 Идея:\n{idea['text']}"
            markup = types.InlineKeyboardMarkup(row_width=2)
            if idea['status'] == 'new':
                markup.add(types.InlineKeyboardButton("✅ Отметить рассмотренной", callback_data=f"idea_consider_{idea_id}"))
            markup.add(types.InlineKeyboardButton("🗑 Удалить", callback_data=f"idea_delete_{idea_id}"))
            markup.add(types.InlineKeyboardButton("◀️ Назад", callback_data="admin_ideas"))
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("idea_consider_"):
        if not is_admin(user_id): return
        idea_id = int(data.split("_")[-1])
        update_idea_status(idea_id, 'considered')
        bot.answer_callback_query(call.id, "Отмечено как рассмотренное", show_alert=True)
        markup, page, total = get_ideas_list_menu(1)
        text = f"💡 <b>Список идей</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери идею:</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return
    if data.startswith("idea_delete_"):
        if not is_admin(user_id): return
        idea_id = int(data.split("_")[-1])
        delete_idea(idea_id)
        bot.answer_callback_query(call.id, "Идея удалена", show_alert=True)
        markup, page, total = get_ideas_list_menu(1)
        text = f"💡 <b>Список идей</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери идею:</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return

    # Админ: Остальные команды
    if data == "admin_add_coins":
        if not is_admin(user_id): return
        msg = bot.send_message(user_id, "💰 <b>Выдать монеты</b>\n\nФормат: ID СУММА\n\nПример: 123456789 500", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_add_coins)
        bot.answer_callback_query(call.id)
        return
    if data == "admin_remove_coins":
        if not is_admin(user_id): return
        msg = bot.send_message(user_id, "💸 <b>Забрать монеты</b>\n\nФормат: ID СУММА\n\nПример: 123456789 500", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_remove_coins)
        bot.answer_callback_query(call.id)
        return
    if data == "admin_give_role":
        if not is_admin(user_id): return
        roles_list = "\n".join(load_roles().keys())
        msg = bot.send_message(user_id, f"🎭 <b>Выдать роль</b>\n\nФормат: ID РОЛЬ\n\nДоступные роли:\n{roles_list}\n\nПример: 123456789 Vip", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_give_role)
        bot.answer_callback_query(call.id)
        return
    if data == "admin_add_role":
        if not is_admin(user_id): return
        msg = bot.send_message(user_id, "➕ <b>Создать роль</b>\n\nФормат: НАЗВАНИЕ ЦЕНА МНОЖИТЕЛЬ\n\nПример: Legend 50000 2.0", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_add_role)
        bot.answer_callback_query(call.id)
        return
    if data == "admin_edit_role":
        if not is_admin(user_id): return
        msg = bot.send_message(user_id, "✏️ <b>Редактировать роль</b>\n\nФормат: НАЗВАНИЕ ЦЕНА МНОЖИТЕЛЬ\n\nИспользуйте - чтобы не менять\nПример: Vip 15000 -", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_edit_role)
        bot.answer_callback_query(call.id)
        return
    if data == "admin_del_role":
        if not is_admin(user_id): return
        roles_list = "\n".join(load_roles().keys())
        msg = bot.send_message(user_id, f"🗑 <b>Удалить роль</b>\n\nФормат: НАЗВАНИЕ\n\nДоступные роли:\n{roles_list}\n\nПример: Legend\n\n⚠️ У пользователей с этой ролью она пропадёт", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_del_role)
        bot.answer_callback_query(call.id)
        return
    if data == "admin_list_roles":
        if not is_admin(user_id): return
        roles = load_roles()
        text = "📋 <b>Список ролей</b>\n\n"
        for name, data in roles.items():
            text += f"┌ <b>{name}</b>\n├ 💰 Цена: {data['price']}💰\n└ 📈 Множитель: x{data['mult']}\n\n"
        text += f"📊 <b>Всего ролей:</b> {len(roles)}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=get_admin_panel())
        bot.answer_callback_query(call.id)
        return
    if data == "admin_ban":
        if not is_admin(user_id): return
        msg = bot.send_message(user_id, "🚫 <b>Забанить</b>\n\nФормат: ID ПРИЧИНА\n\nПример: 123456789 Спам", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_ban)
        bot.answer_callback_query(call.id)
        return
    if data == "admin_unban":
        if not is_admin(user_id): return
        msg = bot.send_message(user_id, "✅ <b>Разбанить</b>\n\nФормат: ID\n\nПример: 123456789", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_unban)
        bot.answer_callback_query(call.id)
        return
    if data == "admin_add_admin":
        if not is_master(user_id):
            bot.answer_callback_query(call.id, "Только для владельца", show_alert=True)
            return
        msg = bot.send_message(user_id, "👑 <b>Добавить админа</b>\n\nФормат: ID\n\nПример: 123456789", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_add_admin)
        bot.answer_callback_query(call.id)
        return
    if data == "admin_remove_admin":
        if not is_master(user_id):
            bot.answer_callback_query(call.id, "Только для владельца", show_alert=True)
            return
        msg = bot.send_message(user_id, "🗑 <b>Удалить админа</b>\n\nФормат: ID\n\nПример: 123456789", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_remove_admin)
        bot.answer_callback_query(call.id)
        return
    if data == "admin_mail":
        if not is_admin(user_id): return
        msg = bot.send_message(user_id, "📢 <b>Рассылка</b>\n\nОтправьте сообщение для рассылки всем пользователям:", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_mail)
        bot.answer_callback_query(call.id)
        return
    if data == "admin_promo":
        if not is_admin(user_id): return
        text = "🎁 <b>Промокоды</b>\n\n<b>Создать промокод на монеты:</b>\n<code>/createpromo КОД СУММА ЛИМИТ ДНИ</code>\n\n<b>Создать промокод на роль:</b>\n<code>/createrole КОД РОЛЬ ДНИ ЛИМИТ</code>\n\n<b>Примеры:</b>\n<code>/createpromo HELLO 500 10 7</code>\n<code>/createrole VIPPROMO Vip 30 5</code>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=get_admin_panel())
        bot.answer_callback_query(call.id)
        return
    if data == "admin_backup":
        if not is_master(user_id):
            bot.answer_callback_query(call.id, "Только для владельца", show_alert=True)
            return
        backup_dir = f"backup_{get_moscow_time().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        for f in [USERS_FILE, ADMINS_FILE, PROMO_FILE, ROLES_FILE, MARKET_FILE, REPORTS_FILE, IDEAS_FILE, SETTINGS_FILE]:
            if os.path.exists(f):
                shutil.copy(f, os.path.join(backup_dir, os.path.basename(f)))
        bot.send_message(user_id, f"✅ <b>Бэкап создан</b>\n\n📁 Папка: {backup_dir}\n📅 {get_moscow_time().strftime('%Y-%m-%d %H:%M:%S')}", parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return
    if data == "admin_images":
        if not is_admin(user_id): return
        text = "🖼️ <b>Смена фото</b>\n\nОтправьте новое фото с командой:\n\n/setphoto main - главное меню\n/setphoto shop - магазин\n/setphoto profile - профиль\n/setphoto market - рынок\n/setphoto workshop - мастерская\n/setphoto bonus - бонус\n/setphoto leaders - топ\n/setphoto help - помощь\n\nПример: /setphoto main (ответом на фото)"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=get_admin_panel())
        bot.answer_callback_query(call.id)
        return

    # Действия над пользователем
    if data.startswith("user_add_coins_"):
        if not is_admin(user_id): return
        target_id = int(data.split("_")[-1])
        msg = bot.send_message(user_id, f"💰 <b>Выдать монеты</b>\n\nПользователь ID: {target_id}\n\nВведите сумму:", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_user_add_coins, target_id)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("user_remove_coins_"):
        if not is_admin(user_id): return
        target_id = int(data.split("_")[-1])
        msg = bot.send_message(user_id, f"💸 <b>Забрать монеты</b>\n\nПользователь ID: {target_id}\n\nВведите сумму:", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_user_remove_coins, target_id)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("user_give_role_"):
        if not is_admin(user_id): return
        target_id = int(data.split("_")[-1])
        roles_list = "\n".join(load_roles().keys())
        msg = bot.send_message(user_id, f"🎭 <b>Выдать роль</b>\n\nПользователь ID: {target_id}\n\nДоступные роли:\n{roles_list}\n\nВведите название роли:", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_user_give_role, target_id)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("user_ban_"):
        if not is_admin(user_id): return
        target_id = int(data.split("_")[-1])
        msg = bot.send_message(user_id, f"🚫 <b>Забанить</b>\n\nПользователь ID: {target_id}\n\nВведите причину бана:", parse_mode='HTML')
        bot.register_next_step_handler(msg, process_user_ban, target_id)
        bot.answer_callback_query(call.id)
        return
    if data.startswith("user_unban_"):
        if not is_admin(user_id): return
        target_id = int(data.split("_")[-1])
        users = load_json(USERS_FILE)
        if str(target_id) in users:
            users[str(target_id)]['is_banned'] = False
            users[str(target_id)]['ban_reason'] = None
            save_json(USERS_FILE, users)
            bot.answer_callback_query(call.id, f"Пользователь {target_id} разбанен", show_alert=True)
            markup, page, total = get_users_list_menu(1)
            text = f"👥 <b>Список пользователей</b>\n\n📄 Страница {page}/{total}\n\n👇 <b>Выбери пользователя:</b>"
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=markup)
        return

    bot.answer_callback_query(call.id)

# ========== ОБРАБОТЧИКИ ШАГОВ ==========
def process_sell_role(message, role_name, original_message):
    user_id = message.from_user.id
    try:
        price = int(message.text.strip())
        min_price = get_market_min_price(role_name)
        if price < min_price:
            bot.send_message(user_id, f"❌ Минимальная цена для этой роли: {min_price}💰", parse_mode='HTML')
            return
        success, msg = add_market_lot(user_id, role_name, price)
        bot.send_message(user_id, msg, parse_mode='HTML')
        if success:
            user = get_user(user_id)
            role = user.get('role') or "Нет роли"
            mult = get_multiplier(user_id)
            workshop_level = user.get('workshop_level', 1)
            workshop_bonus = get_workshop_bonus(workshop_level)
            text = f"""🌟 <b>Role Shop Bot</b>

┌ 👤 <b>{user['first_name']}</b>
├ 🎭 Роль: {role}
├ 📈 Множитель: x{mult:.1f}
├ 🔧 Мастерская: {workshop_level} ур. (+{workshop_bonus}%)
├ 💰 Баланс: {user['coins']}💰
├ 📊 Сообщений: {user['messages']}
└ 🔥 Серия: {user.get('daily_streak', 0)} дн.

👇 <b>Выбери действие:</b>"""
            try:
                bot.send_photo(user_id, IMAGES['main'], caption=text, parse_mode='HTML', reply_markup=get_main_menu(user_id))
            except:
                bot.send_message(user_id, text, parse_mode='HTML', reply_markup=get_main_menu(user_id))
    except ValueError:
        bot.send_message(user_id, "❌ Введите число", parse_mode='HTML')

def process_report(message, user_id):
    text = message.text or "Без текста"
    file_id = None
    if message.photo:
        file_id = message.photo[-1].file_id
        text = message.caption or "Без текста"
    user = get_user(user_id)
    save_report(user_id, user.get('username'), user.get('first_name'), text, file_id)
    bot.send_message(user_id, "✅ <b>Отчёт отправлен!</b> Спасибо за помощь.", parse_mode='HTML')
    user = get_user(user_id)
    role = user.get('role') or "Нет роли"
    mult = get_multiplier(user_id)
    workshop_level = user.get('workshop_level', 1)
    workshop_bonus = get_workshop_bonus(workshop_level)
    text = f"""🌟 <b>Role Shop Bot</b>

┌ 👤 <b>{user['first_name']}</b>
├ 🎭 Роль: {role}
├ 📈 Множитель: x{mult:.1f}
├ 🔧 Мастерская: {workshop_level} ур. (+{workshop_bonus}%)
├ 💰 Баланс: {user['coins']}💰
├ 📊 Сообщений: {user['messages']}
└ 🔥 Серия: {user.get('daily_streak', 0)} дн.

👇 <b>Выбери действие:</b>"""
    try:
        bot.send_photo(user_id, IMAGES['main'], caption=text, parse_mode='HTML', reply_markup=get_main_menu(user_id))
    except:
        bot.send_message(user_id, text, parse_mode='HTML', reply_markup=get_main_menu(user_id))

def process_idea(message, user_id):
    text = message.text or "Без текста"
    user = get_user(user_id)
    save_idea(user_id, user.get('username'), user.get('first_name'), text)
    bot.send_message(user_id, "✅ <b>Идея отправлена!</b> Спасибо за вклад.", parse_mode='HTML')
    user = get_user(user_id)
    role = user.get('role') or "Нет роли"
    mult = get_multiplier(user_id)
    workshop_level = user.get('workshop_level', 1)
    workshop_bonus = get_workshop_bonus(workshop_level)
    text = f"""🌟 <b>Role Shop Bot</b>

┌ 👤 <b>{user['first_name']}</b>
├ 🎭 Роль: {role}
├ 📈 Множитель: x{mult:.1f}
├ 🔧 Мастерская: {workshop_level} ур. (+{workshop_bonus}%)
├ 💰 Баланс: {user['coins']}💰
├ 📊 Сообщений: {user['messages']}
└ 🔥 Серия: {user.get('daily_streak', 0)} дн.

👇 <b>Выбери действие:</b>"""
    try:
        bot.send_photo(user_id, IMAGES['main'], caption=text, parse_mode='HTML', reply_markup=get_main_menu(user_id))
    except:
        bot.send_message(user_id, text, parse_mode='HTML', reply_markup=get_main_menu(user_id))

def process_add_coins(message):
    user_id = message.from_user.id
    try:
        parts = message.text.split()
        target = int(parts[0])
        amount = int(parts[1])
        add_coins(target, amount)
        bot.send_message(user_id, f"✅ <b>Готово!</b>\n\n+{amount}💰 пользователю {target}", parse_mode='HTML')
    except:
        bot.send_message(user_id, "❌ <b>Ошибка!</b>\n\nФормат: ID СУММА", parse_mode='HTML')
    bot.send_message(user_id, "🔧 Админ панель", reply_markup=get_admin_panel())

def process_remove_coins(message):
    user_id = message.from_user.id
    try:
        parts = message.text.split()
        target = int(parts[0])
        amount = int(parts[1])
        remove_coins(target, amount)
        bot.send_message(user_id, f"✅ <b>Готово!</b>\n\n-{amount}💰 пользователю {target}", parse_mode='HTML')
    except:
        bot.send_message(user_id, "❌ <b>Ошибка!</b>\n\nФормат: ID СУММА", parse_mode='HTML')
    bot.send_message(user_id, "🔧 Админ панель", reply_markup=get_admin_panel())

def process_give_role(message):
    user_id = message.from_user.id
    try:
        parts = message.text.split()
        target = int(parts[0])
        role = parts[1].capitalize()
        roles = load_roles()
        if role not in roles:
            bot.send_message(user_id, f"❌ <b>Ошибка!</b>\n\nРоль {role} не найдена", parse_mode='HTML')
        else:
            users = load_json(USERS_FILE)
            users[str(target)]['role'] = role
            save_json(USERS_FILE, users)
            bot.send_message(user_id, f"✅ <b>Готово!</b>\n\nРоль {role} выдана пользователю {target}", parse_mode='HTML')
    except:
        bot.send_message(user_id, "❌ <b>Ошибка!</b>\n\nФормат: ID РОЛЬ", parse_mode='HTML')
    bot.send_message(user_id, "🔧 Админ панель", reply_markup=get_admin_panel())

def process_add_role(message):
    user_id = message.from_user.id
    try:
        parts = message.text.split()
        name = parts[0].capitalize()
        price = int(parts[1])
        mult = float(parts[2])
        roles = load_roles()
        if name in roles:
            bot.send_message(user_id, f"❌ <b>Ошибка!</b>\n\nРоль {name} уже существует", parse_mode='HTML')
        else:
            roles[name] = {'price': price, 'mult': mult}
            save_roles(roles)
            bot.send_message(user_id, f"✅ <b>Роль создана</b>\n\n🎭 {name}\n💰 {price}💰\n📈 x{mult}", parse_mode='HTML')
    except:
        bot.send_message(user_id, "❌ <b>Ошибка!</b>\n\nФормат: НАЗВАНИЕ ЦЕНА МНОЖИТЕЛЬ", parse_mode='HTML')
    bot.send_message(user_id, "🔧 Админ панель", reply_markup=get_admin_panel())

def process_edit_role(message):
    user_id = message.from_user.id
    try:
        parts = message.text.split()
        name = parts[0].capitalize()
        roles = load_roles()
        if name not in roles:
            bot.send_message(user_id, f"❌ <b>Ошибка!</b>\n\nРоль {name} не найдена", parse_mode='HTML')
        else:
            old_price = roles[name]['price']
            old_mult = roles[name]['mult']
            price = int(parts[1]) if len(parts) > 1 and parts[1] != '-' else old_price
            mult = float(parts[2]) if len(parts) > 2 and parts[2] != '-' else old_mult
            roles[name] = {'price': price, 'mult': mult}
            save_roles(roles)
            bot.send_message(user_id, f"✅ <b>Роль обновлена</b>\n\n🎭 {name}\n💰 {price}💰 (было {old_price})\n📈 x{mult} (было x{old_mult})", parse_mode='HTML')
    except:
        bot.send_message(user_id, "❌ <b>Ошибка!</b>\n\nФормат: НАЗВАНИЕ [ЦЕНА] [МНОЖИТЕЛЬ]\n- чтобы не менять", parse_mode='HTML')
    bot.send_message(user_id, "🔧 Админ панель", reply_markup=get_admin_panel())

def process_del_role(message):
    user_id = message.from_user.id
    try:
        name = message.text.strip().capitalize()
        roles = load_roles()
        if name not in roles:
            bot.send_message(user_id, f"❌ <b>Ошибка!</b>\n\nРоль {name} не найдена", parse_mode='HTML')
        else:
            users = load_json(USERS_FILE)
            removed = 0
            for uid, u in users.items():
                if u.get('role') == name:
                    u['role'] = None
                    removed += 1
            del roles[name]
            save_roles(roles)
            save_json(USERS_FILE, users)
            bot.send_message(user_id, f"✅ <b>Роль удалена</b>\n\n🎭 {name}\n👥 У {removed} пользователей роль сброшена", parse_mode='HTML')
    except:
        bot.send_message(user_id, "❌ <b>Ошибка!</b>\n\nФормат: НАЗВАНИЕ", parse_mode='HTML')
    bot.send_message(user_id, "🔧 Админ панель", reply_markup=get_admin_panel())

def process_ban(message):
    user_id = message.from_user.id
    try:
        parts = message.text.split()
        target = int(parts[0])
        reason = ' '.join(parts[1:]) if len(parts) > 1 else "Не указана"
        users = load_json(USERS_FILE)
        users[str(target)]['is_banned'] = True
        users[str(target)]['ban_reason'] = reason
        save_json(USERS_FILE, users)
        bot.send_message(user_id, f"✅ <b>Готово!</b>\n\nПользователь {target} забанен\nПричина: {reason}", parse_mode='HTML')
        try:
            bot.send_message(target, f"🚫 <b>Вы забанены!</b>\n\nПричина: {reason}", parse_mode='HTML')
        except:
            pass
    except:
        bot.send_message(user_id, "❌ <b>Ошибка!</b>\n\nФормат: ID ПРИЧИНА", parse_mode='HTML')
    bot.send_message(user_id, "🔧 Админ панель", reply_markup=get_admin_panel())

def process_unban(message):
    user_id = message.from_user.id
    try:
        target = int(message.text.strip())
        users = load_json(USERS_FILE)
        users[str(target)]['is_banned'] = False
        users[str(target)]['ban_reason'] = None
        save_json(USERS_FILE, users)
        bot.send_message(user_id, f"✅ <b>Готово!</b>\n\nПользователь {target} разбанен", parse_mode='HTML')
        try:
            bot.send_message(target, "✅ <b>Вы разбанены!</b>", parse_mode='HTML')
        except:
            pass
    except:
        bot.send_message(user_id, "❌ <b>Ошибка!</b>\n\nФормат: ID", parse_mode='HTML')
    bot.send_message(user_id, "🔧 Админ панель", reply_markup=get_admin_panel())

def process_add_admin(message):
    user_id = message.from_user.id
    if not is_master(user_id):
        bot.send_message(user_id, "Нет доступа", parse_mode='HTML')
        return
    try:
        target = int(message.text.strip())
        admins = load_json(ADMINS_FILE)
        if 'admin_list' not in admins: admins['admin_list'] = {}
        admins['admin_list'][str(target)] = {'level': 'moderator', 'added_by': user_id, 'added_at': get_moscow_time().strftime('%Y-%m-%d %H:%M:%S')}
        save_json(ADMINS_FILE, admins)
        bot.send_message(user_id, f"✅ <b>Готово!</b>\n\nПользователь {target} назначен администратором", parse_mode='HTML')
        try:
            bot.send_message(target, "👑 <b>Вы стали администратором!</b>", parse_mode='HTML')
        except:
            pass
    except:
        bot.send_message(user_id, "❌ <b>Ошибка!</b>\n\nФормат: ID", parse_mode='HTML')
    bot.send_message(user_id, "🔧 Админ панель", reply_markup=get_admin_panel())

def process_remove_admin(message):
    user_id = message.from_user.id
    if not is_master(user_id):
        bot.send_message(user_id, "Нет доступа", parse_mode='HTML')
        return
    try:
        target = int(message.text.strip())
        if target in MASTER_IDS:
            bot.send_message(user_id, "❌ <b>Ошибка!</b>\n\nНельзя удалить владельца", parse_mode='HTML')
        else:
            admins = load_json(ADMINS_FILE)
            if str(target) in admins.get('admin_list', {}):
                del admins['admin_list'][str(target)]
                save_json(ADMINS_FILE, admins)
                bot.send_message(user_id, f"✅ <b>Готово!</b>\n\nАдминистратор {target} удалён", parse_mode='HTML')
                try:
                    bot.send_message(target, "🗑 <b>Вы были удалены из админов</b>", parse_mode='HTML')
                except:
                    pass
            else:
                bot.send_message(user_id, f"❌ Пользователь {target} не является администратором", parse_mode='HTML')
    except:
        bot.send_message(user_id, "❌ <b>Ошибка!</b>\n\nФормат: ID", parse_mode='HTML')
    bot.send_message(user_id, "🔧 Админ панель", reply_markup=get_admin_panel())

def process_mail(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(user_id, "Нет доступа", parse_mode='HTML')
        return
    users = load_json(USERS_FILE)
    sent = 0
    for uid in users:
        if int(uid) in MASTER_IDS: continue
        try:
            bot.send_message(int(uid), f"📢 <b>Рассылка от администрации</b>\n\n{message.text}", parse_mode='HTML')
            sent += 1
            time.sleep(0.05)
        except:
            pass
    bot.send_message(user_id, f"✅ <b>Рассылка завершена</b>\n\n📤 Отправлено: {sent}", parse_mode='HTML')
    bot.send_message(user_id, "🔧 Админ панель", reply_markup=get_admin_panel())

def process_user_add_coins(message, target_id):
    user_id = message.from_user.id
    try:
        amount = int(message.text.strip())
        add_coins(target_id, amount)
        bot.send_message(user_id, f"✅ <b>Готово!</b>\n\n+{amount}💰 пользователю {target_id}", parse_mode='HTML')
    except:
        bot.send_message(user_id, "❌ <b>Ошибка!</b>\n\nВведите число", parse_mode='HTML')
    bot.send_message(user_id, "🔧 Админ панель", reply_markup=get_admin_panel())

def process_user_remove_coins(message, target_id):
    user_id = message.from_user.id
    try:
        amount = int(message.text.strip())
        remove_coins(target_id, amount)
        bot.send_message(user_id, f"✅ <b>Готово!</b>\n\n-{amount}💰 пользователю {target_id}", parse_mode='HTML')
    except:
        bot.send_message(user_id, "❌ <b>Ошибка!</b>\n\nВведите число", parse_mode='HTML')
    bot.send_message(user_id, "🔧 Админ панель", reply_markup=get_admin_panel())

def process_user_give_role(message, target_id):
    user_id = message.from_user.id
    try:
        role = message.text.strip().capitalize()
        roles = load_roles()
        if role not in roles:
            bot.send_message(user_id, f"❌ <b>Ошибка!</b>\n\nРоль {role} не найдена", parse_mode='HTML')
        else:
            users = load_json(USERS_FILE)
            users[str(target_id)]['role'] = role
            save_json(USERS_FILE, users)
            bot.send_message(user_id, f"✅ <b>Готово!</b>\n\nРоль {role} выдана пользователю {target_id}", parse_mode='HTML')
    except:
        bot.send_message(user_id, "❌ <b>Ошибка!</b>\n\nВведите название роли", parse_mode='HTML')
    bot.send_message(user_id, "🔧 Админ панель", reply_markup=get_admin_panel())

def process_user_ban(message, target_id):
    user_id = message.from_user.id
    try:
        reason = message.text.strip()
        users = load_json(USERS_FILE)
        users[str(target_id)]['is_banned'] = True
        users[str(target_id)]['ban_reason'] = reason
        save_json(USERS_FILE, users)
        bot.send_message(user_id, f"✅ <b>Готово!</b>\n\nПользователь {target_id} забанен\nПричина: {reason}", parse_mode='HTML')
        try:
            bot.send_message(target_id, f"🚫 <b>Вы забанены!</b>\n\nПричина: {reason}", parse_mode='HTML')
        except:
            pass
    except:
        bot.send_message(user_id, "❌ <b>Ошибка!</b>", parse_mode='HTML')
    bot.send_message(user_id, "🔧 Админ панель", reply_markup=get_admin_panel())

# ========== ПРОМОКОДЫ ==========
@bot.message_handler(commands=['createpromo'])
def create_promo(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Нет доступа")
        return
    try:
        parts = message.text.split()
        code = parts[1].upper()
        coins = int(parts[2])
        max_uses = int(parts[3])
        days = int(parts[4]) if len(parts) > 4 else 7
        promos = load_json(PROMO_FILE)
        promos[code] = {'type': 'coins', 'coins': coins, 'max_uses': max_uses, 'used': 0, 'used_by': [], 'expires_at': (get_moscow_time() + timedelta(days=days)).isoformat()}
        save_json(PROMO_FILE, promos)
        bot.reply_to(message, f"✅ <b>Промокод создан</b>\n\nКод: {code}\nМонеты: {coins}💰\nЛимит: {max_uses}\nДней: {days}", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ /createpromo КОД СУММА ЛИМИТ ДНИ")

@bot.message_handler(commands=['createrole'])
def create_role_promo(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Нет доступа")
        return
    try:
        parts = message.text.split()
        code = parts[1].upper()
        role = parts[2].capitalize()
        days = int(parts[3])
        max_uses = int(parts[4])
        roles = load_roles()
        if role not in roles:
            bot.reply_to(message, f"❌ Роль {role} не найдена")
            return
        promos = load_json(PROMO_FILE)
        promos[code] = {'type': 'role', 'role': role, 'days': days, 'max_uses': max_uses, 'used': 0, 'used_by': [], 'expires_at': (get_moscow_time() + timedelta(days=30)).isoformat()}
        save_json(PROMO_FILE, promos)
        bot.reply_to(message, f"✅ <b>Промокод на роль создан</b>\n\nКод: {code}\nРоль: {role}\nДней: {days}\nЛимит: {max_uses}", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ /createrole КОД РОЛЬ ДНИ ЛИМИТ")

@bot.message_handler(commands=['use'])
def use_promo(message):
    if message.chat.type != 'private': return
    user_id = message.from_user.id
    try:
        code = message.text.split()[1].upper()
        promos = load_json(PROMO_FILE)
        if code not in promos:
            bot.reply_to(message, "❌ Промокод не найден")
            return
        promo = promos[code]
        if datetime.fromisoformat(promo['expires_at']) < get_moscow_time():
            bot.reply_to(message, "❌ Промокод истёк")
            return
        if promo['used'] >= promo['max_uses']:
            bot.reply_to(message, "❌ Промокод уже использован")
            return
        if str(user_id) in promo.get('used_by', []):
            bot.reply_to(message, "❌ Вы уже использовали этот промокод")
            return
        if promo['type'] == 'coins':
            add_coins(user_id, promo['coins'])
            promo['used'] += 1
            promo['used_by'].append(str(user_id))
            save_json(PROMO_FILE, promos)
            bot.reply_to(message, f"✅ <b>Промокод активирован!</b>\n\n+{promo['coins']}💰", parse_mode='HTML')
        elif promo['type'] == 'role':
            users = load_json(USERS_FILE)
            users[str(user_id)]['role'] = promo['role']
            save_json(USERS_FILE, users)
            promo['used'] += 1
            promo['used_by'].append(str(user_id))
            save_json(PROMO_FILE, promos)
            bot.reply_to(message, f"✅ <b>Промокод активирован!</b>\n\nВы получили роль {promo['role']} на {promo['days']} дней", parse_mode='HTML')
    except IndexError:
        bot.reply_to(message, "❌ /use КОД")

@bot.message_handler(commands=['setphoto'])
def set_photo_command(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Нет доступа")
        return
    try:
        parts = message.text.split()
        key = parts[1]
        if key not in IMAGES:
            bot.reply_to(message, f"❌ Неверный ключ. Доступные: {', '.join(IMAGES.keys())}")
            return
        if message.reply_to_message and message.reply_to_message.photo:
            bot.reply_to(message, f"✅ Фото для {key} обновлено (временно, для постоянного нужно менять код)", parse_mode='HTML')
        else:
            bot.reply_to(message, "❌ Ответьте на фото командой /setphoto КЛЮЧ", parse_mode='HTML')
    except:
        bot.reply_to(message, "❌ /setphoto КЛЮЧ (ответ на фото)\n\nДоступные ключи: main, shop, profile, market, workshop, bonus, leaders, help", parse_mode='HTML')

# ========== НАЧИСЛЕНИЕ ЗА СООБЩЕНИЯ ==========
@bot.message_handler(func=lambda m: m.chat.type != 'private' and not m.from_user.is_bot)
def handle_chat(m):
    add_message(m.from_user.id)
    check_referral_reward(m.from_user.id)

# ========== ФОНОВЫЙ ПОТОК ==========
def market_cleaner():
    while True:
        time.sleep(3600)
        try:
            cleanup_expired_lots()
        except:
            pass

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    for f in [USERS_FILE, PROMO_FILE, ADMINS_FILE, ROLES_FILE, MARKET_FILE, REPORTS_FILE, IDEAS_FILE, SETTINGS_FILE]:
        if not os.path.exists(f):
            save_json(f, {} if 'admin' not in f else {'admin_list': {}})
    print("="*60)
    print("🌟 ROLE SHOP BOT — ФИНАЛЬНАЯ ВЕРСИЯ 🌟")
    print("="*60)
    print(f"👑 Владелец: {MASTER_IDS[0]}")
    print(f"🎭 Доступно ролей: {len(load_roles())}")
    print("="*60)
    print("✅ БОТ ГОТОВ К РАБОТЕ!")
    print("📌 Команда: /startrole")
    print("="*60)
    threading.Thread(target=market_cleaner, daemon=True).start()
    while True:
        try:
            bot.infinity_polling(timeout=10)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)