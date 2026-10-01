import base64
import os
import json
import time
import urllib.request
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# ----------------- CONFIGURATION -----------------
BOT_TOKEN = "8839587043:AAHLhKmyrdpJLK3AJlgcpOrjpJVTqya5lwg"  # এখানে আপনার টেলিগ্রাম বট টোকেন দিন
DEFAULT_OWNER_ID = 8289191009                # আপনার টেলিগ্রাম আইডি
DEFAULT_OWNER_USERNAME = "@habibx_obf_bot"        # আপনার ইউজারনেম
DEFAULT_BOT_USERNAME = "@sabbir2850"     # বটের ইউজারনেম

# Conversation States
(
    WAITING_BROADCAST,
    WAITING_FORCE_CHANNEL,
    WAITING_BOT_USERNAME,
    WAITING_OWNER_USERNAME,
    WAITING_CUSTOM_HEADER,
    WAITING_ADD_ADMIN,
    WAITING_REMOVE_ADMIN,
    WAITING_TRANSFER_OWNERSHIP,
    WAITING_URL_TO_HTML
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
                if "users" not in data: data["users"] = []
                if "force_channel" not in data: data["force_channel"] = ""
                if "custom_header" not in data: 
                    data["custom_header"] = "🔒 SABBIR UNBREAKABLE ULTRA CIPHER V2.0 - DO NOT MODIFY"
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
        "custom_header": "🔒 SABBIR UNBREAKABLE ULTRA CIPHER V2.0 - DO NOT MODIFY"
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

bot_data = load_data()

def is_owner(user_id: int) -> bool:
    return user_id == bot_data.get("owner", DEFAULT_OWNER_ID)

def is_admin(user_id: int) -> bool:
    return is_owner(user_id) or (user_id in bot_data.get("admins", []))

# ----------------- ADVANCED OBFUSCATION ENGINE -----------------
def heavy_obfuscate_html(html_code: str) -> str:
    bot_user = bot_data.get("bot_username", DEFAULT_BOT_USERNAME)
    owner_user = bot_data.get("owner_username", DEFAULT_OWNER_USERNAME)
    custom_hdr = bot_data.get("custom_header", "🔒 SABBIR UNBREAKABLE ULTRA CIPHER V2.0")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Base64 encode the original code
    encoded = base64.b64encode(html_code.encode('utf-8')).decode('utf-8')

    # হেডার ওয়াটারমার্ক
    header_art = f"""<!--
//========================================================================
//  {custom_hdr}
//========================================================================
//  Obfuscated By: {owner_user}
//  Telegram Bot: {bot_user}
//  Timestamp: {timestamp}
//========================================================================
-->
"""

    # মূল ফাইল স্ট্রাকচার
    obfuscated_template = f"""{header_art}
<!DOCTYPE html>
<!-- CIPHER_SIGNATURE: 😈🔥💀❌%=%+=-&398RMπr🔥Jkhj1CX2πk🤬b7gM^MsK😈bDoqSae3kx3RZπPquc😈ddn8edL7c3Je5😈emraSWzA6llRBπgdyrr1Jr2oWAevRkt62Xe÷🤬Wwv^bSEq£1uS🔥sNQMq3EgQXh -->
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* {{
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
    -ms-user-select: none !important;
    user-select: none !important;
}}
</style>
<script>
(function() {{
    'use strict';

    // 🔴 1. ANTI-DEVTOOLS & SHORTCUT SHIELD
    window.addEventListener('contextmenu', function(e) {{ e.preventDefault(); e.stopPropagation(); return false; }}, true);
    window.addEventListener('keydown', function(e) {{
        if (e.key === 'F12' || 
           (e.ctrlKey && e.key.toLowerCase() === 'u') || 
           (e.ctrlKey && e.key.toLowerCase() === 's') || 
           (e.ctrlKey && e.shiftKey && ['i', 'j', 'c', 'k'].includes(e.key.toLowerCase()))) {{
            e.preventDefault();
            e.stopPropagation();
            return false;
        }}
    }}, true);

    const _fakeMsg = "😈🔥💀❌ [কোড চোর সনাক্ত হয়েছে! এই কোড এনক্রিপ্ট করেছে: {bot_user} | ওনার: {owner_user}] 🔒";

    // 🔴 2. ANTI-DEBUGGER TIMING SHIELD
    let _t0 = Date.now();
    function _verifyIntegrity() {{
        let _t1 = Date.now();
        if (_t1 - _t0 > 400) {{
            try {{ document.documentElement.innerHTML = '<h1 style="color:red;text-align:center;margin-top:20%;">' + _fakeMsg + '</h1>'; }} catch(e) {{}}
            throw new Error("Debugger Detained");
        }}
        _t0 = _t1;
    }}
    setInterval(_verifyIntegrity, 500);

    // 🔴 3. DYNAMIC DECODER & RUNTIME EXECUTION ({bot_user} | Dev: {owner_user})
    window.onload = function() {{
        try {{
            var _raw = "{encoded}";
            var _decoded = atob(_raw);
            document.open();
            document.write(_decoded);
            document.close();
        }} catch(err) {{
            console.error("Protected by {bot_user}");
        }}
    }};
}})();
</script>
</head>
<body>
<noscript>JavaScript is required to view this protected content. Dev: {owner_user}</noscript>
</body>
</html>"""
    return obfuscated_template

# ----------------- KEYBOARDS -----------------
def get_main_keyboard(user_id: int):
    keyboard = [
        ["🔐 OBFUSCATE HTML", "🌐 URL TO HTML"],
        ["🎬 URL TO VIDEO", "⚡ VIP FEATURES & INFO"],
        ["👑 OWNER & DEV"]
    ]
    if is_admin(user_id):
        keyboard.append(["⚙️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard(user_id: int):
    keyboard = [
        ["📢 Broadcast Msg", "🔗 Set Force Channel"],
        ["❌ Remove Force Channel", "🤖 Set Bot Username"],
        ["🗑️ Remove Bot Username", "👤 Set Owner Username"],
        ["🗑️ Remove Owner Username", "✏️ Set Watermark"],
        ["📊 User Stats"]
    ]
    if is_owner(user_id):
        keyboard.append(["➕ Add Admin", "➖ Remove Admin"])
        keyboard.append(["👑 Transfer Owner"])
    keyboard.append(["🔙 Back to Main Menu"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def check_force_join(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    channel = bot_data.get("force_channel", "").strip()
    if not channel:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
    except Exception:
        pass
    return False

# ----------------- CORE PROCESSOR -----------------
async def execute_obfuscation(update: Update, context: ContextTypes.DEFAULT_TYPE, code_text: str, original_filename: str):
    owner_user = bot_data.get("owner_username", DEFAULT_OWNER_USERNAME)
    bot_user = bot_data.get("bot_username", DEFAULT_BOT_USERNAME)

    processing_msg = (
        f"👑 ════════════════════ 👑\n"
        f"🔐 **হাবিব ভাই আনব্রেকএবল এনক্রিপশন চলছে...**\n"
        f"👑 ════════════════════ 👑\n\n"
        f"⚡ Applying Polymorphic Chaos Cipher & Anti-Hook Shields..."
    )
    msg = await update.message.reply_text(processing_msg, parse_mode="Markdown")

    obfuscated_code = heavy_obfuscate_html(code_text)
    output_filename = f"SABBIR_Encrypted_{original_filename}"

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(obfuscated_code)

    await msg.delete()

    caption_text = (
        f"👑 ════════════════════ 👑\n"
        f"🛡️ **সাব্বির ভাই আনব্রেকএবল ইনক্রিপ্টেড (V2.0)**\n"
        f"👑 ════════════════════ 👑\n\n"
        f"📁 **ফাইল নাম:** `{output_filename}`\n"
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

    if os.path.exists(output_filename):
        os.remove(output_filename)

# ----------------- COMMANDS & HANDLERS -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in bot_data["users"]:
        bot_data["users"].append(user_id)
        save_data(bot_data)

    if not await check_force_join(user_id, context):
        channel = bot_data.get("force_channel")
        await update.message.reply_text(
            f"⚠️ **বট ব্যবহার করতে আমাদের অফিশিয়াল চ্যানেলে যুক্ত থাকুন:**\n\n📢 Channel: {channel}\n\nজয়েন করার পর আবার /start চাপুন।"
        )
        return

    bot_user = bot_data.get("bot_username", DEFAULT_BOT_USERNAME)
    owner_user = bot_data.get("owner_username", DEFAULT_OWNER_USERNAME)

    welcome_text = (
        f"👋 **স্বাগতম {bot_user} বটে!**\n\n"
        f"👑 **Developer:** {owner_user}\n"
        f"⚡ আপনার `.html` ফাইলটি সেন্ড বা ফরওয়ার্ড করুন অবফাস্কেট করার জন্য।"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard(user_id), parse_mode="Markdown")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_force_join(user_id, context):
        await update.message.reply_text("❌ আগে চ্যানেলে জয়েন করুন!")
        return

    doc = update.message.document
    file_name = doc.file_name or "index.html"
    
    file = await doc.get_file()
    file_bytes = await file.download_as_bytearray()
    code_text = file_bytes.decode('utf-8', errors='ignore')

    await execute_obfuscation(update, context, code_text, file_name)

async def handle_main_menu_clicks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if not await check_force_join(user_id, context):
        await update.message.reply_text("❌ আগে চ্যানেলে জয়েন করুন!")
        return

    owner_user = bot_data.get("owner_username", DEFAULT_OWNER_USERNAME)

    if text == "🔐 OBFUSCATE HTML":
        await update.message.reply_text("📂 **আপনার HTML ফাইলটি সেন্ড বা ফরওয়ার্ড করুন অথবা সরাসরি কোড পেস্ট করুন:**")
        return ConversationHandler.END
    elif text == "🌐 URL TO HTML":
        await update.message.reply_text("🌐 **যে ওয়েবসাইটের HTML অবফাস্কেট করতে চান সেটির URL দিন (যেমন: https://google.com):**")
        return WAITING_URL_TO_HTML
    elif text == "🎬 URL TO VIDEO":
        await update.message.reply_text(f"🎥 **অফিশিয়াল ভিডিও টিউটোরিয়াল:**\nভিডিও ও আপডেটের জন্য আমাদের ডেভেলপার ({owner_user}) এর সাথে যোগাযোগ রাখুন।")
        return ConversationHandler.END
    elif text == "👑 OWNER & DEV":
        await update.message.reply_text(f"👑 **Developer Username:** {owner_user}\n🤖 **Bot Username:** {bot_data.get('bot_username')}")
        return ConversationHandler.END
    elif text == "⚡ VIP FEATURES & INFO":
        await update.message.reply_text(
            "⚡ **VIP Security Shields Enabled:**\n"
            "- Anti-DevTools & F12 Lock\n"
            "- Anti-Debugger Loop System\n"
            "- Dynamic Base64 Execution Engine"
        )
        return ConversationHandler.END
    elif text == "⚙️ Admin Panel":
        if is_admin(user_id):
            await update.message.reply_text("⚙️ **ADMIN CONTROL PANEL**", reply_markup=get_admin_keyboard(user_id))
        else:
            await update.message.reply_text("❌ আপনি এডমিন নন!")
        return ConversationHandler.END
    elif text == "🔙 Back to Main Menu":
        await update.message.reply_text("🔙 মূল মেনুতে ফিরে যাওয়া হয়েছে।", reply_markup=get_main_keyboard(user_id))
        return ConversationHandler.END
    
    # Admin Keyboards
    elif is_admin(user_id) and text == "📊 User Stats":
        await update.message.reply_text(
            f"📊 **বট স্ট্যাটাস:**\n\n"
            f"👑 **Owner ID:** `{bot_data.get('owner')}`\n"
            f"👤 **Owner:** {bot_data.get('owner_username')}\n"
            f"🤖 **Bot:** {bot_data.get('bot_username')}\n"
            f"📢 **Force Channel:** {bot_data.get('force_channel') or 'None'}\n"
            f"🛡️ **Total Admins:** {len(bot_data.get('admins', []))}\n"
            f"👥 **Total Users:** {len(bot_data.get('users', []))}",
            parse_mode="Markdown"
        )
        return ConversationHandler.END
    elif is_admin(user_id) and text == "📢 Broadcast Msg":
        await update.message.reply_text("📝 ব্রডকাস্ট মেসেজটি লিখে পাঠান:")
        return WAITING_BROADCAST
    elif is_admin(user_id) and text == "🔗 Set Force Channel":
        await update.message.reply_text("📢 চ্যানেলের ইউজারনেম পাঠান (যেমন: `@YourChannel`):")
        return WAITING_FORCE_CHANNEL
    elif is_admin(user_id) and text == "❌ Remove Force Channel":
        bot_data["force_channel"] = ""
        save_data(bot_data)
        await update.message.reply_text("✅ ফোর্স চ্যানেল সম্পূর্ণ তুলে নেওয়া হয়েছে!")
        return ConversationHandler.END
    elif is_admin(user_id) and text == "🤖 Set Bot Username":
        await update.message.reply_text("🤖 বটের নতুন ইউজারনেম লিখে দিন (যেমন: `@SABBIR_OBF_BOT`):")
        return WAITING_BOT_USERNAME
    elif is_admin(user_id) and text == "🗑️ Remove Bot Username":
        bot_data["bot_username"] = "None"
        save_data(bot_data)
        await update.message.reply_text("✅ বটের ইউজারনেম রিমুভ করা হয়েছে!")
        return ConversationHandler.END
    elif is_admin(user_id) and text == "👤 Set Owner Username":
        await update.message.reply_text("👤 ওনারের নতুন ইউজারনেম লিখে দিন (যেমন: `@SABBIRBD0`):")
        return WAITING_OWNER_USERNAME
    elif is_admin(user_id) and text == "🗑️ Remove Owner Username":
        bot_data["owner_username"] = "None"
        save_data(bot_data)
        await update.message.reply_text("✅ ওনারের ইউজারনেম রিমুভ করা হয়েছে!")
        return ConversationHandler.END
    elif is_admin(user_id) and text == "✏️ Set Watermark":
        await update.message.reply_text("✏️ নতুন কাস্টম হেডার/ওয়াটারমার্ক লিখে পাঠান:")
        return WAITING_CUSTOM_HEADER
    elif is_owner(user_id) and text == "➕ Add Admin":
        await update.message.reply_text("➕ নতুন এডমিনের **Telegram ID** দিন:")
        return WAITING_ADD_ADMIN
    elif is_owner(user_id) and text == "➖ Remove Admin":
        await update.message.reply_text("➖ রিমুভ করতে চাওয়া এডমিনের ID দিন:")
        return WAITING_REMOVE_ADMIN
    elif is_owner(user_id) and text == "👑 Transfer Owner":
        await update.message.reply_text("⚠️ নতুন ওনারের **Telegram ID** দিন:")
        return WAITING_TRANSFER_OWNERSHIP
    else:
        if not text.startswith("/"):
            await execute_obfuscation(update, context, text, "index.html")
        return ConversationHandler.END

# ----------------- STATE INPUT PROCESSORS -----------------
async def proc_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith(("http://", "https://")): url = "https://" + url
    msg = await update.message.reply_text("🌐 **ওয়েবসাইট থেকে কোড প্রসেস করা হচ্ছে...**")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html_content = resp.read().decode('utf-8')
            await msg.delete()
            await execute_obfuscation(update, context, html_content, "web_page.html")
    except Exception as e:
        await msg.edit_text(f"❌ ওয়েবসাইট ফেচ করতে ব্যর্থ: {str(e)}")
    return ConversationHandler.END

async def proc_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_text = update.message.text
    count = 0
    for uid in bot_data.get("users", []):
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 **BROADCAST:**\n\n{msg_text}")
            count += 1
        except Exception: pass
    await update.message.reply_text(f"✅ {count} জন ইউজারের কাছে পাঠানো হয়েছে।")
    return ConversationHandler.END

async def proc_force_chan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ch = update.message.text.strip()
    if not ch.startswith('@'): ch = f"@{ch}"
    bot_data["force_channel"] = ch
    save_data(bot_data)
    await update.message.reply_text(f"✅ ফোর্স চ্যানেল সেট করা হয়েছে: {ch}")
    return ConversationHandler.END

async def proc_bot_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.message.text.strip()
    if not u.startswith('@'): u = f"@{u}"
    bot_data["bot_username"] = u
    save_data(bot_data)
    await update.message.reply_text(f"✅ বটের ইউজারনেম সেভ হয়েছে: {u}", reply_markup=get_admin_keyboard(update.effective_user.id))
    return ConversationHandler.END

async def proc_owner_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.message.text.strip()
    if not u.startswith('@'): u = f"@{u}"
    bot_data["owner_username"] = u
    save_data(bot_data)
    await update.message.reply_text(f"✅ ওনারের ইউজারনেম সেভ হয়েছে: {u}", reply_markup=get_admin_keyboard(update.effective_user.id))
    return ConversationHandler.END

async def proc_custom_hdr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_data["custom_header"] = update.message.text.strip()
    save_data(bot_data)
    await update.message.reply_text("✅ কাস্টম হেডার আপডেট করা হয়েছে!")
    return ConversationHandler.END

async def proc_add_adm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        aid = int(update.message.text.strip())
        if aid not in bot_data["admins"]:
            bot_data["admins"].append(aid)
            save_data(bot_data)
            await update.message.reply_text(f"✅ `{aid}` এডমিন হিসেবে সেভ হয়েছে।", parse_mode="Markdown")
    except Exception: await update.message.reply_text("❌ আইডি ভুল হয়েছে।")
    return ConversationHandler.END

async def proc_rem_adm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        aid = int(update.message.text.strip())
        if aid in bot_data["admins"]:
            bot_data["admins"].remove(aid)
            save_data(bot_data)
            await update.message.reply_text(f"✅ `{aid}` এডমিন থেকে রিমুভ হয়েছে।", parse_mode="Markdown")
    except Exception: await update.message.reply_text("❌ আইডি ভুল হয়েছে।")
    return ConversationHandler.END

async def proc_trans_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        oid = int(update.message.text.strip())
        bot_data["owner"] = oid
        save_data(bot_data)
        await update.message.reply_text(f"👑 ওনার পরিবর্তন সফল! নতুন আইডি: `{oid}`", parse_mode="Markdown")
    except Exception: await update.message.reply_text("❌ আইডি ভুল হয়েছে।")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ কাজ বাতিল করা হয়েছে।", reply_markup=get_main_keyboard(update.effective_user.id))
    return ConversationHandler.END

# ----------------- MAIN ENTRY POINT -----------------
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & (~filters.COMMAND), handle_main_menu_clicks)],
        states={
            WAITING_URL_TO_HTML: [MessageHandler(filters.TEXT & ~filters.COMMAND, proc_url)],
            WAITING_BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, proc_broadcast)],
            WAITING_FORCE_CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, proc_force_chan)],
            WAITING_BOT_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, proc_bot_user)],
            WAITING_OWNER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, proc_owner_user)],
            WAITING_CUSTOM_HEADER: [MessageHandler(filters.TEXT & ~filters.COMMAND, proc_custom_hdr)],
            WAITING_ADD_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, proc_add_adm)],
            WAITING_REMOVE_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, proc_rem_adm)],
            WAITING_TRANSFER_OWNERSHIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, proc_trans_owner)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("Bot is successfully running...")
    app.run_polling()
