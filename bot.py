import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3

BOT_TOKEN = "8396173791:AAGHu58HpesQrdq0A0BeCZWm9EHf2LBXtEM"
MONETAG_PAGE = "https://earningbot2.vercel.app/"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Database setup
conn = sqlite3.connect("users.db")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0,
    referred_by INTEGER DEFAULT 0
)
""")
conn.commit()

@dp.message(F.text == "/start")
async def start(message: types.Message):
    args = message.text.split(" ")
    user_id = message.from_user.id
    ref = 0
    if len(args) > 1 and args[1].isdigit():
        ref = int(args[1])

    # Register user if new
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users (user_id, referred_by) VALUES (?, ?)", (user_id, ref))
        conn.commit()

    # Detect if ad was completed
    if len(args) > 1 and args[1] == "ad_done":
        cur.execute("UPDATE users SET balance = balance + 0.25 WHERE user_id=?", (user_id,))
        conn.commit()
        await message.answer("✅ Thanks! 0.25 BDT added to your balance.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Watch Ad", callback_data="watch_ad")],
        [InlineKeyboardButton(text="👥 Refer & Earn", callback_data="ref")],
        [InlineKeyboardButton(text="💵 Withdraw", callback_data="withdraw")]
    ])

    await message.answer("👋 Welcome to BDTEarnBot!\nEarn BDT by watching ads and referring friends.", reply_markup=keyboard)

@dp.callback_query(F.data == "watch_ad")
async def watch_ad(callback: types.CallbackQuery):
    ad_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖼 View Ad", url=MONETAG_PAGE)]
    ])
    await callback.message.edit_text("Click below to view the ad (wait 15s before pressing Done):", reply_markup=ad_button)

@dp.callback_query(F.data == "ref")
async def ref(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    me = await bot.get_me()
    ref_link = f"https://t.me/{me.username}?start={user_id}"
    await callback.message.edit_text(f"👥 Refer & Earn\n\nShare your link:\n{ref_link}")

@dp.callback_query(F.data == "withdraw")
async def withdraw(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    cur.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    balance = cur.fetchone()[0]
    await callback.message.edit_text(f"💵 Your balance: {balance:.2f} BDT\nMinimum withdrawal: 50 BDT")

async def main():
    print("🤖 Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())