try:
    import telebot
    from telebot import types
except ImportError:
    print("Ошибка: telebot не установлен. pip install pyTelegramBotAPI")
    exit(1)

import random
import json
import os

TOKEN = "7766594100:AAH7j4yGEW5Tqoiu8IguYh0Mn3g7lMbPwj8"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 8388843828

USERS_FILE = "guess_users.json"
WORDS_FILE = "guess_words.json"

# БОЛЬШОЙ СЛОВАРЬ РЕАЛЬНЫХ СЛОВ (одной строкой)
RUSSIAN_WORDS = "КОТ,ДОМ,ЛЕС,САД,ДУБ,МАК,РОЗА,МАМА,ПАПА,СЫН,ДОЧЬ,БРАТ,СЕСТРА,ДРУГ,МИР,ДЕНЬ,НОЧЬ,ГОД,ЧАС,МИНУТА,СЕКУНДА,ГОРОД,СОЛНЦЕ,ЗВЕЗДА,КНИГА,СТОЛ,СТУЛ,ОКНО,ДВЕРЬ,РУЧКА,МАШИНА,УЛИЦА,ПАРК,ЛУНА,ЗЕМЛЯ,ВОДА,ОГОНЬ,ВЕТЕР,СНЕГ,ДОЖДЬ,ЛЕТО,ЗИМА,ВЕСНА,ОСЕНЬ,УТРО,ВЕЧЕР,ЗВУК,СВЕТ,ТЕНЬ,ЦВЕТ,ВКУС,ЗАПАХ,ГОЛОС,СЛОВО,БУКВА,ЦИФРА,НОМЕР,АДРЕС,ГОРОД,СТРАНА,МИР,ПЛАНЕТА,ЗВЕЗДА,ГАЛАКТИКА,ВСЕЛЕННАЯ,ПРИРОДА,ЖИВОТНОЕ,РАСТЕНИЕ,ЧЕЛОВЕК,СЧАСТЬЕ,ЛЮБОВЬ,ДРУЖБА,УЧИТЕЛЬ,ШКОЛА,УНИВЕРСИТЕТ,БИБЛИОТЕКА,МАГАЗИН,АПТЕКА,БОЛЬНИЦА,РЕСТОРАН,КАФЕ,КИНО,ТЕАТР,МУЗЕЙ,ПАРК,ЛЕС,РЕКА,МОРЕ,ОКЕАН,ГОРА,НЕБО,ОБЛАКО,ВЕТЕР,БУРЯ,ГРОЗА,МОЛНИЯ,ГРАД,ТУМАН,РОСА,ИНЕЙ,ЛЕД,СНЕГ,ДОЖДЬ,СОЛНЦЕ,ЛУНА,ЗВЕЗДА,КОСМОС,РАКЕТА,СПУТНИК,ОРБИТА,ТЕЛЕФОН,КОМПЬЮТЕР,НОУТБУК,ПЛАНШЕТ,ЭКРАН,КЛАВИАТУРА,МЫШЬ,ПРИНТЕР,СКАНЕР,ИНТЕРНЕТ,САЙТ,ПРОГРАММА,ИГРА,ФИЛЬМ,МУЗЫКА,ПЕСНЯ,ТАНЕЦ,РИСУНОК,ФОТОГРАФИЯ,КАРТИНА,ЦВЕТОК,ДЕРЕВО,КУСТ,ТРАВА,ЛИСТ,ВЕТКА,КОРЕНЬ,СТВОЛ,ПЛОД,ЯГОДА,ГРИБ,ОВОЩ,ФРУКТ,ХЛЕБ,МОЛОКО,МЯСО,РЫБА,ПТИЦА,ЗВЕРЬ,НАСЕКОМОЕ,РЫБА,КИТ,ДЕЛЬФИН,АКУЛА,МЕДВЕДЬ,ВОЛК,ЛИСА,ЗАЯЦ,ЛОСЬ,ОЛЕНЬ,ТИГР,ЛЕВ,СЛОН,ЖИРАФ,ОБЕЗЬЯНА,КЕНГУРУ,ПАНДА,КОАЛА,ПИНГВИН,ОРЁЛ,СОКОЛ,ВОРОН,ВОРОБЕЙ,СИНИЦА,ГОЛУБЬ,КУРИЦА,ПЕТУХ,КОРОВА,БЫК,ЛОШАДЬ,СВИНЬЯ,ОВЦА,КОЗА,СОБАКА,КОШКА,МЫШЬ,КРЫСА,ХОМЯК,КРОЛИК,ЧЕРЕПАХА,ЗМЕЯ,ЯЩЕРИЦА,ЛЯГУШКА,РЫБА,КАРАСЬ,ЩУКА,ОКУНЬ,СОМ,ЛОСОСЬ,ФОРЕЛЬ,КРАБ,КРЕВЕТКА,ОСЬМИНОГ,МЕДУЗА,БАБОЧКА,СТРЕКОЗА,ПЧЕЛА,ОСА,ШМЕЛЬ,МУРАВЕЙ,ПАУК,ЖУК,КУЗНЕЧИК,СВЕРЧОК,МУХА,КОМАР,БЛОХА,ВОШЬ,КЛЕЩ,ЧЕРВЬ,ГУСЕНИЦА,УЛИТКА,РАКУШКА,КОРАЛЛ,ВОДОРОСЛЬ,ГРИБ,ПОДБЕРЁЗОВИК,ПОДОСИНОВИК,БЕЛЫЙ,ЛИСИЧКА,ОПЁНОК,МУХОМОР,ПОГАНКА,ЯБЛОКО,ГРУША,СЛИВА,ВИШНЯ,ЧЕРЕШНЯ,АПЕЛЬСИН,МАНДАРИН,ЛИМОН,БАНАН,АНАНАС,КИВИ,МАНГО,АРБУЗ,ДЫНЯ,ВИНОГРАД,КЛУБНИКА,МАЛИНА,ЕЖЕВИКА,СМОРОДИНА,КРЫЖОВНИК,ЧЕРНИКА,ГОЛУБИКА,КЛЮКВА,БРУСНИКА,РЯБИНА,КАЛИНА,ОГУРЕЦ,ПОМИДОР,КАРТОФЕЛЬ,МОРКОВЬ,СВЁКЛА,ЛУК,ЧЕСНОК,КАПУСТА,БАКЛАЖАН,ПЕРЕЦ,ТЫКВА,КАБАЧОК,РЕДИС,РЕПА,РЕДЬКА,ХРЕН,ПЕТРУШКА,УКРОП,САЛАТ,ШПИНАТ,ФАСОЛЬ,ГОРОХ,КУКУРУЗА,ПШЕНИЦА,РЖЬ,ОВЁС,ЯЧМЕНЬ,ГРЕЧКА,РИС,ПШЕНО,МАНКА,ХЛЕБ,БУЛКА,ПИРОГ,ТОРТ,ПЕЧЕНЬЕ,КОНФЕТА,ШОКОЛАД,МОРОЖЕНОЕ,ВАРЕНЬЕ,МЁД,САХАР,СОЛЬ,МАСЛО,СЫР,ТВОРОГ,СМЕТАНА,ЙОГУРТ,КЕФИР,РЯЖЕНКА,ПРОСТОКВАША,МОЛОКО,СЛИВКИ,МАСЛО,МАРГАРИН,МАЙОНЕЗ,КЕТЧУП,ГОРЧИЦА,УКСУС,СОУС,СУП,БОРЩ,ЩИ,ОКРОШКА,СОЛЯНКА,УХА,КАША,ПЛОВ,МАКАРОНЫ,ПЕЛЬМЕНИ,ВАРЕНИКИ,БЛИНЫ,ОЛАДЬИ,СЫРНИКИ,ЗАПЕКАНКА,КОТЛЕТА,БИФШТЕКС,СТЕЙК,ШАШЛЫК,КУРИЦА,ИНДЕЙКА,УТКА,ГУСЬ,РЫБА,СЕЛЬДЬ,КИЛЬКА,ШПРОТЫ,САРДИНЫ,ТУНЕЦ,СКУМБРИЯ,СТАВРИДА,МОЙВА,КОРЮШКА,КАМБАЛА,ПАЛТУС,ТРЕСКА,МИНТАЙ,ПИКША,ХЕК,МЕРЛУЗА,ДОРАДО,СИБАС,ФОРЕЛЬ,СЁМГА,ЛОСОСЬ,ОСЕТР,БЕЛУГА,ИКРА,КАЛЬМАР,КРЕВЕТКА,МИДИЯ,УСТРИЦА,РАК,КРАБ,ЛАНГУСТ,ОМАР,КОЛБАСА,СОСИСКА,САРДЕЛЬКА,ВЕТЧИНА,БАЛЫК,БЕКОН,САЛО,ШПИК,ПАШТЕТ,КОНСЕРВЫ,ПРЕЗЕРВЫ,ВАРЕНЬЕ,ДЖЕМ,ПОВИДЛО,МАРМЕЛАД,ЗЕФИР,ПАСТИЛА,ХАЛВА,НУГА,ИРИС,КАРАМЕЛЬ,ЛЕДЕНЕЦ,ЧУПАЧУПС,ЖВАЧКА,ГАЗИРОВКА,ЛИМОНАД,КОМПОТ,КИСЕЛЬ,МОРС,СОК,ВОДА,ЧАЙ,КОФЕ,КАКАО,ГОРЯЧИЙ,ХОЛОДНЫЙ,ТЁПЛЫЙ,СВЕЖИЙ,СТАРЫЙ,НОВЫЙ,КРАСИВЫЙ,УРОДЛИВЫЙ,БОЛЬШОЙ,МАЛЕНЬКИЙ,ВЫСОКИЙ,НИЗКИЙ,ШИРОКИЙ,УЗКИЙ,ДЛИННЫЙ,КОРОТКИЙ,ТОЛСТЫЙ,ТОНКИЙ,ТЯЖЁЛЫЙ,ЛЁГКИЙ,БЫСТРЫЙ,МЕДЛЕННЫЙ,СИЛЬНЫЙ,СЛАБЫЙ,УМНЫЙ,ГЛУПЫЙ,ВЕСЁЛЫЙ,ГРУСТНЫЙ,ДОБРЫЙ,ЗЛОЙ,ХОРОШИЙ,ПЛОХОЙ,ЧИСТЫЙ,ГРЯЗНЫЙ,СВЕТЛЫЙ,ТЁМНЫЙ,ЯРКИЙ,ТУСКЛЫЙ,ГРОМКИЙ,ТИХИЙ,СЛАДКИЙ,СОЛЁНЫЙ,КИСЛЫЙ,ГОРЬКИЙ,ОСТРЫЙ,ПРЕСНЫЙ,ВКУСНЫЙ,НЕВКУСНЫЙ,ПОЛЕЗНЫЙ,ВРЕДНЫЙ,ИНТЕРЕСНЫЙ,СКУЧНЫЙ,ЛЮБИМЫЙ,НЕНАВИСТНЫЙ,РОДНОЙ,ЧУЖОЙ,СВОЙ,ЧУЖОЙ,ОБЩИЙ,ЧАСТНЫЙ,ГЛАВНЫЙ,ВТОРОСТЕПЕННЫЙ,ПЕРВЫЙ,ВТОРОЙ,ТРЕТИЙ,ПОСЛЕДНИЙ,ОДИН,ДВА,ТРИ,ЧЕТЫРЕ,ПЯТЬ,ШЕСТЬ,СЕМЬ,ВОСЕМЬ,ДЕВЯТЬ,ДЕСЯТЬ,СТО,ТЫСЯЧА,МИЛЛИОН,МИЛЛИАРД"

