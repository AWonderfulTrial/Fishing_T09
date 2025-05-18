import asyncio
import logging
import random
import numpy
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
import sqlite3


from config import BOT_TOKEN

dp = Dispatcher()
logger = logging.getLogger(__name__)

user_data = {}

conn_info = sqlite3.connect('Users_info.db', check_same_thread=False)
infocursor = conn_info.cursor()

conn_inventory = sqlite3.connect('Users_inventory.db', check_same_thread=False)
itemcursor = conn_inventory.cursor()

conn_fishing_rod_info = sqlite3.connect('fishing_rod_info.db', check_same_thread=False)
rod_infocursor = conn_fishing_rod_info.cursor()

catches = ['common_fish', 'uncommon_fish', 'rare_fish', 'super_rare_fish', 'epic_fish', 'legendary_fish', 'mythic_fish', 'collectibles']

code = str(random.randint(10000000, 99999999))
code_first_part = code[0:4]
code_second_part = code[4:9]

bot = Bot(token=BOT_TOKEN)

all_collection = [
    {
        "name": "Карта сокровищ",
        "nickname": "treasure_map",
        "type": "photo",
        "file_path": "data/images/treasure_map.png",
        "description": "Неизвестная бутылка с картой сокровищ внутри."
    },
    {
        "name": "Старинный золотой кубок",
        "nickname": "golden_chalice",
        "type": "photo",
        "file_path": "data/images/golden_chalice.png",
        "description": "Такое жалко продавать, как и впрочем все остальные вещи из коллекции."
    },
    {
        "name": "Старинный магнитный компас.",
        "nickname": "ancient_compass",
        "type": "photo",
        "file_path": "data/images/ancient_compass.png",
        "description": "Самая настоящая реликвия. Правда, неизвестно, как он сюда попал."
    },
    {
        "name": "Аудио кассета #1",
        "nickname": "audio_tape01",
        "type": "audio",
        "file_path": "CQACAgIAAxkBAAIB...",
        "description": "Слегка потрепана, из за чего качество аудио там заметно ухудшилось."
    },
    {
        "name": "Аудио кассета #2",
        "nickname": "audio_tape02",
        "type": "audio",
        "file_path": "CQACAgIAAxkBAAIB...",
        "description": "Слегка потрепана, из за чего качество аудио там заметно ухудшилось."
    },
    {
        "name": "Аудио кассета #3",
        "nickname": "audio_tape03",
        "type": "audio",
        "file_path": "CQACAgIAAxkBAAIB...",
        "description": "Слегка потрепана, из за чего качество аудио там заметно ухудшилось."
    },
    {
        "name": "???",
        "nickname": "unknown",
        "type": "None",
        "description": f"Неизвестная бутылка с запиской внутри. На записке написан код: {code_second_part}."
    }
]

relics = [item["nickname"] for item in all_collection]
relics_names = [item["name"] for item in all_collection]
relic_chances = [0.25, 0.20, 0.18, 0.15, 0.12, 0.08, 0.02]

shop_items_ids = ["stick_fishing_rod", "rusty_reel_fishing_rod",
        "woven_willow_fishing_rod", "copper_catcher_fishing_rod", "frostbite_fisher_fishing_rod", "emberflow_fishing_rod",
        "moonlit_mender_fishing_rod", "serpentspine_fishing_rod", "thunderlord_fishing_rod", "leviathans_grasp_fishing_rod",
        "phoenixfeather_fishing_rod", "abyssal_whisper_fishing_rod", "celestial_harpoon_fishing_rod", "eternaltide_fishing_rod",
        "neptunes_trident_fishing_rod", "underwater_flashlight", "diving_suit"]

shop_item_nicknames_1 = rod_infocursor.execute("SELECT nickname FROM fishing_rod_info").fetchall()
shop_item_nicknames = [element[0] for element in shop_item_nicknames_1]
shop_item_nicknames.extend(["Подводный фонарик", "Подводный костюм"])

shop_item_prices_1 = rod_infocursor.execute("SELECT price FROM fishing_rod_info").fetchall()
shop_item_prices = [element[0] for element in shop_item_prices_1]
shop_item_prices.extend([300, 500])

