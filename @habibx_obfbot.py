import base64
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, MenuButtonWebApp, WebAppInfo
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes, ConversationHandler
)

# ----------------- CONFIGURATION -----------------
BOT_TOKEN = "8839587043:AAHLhKmyrdpJLK3AJlgcpOrjpJVTqya5lwg" # BotFather থেকে পাওয়া টোকেন দিন
DEFAULT_OWNER_ID = 8289191009               # প্রাথমিক ওনার আইডি

# Conversation States
(
    WAITING_BROADCAST,
    WAITING_FORCE_CHANNEL,
    WAITING_BUTTON_TITLE,
    WAITING_BUTTON_URL,
    WAITING_ADD_ADMIN,
    WAITING_REMOVE_ADMIN,
    WAITING_TRANSFER_OWNERSHIP
) = range(7)

DATA_FILE = "bot_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "owner" not in data:
                data["owner"] = DEFAULT_OWNER_ID
            if "admins" not in data:
                data["admins"] = []
            return data
    return {
        "owner": DEFAULT_OWNER_ID,
        "admins": [],
        "users": [],
        "force_channel": "",
        "web_button": {"title": "", "url": ""}
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

bot_data = load_data()

# ----------------- HELPER FUNCTIONS -----------------
def is_owner(user_id: int) -> bool:
    return user_id == bot_data.get("owner", DEFAULT_OWNER_ID)

def is_admin(user_id: int) -> bool:
    return is_owner(user_id) or (user_id in bot_data.get("admins", []))

def heavy_obfuscate_html(html_code: str) -> str:
    encoded = base64.b64encode(html_code.encode('utf-8')).decode('utf-8')
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script>
(function(_0x12a, _0x3b8){{
    var _0x5c1 = function(_0x4d2){{
        while(--_0x4d2){{ _0x12a['push'](_0x12a['shift']()); }}
    }};
    _0x5c1(++_0x3b8);
}})(['{encoded}'], 0x1a4);

(function(){{
    var _0x2f1 = function(){{
        var _0x98a = '{encoded}';
        var _0x41b = atob(_0x98a);
        document.open();
        document.write(_0x41b);
        document.close();
    }};
    window.onload = _0x2f1;
}})();
</script>
</head>
<body>
<noscript>JavaScript required.</noscript>
</body>
</html>"""

def get_main_keyboard():
    keyboard = [
        ["🔐 Obfuscate HTML", "ℹ️ Help"],
        ["⚙️ Admin Panel"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def check_force_join(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    channel = bot_data.get("force_channel")
    if not channel:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
    except Exception:
        pass
    return False

# ----------------- USER HANDLERS -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in bot_data["users"]:
        bot_data["users"].append(user_id)
        save_data(bot_data)

    if not await check_force_join(user_id, context):
        channel = bot_data["force_channel"]
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{channel.replace('@','')}")]]
        await update.message.reply_text(
            f"⚠️ বট ব্যবহার করতে আপনাকে অবশ্যই আমাদের চ্যানেলে জয়েন করতে হবে:\n{channel}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    inline_kb = []
    web_btn = bot_data.get("web_button", {})
    if web_btn.get("title") and web_btn.get("url"):
        inline_kb.append([InlineKeyboardButton(web_btn["title"], web_app=WebAppInfo(url=web_btn["url"]))])

    reply_markup = InlineKeyboardMarkup(inline_kb) if inline_kb else None

    await update.message.reply_text(
        "👋 **স্বাগতম!**\nআমাকে কোনো `.html` ফাইল অথবা কোড লিখে পাঠান, আমি সেটা এনক্রিপ্ট করে নিরাপদ ফাইল বানিয়ে ফেরত দেব।",
        reply_markup=get_main_keyboard()
    )
    if reply_markup:
        await update.message.reply_text("🔗 **ওয়েবসাইট ওপেন করুন:**", reply_markup=reply_markup)

# ----------------- ADMIN PANEL HANDLERS -----------------
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ আপনি এডমিন নন!")
        return

    keyboard = [
        [InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔗 Set Force Channel", callback_data="admin_force")],
        [InlineKeyboardButton("🌐 Add Open Web Button", callback_data="admin_add_button")],
        [InlineKeyboardButton("📊 User Stats", callback_data="admin_stats")]
    ]

    # শুধুমাত্র Owner দেখতে পাবেন এমন অপশন
    if is_owner(user_id):
        keyboard.append([InlineKeyboardButton("➕ Add Admin", callback_data="admin_add_admin"),
                         InlineKeyboardButton("➖ Remove Admin", callback_data="admin_remove_admin")])
        keyboard.append([InlineKeyboardButton("👑 Transfer Ownership", callback_data="admin_transfer_owner")])

    role = "OWNER" if is_owner(user_id) else "ADMIN"
    await update.message.reply_text(f"⚙️ **ADMIN CONTROL PANEL** ({role})", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if not is_admin(user_id):
        return

    if query.data == "admin_stats":
        total_users = len(bot_data.get("users", []))
        total_admins = len(bot_data.get("admins", []))
        owner_id = bot_data.get("owner")
        await query.edit_message_text(
            f"📊 **বট স্ট্যাটাস:**\n\n"
            f"👑 **Owner ID:** `{owner_id}`\n"
            f"🛡️ **Total Admins:** {total_admins}\n"
            f"👥 **Total Users:** {total_users}",
            parse_mode="Markdown"
        )
        return
        
    elif query.data == "admin_broadcast":
        await query.edit_message_text("📝 ব্রডকাস্ট মেসেজটি লিখে পাঠান:")
        return WAITING_BROADCAST

    elif query.data == "admin_force":
        await query.edit_message_text("📢 চ্যানেলের ইউজারনেম পাঠান (যেমন: `@MyChannel`):")
        return WAITING_FORCE_CHANNEL

    elif query.data == "admin_add_button":
        await query.edit_message_text("🔘 বাটনের নাম (Title) লিখে পাঠান (যেমন: `Open Website`):")
        return WAITING_BUTTON_TITLE

    # ওনার সংক্রান্ত অপশনসমূহ
    if is_owner(user_id):
        if query.data == "admin_add_admin":
            await query.edit_message_text("➕ নতুন এডমিনের **Telegram ID (Numerics)** লিখে পাঠান:")
            return WAITING_ADD_ADMIN

        elif query.data == "admin_remove_admin":
            admins = bot_data.get("admins", [])
            if not admins:
                await query.edit_message_text("❌ কোনো এডমিন তালিকাভুক্ত নেই।")
                return ConversationHandler.END
            
            admin_list = "\n".join([f"`{a}`" for a in admins])
            await query.edit_message_text(
                f"➖ রিমুভ করতে চাওয়া এডমিনের Telegram ID লিখে পাঠান:\n\n**বর্তমান এডমিনগণ:**\n{admin_list}",
                parse_mode="Markdown"
            )
            return WAITING_REMOVE_ADMIN

        elif query.data == "admin_transfer_owner":
            await query.edit_message_text("⚠️ **সতর্কতা:** নতুন ওনারের **Telegram ID** লিখে পাঠান। মালিকানা হস্তান্তর হলে আপনি ওনার থেকে এডমিন হয়ে যাবেন।")
            return WAITING_TRANSFER_OWNERSHIP

# --- Conversation Steps ---
async def process_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    users = bot_data.get("users", [])
    count = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 **ADMIN MESSAGE:**\n\n{msg}")
            count += 1
        except Exception:
            pass
    await update.message.reply_text(f"✅ {count} জন ইউজারের কাছে মেসেজ পাঠানো হয়েছে।")
    return ConversationHandler.END

async def process_force_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel = update.message.text.strip()
    bot_data["force_channel"] = channel
    save_data(bot_data)
    await update.message.reply_text(f"✅ ফোর্স চ্যানেল সেটিং আপডেট হয়েছে: {channel}")
    return ConversationHandler.END

async def process_button_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["temp_title"] = update.message.text.strip()
    await update.message.reply_text("🔗 এবার ওয়েবসাইটের লিঙ্ক (URL) দিন (অবশ্যই `https://` সহ):")
    return WAITING_BUTTON_URL

async def process_button_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    title = context.user_data.get("temp_title", "Open Web")
    
    bot_data["web_button"] = {"title": title, "url": url}
    save_data(bot_data)

    try:
        await context.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text=title, web_app=WebAppInfo(url=url))
        )
    except Exception:
        pass

    await update.message.reply_text(f"✅ বাটন যোগ করা হয়েছে!\n\n**Name:** {title}\n**URL:** {url}")
    return ConversationHandler.END

async def process_add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_admin = int(update.message.text.strip())
        if new_admin in bot_data["admins"]:
            await update.message.reply_text("⚠️ এই ইউজার ইতোমধ্যে এডমিন আছে।")
        else:
            bot_data["admins"].append(new_admin)
            save_data(bot_data)
            await update.message.reply_text(f"✅ `{new_admin}` সফলভাবে নতুন এডমিন হিসেবে যুক্ত হয়েছে।", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ ভুল আইডি ফরম্যাট! শুধুমাত্র সংখ্যা (Numeric ID) ব্যবহার করুন।")
    return ConversationHandler.END

async def process_remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        rem_admin = int(update.message.text.strip())
        if rem_admin in bot_data["admins"]:
            bot_data["admins"].remove(rem_admin)
            save_data(bot_data)
            await update.message.reply_text(f"✅ `{rem_admin}` আইডিটি এডমিন তালিকা থেকে রিমুভ করা হয়েছে।", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ এই আইডি এডমিন তালিকায় পাওয়া যায়নি।")
    except ValueError:
        await update.message.reply_text("❌ ভুল আইডি ফরম্যাট!")
    return ConversationHandler.END

async def process_transfer_ownership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_owner = int(update.message.text.strip())
        old_owner = bot_data["owner"]
        
        bot_data["owner"] = new_owner
        if old_owner not in bot_data["admins"]:
            bot_data["admins"].append(old_owner) # পুরোনো ওনারকে এডমিন লিস্টে নামিয়ে নেওয়া
            
        save_data(bot_data)
        await update.message.reply_text(f"👑 **মালিকানা সফলভাবে হস্তান্তর করা হয়েছে!**\n\nনতুন ওনার আইডি: `{new_owner}`", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ ভুল আইডি ফরম্যাট!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ অপারেশন বাতিল করা হয়েছে।")
    return ConversationHandler.END

# ----------------- FILE & TEXT OBFUSCATION -----------------
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_force_join(user_id, context):
        await start(update, context)
        return

    doc = update.message.document
    if not doc.file_name.endswith(('.html', '.htm')):
        await update.message.reply_text("❌ শুধুমাত্র .html অথবা .htm ফাইল গ্রহণ করা হয়।")
        return

    file = await doc.get_file()
    input_path = "temp_input.html"
    await file.download_to_drive(input_path)

    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    obfuscated_code = heavy_obfuscate_html(code)
    output_filename = f"protected_{doc.file_name}"

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(obfuscated_code)

    await update.message.reply_document(
        document=open(output_filename, "rb"),
        filename=output_filename,
        caption="🔐 **আপনার HTML ফাইলটি এনক্রিপ্ট করা হয়েছে!**"
    )

    if os.path.exists(input_path): os.remove(input_path)
    if os.path.exists(output_filename): os.remove(output_filename)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⚙️ Admin Panel":
        await admin_panel(update, context)
        return
    elif text == "ℹ️ Help":
        await update.message.reply_text("💡 আমাকে যেকোনো HTML ফাইল বা কোড পাঠালে তা এনক্রিপ্ট করে সুরক্ষিত করে দেওয়া হবে।")
        return

    user_id = update.effective_user.id
    if not await check_force_join(user_id, context):
        await start(update, context)
        return

    obfuscated_code = heavy_obfuscate_html(text)
    output_filename = "protected_code.html"

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(obfuscated_code)

    await update.message.reply_document(
        document=open(output_filename, "rb"),
        filename="protected_index.html",
        caption="🔐 **আপনার দেওয়া কোডটি এনক্রিপ্ট করে ফাইল বানিয়ে দেওয়া হয়েছে।**"
    )

    if os.path.exists(output_filename): os.remove(output_filename)

# ----------------- MAIN EXECUTION -----------------
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_callback)],
        states={
            WAITING_BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_broadcast)],
            WAITING_FORCE_CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_force_channel)],
            WAITING_BUTTON_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_button_title)],
            WAITING_BUTTON_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_button_url)],
            WAITING_ADD_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_add_admin)],
            WAITING_REMOVE_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_remove_admin)],
            WAITING_TRANSFER_OWNERSHIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_transfer_ownership)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

    print("Bot is running...")
    app.run_polling()
