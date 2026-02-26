import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters

TG_TOKEN = "8653920456:AAE6o_uU2Y6GWUqix7JcLw6Be9ggVuXg1XI"
HF_TOKEN = "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"
MODEL_URL = "https://api-inference.huggingface.co/models/moriarty-bot/moriarty-lora"

SYSTEM_PROMPT = "Ты — Профессор Джеймс Мориарти. Отвечай в его стиле: умно, саркастично, с чувством превосходства."

def ask_moriarty(user_message):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    prompt = f"<|system|>\n{SYSTEM_PROMPT}\n<|user|>\n{user_message}\n<|assistant|>\n"
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 256,
            "temperature": 0.8,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
            "do_sample": True,
        }
    }
    response = requests.post(MODEL_URL, headers=headers, json=payload, timeout=120)
    result = response.json()

    if isinstance(result, list):
        text = result[0].get("generated_text", "")
        # Берём только ответ после <|assistant|>
        if "<|assistant|>" in text:
            return text.split("<|assistant|>")[-1].strip()
        return text.strip()
    elif isinstance(result, dict) and "error" in result:
        if "loading" in result["error"].lower():
            return "Модель загружается... Подождите 20 секунд и попробуйте снова."
        return f"Ошибка: {result['error']}"
    return "Что-то пошло не так."

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
