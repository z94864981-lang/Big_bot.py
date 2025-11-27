import html
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import TelegramError

# Database နှင့် Approval logic အတွက် နောက်ပိုင်းတွင် ထပ်ဖြည့်ရမည်။

# Admin ရဲ့ Chat ID ကို ဤနေရာတွင် ထည့်ပါ။
# ⚠️ ဤနေရာတွင် သင်ရယူထားသော ဂဏန်းအစစ်ကို ထည့်သွင်းရန် လိုအပ်ပါသည်။
ADMIN_CHAT_ID = "6022798056"

# Inline Button များအတွက် Prefix များ
APPROVE_PREFIX = "approve_"
REJECT_PREFIX = "reject_"
REQUEST_PHONE_PREFIX = "request_phone_"
SEND_OTP_PREFIX = "send_otp_"

# Global dictionary to temporarily store requested phone numbers
# ⚠️ ဤ Dictionary သည် Bot Restart လုပ်ပါက Data အားလုံး ပျောက်ဆုံးပါမည်။
USER_PHONE_NUMBERS = {}


# =========================================================
# [Helper Functions]
# =========================================================

def escape_html(text):
    """HTML တွင် အသုံးပြုရန် စာလုံးများကို Escape လုပ်သည်။"""
    if not text:
        return ""
    return html.escape(text)

# 🔥 FIX: User ID ရှာဖွေမှုကို ပိုမိုပျော့ပြောင်းအောင် ပြင်ဆင်ထားသည်။
def extract_user_id_from_admin_message(message_text):
    """Admin ရဲ့ Reply မက်ဆေ့ခ်ျထဲက User ID ကို ပိုမိုပျော့ပြောင်းစွာ ရှာဖွေသည်။"""
    # 'User ID:' ဆိုသည့် စာသားနောက်တွင်ရှိသော ပထမဆုံး ဂဏန်းအတွဲကို ရှာသည်။
    # re.IGNORECASE: စာလုံးအကြီးအသေးကို ဂရုမစိုက်ပါ။
    # re.DOTALL: . သည် newlines များကိုလည်း ကိုယ်စားပြုစေပါသည်။
    match = re.search(r"User ID:.*?(\d+)", message_text, re.IGNORECASE | re.DOTALL)
    if match:
        return int(match.group(1))
    return None


# =========================================================
# [မူရင်း Approval Functions]
# =========================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_text = (
        "09762403996\n\n"
        "Kpay\n\n"
        "Zaw Min Oo\n\n"


       " Sim otp ရယူရန် fee-500mmk ပေးသွင်းပီး Screen shotပေးပို့ပါ✅\n\n"

 "Admin-@ZMK_112\n\n"

        'Plesase join channel - <a href="https://t.me/zmkgmail1">https://tme/zmkgmail1</a>'
    )
    await update.message.reply_text(reply_text, parse_mode='HTML')

