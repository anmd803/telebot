import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_stats, get_logs, log_operation, add_service, update_service_price
from config import TOKEN, ADMIN_ID, SYRIATEL_CASH_NUMBER

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect("bot_database.db", check_same_thread=False)
cur = conn.cursor()

# **إحصائيات البوت**
@dp.message_handler(commands=['stats'])
async def show_stats(message: types.Message):
    stats = get_stats()
    text = f"""
📊 **إحصائيات البوت**:
👥 المستخدمون: {stats['users']}
✅ الطلبات المكتملة: {stats['completed_orders']}
💰 إجمالي النقاط المستهلكة: {stats['total_points']}
"""
    await message.answer(text, parse_mode="Markdown")

# **إضافة خدمة جديدة**
@dp.message_handler(commands=['add_service'])
async def add_service_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ ليس لديك الصلاحية لاستخدام هذا الأمر.")
    
    try:
        args = message.get_args().split("|")
        service_name = args[0].strip()
        price = int(args[1].strip())
        request_info = args[2].strip()

        add_service(service_name, price, request_info)
        await message.answer(f"✅ تم إضافة الخدمة: {service_name}\n💰 السعر: {price} نقطة\n📌 الطلب المطلوب: {request_info}")
    except:
        await message.answer("❌ صيغة الأمر غير صحيحة، استخدم:\n`/add_service اسم الخدمة | السعر | الطلب المطلوب`", parse_mode="Markdown")

# **تحديث سعر خدمة**
@dp.message_handler(commands=['update_price'])
async def update_service_price_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ ليس لديك الصلاحية لاستخدام هذا الأمر.")
    
    try:
        args = message.get_args().split("|")
        service_name = args[0].strip()
        new_price = int(args[1].strip())

        update_service_price(service_name, new_price)
        await message.answer(f"✅ تم تحديث سعر الخدمة: {service_name} إلى {new_price} نقطة.")
    except:
        await message.answer("❌ صيغة الأمر غير صحيحة، استخدم:\n`/update_price اسم الخدمة | السعر الجديد`", parse_mode="Markdown")

# **شحن الرصيد عبر سيرياتيل كاش**
@dp.message_handler(commands=['recharge'])
async def recharge_handler(message: types.Message):
    await message.answer(f"📌 قم بتحويل المبلغ إلى الرقم: `{SYRIATEL_CASH_NUMBER}` ثم أرسل الأمر التالي:\n\n"
                         "`/confirm_recharge رقم العملية | المبلغ`", parse_mode="Markdown")

@dp.message_handler(commands=['confirm_recharge'])
async def confirm_recharge_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ فقط المشرف يمكنه تأكيد عمليات الشحن.")

    try:
        args = message.get_args().split("|")
        transaction_id = args[0].strip()
        amount = int(args[1].strip())

        # زر التأكيد
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ تأكيد الشحن", callback_data=f"confirm_recharge:{transaction_id}:{amount}")
        )

        await message.answer(f"🔔 طلب شحن جديد:\n📌 رقم العملية: `{transaction_id}`\n💰 المبلغ: {amount} نقطة\n\n"
                             "🔽 اضغط على الزر أدناه للتأكيد.", parse_mode="Markdown", reply_markup=keyboard)
    except:
        await message.answer("❌ صيغة الأمر غير صحيحة، استخدم:\n`/confirm_recharge رقم العملية | المبلغ`", parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data.startswith("confirm_recharge"))
async def process_recharge_callback(callback_query: types.CallbackQuery):
    _, transaction_id, amount = callback_query.data.split(":")
    user_id = callback_query.from_user.id

    cur.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (int(amount), user_id))
    conn.commit()

    await bot.answer_callback_query(callback_query.id, "✅ تم تأكيد الشحن بنجاح!")
    await bot.send_message(user_id, f"✅ تم شحن {amount} نقطة إلى رصيدك بنجاح!")

# **تشغيل البوت**
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)