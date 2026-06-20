import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# Сюди вставляєш токен від BotFather
TOKEN = "8825318226:AAHOTveqoEF8Hx23rUuc4sID-UmJMnNoRFs"

bot = Bot(token=TOKEN)
dp = Dispatcher()
games = {}

# ВЕЛИЧЕЗНИЙ СПИСОК КЛАСИЧНИХ ЛОКАЦІЙ
classic_locations = [
    "🏨 Готель", "🏫 Школа", "🏥 Лікарня", "🏦 Банк", "🏢 Супермаркет", 
    "🚒 Пожежна частина", "👮 Поліцейська дільниця", "🏛 Музей", "📚 Бібліотека", "⛪ Церква",
    "🚢 Підводний човен", "✈️ Літак", "🚀 Космічна станція", "🚂 Потяг", "🛳 Круїзний лайнер",
    "🏰 Замок", "🎭 Театр", "🎪 Цирк", "🎰 Казино", "🌋 Вулкан", 
    "🛸 Корабель прибульців", "⛏️ Шахта", "🏝️ Безлюдний острів", "🍕 Піцерія", "ж Вокзал",
    "🪖 Військова база", "🧪 Лабораторія", "🎥 Кіностудія", "🏟️ Стадіон", "🏎️ Трек Формули-1"
]

# АБСОЛЮТНО ВСІ ПЕРСОНАЖІ ТА КАРТИ З CLASH ROYALE
clash_royale_cards = [
    "⚔️ П.Е.К.К.А (P.E.K.K.A)", "🐗 Вершник на кабані (Hog Rider)", "🛡️ Мегалицар (Mega Knight)", 
    "⚡ Електромаг (Electro Wizard)", "🪵 Колода (The Log)", "🏹 Принцеса (Princess)",
    "👑 Король (King)", "👸 Королева ЛучOperation (Archer Queen)", "🧱 Хранителі (Guardians)",
    "🤴 Принц (Prince)", "🐴 Темний Принц (Dark Prince)", "☠️ Армія Скелетів (Skeleton Army)",
    "🧙‍♂️ Маг (Wizard)", "❄️ Крижаний Маг (Ice Wizard)", "👺 Гобліни (Goblins)", 
    "🎯 Мушкетер (Musketeer)", "🛡️ Лицар (Knight)", "🦇 Кажани (Bats)",
    "🐉 Полум'яний Дракон (Inferno Dragon)", "👻 Привид (Royal Ghost)", "🏹 Лучники (Archers)",
    "💣 Гігантський Скелет (Giant Skeleton)", "🧔 Гігант (Giant)", "⚡ Іскриста (Sparky)",
    "🎈 Повітряна куля (Balloon)", "⛏️ Шахтар (Miner)", "🧙‍♀️ Відьма (Witch)", 
    "🦇 Нічна Відьма (Night Witch)", "🐐 Вершниця на барані (Ram Rider)", "🪵 Ка can (Executioner)",
    "🪓 Валькірія (Valkyrie)", "🩻 Скелет-Еволюція (Evolved Skeleton)", "👑 Королівський Гігант (Royal Giant)"
]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Скільки людей грає? Напиши цифру:")

@dp.message(F.text.regexp(r'^\d+$'))
async def get_players_count(message: types.Message):
    count = int(message.text)
    if count < 3:
        await message.answer("Треба хоча б 3 гравці!")
        return
    games[message.chat.id] = {"players_count": count}
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌍 Класичний Шпигун", callback_data="mode_classic")],
        [InlineKeyboardButton(text="👑 Режим Clash Royale", callback_data="mode_clash")]
    ])
    await message.answer("Оберіть режим:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("mode_"))
async def choose_mode_handler(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    mode = callback.data.split("_")[1]
    count = games[chat_id]["players_count"]
    
    secret_pool = classic_locations if mode == "classic" else clash_royale_cards
    spy_name = "🕵️‍♂️ ШПИГУН" if mode == "classic" else "🎭 ГОБЛІН-ШПИГУН"
    
    chosen_secret = random.choice(secret_pool)
    roles = [spy_name] + [f"📍 Локація/Карта: {chosen_secret}"] * (count - 1)
    random.shuffle(roles)
    
    games[chat_id].update({"current_player": 1, "roles": roles})
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="👁 Гравець 1: Роль", callback_data="show_role")]])
    await callback.message.edit_text(f"Гру на {count} гравців створено!", reply_markup=keyboard)

@dp.callback_query(F.data == "show_role")
async def show_role_handler(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    game = games[chat_id]
    current = game["current_player"]
    role = game["roles"][current - 1]
    
    await callback.message.edit_text(f"Гравець {current}, твоя роль:\n\n**{role}**", parse_mode="Markdown")
    await asyncio.sleep(3)
    
    if current < game["players_count"]:
        game["current_player"] += 1
        next_p = game["current_player"]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"👁 Гравець {next_p}: Роль", callback_data="show_role")]])
        await callback.message.edit_text(f"Роль сховано! Черга: Гравець {next_p}", reply_markup=keyboard)
    else:
        await callback.message.edit_text("🎭 Всі дізналися ролі! Починайте!")
        del games[chat_id]

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def handle_index(request):
    return web.Response(text="Бот працює!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_index)
    runner = web.AppRunner(app)
    await runner.setup()
    import os
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Веб-сервер запущено на порту {port}")

async def main():
    await start_web_server()
    print("Бот запущений з двома режимами!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())