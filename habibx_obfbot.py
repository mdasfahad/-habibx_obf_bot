import base64
import os
import json
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, ReplyKeyboardRemove, MenuButtonWebApp, WebAppInfo
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes, ConversationHandler
)

# ----------------- YOUR CONFIGURATION -----------------
BOT_TOKEN = "8839587043:AAHLhKmyrdpJLK3AJlgcpOrjpJVTqya5lwg"  # BotFather থেকে পাওয়া আপনার বটের টোকেন দিন
DEFAULT_OWNER_ID = 8289191009                # আপনার টেলিগ্রাম আইডি
DEFAULT_OWNER_USERNAME = "@OWNER_USERNAME"   # আপনার টেলিগ্রাম ইউজারনেম
DEFAULT_BOT_USERNAME = "@YOUR_BOT_USERNAME"  # আপনার বটের ইউজারনেম

# Conversation States
(
    WAITING_BROADCAST,
    WAITING_FORCE_CHANNEL,
    WAITING_BUTTON_TITLE,
    WAITING_BUTTON_URL,
    WAITING_ADD_ADMIN,
    WAITING_REMOVE_ADMIN,
    WAITING_TRANSFER_OWNERSHIP,
    WAITING_CUSTOM_HEADER,
    WAITING_OWNER_USERNAME
) = range(9)

