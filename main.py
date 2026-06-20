import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Сюди вставляєш токен від BotFather
TOKEN = "8825318226:AAHOTveqoEF8Hx23rUuc4sID-UmJMnNoRFs"

bot = Bot(token=TOKEN)
dp = Dispatcher()

games = {}

# 1. Класичні локації (50 штук)
classic_locations = [
    "🏨 Готель", "🏫 Школа", "🏥 Лікарня", "🏦 Банк", "🏢 Супермаркет", 
    "🚒 Пожежна частина", "👮 Поліцейська дільниця", "🏛 Музей", "📚 Бібліотека", "⛪ Церква",
    "🚢 Підводний човен", "✈️ Літак", "🚀 Космічна станція", "🚂 Потяг", "🛳 Круїзний лайнер", 
    "🛸 НЛО", "🏴‍☠️ Піратський корабель", "🚌 Шкільний автобус", "🚕 Автосервіс", "⛽ Заправка",
    "🎪 Цирк", "🎡 Парк атракціонів", "🏖 Пляж", "🍿 Кінотеатр", "🎭 Театр", 
    "🏟 Стадіон", "🎰 Казино", "💃 Нічний клуб", "🧗 Скеледром", "🎿 Гірськолижний курорт",
    "🍕 Піцерія", "☕ Кав'явня", "🥩 Ресторан", "🍺 Паб", "🍭 Магазин іграшок",
    "🌳 Зоопарк", "🌵 Пустеля", "🌴 Джунглі", "🌋 Вулкан", "❄️ Антарктична станція", 
    "⛏ Шахта", "🏕 Кемпінг у лісі", "🏜 Оазис", "🌊 Безлюдний острів", "🪐 Марсіанська база",
    "⚔️ Середньовічний замок", "🎖 Військова база", "🧪 Наукова лабораторія", "👑 Королівський палац", "🎬 Кіностудія"
]

# 2. Список бійців з Clash Royale
clash_royale_cards = [
    "⚔️ П.Е.К.К.А (P.E.K.K.A)", "🐗 Вершник на кабані (Hog Rider)", "🛡️ Мегалицар (Mega Knight)", 
    "⚡ Електромаг (Electro Wizard)", "🪵 Колода (The Log)", "🏹 Принцеса (Princess)", 
    "👑 Шахтар (Miner)", "🧙‍♂️ Маг (Wizard)", "🦇 Нічна відьма (Night Witch)", 
    "🧱 Гіліам / Гігант (Giant)", "☠️ Гігантський скелет (Giant Skeleton)", "🎈 Повітряна куля (Balloon)", 
    "🐉 Плазмовий дракон (Inferno Dragon)", "👻 Привид (Royal Ghost)", "🏹 Лучники (Archers)", 
    "🪓 Кат (Executioner)", "🐐 Вершниця на барані (Ram Rider)", "⚡ Іскромет (Sparky)", 
    "🤖 Маленький П.Е.К.К.А (Mini P.E.K.K.A)", "🛡️ Темний лицар (Dark Prince)", " Valkyrie (Валкірія)", 
    "🦁 Загадкові Елітні варвари", "🧊 Крижаний маг (Ice Wizard)", "🔮 Відьма (Witch)", " Muskelteer (Мушкетер)"
]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привіт! Граємо в Шпигуна з одного телефону. 📱\n"
        "Скільки людей буде грати? Напиши просто цифрою (наприклад: 5)"
    )

# Ловимо введення кількості гравців
@dp.message(F.text.regexp(r'^\d+$'))
async def get_players_count(message: types.Message):
    count = int(message.text)
    
    if count < 3:
        await message.answer("Для гри потрібно хоча б 3 гравці! Напиши більшу цифру.")
        return

    # Тимчасово зберігаємо кількість гравців у пам'ять
    games[message.chat.id] = {"players_count": count}

    # Створюємо меню вибору режиму гри
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Класичний Шпигун (50 локацій)", callback_data="mode_classic")],
        [InlineKeyboardButton(text="👑 Режим Clash Royale (Бійці)", callback_data="mode_clash")]
    ])
    
    await message.answer("Оберіть режим гри:", reply_markup=keyboard)

# Обробка вибору режиму
@dp.callback_query(F.data.startswith("mode_"))
async def choose_mode_handler(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    
    if chat_id not in games:
        await callback.message.edit_text("Помилка! Почніть гру заново через /start")
        return

    mode = callback.data.split("_")[1]
    count = games[chat_id]["players_count"]

    # Визначаємо пул секретів та ім'я шпигуна залежно від режиму
    if mode == "classic":
        secret_pool = classic_locations
        spy_name = "🕵️‍♂️ ШПИГУН"
        mode_text = "Класичний"
    else:
        secret_pool = clash_royale_cards
        spy_name = "🎭 ГОБЛІН-ШПИГУН (Clash Royale)"
        mode_text = "Clash Royale 👑"

    # Вибираємо випадковий секрет (локацію чи карту)
    chosen_secret = random.choice(secret_pool)
    
    # Генеруємо ролі
    roles = [spy_name] + [f"🃏 Твоя карта: {chosen_secret}" if mode == "clash" else f"📍 Локація: {chosen_secret}"] * (count - 1)
    random.shuffle(roles)

    # Оновлюємо дані гри
    games[chat_id].update({
        "current_player": 1,
        "roles": roles,
        "mode_text": mode_text
    })

    # Кнопка для першого гравця
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👁 Гравець 1: Дізнатися роль", callback_data="show_role")]
    ])
    
    await callback.message.edit_text(
        f"Режим: **{mode_text}**\n"
        f"Гру на {count} гравців створено! Передайте телефон першому гравцю.", 
        parse_mode="Markdown", 
        reply_markup=keyboard
    )

# Показ ролі (таймер на 3 секунди)
@dp.callback_query(F.data == "show_role")
async def show_role_handler(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    
    if chat_id not in games or "roles" not in games[chat_id]:
        await callback.message.edit_text("Гра не знайдена. Напишіть /start")
        return

    game = games[chat_id]
    current = game["current_player"]
    role = game["roles"][current - 1]

    await callback.message.edit_text(
        f"Гравець {current}, твоя роль:\n\n"
        f"**{role}**\n\n"
        f"⏳ *(Зникне через 3 секунди...)*",
        parse_mode="Markdown"
    )
    
    await asyncio.sleep(3)

    if current < game["players_count"]:
        game["current_player"] += 1
        next_player = game["current_player"]
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"👁 Гравець {next_player}: Дізнатися роль", callback_data="show_role")]
        ])
        
        await callback.message.edit_text(
            f"✅ Роль сховано!\n\nПередайте телефон наступному.\nЗараз черга: Гравець {next_player}.", 
            reply_markup=keyboard
        )
    else:
        await callback.message.edit_text(
            f"🎭 **Усі гравці дізналися свої ролі!** 🎭\n\n"
            f"Режим: {game['mode_text']}\n"
            f"Час починати обговорення! Першим запитує Гравець 1.\n\n"
            f"Щоб почати заново, просто введіть кількість гравців.",
            parse_mode="Markdown"
        )
        del games[chat_id]

async def main():
    print("Бот запущений з двома режимами!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())