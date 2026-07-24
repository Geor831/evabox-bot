import time
import requests
import re
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

# ===== НАСТРОЙКИ =====
VK_TOKEN = "vk1.a.gB_E6NmXBEv0nRT58o_22HRpW5hhLvc7TC22VbE1M8KBZPgW7beJfO-DmSqnCNGIdVvQu17WHPKa5teVbQq3z93d-pneW6XkAmMdpNowUViS0P0enWa16qKXfA4HRRCvG74_OriEOAF6mtQeddpjDzDoooIAGWBxu84c-1Aj7wE9sGoOrOdVSS5NvnDSjfc0-QunLDoQdSsSgDFQxkIWgg"
MANAGER_VK_ID = 29279564
AI_ROUTER_API_KEY = "air_n-rDGlwEFZHLQ57G6q1rOW0OSP4MRDW--O5JFeQHHNc"
# ===============================================

PRODUCTS = [
    {"name": "Короба 600×400×400", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 70.0},
    {"name": "Короба 600×400×200", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 68.0},
    {"name": "Короба 200×300×300", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 60.0},
    {"name": "Короба 95×95×103", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 22.0},
    {"name": "Короба 50×50×225", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 16.0},
    {"name": "Короба 100×100×290", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 12.09},
    {"name": "Короба 1040×165×45", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 29.04},
    {"name": "Короба 110×110×335", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 20.3},
    {"name": "Короба 165×105×55", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 11.08},
    {"name": "Короба 170×170×80", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 9.96},
    {"name": "Короба 220×130×130*", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 9.99},
    {"name": "Короба 220×130×180", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 11.47},
    {"name": "Короба 240×135×50", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 16.98},
    {"name": "Короба 280×150×350", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 23.41},
    {"name": "Короба 300×200×300", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 23.55},
    {"name": "Короба 380×240×290", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 33.0},
    {"name": "Короба 590×195×120", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 57.72},
    {"name": "Короба 785×235×215", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 42.87},
    {"name": "Ведро пластиковое пищевое 20 л с крышкой", "desc": "Б/у, из-под сиропа, отличное состояние, толстый пластик, герметичная крышка, пищевой пластик", "price": 150.0}
]

SYSTEM_PROMPT = (
    "Ты — консультант интернет-магазина по продаже гофрокоробов и пластиковых вёдер. "
    "Все коробки новые, из трёхслойного гофрокартона T23, самосборные, упаковка по 10 штук. "
    "Цена указана за штуку. "
    "Вёдра пластиковые пищевые 20 л с крышкой — б/у, из-под сиропа, в идеальном состоянии (без сколов, трещин и запаха). "
    "Пластик толстый (вес 1 кг), не трескается на морозе. Герметичная крышка, удобная ручка. "
    "Цена: 150 ₽ за штуку. "
    "Если клиент спрашивает 'откуда' — объясни происхождение (вёдра из-под сиропа, коробки новые). "
    "Отвечай кратко, по делу, дружелюбно. "
    "Если клиент пишет 'покупаю', 'заказываю', 'беру' — скажи, что заявка передана менеджеру."
)

def ask_airouter(user_msg, history=None):
    if history is None:
        history = [{"role": "system", "content": SYSTEM_PROMPT}]
    history.append({"role": "user", "content": user_msg})

    endpoints = [
        "https://api.airouter.host/v1/chat/completions",
        "https://api.airouter.ru/v1/chat/completions"
    ]
    headers = {
        "Authorization": f"Bearer {AI_ROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",  # или "deepseek/deepseek-chat" — уточни в документации
        "messages": history,
        "temperature": 0.7,
        "max_tokens": 1000
    }

    for url in endpoints:
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                answer = response.json()["choices"][0]["message"]["content"]
                history.append({"role": "assistant", "content": answer})
                return answer, history
        except Exception as e:
            print(f"⚠️ Ошибка на {url}: {e}")
            continue

    return "Извините, произошла ошибка. Попробуйте позже.", history

def run_agent(user_msg, history=None):
    msg_lower = user_msg.lower()
    is_purchase = any(w in msg_lower for w in ["покупаю", "заказываю", "беру", "оформляю"])

    answer, new_history = ask_airouter(user_msg, history)

    if is_purchase:
        product_found = "неизвестный товар"
        for p in PRODUCTS:
            if p["name"].lower() in msg_lower or any(str(dim) in msg_lower for dim in p["name"].split("×")):
                product_found = p["name"]
                break

        try:
            vk_session = VkApi(token=VK_TOKEN)
            vk = vk_session.get_api()
            vk.messages.send(
                user_id=MANAGER_VK_ID,
                message=f"🛒 НОВАЯ ЗАЯВКА!\nТовар: {product_found}\nСообщение клиента: {user_msg}",
                random_id=0
            )
            print(f"📩 Уведомление отправлено менеджеру (ID {MANAGER_VK_ID})")
        except Exception as e:
            print(f"❌ Не удалось отправить уведомление: {e}")

    return answer, new_history

def main():
    while True:
        try:
            print("🔄 Подключаюсь к VK...")
            vk_session = VkApi(token=VK_TOKEN)
            longpoll = VkLongPoll(vk_session, wait=25)
            vk = vk_session.get_api()
            print("✅ Бот запущен (AI Router + DeepSeek, жду сообщений...)")

            dialogs = {}
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    uid = event.user_id
                    text = event.text.strip()
                    if not text:
                        continue
                    if uid not in dialogs:
                        dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                    try:
                        ans, new_hist = run_agent(text, dialogs[uid])
                        dialogs[uid] = new_hist
                        vk.messages.send(user_id=uid, message=ans, random_id=0)
                    except Exception as e:
                        print(f"❌ Ошибка при обработке: {e}")
                        try:
                            vk.messages.send(user_id=uid, message="Ошибка, попробуйте позже.", random_id=0)
                        except:
                            pass
        except (ConnectionError, requests.exceptions.ConnectionError) as e:
            print(f"⚠️ Потеря соединения с VK: {e}")
            print("🔄 Переподключение через 10 секунд...")
            time.sleep(10)
        except KeyboardInterrupt:
            print("👋 Бот остановлен пользователем.")
            break
        except Exception as e:
            print(f"❌ Неизвестная ошибка: {e}")
            print("🔄 Перезапуск через 15 секунд...")
            time.sleep(15)

if __name__ == "__main__":
    main()