DATA_FILE = "bot_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "owner" not in data: data["owner"] = DEFAULT_OWNER_ID
                if "owner_username" not in data: data["owner_username"] = DEFAULT_OWNER_USERNAME
                if "bot_username" not in data: data["bot_username"] = DEFAULT_BOT_USERNAME
                if "admins" not in data: data["admins"] = []
                if "custom_header" not in data: 
                    data["custom_header"] = f"<!-- 😈🔥 Protected by {DEFAULT_BOT_USERNAME} | Dev: {DEFAULT_OWNER_USERNAME} 🔥😈 -->"
                return data
        except Exception:
            pass
    return {
        "owner": DEFAULT_OWNER_ID,
        "owner_username": DEFAULT_OWNER_USERNAME,
        "bot_username": DEFAULT_BOT_USERNAME,
        "admins": [],
        "users": [],
        "force_channel": "",
        "web_button": {"title": "", "url": ""},
        "custom_header": f"<!-- 😈🔥 Protected by {DEFAULT_BOT_USERNAME} | Dev: {DEFAULT_OWNER_USERNAME} 🔥😈 -->"
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
    custom_header = bot_data.get("custom_header", "")
    full_code = f"{custom_header}\n{html_code}"
    encoded = base64.b64encode(full_code.encode('utf-8')).decode('utf-8')
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
<noscript>JavaScript required to view this protected page.</noscript>
</body>
</html>"""

def get_main_keyboard(user_id: int):
    # আপনার কাস্টম স্থায়ী মেনু বাটন
    keyboard = [
        ["🎬 URL TO VIDEO"],
        ["🔐 OBFUSCATE HTML", "🌐 URL TO HTML"],
        ["👑 OWNER & DEV", "⚡ VIP FEATURES & INFO"]
    ]
    if is_admin(user_id):
        keyboard.append(["⚙️ Admin Panel"])
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

async def send_force_join_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel = bot_data.get("force_channel", "@YourChannel")
    channel_clean = channel.replace('@', '')
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{channel_clean}")],
        [InlineKeyboardButton("✅ Joined / Verify", callback_data="verify_join")]
    ]
    
    msg_text = f"⚠️ **বট ব্যবহার করতে আপনাকে অবশ্যই আমাদের চ্যানেলে জয়েন করতে হবে:**\n\n📢 Channel: {channel}"
    
    if update.message:
        await update.message.reply_text(
            msg_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text("🔒 চ্যানেল জয়েন না করা পর্যন্ত মেনু লক থাকবে।", reply_markup=ReplyKeyboardRemove())
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            msg_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ----------------- USER HANDLERS -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in bot_data["users"]:
        bot_data["users"].append(user_id)
        save_data(bot_data)

    if not await check_force_join(user_id, context):
        await send_force_join_msg(update, context)
        return

    await send_welcome_message(update, context)

async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    inline_kb = []
    web_btn = bot_data.get("web_button", {})
    if web_btn.get("title") and web_btn.get("url"):
        inline_kb.append([InlineKeyboardButton(web_btn["title"], web_app=WebAppInfo(url=web_btn["url"]))])

    reply_markup = InlineKeyboardMarkup(inline_kb) if inline_kb else None

    welcome_text = (
        f"👋 **স্বাগতম {bot_data.get('bot_username', DEFAULT_BOT_USERNAME)} এ!**\n\n"
        f"নিচের মেনু বাটন ব্যবহার করে কাজ সম্পাদন করুন অথবা আপনার `.html` ফাইলটি পাঠাতে পারেন।"
    )

    if update.callback_query:
        await update.callback_query.message.reply_text(welcome_text, reply_markup=get_main_keyboard(user_id), parse_mode="Markdown")
    else:
        await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard(user_id), parse_mode="Markdown")

    if reply_markup:
        target = update.callback_query.message if update.callback_query else update.message
        await target.reply_text("🔗 **ওয়েবসাইট ওপেন করুন:**", reply_markup=reply_markup)

# ----------------- ADMIN PANEL HANDLERS -----------------
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ আপনি এডমিন নন!")
        return

    keyboard = [
        [InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔗 Set Force Channel", callback_data="admin_force")],
        [InlineKeyboardButton("👤 Set Owner Username", callback_data="admin_set_owner_user")],
        [InlineKeyboardButton("🌐 Add Open Web Button", callback_data="admin_add_button")],
        [InlineKeyboardButton("✏️ Set Code Watermark/Msg", callback_data="admin_set_header")],
        [InlineKeyboardButton("📊 User Stats", callback_data="admin_stats")]
    ]

    if is_owner(user_id):
        keyboard.append([InlineKeyboardButton("➕ Add Admin", callback_data="admin_add_admin"),
                         InlineKeyboardButton("➖ Remove Admin", callback_data="admin_remove_admin")])
        keyboard.append([InlineKeyboardButton("👑 Transfer Ownership", callback_data="admin_transfer_owner")])

    role = "OWNER" if is_owner(user_id) else "ADMIN"
    await update.message.reply_text(f"⚙️ **ADMIN CONTROL PANEL** ({role})", reply_markup=InlineKeyboardMarkup(keyboard))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "verify_join":
        if await check_force_join(user_id, context):
            await query.message.delete()
            await query.message.reply_text("✅ জয়েন ভেরিফিকেশন সফল হয়েছে!")
            await send_welcome_message(update, context)
        else:
            await query.answer("❌ আপনি এখনো চ্যানেলে জয়েন করেননি! আগে জয়েন করুন।", show_alert=True)
        return

    if not is_admin(user_id):
        return

    if query.data == "admin_stats":
        total_users = len(bot_data.get("users", []))
        total_admins = len(bot_data.get("admins", []))
        owner_id = bot_data.get("owner")
        owner_username = bot_data.get("owner_username", DEFAULT_OWNER_USERNAME)
        await query.edit_message_text(
            f"📊 **বট স্ট্যাটাস:**\n\n"
            f"👑 **Owner ID:** `{owner_id}`\n"
            f"👤 **Owner Username:** {owner_username}\n"
            f"🛡️ **Total Admins:** {total_admins}\n"
            f"👥 **Total Users:** {total_users}",
            parse_mode="Markdown"
        )
        return
        
    elif query.data == "admin_broadcast":
        await query.edit_message_text("📝 ব্রডকাস্ট মেসেজটি লিখে পাঠান:")
        return WAITING_BROADCAST

    elif query.data == "admin_force":
        await query.edit_message_text("📢 চ্যানেলের ইউজারনেম পাঠান (যেমন: `@YourChannel`):")
        return WAITING_FORCE_CHANNEL

    elif query.data == "admin_set_owner_user":
        await query.edit_message_text("👤 ওনারের ইউজারনেম পাঠান (যেমন: `@YourUsername`):")
        return WAITING_OWNER_USERNAME

    elif query.data == "admin_add_button":
        await query.edit_message_text("🔘 বাটনের নাম (Title) লিখে পাঠান (যেমন: `Open Website`):")
        return WAITING_BUTTON_TITLE

    elif query.data == "admin_set_header":
        current = bot_data.get("custom_header", "None")
        await query.edit_message_text(f"✏️ **বর্তমান ওয়াটারমার্ক/মেসেজ:**\n`{current}`\n\nনতুন কাস্টম মেসেজ/ওয়াটারমার্কটি লিখে পাঠান:", parse_mode="Markdown")
        return WAITING_CUSTOM_HEADER

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
            await query.edit_message_text("⚠️ **সতর্কতা:** নতুন ওনারের **Telegram ID** লিখে পাঠান:")
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
    await update.message.reply_text(f"✅ ফোর্স চ্যানেল আপডেট হয়েছে: {channel}")
    return ConversationHandler.END

async def process_owner_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    if not username.startswith('@'):
        username = f"@{username}"
    bot_data["owner_username"] = username
    save_data(bot_data)
    await update.message.reply_text(f"✅ ওনার ইউজারনেম আপডেট হয়েছে: {username}")
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

async def process_custom_header(update: Update, context: ContextTypes.DEFAULT_TYPE):
    header = update.message.text.strip()
    bot_data["custom_header"] = header
    save_data(bot_data)
    await update.message.reply_text(f"✅ কাস্টম ওয়াটারমার্ক সেট হয়েছে:\n`{header}`", parse_mode="Markdown")
    return ConversationHandler.END

async def process_add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_admin = int(update.message.text.strip())
        if new_admin in bot_data["admins"]:
            await update.message.reply_text("⚠️ এই ইউজার ইতোমধ্যে এডমিন আছে।")
        else:
            bot_data["admins"].append(new_admin)
            save_data(bot_data)
            await update.message.reply_text(f"✅ `{new_admin}` সফলভাবে নতুন এডমিন যুক্ত হয়েছে।", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ ভুল আইডি ফরম্যাট!")
    return ConversationHandler.END

async def process_remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        rem_admin = int(update.message.text.strip())
        if rem_admin in bot_data["admins"]:
            bot_data["admins"].remove(rem_admin)
            save_data(bot_data)
            await update.message.reply_text(f"✅ `{rem_admin}` আইডিটি রিমুভ করা হয়েছে।", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ এই আইডি তালিকায় নেই।")
    except ValueError:
        await update.message.reply_text("❌ ভুল আইডি ফরম্যাট!")
    return ConversationHandler.END

async def process_transfer_ownership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_owner = int(update.message.text.strip())
        old_owner = bot_data["owner"]
        
        bot_data["owner"] = new_owner
        if old_owner not in bot_data["admins"]:
            bot_data["admins"].append(old_owner)
            
        save_data(bot_data)
        await update.message.reply_text(f"👑 **মালিকানা হস্তান্তর সম্পন্ন!**\n\nনতুন ওনার: `{new_owner}`", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ ভুল আইডি ফরম্যাট!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ কাজ বাতিল করা হয়েছে।")
    return ConversationHandler.END

# ----------------- OBFUSCATION CORE LOGIC -----------------
async def execute_obfuscation(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str, original_filename: str):
    msg = await update.message.reply_text("⏳ **Processing & Encrypting code... Please wait.**")
    
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    obfuscated_code = heavy_obfuscate_html(code)
    output_filename = f"Encrypted_{original_filename}"

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(obfuscated_code)

    await msg.delete()

    owner_user = bot_data.get("owner_username", DEFAULT_OWNER_USERNAME)
    bot_user = bot_data.get("bot_username", DEFAULT_BOT_USERNAME)

    caption_text = (
        f"👑 ════════════════════ 👑\n"
        f"👑 **UNBREAKABLE ENCRYPTED FILE (V2.0)** 👑\n"
        f"👑 ════════════════════ 👑\n\n"
        f"📁 **ফাইল নাম:** {output_filename}\n"
        f"🔒 **সাইফার:** 😈🔥 Polymorphic Chaos Stream (Unbreakable)\n"
        f"🚫 **প্রোটেকশন:** Anti-Hook + Anti-Debugger + CSS/JS Zero-Leak\n"
        f"🌐 **ব্রাউজার রানিং:** 100% Native Execution\n"
        f"⚡ **সিকিউরিটি:** Military-Grade Lock\n\n"
        f"🤖 **Bot:** {bot_user} | 👑 **Dev:** {owner_user}"
    )

    await update.message.reply_document(
        document=open(output_filename, "rb"),
        filename=output_filename,
        caption=caption_text,
        parse_mode="Markdown"
    )

    if os.path.exists(file_path): os.remove(file_path)
    if os.path.exists(output_filename): os.remove(output_filename)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_force_join(user_id, context):
        await send_force_join_msg(update, context)
        return

    doc = update.message.document
    if not doc.file_name.endswith(('.html', '.htm', '.txt')):
        await update.message.reply_text("❌ শুধুমাত্র `.html` অথবা `.htm` ফাইল সাপোর্ট করে।")
        return

    file = await doc.get_file()
    input_path = "temp_input.html"
    await file.download_to_drive(input_path)
    await execute_obfuscation(update, context, input_path, doc.file_name)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if not await check_force_join(user_id, context):
        await send_force_join_msg(update, context)
        return

    owner_user = bot_data.get("owner_username", DEFAULT_OWNER_USERNAME)

    # কাস্টম মেনু বাটন রেসপন্স
    if text == "🔐 OBFUSCATE HTML":
        await update.message.reply_text("📂 **আপনার `.html` ফাইলটি সেন্ড করুন অথবা কোডটি সরাসরি এখানে পেস্ট করুন:**")
        return
    elif text == "🎬 URL TO VIDEO":
        await update.message.reply_text("🎥 **টিউটোরিয়াল ভিডিও লিঙ্ক:**\nপ্রয়োজনীয় টিউটোরিয়াল দেখতে চ্যানেলে ভিজিট করুন।")
        return
    elif text == "🌐 URL TO HTML":
        await update.message.reply_text("🌐 ওয়েবসাইট URL থেকে এইচটিএমএল ফেচ করার সুবিধা শীঘ্রই যুক্ত করা হবে।")
        return
    elif text == "👑 OWNER & DEV":
        await update.message.reply_text(f"👑 **Developer Contact:** {owner_user}")
        return
    elif text == "⚡ VIP FEATURES & INFO":
        await update.message.reply_text(
            "⚡ **VIP Security Features:**\n"
            "- Polymorphic Chaos Stream Encryption\n"
            "- Anti-Hook & Anti-Debugger Protection\n"
            "- Zero-Leak High Compression"
        )
        return
    elif text == "⚙️ Admin Panel":
        await admin_panel(update, context)
        return

    # সরাসরি কোড পেস্ট করা হলে
    input_path = "temp_input.html"
    with open(input_path, "w", encoding="utf-8") as f:
        f.write(text)

    await execute_obfuscation(update, context, input_path, "code.html")

# ----------------- MAIN EXECUTION -----------------
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback_handler)],
        states={
            WAITING_BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_broadcast)],
            WAITING_FORCE_CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_force_channel)],
            WAITING_OWNER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_owner_username)],
            WAITING_BUTTON_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_button_title)],
            WAITING_BUTTON_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_button_url)],
            WAITING_CUSTOM_HEADER: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_custom_header)],
            WAITING_ADD_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_add_admin)],
            WAITING_REMOVE_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_remove_admin)],
            WAITING_TRANSFER_OWNERSHIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_transfer_ownership)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

    print("Bot is running...")
    app.run_polling()
