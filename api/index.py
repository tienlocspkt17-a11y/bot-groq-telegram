import os
import requests
from groq import Groq
from flask import Flask, request, jsonify

app = Flask(__name__)

# Lấy biến môi trường từ Vercel
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
BOT_USERNAME = os.environ.get("BOT_USERNAME") 

# Khởi tạo Groq Client
client = Groq(api_key=GROQ_API_KEY)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def webhook(path):
    if request.method == 'POST':
        update = request.get_json()
        if "message" in update and "text" in update["message"]:
            message = update["message"]
            chat_id = message["chat"]["id"]
            text = message["text"]
            
            # Xử lý cắt tên bot nếu ở trong Group
            if BOT_USERNAME and text.startswith(BOT_USERNAME):
                text = text.replace(BOT_USERNAME, "", 1).strip()

            if not text:
                return jsonify(status="ok")

            # 3. Gọi AI Groq chuẩn chỉnh
            try:
                chat_completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": "Bạn là một trợ lý AI thân thiện, nhiệt tình. Trả lời bằng tiếng Việt tự nhiên nhất."
                        },
                        {
                            "role": "user",
                            "content": text
                        }
                    ]
                )
                reply_text = chat_completion.choices[0].message.content
            except Exception as e:
                reply_text = "Groq đang phản hồi chậm, bạn thử lại nha."
                print(f"Lỗi Groq chi tiết: {e}")
                    model="llama-3.3-70b-versatile",
                )
                reply_text = chat_completion.choices[0].message.content
            except Exception as e:
                reply_text = "Groq đang phản hồi chậm, bạn thử lại nha."
                print(f"Lỗi Groq: {e}")

            # 4. Trả lời lại qua Telegram API
            send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": reply_text,
                "reply_to_message_id": message.get("message_id")
            }
            
            # Hỗ trợ Group Topics
            if message.get("is_topic_message") or message.get("message_thread_id"):
                payload["message_thread_id"] = message.get("message_thread_id")

            try:
                requests.post(send_url, json=payload)
            except Exception as e:
                print(f"Lỗi Telegram: {e}")

    return jsonify(status="ok")
