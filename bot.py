from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from database import add_user, has_access

API_TOKEN = '8094739628:AAGrUMXNUfwe0iYb-Tk8GGA2azEacLdvMDA'
ADMIN_ID = 847794446
PRIVATE_LINK = "https://t.me/+bjzQ1cK3weQ1Njgy"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Словник: user_id -> мова ('ua' або 'en')
user_languages = {}

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Українська", callback_data="lang_ua"),
        InlineKeyboardButton("English", callback_data="lang_en")
    )
    await message.answer("👋Hi! This is a bot from @valeramiami for joining my paid channel. Here, I share my experience, useful tips, and calls. If you're my axiom referral (1+ sol volume), dm me after your purchase, and I’ll refund you 0.08 sol.\n\n""👋Привіт! Це бот від @valeramiami для вступу до мого платного каналу. Тут я ділюся своїм досвідом, корисними фішками та коллами. Якщо ти мій аxiom реферал (вольюм 1 sol+), після покупки напиши мені в особисті повідомлення, і я поверну тобі 0.08 sol. \n\nChoose your language:\nОберіть вашу мову:", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data in ['lang_ua', 'lang_en'])
async def process_language(callback_query: types.CallbackQuery):
    lang = 'ua' if callback_query.data == 'lang_ua' else 'en'
    user_languages[callback_query.from_user.id] = lang

    if lang == 'ua':
        text = (
            "💸 Щоб отримати доступ, скиньте 0.33 SOL на адресу:\n"
            "`HmYkEoTBcPw5jfesNA2FFNwdt7465TsRbuoJpkQwoCRk`\n\n"
            "Після оплати натисніть кнопку нижче для перевірки."
        )
        check_button = InlineKeyboardMarkup().add(InlineKeyboardButton("🔍 Перевірити оплату", callback_data="check_ua"))
    else:
        text = (
            "💸 To get access, send 0.33 SOL to the address:\n"
            "`HmYkEoTBcPw5jfesNA2FFNwdt7465TsRbuoJpkQwoCRk`\n\n"
            "After payment, click the button below to check."
        )
        check_button = InlineKeyboardMarkup().add(InlineKeyboardButton("🔍 Check Payment", callback_data="check_en"))

    await bot.send_message(callback_query.from_user.id, text, reply_markup=check_button, parse_mode='Markdown')
    await callback_query.answer()

# Обробка кнопки "перевірити оплату"
@dp.callback_query_handler(lambda c: c.data in ['check_ua', 'check_en'])
async def fake_check(callback_query: types.CallbackQuery):
    user = callback_query.from_user
    lang = 'ua' if callback_query.data == 'check_ua' else 'en'

    if lang == 'ua':
        msg = "⏳ Зачекайте, перевіряємо оплату...\n""Це займе не більше 30 хвилин"
        waiting_button = "⏳ Очікуйте..."
    else:
        msg = "⏳ Please wait, checking payment...\n""It will take no more than 30 minutes"
        waiting_button = "⏳ Please wait..."

    # Відповідь користувачу
    await bot.send_message(user.id, msg)

    # Повідомлення адміна з кнопкою
    text_for_admin = f"🔔 Користувач @{user.username or 'без юзернейму'} (ID: {user.id}) натиснув 'Перевірити оплату'"
    allow_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Дати доступ", callback_data=f"give_access:{user.id}")
    )
    await bot.send_message(ADMIN_ID, text_for_admin, reply_markup=allow_markup)

    # Замінюємо кнопку на неактивну з правильною мовою
    new_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(waiting_button, callback_data="none")
    )
    try:
        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=new_markup
        )
    except Exception as e:
        print(f"[edit_button_error] {e}")

    await callback_query.answer()

# Обробка натискання адміном "Дати доступ"
@dp.callback_query_handler(lambda c: c.data.startswith("give_access:"))
async def give_access(callback_query: types.CallbackQuery):
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("⛔ Тільки адмін може давати доступ!", show_alert=True)
        return

    from database import add_user, has_access

    user_id = int(callback_query.data.split(":")[1])
    lang = user_languages.get(user_id, 'ua')  # якщо мова не збережена — буде 'ua'
    user = await bot.get_chat(user_id)

    if has_access(user_id):
        await callback_query.answer("ℹ️ Користувач вже має доступ.")
        return

    try:
        # Додаємо в базу
        add_user(user_id, user.username, lang)

        # Надсилаємо посилання користувачу
        if lang == 'ua':
            text = f"✅ Вам надано доступ!\n\nОсь ваше посилання:\n{PRIVATE_LINK}"
        else:
            text = f"✅ Access granted!\n\nHere is your link:\n{PRIVATE_LINK}"

        await bot.send_message(user_id, text)

        # Редагуємо кнопку — замінюємо її на неактивну
        new_markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Доступ надано", callback_data="none")
        )
        await bot.edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=new_markup
        )

        await callback_query.answer("✅ Доступ надано!")

    except Exception as e:
        await callback_query.answer("❌ Не вдалося надіслати доступ.")
        print(f"[ERROR] give_access: {e}")


@dp.message_handler(commands=['admin_list'])
async def show_user_list(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("")
        return

    from database import get_all_users
    users = get_all_users()

    if not users:
        await message.reply("❌ Немає жодного користувача з доступом.")
        return

    text = "📋 Список користувачів з доступом:\n\n"
    for user_id, username, lang, access_time in users:
        uname = f"@{username}" if username else "без юзернейму"
        text += f"🧑 {uname}\n🆔 {user_id}\n🌐 Мова: {lang}\n🗓 {access_time}\n\n"

    await message.reply(text)

@dp.callback_query_handler(lambda c: c.data == "none")
async def ignore_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
