# 💸 Hawala Assistant: AI Telegram Bot

A Telegram bot that turns messy Hawala transfer requests into clean, confirmed transfers.
It understands English, Pashto, and Dari, calculates fees and totals, asks for missing
details, and saves confirmed transfers with a reference number.

## ✨ Features

- **AI extraction:** reads free-text requests like _"send 500 dollars to Ahmad in Kabul,
  sender Karim"_ and extracts amount, currency, sender, receiver, city, and phone
- **Multi-language:** works with English, Pashto, Dari, or mixed messages
- **Never guesses:** missing details are left empty and requested from the customer
- **Remembers the conversation:** customers can send missing details in follow-up messages
- **Exact calculations in code:** fee (1%, minimum 150 AFN), total, and AFN equivalent
- **Human confirmation:** Confirm / Cancel buttons before anything is saved
- **Reference numbers:** each confirmed transfer gets a unique reference
- **Multiple transfers:** detects several transfers in one message

## 🧠 How it works

1. Customer sends a message in Telegram
2. **Gemini** extracts the transfer details into a fixed schema (structured JSON output)
3. **Python code** calculates the fee and totals (AI is never used for money math)
4. If details are missing, the bot asks and merges the follow-up with the original message
5. When complete, the customer confirms, and the transfer is saved with a reference

## 🛠️ Tech stack

Python · python-telegram-bot (async) · Google Gemini API (structured output) · Pydantic

## 📁 Project structure

- `bot.py`: Telegram handlers, conversation state, buttons
- `extractor.py`: AI extraction with Gemini and a Pydantic schema
- `calculator.py`: rates, fees, and totals

## ▶️ Run locally

1. Create a bot with [@BotFather](https://t.me/BotFather) and get a token
2. Install: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your keys
4. Run: `python bot.py`

## ⚠️ Limitations

- Practice project: rates are sample values, and "confirmed" means saved to a local file
- Conversations in progress are forgotten if the bot restarts
- Not hosted 24/7 yet (runs locally)

## 🚀 Future improvements

- Live exchange rates from an API or a business system
- Database storage instead of a JSON file
- Staff dashboard to process confirmed transfers
- 24/7 deployment on a server

## 👤 Author

**Mohammad Numan Danish** · [GitHub](https://github.com/NumanDanish)