def setup_db():
    infocursor.execute('CREATE TABLE IF NOT EXISTS Users_info (user_id STRING, last_location STRING, code STRING, current_fishing_rod STRING)')
    conn_info.commit()
    itemcursor.execute('CREATE TABLE IF NOT EXISTS Users_inventory (user_id STRING, coins INTEGER, common_fish INTEGER, uncommon_fish INTEGER, rare_fish INTEGER, '
                   'super_rare_fish INTEGER, epic_fish INTEGER, legendary_fish INTEGER, mythic_fish INTEGER, stick_fishing_rod INTEGER, rusty_reel_fishing_rod INTEGER, '
                   'woven_willow_fishing_rod INTEGER, copper_catcher_fishing_rod INTEGER, frostbite_fisher_fishing_rod INTEGER, emberflow_fishing_rod INTEGER, '
                   'moonlit_mender_fishing_rod INTEGER, serpentspine_fishing_rod INTEGER, thunderlord_fishing_rod INTEGER, leviathans_grasp_fishing_rod INTEGER, '
                   'phoenixfeather_fishing_rod INTEGER, abyssal_whisper_fishing_rod INTEGER, celestial_harpoon_fishing_rod INTEGER, eternaltide_fishing_rod INTEGER, '
                   'neptunes_trident_fishing_rod INTEGER, treasure_map INTEGER, golden_chalice INTEGER, ancient_compass INTEGER, audio_tape01 INTEGER, audio_tape02 INTEGER, '
                   'audio_tape03 INTEGER, unknown INTEGER, important_note INTEGER, underwater_flashlight INTEGER, diving_suit INTEGER)')
    conn_inventory.commit()

@dp.message(CommandStart())
async def start(message: Message):
    global k
    global code
    user_id = message.from_user.id
    s = infocursor.execute('SELECT * FROM Users_info WHERE user_id = ?', (user_id,)).fetchall()
    if len(s) == 0:
        infocursor.execute(
            'INSERT INTO Users_info (user_id, last_location, code, current_fishing_rod) VALUES (?, NULL, ?, ?)',
            (user_id, code, "stick_fishing_rod")
        )
        conn_info.commit()
        itemcursor.execute(f"INSERT INTO Users_inventory (user_id, coins, common_fish, uncommon_fish, rare_fish, "
                            f"super_rare_fish, epic_fish, legendary_fish, mythic_fish, stick_fishing_rod, rusty_reel_fishing_rod, "
                            f"woven_willow_fishing_rod, copper_catcher_fishing_rod, frostbite_fisher_fishing_rod, emberflow_fishing_rod, "
                            f"moonlit_mender_fishing_rod, serpentspine_fishing_rod, thunderlord_fishing_rod, leviathans_grasp_fishing_rod, "
                            f"phoenixfeather_fishing_rod, abyssal_whisper_fishing_rod, celestial_harpoon_fishing_rod, eternaltide_fishing_rod, "
                            f"neptunes_trident_fishing_rod, treasure_map, golden_chalice, ancient_compass, audio_tape01, audio_tape02, "
                            f"audio_tape03, unknown, important_note, underwater_flashlight, diving_suit) VALUES ({user_id}, 0, 0, 0, 0, 0, 0, 0,"
                            f"0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)")
        conn_inventory.commit()
        await message.answer('Добро пожаловать на рыбалку! Надеюсь, что вы тут хорошо проведёте своё время!')
    await cmd_menu_start(message)

async def cmd_menu_start(message: Message):
    user_id = message.from_user.id
    infocursor.execute("UPDATE Users_info SET last_location = 'menu_start' WHERE user_id = ?",
                       (user_id,))
    conn_info.commit()
    reply_keyboard = [[KeyboardButton(text='🎣Рыбалка🎣'),
                       KeyboardButton(text='🛒Магазин🛒')],
                      [KeyboardButton(text='🎒Инвентарь🎒'),
                       KeyboardButton(text='🧿Коллекция🧿')],
                      [KeyboardButton(text='⚙Настройки⚙'),
                       KeyboardButton(text='📚Гайд📚')]]
    kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    await message.answer('ГЛАВНОЕ МЕНЮ', reply_markup=kb)

async def cmd_fishing(message: Message):
    user_id = message.from_user.id
    infocursor.execute(f"UPDATE Users_info SET last_location = 'fishing' WHERE user_id = {user_id}")
    conn_info.commit()
    reply_keyboard = [[KeyboardButton(text='🐠Закинуть удочку🐠')],
                      [KeyboardButton(text='🎣Выбрать удочку🎣')],
                      [KeyboardButton(text='⏪ВЕРНУТЬСЯ⏪')]]
    kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    await message.answer("РЫБАЛКА", reply_markup=kb)

