import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters

TG_TOKEN = "8653920456:AAE6o_uU2Y6GWUqix7JcLw6Be9ggVuXg1XI"
HF_TOKEN = "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"
MODEL_URL = "https://router.huggingface.co/hf-inference/models/moriarty-bot/moriarty-lora/v1/chat/completions"

SYSTEM_PROMPT = "Ты — Профессор Джеймс Мориарти. Отвечай в его стиле: умно, саркастично, с чувством превосходства."

def ask_moriarty(user_message):
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "moriarty-bot/moriarty-lora",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 256,
        "temperature": 0.8,
    }
    try:
        response = requests.post(MODEL_URL, headers=headers, json=payload, timeout=120)
        result = response.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"].strip()
        elif "error" in result:
            return f"Ошибка: {result['error']}"
        return "Что-то пошло не так."
    except Exception as e:
        return f"Ошибка соединения: {str(e)}"

async def start(update: Update, context):
    await update.message.reply_text(
        "Привет? Какое банальное начало. Я — Джеймс Мориарти. Чего вы хотите?"
    )

async def handle_message(update: Update, context):
    user_text = update.message.text
    await update.message.chat.send_action("typing")
    reply = ask_moriarty(user_text)
    await update.message.reply_text(reply)

app = ApplicationBuilder().token(TG_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
print("Бот запущен!")
app.run_polling()