ENGLISH_WORDS = "CAT,DOG,SUN,MOON,STAR,TREE,FLOWER,BIRD,FISH,CAR,BUS,MOM,DAD,SON,DAUGHTER,BROTHER,SISTER,FRIEND,LOVE,HOPE,HOUSE,APPLE,WATER,FIRE,EARTH,WIND,CLOUD,RAIN,SNOW,SUMMER,WINTER,SPRING,AUTUMN,DAY,NIGHT,YEAR,MONTH,WEEK,HOUR,MINUTE,SECOND,CITY,TOWN,STREET,PARK,GARDEN,FOREST,RIVER,LAKE,SEA,OCEAN,MOUNTAIN,HILL,VALLEY,DESERT,ISLAND,BEACH,SKY,SUN,MOON,STAR,PLANET,GALAXY,UNIVERSE,SPACE,ROCKET,ASTRONAUT,COMPUTER,LAPTOP,PHONE,TABLET,SCREEN,KEYBOARD,MOUSE,PRINTER,SCANNER,INTERNET,WEBSITE,PROGRAM,GAME,MOVIE,MUSIC,SONG,DANCE,PICTURE,PHOTO,PAINTING,COLOR,RED,BLUE,GREEN,YELLOW,BLACK,WHITE,PURPLE,PINK,ORANGE,BROWN,GRAY,GOLD,SILVER,COPPER,BRONZE,WOOD,STONE,GLASS,METAL,PLASTIC,PAPER,FABRIC,LEATHER,WOOL,COTTON,SILK,LINEN,VELVET,SATIN,DENIM,JEANS,SHIRT,PANTS,DRESS,SKIRT,JACKET,COAT,HAT,CAP,SHOES,BOOTS,SANDALS,SNEAKERS,SOX,GLOVES,SCARF,BELT,WATCH,RING,NECKLACE,EARRINGS,BRACELET,GLASSES,PHONE,COMPUTER,TABLE,CHAIR,SOFA,BED,DESK,LAMP,WINDOW,DOOR,WALL,FLOOR,CEILING,ROOM,KITCHEN,BATHROOM,BEDROOM,LIVINGROOM,DININGROOM,GARAGE,GARDEN,YARD,FENCE,GATE,ROOF,CHIMNEY,DRIVE,LANE,ROAD,STREET,AVENUE,BOULEVARD,BRIDGE,TUNNEL,CROSSROAD,TRAFFIC,LIGHT,SIGN,BIKE,MOTORCYCLE,TRUCK,VAN,BUS,TRAIN,PLANE,SHIP,BOAT,SUBMARINE,HELICOPTER,DRONE,ROCKET,SATELLITE,SPACESHIP,TEACHER,STUDENT,DOCTOR,NURSE,ENGINEER,SCIENTIST,ARTIST,MUSICIAN,WRITER,POET,ACTOR,SINGER,DANCER,ATHLETE,COACH,TRAINER,MANAGER,WORKER,EMPLOYEE,BOSS,LEADER,PRESIDENT,KING,QUEEN,PRINCE,PRINCESS,KNIGHT,SOLDIER,POLICE,FIREFIGHTER,PILOT,SAILOR,FARMER,COOK,CHEF,WAITER,DRIVER,PILOT,GUIDE,TOURIST,VISITOR,GUEST,HOST,FRIEND,ENEMY,NEIGHBOR,COLLEAGUE,PARTNER,COMPANION,STRANGER,CHILD,ADULT,BABY,KID,TEENAGER,YOUTH,ELDER,SENIOR,MALE,FEMALE,MAN,WOMAN,BOY,GIRL,GENTLEMAN,LADY,PERSON,PEOPLE,FAMILY,RELATIVE,ANCESTOR,DESCENDANT,MARRIAGE,WEDDING,DIVORCE,BIRTH,DEATH,LIFE,HEALTH,SICKNESS,DISEASE,MEDICINE,TREATMENT,HOSPITAL,CLINIC,PHARMACY,DOCTOR,NURSE,PATIENT,AMBULANCE,EMERGENCY,ACCIDENT,INJURY,PAIN,SUFFERING,HEALING,RECOVERY,EXERCISE,SPORT,GAME,PLAY,COMPETITION,TOURNAMENT,CHAMPIONSHIP,VICTORY,DEFEAT,WIN,LOSS,TIE,SCORE,POINT,GOAL,TEAM,PLAYER,FAN,SPECTATOR,STADIUM,ARENA,COURT,FIELD,TRACK,POOL,GYM,YOGA,MEDITATION,RUNNING,WALKING,JUMPING,SWIMMING,CYCLING,DRIVING,FLYING,SAILING,CLIMBING,HIKING,CAMPING,FISHING,HUNTING,COOKING,BAKING,GRILLING,EATING,DRINKING,SLEEPING,RESTING,WAKING,DREAMING,THINKING,LEARNING,TEACHING,READING,WRITING,COUNTING,CALCULATING,MEASURING,WEIGHING,MIXING,STIRRING,POURING,CUTTING,CHOPPING,PEELING,WASHING,CLEANING,SWEEPING,MOPPING,VACUUMING,DUSTING,POLISHING,ORGANIZING,SORTING,ARRANGING,DECORATING,PAINTING,DRAWING,SCULPTING,BUILDING,CONSTRUCTING,CREATING,MAKING,FIXING,REPAIRING,IMPROVING,CHANGING,MOVING,GROWING,DEVELOPING,EVOLVING,TRANSFORMING"