async def cmd_fishing_in_process(message: Message):
    global catches
    global relics
    global relic_chances
    user_id = message.from_user.id
    infocursor.execute(f"UPDATE Users_info SET last_location = 'fishing_in_process' WHERE user_id = {user_id}")
    conn_info.commit()

    current_fishing_rod = infocursor.execute(
        "SELECT current_fishing_rod FROM Users_info WHERE user_id = ?",
        (user_id,)
    ).fetchone()[0]

    time = rod_infocursor.execute(
        "SELECT time_sec FROM fishing_rod_info WHERE rod_id = ?",
        (current_fishing_rod,)
    ).fetchone()[0]
    msg = await message.answer(f"Время ожидания: {time} секунд", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(time)
    await msg.delete()

    chances_row = rod_infocursor.execute(
        "SELECT * FROM fishing_rod_info WHERE rod_id = ?",
        (current_fishing_rod,)
    ).fetchone()

    chances = list(chances_row[5:])
    chances = [x / 100 for x in chances]
    r = numpy.random.choice(catches, p=chances)

    current_count = itemcursor.execute(
        f"SELECT {r} FROM Users_inventory WHERE user_id = ?",
        (user_id,)
    ).fetchone()[0]

    double_chance = chances_row[4] / 100
    add_count = 1 + (1 if random.random() < double_chance else 0)

    itemcursor.execute(
        f"UPDATE Users_inventory SET {r} = ? WHERE user_id = ?",
        (current_count + add_count, user_id)
    )
    conn_inventory.commit()

    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='🐠Закинуть удочку ещё раз🐠')],
        [KeyboardButton(text='🎣Выбрать удочку🎣')],
        [KeyboardButton(text='⏪ВЕРНУТЬСЯ⏪')]
    ], resize_keyboard=True)

    if r == 'collectibles':
        q = numpy.random.choice(relics, p=relic_chances)
        itemcursor.execute(
            f"UPDATE Users_inventory SET {q} = {q} + 1 WHERE user_id = ?",
            (user_id,)
        )
        conn_inventory.commit()
        await message.answer(
            f"Вы поймали редкий предмет! Это {q}!" + (" А ещё это двойной улов!" if add_count > 1 else ""),
            reply_markup=kb)
    else:
        await message.answer(f"Вы поймали {r}!" + (" А ещё это двойной улов!" if add_count > 1 else ""),
                             reply_markup=kb)

