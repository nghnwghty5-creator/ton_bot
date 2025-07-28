from aiogram import Bot, Dispatcher, types, executor
import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json

API_TOKEN = '8455328567:AAH11VGIszGfbFkXUROGdZYeNURcvYTCDP0'
ADMIN_ID = 8494911313
REWARD_AMOUNT = 0.02

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# قاعدة بيانات بسيطة
users = {}
tasks = []
withdraws = []

def save_data():
    with open("data.json", "w") as f:
        json.dump({'users': users, 'tasks': tasks, 'withdraws': withdraws}, f)

def load_data():
    global users, tasks, withdraws
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
            users = data.get("users", {})
            tasks = data.get("tasks", [])
            withdraws = data.get("withdraws", [])
    except:
        pass

load_data()

# الكيبورد
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add("📋 تنفيذ المهام", "💸 رصيدي")
main_kb.add("👥 رابط الإحالة", "💰 طلب سحب")

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    user_id = str(msg.from_user.id)
    if user_id not in users:
        users[user_id] = {"balance": 0.0, "ref_by": None}
        if len(msg.text.split()) > 1:
            ref = msg.text.split()[1]
            if ref != user_id and ref in users:
                users[ref]["balance"] += REWARD_AMOUNT
                users[user_id]["ref_by"] = ref
    await msg.answer(f"🎉 أهلاً بك في بوت *اربح مني*\n\n💸 اجمع عملة TON من تنفيذ المهام.\n🔗 لكل مهمة: {REWARD_AMOUNT} TON", parse_mode="Markdown", reply_markup=main_kb)
    save_data()

@dp.message_handler(lambda m: m.text == "📋 تنفيذ المهام")
async def tasks_list(msg: types.Message):
    if not tasks:
        return await msg.answer("🚫 لا توجد مهام حالياً.")
    text = "📝 المهام المتوفرة:\n"
    for i, t in enumerate(tasks, 1):
        text += f"{i}. {t}\n"
    user_id = str(msg.from_user.id)
    users[user_id]["balance"] += REWARD_AMOUNT
    await msg.answer(text + f"\n✅ تم إضافة {REWARD_AMOUNT} TON لرصيدك.")
    save_data()

@dp.message_handler(lambda m: m.text == "💸 رصيدي")
async def my_balance(msg: types.Message):
    user_id = str(msg.from_user.id)
    bal = users.get(user_id, {}).get("balance", 0.0)
    await msg.answer(f"💰 رصيدك الحالي: {bal:.4f} TON")

@dp.message_handler(lambda m: m.text == "👥 رابط الإحالة")
async def referral(msg: types.Message):
    uid = msg.from_user.id
    await msg.answer(f"🔗 رابط الإحالة الخاص بك:\nhttps://t.me/Erba7MiniBot?start={uid}")

@dp.message_handler(lambda m: m.text == "💰 طلب سحب")
async def withdraw_request(msg: types.Message):
    await msg.answer("✍️ أرسل عنوان محفظتك TON لاستلام السحب:")
    dp.register_message_handler(process_wallet, content_types=types.ContentTypes.TEXT, state=None)

async def process_wallet(msg: types.Message):
    user_id = str(msg.from_user.id)
    wallet = msg.text.strip()
    amount = users.get(user_id, {}).get("balance", 0.0)
    if amount < 1.0:
        return await msg.answer("🚫 الحد الأدنى للسحب هو 1 TON")
    withdraws.append({"user_id": user_id, "wallet": wallet, "amount": amount})
    users[user_id]["balance"] = 0.0
    await msg.answer("✅ تم تقديم طلب السحب بنجاح، سيتم مراجعته من قبل الأدمن.")
    await bot.send_message(ADMIN_ID, f"📤 طلب سحب جديد:\nID: {user_id}\nWallet: {wallet}\nAmount: {amount:.4f} TON")
    save_data()

@dp.message_handler(commands=['admin'])
async def admin_panel(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    text = "🛠️ لوحة تحكم الأدمن:\n"
    text += f"📋 عدد المستخدمين: {len(users)}\n"
    text += f"🧾 المهام الحالية:\n"
    for i, t in enumerate(tasks, 1):
        text += f"{i}. {t}\n"
    text += "\n✍️ أرسل مهمة جديدة (رابط أو وصف)"
    await msg.answer(text)
    dp.register_message_handler(add_task, content_types=types.ContentTypes.TEXT, state=None)

async def add_task(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    tasks.append(msg.text.strip())
    await msg.answer("✅ تم إضافة المهمة.")
    save_data()

if __name__ == '__main__':
    executor.start_polling(dp)