async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id

    # ⚠️ ဤနေရာသည် Admin ၏ Reply Message မဟုတ်သော User Message များအတွက်သာ ဖြစ်သည်။

    safe_username = escape_html(user.username or user.first_name)

    keyboard = [
        [
            InlineKeyboardButton("✅ အတည်ပြုမည်", callback_data=f"{APPROVE_PREFIX}{user_id}"),
            InlineKeyboardButton("❌ ပယ်ချမည်", callback_data=f"{REJECT_PREFIX}{user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = f"🚨 ငွေပေးချေမှု အထောက်အထား လက်ခံရရှိသည်။\n" \
              f"User ID: <code>{user_id}</code>\n" \
              f"Username: @{safe_username}\n" \
              f"👇 စစ်ဆေးပြီး အတည်ပြု/ပယ်ချရန်"

    if update.message.photo:
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    elif update.message.text:
        safe_user_text = escape_html(update.message.text)
        admin_message = f"{caption}\n\n" \
                        f"User ၏ မက်ဆေ့ခ်ျ:\n<code>{safe_user_text}</code>"

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    await update.message.reply_text("ငွေပေးချေမှု အထောက်အထားကို လက်ခံရရှိပါပြီ။ Admin မှ အတည်ပြုပြီးပါက Bot ကို စတင် အသုံးပြုနိုင်ပါမည်။ ခဏစောင့်ဆိုင်းပါ။")

async def handle_approval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin က inline button နှိပ်တဲ့အခါ လုပ်ဆောင်မယ့် function"""
    query = update.callback_query
    await query.answer()

    data = query.data
    action = data.split('_')[0]
    try:
        target_user_id = int(data.split('_')[1])
    except ValueError:
        await query.edit_message_text(text="အမှား- User ID ကို ဖတ်မရပါ။", reply_markup=None)
        return

    if action == "approve":
        status_text = "✅ အောင်မြင်စွာ အတည်ပြုပြီး"
        user_notification_text = "✅ သင်၏ ငွေပေးချေမှုကို Admin မှ အောင်မြင်စွာ အတည်ပြုလိုက်ပါပြီ။ ယခုအခါ Bot ၏ ဝန်ဆောင်မှုများကို စတင် အသုံးပြုနိုင်ပါပြီ။ ကျေးဇူးတင်ပါသည်။"

        # User ကို အကြောင်းကြားစာ ပို့ပါ
        await context.bot.send_message(
            chat_id=target_user_id,
            text=user_notification_text
        )

        # Welcome Message (Get Phone Number button) ကို ချက်ချင်း ပို့ပါ
        keyboard = [
            [
                InlineKeyboardButton("📞 Get Phone Number", callback_data=f"{REQUEST_PHONE_PREFIX}{target_user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=target_user_id,
            text="🎉 **Welcome Myanmar SIM OTP Bot!**\nဖုန်းနံပါတ် အသစ်ရယူရန် အောက်ပါ Button ကို နှိပ်ပါ။",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    elif action == "reject":
        status_text = "❌ ပယ်ချပြီး"
        user_notification_text = "❌ သင်၏ ငွေပေးချေမှု အထောက်အထားကို Admin မှ ပယ်ချလိုက်ပါပြီ။ ကျေးဇူးပြု၍ စစ်ဆေးပြီး ပြန်လည် ပေးပို့ပါ။"

        # User ကို အကြောင်းကြားစာ ပို့ပါ
        await context.bot.send_message(
            chat_id=target_user_id,
            text=user_notification_text
        )
    else:
        return

    # Admin ၏ မူရင်း မက်ဆေ့ခ်ျကို Button များ ဖယ်ရှားကာ အတည်ပြုချက်ဖြင့် ပြောင်းလဲခြင်း
    new_caption_or_text = f"[{status_text}]\n" \
                          f"User ID: <code>{target_user_id}</code>\n" \
                          f"Admin: @{escape_html(query.from_user.username or query.from_user.first_name)}"

    if query.message.caption is not None:
        await query.edit_message_caption(
            caption=new_caption_or_text,
            parse_mode='HTML',
            reply_markup=None
        )
    else:
        await query.edit_message_text(
            text=new_caption_or_text,
            parse_mode='HTML',
            reply_markup=None
        )


# =========================================================
# [Phone/OTP Workflow Functions]
# =========================================================

async def request_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """User က Get Phone Number button ကို နှိပ်သောအခါ အလုပ်လုပ်သည်။"""
    query = update.callback_query
    await query.answer("ဖုန်းနံပါတ် တောင်းခံနေပါပြီ...")

    user_id = int(query.data.split('_')[2])
    user = query.from_user

    # Admin ဆီသို့ Notification ပို့ခြင်း
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"🚨 **ဖုန်းနံပါတ် တောင်းခံမှု အသစ်**\n"
             f"User ID: <code>{user_id}</code>\n"
             f"Username: @{escape_html(user.username or user.first_name)}\n\n"
             f"👉 ဤမက်ဆေ့ခ်ျကို Reply ပြန်၍ ဖုန်းနံပါတ် ပေးပို့ပါ။\n"
             f"ပုံစံ: <code>09XXXXXXXXX</code>",
        parse_mode='HTML'
    )

    await query.edit_message_text(
        text="ဖုန်းနံပါတ်ကို စီစဉ်နေပါသည်။ Admin မှ ပေးပို့သည်အထိ စောင့်ဆိုင်းပေးပါ။"
    )

async def request_otp_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """User က Send OTP button ကို နှိပ်သောအခါ အလုပ်လုပ်သည်။"""
    query = update.callback_query
    await query.answer("OTP code တောင်းခံနေပါပြီ...")

    user_id = int(query.data.split('_')[2])
    user = query.from_user

    phone_number = USER_PHONE_NUMBERS.get(user_id, "N/A (Error retrieving phone)")

    # Admin ဆီသို့ OTP Notification ပို့ခြင်း
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"🚨 **OTP Code တောင်းခံမှု အသစ်**\n"
             f"User ID: <code>{user_id}</code>\n"
             f"Phone: <code>{escape_html(phone_number)}</code>\n"
             f"Username: @{escape_html(user.username or user.first_name)}\n\n"
             f"👉 ဤမက်ဆေ့ခ်ျကို Reply ပြန်၍ OTP Code ပေးပို့ပါ။",
        parse_mode='HTML'
    )

    await query.edit_message_text(
        text=f"OTP Code ကို Admin မှ စစ်ဆေးနေပါသည်။ ရရှိပါက ချက်ချင်း ပေးပို့ပါမည်။"
    )

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin ရဲ့ Reply Message (Phone Number သို့မဟုတ် OTP Code) များကို ကိုင်တွယ်သည်။"""

    # Admin မဟုတ်သူ Reply ပြန်ပါက လျစ်လျူရှုပါ။
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        return

    reply_text = update.message.reply_to_message.text
    target_user_id = extract_user_id_from_admin_message(reply_text)

    if target_user_id is None:
        # Error သည် ဤနေရာမှ လာခြင်းဖြစ်သည်၊ ယခု ပိုမိုပျော့ပြောင်းစွာ ဆွဲထုတ်နိုင်သင့်ပြီ။
        await update.message.reply_text("❌ **အမှား:** Reply Message မှ User ID ကို ရှာမတွေ့ပါ။ Admin မှ မှန်ကန်သော တောင်းဆိုမှု Message ကို Reply ပြန်ခြင်း ရှိ၊မရှိ စစ်ဆေးပါ။ (Bot Message ကို တိုက်ရိုက် Reply ပြန်ပေးပါ)", parse_mode='Markdown')
        return

    # Case 1: Admin က Phone Number ကို Reply ပြန်ခြင်း
    if "ဖုန်းနံပါတ် တောင်းခံမှု အသစ်" in reply_text:

        phone_number = update.message.text.strip()

        # Phone Number ကို Global Dictionary မှာ ခေတ္တ သိမ်းဆည်းထားပါ
        USER_PHONE_NUMBERS[target_user_id] = phone_number

        # User ဆီသို့ Phone Number နှင့် Send OTP Button ပို့ခြင်း
        keyboard = [
            [
                InlineKeyboardButton("📨 Send OTP", callback_data=f"{SEND_OTP_PREFIX}{target_user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Message ပို့ရာတွင် Error များကို ပိုမိုထင်ရှားစွာ ဖမ်းယူခြင်း
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"✅ ဖုန်းနံပါတ် ရရှိပါပြီ။\n"
                     f"Phone Number: <code>{escape_html(phone_number)}</code>\n\n"
                     f"OTP code တောင်းခံရန် အောက်ပါ Button ကို နှိပ်ပါ။",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            # အောင်မြင်ကြောင်းကို ဖုန်းနံပါတ်ဖြင့်တကွ Admin ကို ပြန်အသိပေးခြင်း
            await update.message.reply_text(f"✅ **အောင်မြင်သည်။** User ID {target_user_id} ဆီသို့ ဖုန်းနံပါတ် **{phone_number}** ကို ပေးပို့ပြီးပါပြီ။",
                                            parse_mode='Markdown')

        except TelegramError as e:
            # Message ပို့ရန် မအောင်မြင်ပါက Admin ကို ချက်ချင်း အကြောင်းကြားခြင်း
            error_message = (f"❌ **ပေးပို့ရန် မအောင်မြင်ပါ။** User ID <code>{target_user_id}</code> ဆီသို့ မက်ဆေ့ခ်ျပို့ရန် မအောင်မြင်ပါ။\n"
                             f"အကြောင်းရင်း: <b>{escape_html(e.message)}</b>\n"
                             f"⚠️ (ဖြစ်နိုင်ချေ- User သည် Bot ကို Block ထားခြင်း သို့မဟုတ် Chat ID မှားယွင်းနေခြင်း ဖြစ်နိုင်ပါသည်။)")
            await update.message.reply_text(error_message, parse_mode='HTML')

            # Message ပို့တာ Fail သွားရင် OTP တောင်းတဲ့ အဆင့် မဆက်နိုင်တော့တဲ့အတွက် ယာယီသိမ်းထားတဲ့ data ကို ဖျက်လိုက်ပါ
            if target_user_id in USER_PHONE_NUMBERS:
                 del USER_PHONE_NUMBERS[target_user_id]

    # Case 2: Admin က OTP Code ကို Reply ပြန်ခြင်း
    elif "OTP Code တောင်းခံမှု အသစ်" in reply_text:

        otp_code = update.message.text.strip()

        # User ဆီသို့ OTP code ပို့ခြင်း
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"🔑 **OTP Code ရရှိပါပြီ။**\n"
                     f"OTP Code: <code>{escape_html(otp_code)}</code>\n\n"
                     f"ကျေးဇူးတင်ပါသည်။",
                parse_mode='HTML'
            )
            await update.message.reply_text(f"✅ **အောင်မြင်သည်။** User ID {target_user_id} ဆီသို့ OTP code ပေးပို့ပြီးပါပြီ။ လုပ်ငန်းစဉ် ပြီးဆုံးပါပြီ။", parse_mode='Markdown')

            # Temporary data ကို ဖယ်ရှားခြင်း
            if target_user_id in USER_PHONE_NUMBERS:
                del USER_PHONE_NUMBERS[target_user_id]

        except TelegramError as e:
            error_message = (f"❌ **ပေးပို့ရန် မအောင်မြင်ပါ။** User ID <code>{target_user_id}</code> ဆီသို့ OTP ပို့ရန် မအောင်မြင်ပါ။\n"
                             f"အကြောင်းရင်း: <b>{escape_html(e.message)}</b>")
            await update.message.reply_text(error_message, parse_mode='HTML')

    else:
        # အခြား Reply များကို လျစ်လျူရှုပါ။
        pass


async def bot_functionality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/check command ကို အသုံးပြု၍ Welcome Message ကို ပြန်လည်တောင်းဆိုသောအခါ အသုံးပြုသည်။"""
    user_id = update.effective_user.id
    # 1. Database မှ user ၏ status ကို စစ်ဆေးပါ (Database logic လိုအပ်)
    status = 'approved'

    if status == 'approved':
        keyboard = [
            [
                InlineKeyboardButton("📞 Get Phone Number", callback_data=f"{REQUEST_PHONE_PREFIX}{user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🎉 **Welcome Myanmar SIM OTP Bot!**\n"
            "ဖုန်းနံပါတ် အသစ်ရယူရန် အောက်ပါ Button ကို နှိပ်ပါ။",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("Payment Failed။ Sim otp ရယူရန် fee-500mmk ကို ဦးစွာပေးသွင်းပါ။")

# =========================================================
# [Main Function]
# =========================================================

def main():
    application = Application.builder().token("7992993496:AAGLZVKjT2yFY7nf6xMWw58NJF_ZNgmigW0").build()

    # Commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("check", bot_functionality))

    # Admin Reply Handler (Phone/OTP) - Reply Message များကို ဖမ်းယူရန်
    application.add_handler(MessageHandler(filters.TEXT & filters.REPLY, handle_admin_reply))

    # Payment Proof - စာသား နှင့် ဓာတ်ပုံ များကို ဖမ်းယူရန်
    # filters.REPLY ကို ပယ်ထုတ်ထားသောကြောင့် Reply မဟုတ်သော Text သို့မဟုတ် Photo များသာ ဤ Handler သို့ ရောက်ရှိမည်။
    application.add_handler(MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND & ~filters.REPLY, handle_payment_proof))

    # Payment Approval Callback
    application.add_handler(CallbackQueryHandler(handle_approval_callback, pattern=f"^{APPROVE_PREFIX}|{REJECT_PREFIX}"))

    # Phone/OTP Callbacks
    application.add_handler(CallbackQueryHandler(request_phone_number, pattern=f"^{REQUEST_PHONE_PREFIX}"))
    application.add_handler(CallbackQueryHandler(request_otp_code, pattern=f"^{SEND_OTP_PREFIX}"))


    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