async def cmd_select_fishing_rod(message: Message):
    user_id = message.from_user.id
    infocursor.execute("UPDATE Users_info SET last_location = 'select_fishing_rod' WHERE user_id = ?", (user_id,))
    conn_info.commit()

    try:
        current_rod = infocursor.execute(
            "SELECT current_fishing_rod FROM Users_info WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]

        itemcursor.execute("PRAGMA table_info(Users_inventory)")
        columns = [col[1] for col in itemcursor.fetchall() if "_fishing_rod" in col[1]]

        rods_query = f"SELECT {', '.join(columns)} FROM Users_inventory WHERE user_id = ?"
        itemcursor.execute(rods_query, (user_id,))
        owned_rods = [col for col, val in zip(columns, itemcursor.fetchone()) if val > 0]

        rod_buttons = []
        for rod_id in owned_rods:
            rod_name = rod_infocursor.execute(
                "SELECT nickname FROM fishing_rod_info WHERE rod_id = ?",
                (rod_id,)
            ).fetchone()[0]

            display_name = f"{rod_name} ✅" if rod_id == current_rod else rod_name
            rod_buttons.append([KeyboardButton(text=display_name)])

        rod_buttons.append([KeyboardButton(text='⏪ВЕРНУТЬСЯ⏪')])
        kb = ReplyKeyboardMarkup(keyboard=rod_buttons, resize_keyboard=True)

        await message.answer(
            "🎣 Выберите удочку:" if rod_buttons else "❌ У вас нет доступных удочек!",
            reply_markup=kb
        )

    except Exception as e:
        logging.error(f"Rod selection error: {e}")
        await message.answer("⚠️ Ошибка загрузки удочек", reply_markup=ReplyKeyboardRemove())

@dp.message(F.text.endswith('✅'))
async def handle_rod_selection(message: Message):
    user_id = message.from_user.id
    selected_name = message.text.replace(' ✅', '').strip()

    try:
        rod_id, = rod_infocursor.execute(
            "SELECT rod_id FROM fishing_rod_info WHERE nickname = ?",
            (selected_name,)
        ).fetchone()

        has_rod = itemcursor.execute(
            f"SELECT {rod_id} FROM Users_inventory WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]

        if has_rod:
            infocursor.execute(
                "UPDATE Users_info SET current_fishing_rod = ? WHERE user_id = ?",
                (rod_id, user_id)
            )
            conn_info.commit()
            await message.answer(f"⚡ Активная удочка изменена на: {selected_name}!")
            await cmd_fishing(message)

    except TypeError:
        await message.answer("❌ Удочка не найдена в базе данных!")
    except Exception as e:
        logging.error(f"Rod change error: {e}")
        await message.answer("⚠️ Ошибка смены удочки", reply_markup=ReplyKeyboardRemove())

async def cmd_shop(message: Message):
    user_id = message.from_user.id
    infocursor.execute(f"UPDATE Users_info SET last_location = 'shop' WHERE user_id = {user_id}")
    conn_info.commit()
    reply_keyboard = []
    for i in range(len(shop_items_ids)):
        shop_text = f"КУПИТЬ {shop_item_nicknames[i]} ЗА {shop_item_prices[i]} COINS"
        reply_keyboard.append([KeyboardButton(text=shop_text)])
    reply_keyboard.append([KeyboardButton(text='⏪ВЕРНУТЬСЯ⏪')])
    kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True)
    await message.answer("МАГАЗИН", reply_markup=kb)

async def cmd_inventory(message: Message):
    user_id = message.from_user.id
    infocursor.execute(f"UPDATE Users_info SET last_location = 'inventory' WHERE user_id = {user_id}")
    conn_info.commit()
    itemcursor.execute("PRAGMA table_info(Users_inventory)")
    columns = [column[1] for column in itemcursor.fetchall()][1:]

    itemcursor.execute("SELECT * FROM Users_inventory WHERE user_id = ?",(user_id,))
    data = itemcursor.fetchone()[1:]
    inventory_lines = [f"{name.replace('_', ' ').title()}: {value}" for name, value in zip(columns, data)if value > 0]
    if not inventory_lines:
        inventory_text = "Ваш инвентарь пуст!"
    else:
        inventory_text = "🎒 Ваш инвентарь:\n\n" + "\n".join(inventory_lines)
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='💵ПРОДАТЬ ВСЮ РЫБУ💵')],
                  [KeyboardButton(text='⏪ВЕРНУТЬСЯ⏪')]], resize_keyboard=True)
    await message.answer(inventory_text, reply_markup=kb)


async def cmd_collections(message: Message):
    user_id = message.from_user.id
    infocursor.execute(f"UPDATE Users_info SET last_location = 'collections' WHERE user_id = {user_id}")
    conn_info.commit()

    itemcursor.execute(f"""
        SELECT treasure_map, golden_chalice, ancient_compass, 
               audio_tape01, audio_tape02, audio_tape03, unknown 
        FROM Users_inventory 
        WHERE user_id = {user_id}
    """)
    relics_counts = itemcursor.fetchone()

    keyboard = []
    for i, relic in enumerate(all_collection):
        if relics_counts[i] > 0:
            keyboard.append([KeyboardButton(text=relic['name'])])

    keyboard.append([KeyboardButton(text='⏪ВЕРНУТЬСЯ⏪')])

    kb = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    if len(keyboard) == 1:
        await message.answer("Здесь пока что ничего нет... Собирайте реликвии чтобы они тут были!", reply_markup=kb)
    else:
        await message.answer("КОЛЛЕКЦИИ", reply_markup=kb)


@dp.message(F.text.in_([item['name'] for item in all_collection]))
async def handle_collection_item(message: Message):
    user_id = message.from_user.id
    item_name = message.text

    selected_relic = next((item for item in all_collection if item['name'] == item_name), None)

    if not selected_relic:
        await message.answer("Реликвия не найдена")
        return

    try:
        if selected_relic['type'] == 'photo':
            photo = FSInputFile(selected_relic['file_path'])
            await message.answer_photo(
                photo=photo,
                caption=selected_relic['description']
            )
        elif selected_relic['type'] == 'audio':
            await message.answer_audio(
                audio=selected_relic['file_path'],
                caption=selected_relic['description']
            )
        else:
            await message.answer(selected_relic['description'])

    except Exception as e:
        logger.error(f"Ошибка отправки медиа: {e}")
        await message.answer("⚠️ Не удалось загрузить реликвию")

