import json
import os
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
)
from extractor import extract
from calculator import calculate

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TRANSFERS_FILE = "transfers.json"

LABELS = {
    "amount": "💵 Amount",
    "currency": "💱 Currency",
    "sender": "👤 Sender",
    "receiver": "👥 Receiver",
    "city": "📍 City",
    "receiver_phone": "📞 Receiver phone",
}


# ---------- Helpers ----------

def get_missing(transfer):
    return [label.split(" ", 1)[1] for field, label in LABELS.items()
            if getattr(transfer, field) is None]


def format_transfer(number, transfer):
    lines = [f"✅ Transfer {number}"]
    for field, label in LABELS.items():
        value = getattr(transfer, field)
        if value is not None:
            if isinstance(value, float) and value.is_integer():
                value = f"{int(value):,}"
            lines.append(f"{label}: {value}")

    if transfer.amount is not None and transfer.currency:
        result = calculate(transfer.amount, transfer.currency)
        if result is None:
            lines.append(f"\n❌ Sorry, we don't handle {transfer.currency} yet.")
        else:
            cur = transfer.currency.upper()
            lines.append(f"\n🧾 Fee: {result['fee']:,g} {cur}")
            lines.append(f"💰 Total to pay: {result['total']:,g} {cur}")
            if cur != "AFN":
                lines.append(f"🇦🇫 In afghani: {result['total_afn']:,} AFN (rate {result['rate']:g})")
    else:
        lines.append("\n🧾 Fee will be calculated once the amount and currency are known.")

    missing = get_missing(transfer)
    if missing:
        lines.append(f"\n⚠️ Missing: {', '.join(missing)}. Please send them.")
    return "\n".join(lines)


def save_transfer(transfer, user):
    now = datetime.now()
    record = {
        "reference": f"HW-{now:%Y%m%d-%H%M%S}",
        "time": now.isoformat(timespec="seconds"),
        "telegram_user": user.full_name,
        **transfer,
    }
    records = []
    if os.path.exists(TRANSFERS_FILE):
        with open(TRANSFERS_FILE, encoding="utf-8") as f:
            records = json.load(f)
    records.append(record)
    with open(TRANSFERS_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    return record["reference"]


# ---------- Commands ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Salam! 👋 I'm your Hawala Assistant.\n"
        "Send me a transfer request, like:\n"
        "send 500 dollars to Ahmad in Kabul, sender Karim\n\n"
        "Type /cancel anytime to start over."
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled. Send a new transfer anytime.")


# ---------- Messages ----------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    previous = context.user_data.get("pending_text", "")
    full_text = f"{previous}\n{update.message.text}".strip()

    try:
        transfers = await extract(full_text)
    except Exception as e:
        print("Error:", e)
        await update.message.reply_text("Sorry, I'm having trouble right now. Please try again in a minute.")
        return

    if not transfers:
        await update.message.reply_text(
            "I couldn't find a transfer in your message. 🤔\n"
            "Try something like: send 500 dollars to Ahmad in Kabul, sender Karim"
        )
        return

    if len(transfers) > 1:
        for number, transfer in enumerate(transfers, start=1):
            await update.message.reply_text(format_transfer(number, transfer))
        await update.message.reply_text("📌 To confirm, please send one transfer at a time.")
        context.user_data.clear()
        return

    transfer = transfers[0]
    summary = format_transfer(1, transfer)

    # Still missing details: remember the conversation and wait
    if get_missing(transfer):
        context.user_data["pending_text"] = full_text
        await update.message.reply_text(summary)
        return

    # Currency we don't handle: stop here
    if calculate(transfer.amount, transfer.currency) is None:
        context.user_data.clear()
        await update.message.reply_text(summary)
        return

    # Complete: ask for confirmation
    context.user_data["pending_text"] = full_text
    context.user_data["ready"] = transfer.model_dump()
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Confirm", callback_data="confirm"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel"),
    ]])
    await update.message.reply_text(
        summary + "\n\nEverything looks complete. Confirm this transfer?",
        reply_markup=keyboard,
    )


# ---------- Buttons ----------

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm":
        transfer = context.user_data.get("ready")
        if not transfer:
            await query.edit_message_text("Nothing to confirm. Please send a new transfer.")
            return
        reference = save_transfer(transfer, query.from_user)
        context.user_data.clear()
        await query.edit_message_text(query.message.text + f"\n\n✅ Confirmed! Reference: {reference}")
    else:
        context.user_data.clear()
        await query.edit_message_text(query.message.text + "\n\n❌ Cancelled.")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_button))
    print("Bot is running... Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()