# Превращаем строки в списки
RUSSIAN_WORDS_LIST = RUSSIAN_WORDS.split(",")
ENGLISH_WORDS_LIST = ENGLISH_WORDS.split(",")

SHOP_ITEMS = {
    "hint": {"price": 50, "emoji": "🔍", "name": "Подсказка"},
    "reroll": {"price": 100, "emoji": "🔄", "name": "Сменить слово"},
    "shield": {"price": 150, "emoji": "🛡️", "name": "Защита"},
    "double": {"price": 500, "emoji": "💎", "name": "Кристалл x2"}
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
    """Берёт случайное слово из большого словаря"""
    if lang == "ru":
        return random.choice(RUSSIAN_WORDS_LIST)
    else:
        return random.choice(ENGLISH_WORDS_LIST)

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
            return f"🔍 Подсказка: буква {hint_letter} есть в слове!"
        return "❌ Все буквы уже открыты!"
    
    def reroll_word(self):
        self.word = get_word(self.lang).upper()
        self.guessed_letters = []
        self.wrong_letters = []
        self.attempts = 6
        return f"🔄 Слово заменено на: {self.get_display_word()}"

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
                menu_text = f"""🎮 УГАДАЙ СЛОВО

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}"""
                bot.send_message(message.chat.id, menu_text, reply_markup=main_menu_kb())
            else:
                new_text = game.get_game_text(msg)
                try:
                    bot.edit_message_text(new_text, game.chat_id, game.message_id, reply_markup=game_kb())
                except Exception as e:
                    print(f"Ошибка обновления: {e}")
            
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
    else:
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
    user = get_user(user_id)
    lang = user.get('lang', 'ru')
    
    if data == "back_to_main":
        text = f"""🎮 УГАДАЙ СЛОВО

💰 Кристаллов: {user['crystals']}
🏆 Побед: {user['wins']}"""
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
        user['lang'] = 'ru'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "🇷🇺 Язык: русский")
        text = f"🎮 УГАДАЙ СЛОВО\n\n💰 Кристаллов: {user['crystals']}\n🏆 Побед: {user['wins']}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb())
    
    elif data == "lang_en":
        user['lang'] = 'en'
        update_user(user_id, user)
        bot.answer_callback_query(call.id, "🇬🇧 Language: English")
        text = f"🎮 GUESS THE WORD\n\n💰 Crystals: {user['crystals']}\n🏆 Wins: {user['wins']}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb())
    
    elif data == "start_game":
        lang = user.get('lang', 'ru')
        
        if user_id in active_games and active_games[user_id].active:
            bot.answer_callback_query(call.id, "У вас уже есть активная игра!", show_alert=True)
            return
        
        text = "🎮 НАЧИНАЕМ ИГРУ..."
        sent = bot.send_message(call.message.chat.id, text)
        
        game = Game(call.message.chat.id, user_id, lang, sent.message_id)
        active_games[user_id] = game
        
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
    
    elif data == "stats":
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
        text = f"🎮 УГАДАЙ СЛОВО\n\n💰 Кристаллов: {user['crystals']}\n🏆 Побед: {user['wins']}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu_kb())
    
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
        for lang_key, word_list in words.items():
            text += f"{lang_key}: {', '.join(word_list[:15])}\n"
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
    print(f"📚 Русских слов: {len(RUSSIAN_WORDS_LIST)}")
    print(f"📚 Английских слов: {len(ENGLISH_WORDS_LIST)}")
    print("Команды: /start, /stats, /top, /shop, /lang, /help, /admin")
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")