async def cmd_settings(message: Message):
    user_id = message.from_user.id
    infocursor.execute(f"UPDATE Users_info SET last_location = 'settings' WHERE user_id = {user_id}")
    conn_info.commit()
    reply_keyboard = [[KeyboardButton(text='❌УДАЛИТЬ ДАННЫЕ❌')],
                        [KeyboardButton(text='⏪ВЕРНУТЬСЯ⏪')]]
    kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    await message.answer("НАСТРОЙКИ", reply_markup=kb)

async def cmd_reset_request(message: Message):
    user_id = message.from_user.id
    infocursor.execute(f"UPDATE Users_info SET last_location = 'reset_request' WHERE user_id = {user_id}")
    conn_info.commit()
    reply_keyboard = [[KeyboardButton(text='✅ДА✅'),
                       KeyboardButton(text='⏪ВЕРНУТЬСЯ⏪')]]
    kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    await message.answer('Вы точно хотите удалить данные?', reply_markup=kb)

async def cmd_reset_request_approved(message: Message):
    user_id = message.from_user.id
    infocursor.execute(f'DELETE from Users_info WHERE user_id = {user_id}')
    conn_info.commit()
    itemcursor.execute(f'DELETE from Users_inventory WHERE user_id = {user_id}')
    conn_inventory.commit()
    await message.answer('Ваши данные были успешно удалены!', reply_markup=ReplyKeyboardRemove())

async def cmd_guide(message: Message):
    user_id = message.from_user.id
    infocursor.execute(f"UPDATE Users_info SET last_location = 'settings' WHERE user_id = {user_id}")
    conn_info.commit()
    reply_keyboard = [[KeyboardButton(text='⏪ВЕРНУТЬСЯ⏪')]]
    kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    await message.answer(
        "1️⃣ 🎣 Рыбалка: Начните ловить рыбу! Закиньте удочку и ждите, пока клюнет. Чем больше рыбы поймаете, тем больше денег заработаете!\n\n"
        "2️⃣ 🛒 Магазин: Загляните в магазин, чтобы купить новые удочки и специальные предметы. Используйте свои деньги для улучшения снаряжения и увеличения шансов на удачный улов!\n\n"
        "3️⃣ 🎒 Инвентарь: Просмотрите свои вещи в инвентаре. Здесь вы можете увидеть ваш баланс, все ващи пойманные рыбы, удочки и все остальное, что у вас есть.\n\n"
        "Также это место, где мы можете продать свою рыбу и получить за это деньги\n\n"
        "4️⃣ 🧿 Коллекции: Ознакомьтесь с коллекциями реликвий, чтобы увидеть, какие уникальные предметы вы уже собрали. Реликвии нельзя купить, их можно только найти в процессе игры!\n\n"
        "5️⃣ ⚙️ Настройки: В разделе настроек вы можете удалить свои данные. Будьте осторожны, эта операция необратима!\n\n"
        "Удачной рыбалки!",
        reply_markup=kb)



