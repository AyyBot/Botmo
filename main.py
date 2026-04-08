import logging
from datetime import datetime
import requests
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# -------------------- CẤU HÌNH --------------------
TOKEN = "8774776432:AAEtoHLJahJpdBtZ7xCDg2R3VVlsnNYSnBA"  # 👈 Giữ nguyên token của bạn
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# -------------------- FLASK WEB SERVER (để Render và UptimeRobot ping) --------------------
flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return "Bot is running!", 200

def run_flask():
    """Chạy Flask server trên cổng 8080 (Render yêu cầu)"""
    flask_app.run(host='0.0.0.0', port=8080)

# -------------------- HÀM XỬ LÝ LỆNH (giữ nguyên của bạn) --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🕒 Thời gian", callback_data='time'),
         InlineKeyboardButton("🌤️ Thời tiết", callback_data='weather')],
        [InlineKeyboardButton("🔊 Echo", callback_data='echo'),
         InlineKeyboardButton("🧮 Tính toán", callback_data='calc')],
        [InlineKeyboardButton("ℹ️ Thông tin", callback_data='info'),
         InlineKeyboardButton("🆘 Trợ giúp", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Xin chào! Tôi là bot MMO by Ayy dzaii.\n"
        "/start hoặc bấm các nút bên dưới để sử dụng không biết thì gõ /help.:)))",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """<b>📋 Danh sách lệnh có sẵn:</b>
/start - Hiển thị menu chính
/help - Hướng dẫn này
/time - Xem giờ hiện tại
/weather &lt;thành phố&gt; - Thời tiết (vd: /weather Hanoi)
/echo &lt;nội dung&gt; - Bot nhại lại
/calc &lt;biểu thức&gt; - Tính toán (vd: /calc 2+3*4)
/info - Thông tin người dùng

<i>💡 Mẹo:</i> Bạn có thể dùng inline keyboard trong menu /start để thao tác nhanh hơn."""
    await update.message.reply_text(text, parse_mode="HTML")

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
    await update.message.reply_text(f"🕒 <b>{now}</b>", parse_mode="HTML")

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🌍 Vui lòng nhập tên thành phố.\nVí dụ: <code>/weather Ho Chi Minh</code>", parse_mode="HTML")
        return
    city = " ".join(context.args)
    url = f"https://wttr.in/{city}?format=%C+%t"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            weather_info = response.text.strip()
            await update.message.reply_text(f"🌤️ <b>{city.title()}</b>: {weather_info}", parse_mode="HTML")
        else:
            await update.message.reply_text("❌ Không thể lấy dữ liệu. Kiểm tra lại tên thành phố.")
    except Exception:
        await update.message.reply_text("⚠️ Lỗi kết nối đến dịch vụ thời tiết.")

async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🔊 Bạn muốn tôi nói gì? Gõ <code>/echo nội dung</code>", parse_mode="HTML")
        return
    text = " ".join(context.args)
    await update.message.reply_text(f"🔊 {text}")

async def calc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🧮 Nhập biểu thức cần tính. Ví dụ: <code>/calc 2+3*4</code>", parse_mode="HTML")
        return
    expr = "".join(context.args)
    try:
        result = eval(expr)
        await update.message.reply_text(f"📊 <code>{expr} = {result}</code>", parse_mode="HTML")
    except Exception:
        await update.message.reply_text("❌ Biểu thức không hợp lệ.")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = f"@{user.username}" if user.username else "Không có username"
    text = f"""<b>👤 Thông tin của bạn</b>
- Tên: {user.first_name} {user.last_name or ''}
- ID: <code>{user.id}</code>
- Username: {username}
- Bot hiện tại: {context.bot.username}"""
    await update.message.reply_text(text, parse_mode="HTML")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == 'time':
        now = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        await query.edit_message_text(f"🕒 <b>{now}</b>", parse_mode="HTML")
    elif data == 'weather':
        await query.edit_message_text(
            "🌍 <b>Hãy nhập tên thành phố bạn muốn xem thời tiết</b>\n"
            "Ví dụ: <code>/weather Hanoi</code>\n\n"
            "👉 Bạn có thể gõ trực tiếp lệnh trong chat.",
            parse_mode="HTML"
        )
    elif data == 'echo':
        await query.edit_message_text(
            "🔊 <b>Hãy gõ lệnh echo</b>\n"
            "Ví dụ: <code>/echo Hello world</code>",
            parse_mode="HTML"
        )
    elif data == 'calc':
        await query.edit_message_text(
            "🧮 <b>Hãy gõ phép tính</b>\n"
            "Ví dụ: <code>/calc 5*3-2</code>",
            parse_mode="HTML"
        )
    elif data == 'info':
        user = update.effective_user
        username = f"@{user.username}" if user.username else "Không có username"
        text = f"""<b>👤 Thông tin của bạn</b>
- Tên: {user.first_name} {user.last_name or ''}
- ID: <code>{user.id}</code>
- Username: {username}
- Bot hiện tại: {context.bot.username}"""
        await query.edit_message_text(text, parse_mode="HTML")
    elif data == 'help':
        text = """<b>📋 Danh sách lệnh có sẵn:</b>
/start - Menu chính
/help - Hướng dẫn
/time - Giờ hiện tại
/weather &lt;tp&gt; - Thời tiết
/echo &lt;nd&gt; - Lặp lại
/calc &lt;bt&gt; - Tính toán
/info - Thông tin bạn

<i>💡 Gợi ý:</i> Dùng menu /start để thao tác nhanh."""
        await query.edit_message_text(text, parse_mode="HTML")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text:
        await update.message.reply_text(f"Bạn vừa nói: {text}\n👉 Gõ /help để xem các lệnh có sẵn.")

# -------------------- KHỞI CHẠY BOT (POLLING) VÀ FLASK CÙNG LÚC --------------------
def run_bot():
    """Chạy bot Telegram polling"""
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CommandHandler("weather", weather_command))
    app.add_handler(CommandHandler("echo", echo_command))
    app.add_handler(CommandHandler("calc", calc_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot Telegram đang chạy...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # Chạy Flask trong một luồng riêng
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True  # Luồng sẽ tắt khi chương trình chính kết thúc
    flask_thread.start()
    # Chạy bot ở luồng chính
    run_bot()