@dp.message()
async def handle_buttons(message: Message):
    user_id = message.from_user.id
    location = infocursor.execute('SELECT last_location FROM Users_info WHERE user_id = ?',
            (user_id,)).fetchone()
    if message.text == '/fishing':
        await cmd_fishing(message)
    elif message.text == '/shop':
        await cmd_shop(message)
    elif message.text == '/inventory':
        await cmd_inventory(message)
    elif message.text == '/collection':
        await cmd_collections(message)
    elif message.text == '/settings':
        await cmd_settings(message)
    elif message.text == '/guide':
        await cmd_guide(message)
    elif location[0] == 'menu_start':
        if message.text == '🎣Рыбалка🎣':
            await cmd_fishing(message)
        elif message.text == '🛒Магазин🛒':
            await cmd_shop(message)
        elif message.text == '🎒Инвентарь🎒':
            await cmd_inventory(message)
        elif message.text == '🧿Коллекция🧿':
            await cmd_collections(message)
        elif message.text == '⚙Настройки⚙':
            await cmd_settings(message)
        elif message.text == '📚Гайд📚':
            await cmd_guide(message)
    elif location[0] == 'fishing':
        if message.text == '🐠Закинуть удочку🐠':
            await cmd_fishing_in_process(message)
        elif message.text == '🎣Выбрать удочку🎣':
            await cmd_select_fishing_rod(message)
        elif message.text == '⏪ВЕРНУТЬСЯ⏪':
            await cmd_menu_start(message)
    elif location[0] == 'fishing_in_process':
        if message.text == '🐠Закинуть удочку ещё раз🐠':
            await cmd_fishing_in_process(message)
        elif message.text == '🎣Выбрать удочку🎣':
            await cmd_select_fishing_rod(message)
        elif message.text == '⏪ВЕРНУТЬСЯ⏪':
            await cmd_menu_start(message)
    elif location[0] == 'select_fishing_rod':
        if message.text == '⏪ВЕРНУТЬСЯ⏪':
            await cmd_menu_start(message)
    elif location[0] == 'shop':
        if message.text == '⏪ВЕРНУТЬСЯ⏪':
            await cmd_menu_start(message)
        elif message.text:
            for i in range(len(shop_item_nicknames)):
                if shop_item_nicknames[i] in message.text and str(shop_item_prices[i]) in message.text:
                    y = shop_item_nicknames[i]
                    u = shop_item_prices[i]
                    l = 1
                    break
            coins = itemcursor.execute(f"SELECT coins FROM Users_inventory where user_id = {user_id}").fetchone()[0]
            if coins >= u:
                coins -= u
                itemcursor.execute(f"UPDATE Users_inventory SET coins = {coins}, {shop_items_ids[l]} = {shop_items_ids[l]} + 1 WHERE user_id = {user_id}")
                conn_inventory.commit()
                await message.answer(f"Вы успешно купили {y} за {u} COINS! У вас осталось {coins} монет в кошельке!")
                await cmd_shop(message)
            else:
                await message.answer(f"У вас не хватает средств на покупку!")


    elif location[0] == 'inventory':
        if message.text == '💵ПРОДАТЬ ВСЮ РЫБУ💵':
            try:
                itemcursor.execute("""
                            SELECT common_fish, uncommon_fish, rare_fish, 
                                   super_rare_fish, epic_fish, legendary_fish, mythic_fish 
                            FROM Users_inventory 
                            WHERE user_id = ?""", (user_id,))

                fish_counts = itemcursor.fetchone()

                if not fish_counts:
                    await message.answer("❌ Ошибка: данные не найдены")
                    return

                prices = [10, 50, 125, 500, 2500, 5000, 7500]
                total = sum(count * price for count, price in zip(fish_counts, prices))

                itemcursor.execute("""
                            UPDATE Users_inventory SET
                                coins = coins + ?,
                                common_fish = 0,
                                uncommon_fish = 0,
                                rare_fish = 0,
                                super_rare_fish = 0,
                                epic_fish = 0,
                                legendary_fish = 0,
                                mythic_fish = 0
                            WHERE user_id = ?""", (total, user_id))
                conn_inventory.commit()

                await message.answer(f"💰 Вы успешно продали всю рыбу за {total} монет!")
                await cmd_menu_start(message)

            except sqlite3.Error as e:
                conn_inventory.rollback()
                logger.error(f"Ошибка продажи: {e}")
                await message.answer("⚠️ Произошла ошибка при продаже, попробуйте позже")
        elif message.text == '⏪ВЕРНУТЬСЯ⏪':
            await cmd_menu_start(message)
    elif location[0] == 'collections':
        if message.text == '⏪ВЕРНУТЬСЯ⏪':
            await cmd_menu_start(message)
    elif location[0] == 'settings':
        if message.text == '❌УДАЛИТЬ ДАННЫЕ❌':
            await cmd_reset_request(message)
        elif message.text == '⏪ВЕРНУТЬСЯ⏪':
            await cmd_menu_start(message)
    elif location[0] == 'reset_request':
        if message.text == '✅ДА✅':
            await cmd_reset_request_approved(message)
        elif message.text == '⏪ВЕРНУТЬСЯ⏪':
            await cmd_menu_start(message)
    elif location[0] == 'guide':
        if message.text == '⏪ВЕРНУТЬСЯ⏪':
            await cmd_menu_start(message)
    else:
        await message.answer('Выберите действие')


async def main():
    setup_db()
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
    )
    asyncio.run(main())