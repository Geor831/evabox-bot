import time
import requests
import re
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

VK_TOKEN = "vk1.a.gB_E6NmXBEv0nRT58o_22HRpW5hhLvc7TC22VbE1M8KBZPgW7beJfO-DmSqnCNGIdVvQu17WHPKa5teVbQq3z93d-pneW6XkAmMdpNowUViS0P0enWa16qKXfA4HRRCvG74_OriEOAF6mtQeddpjDzDoooIAGWBxu84c-1Aj7wE9sGoOrOdVSS5NvnDSjfc0-QunLDoQdSsSgDFQxkIWgg"
MANAGER_VK_ID = 29279564
AI_ROUTER_API_KEY = "air_n-rDGlwEFZHLQ57G6q1rOW0OSP4MRDW--O5JFeQHHNc"

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
    {"name": "Ведро пластиковое пищевое 20 л с крышкой", "desc": "Б/У, из-под сиропа, идеальное состояние, без сколов, трещин и запаха. Толстый пластик (1 кг), герметичная крышка, пищевой пластик.", "price": 150.0}
]

# Жёсткие ответы про вёдра (без AI)
def get_bucket_answer(question):
    q = question.lower().replace("ё", "е")
    if "откуда" in q and "ведр" in q:
        return "Вёдра Б/У, из-под сиропа, в идеальном состоянии. Без сколов, трещин и запаха."
    if "состояни" in q and "ведр" in q:
        return "Вёдра Б/У, но в идеальном состоянии — без дефектов, без запаха, пищевой пластик. Отличный вариант для хранения."
    if "нов" in q and "ведр" in q:
        return "Вёдра не новые, они Б/У (из-под сиропа). Но состояние отличное, без сколов и трещин. Цена — 150 ₽."
    if "б/у" in q and "ведр" in q:
        return "Да, вёдра Б/У, из-под сиропа. Состояние идеальное, герметичная крышка, пищевой пластик, толстые стенки."
    if "объявл" in q and "ведр" in q:
        return "В объявлении указано Б/У. Вёдра из-под сиропа, в идеальном состоянии. Цена 150 ₽ за штуку."
    return None

SYSTEM_PROMPT = (
    "Ты — консультант EVA.store.\n"
    "Товары:\n"
    "- Коробки: НОВЫЕ, гофрокартон T23, упаковка 10 шт.\n"
    "- Вёдра 20 л: Б/У, из-под сиропа, идеальное состояние, 150 ₽.\n\n"
    "ВАЖНО: Вёдра — НЕ НОВЫЕ. Всегда подчёркивай это.\n"
    "Отвечай кратко и дружелюбно."
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
        "model": "deepseek/deepseek-chat",
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
    msg_lower = user_msg.lower().replace("ё", "е")

    # Жёсткий перехват — отвечаем сами, без AI
    bucket_answer = get_bucket_answer(msg_lower)
    if bucket_answer:
        return bucket_answer, history

    # AI Router для остальных вопросов
    is_purchase = any(w in msg_lower for w in ["покупаю", "заказываю", "беру", "оформляю"])
    answer, new_history = ask_airouter(user_msg, history)

    if is_purchase:
        product_found = "неизвестный товар"
        for p in PRODUCTS:
            if p["name"].lower() in msg_lower or any(str(dim) in msg_lower for dim in p["name"].split("×")):
                product_found = p["name"]
                break
        try:
            vk = VkApi(token=VK_TOKEN).get_api()
            vk.messages.send(
                user_id=MANAGER_VK_ID,
                message=f"🛒 ЗАЯВКА!\nТовар: {product_found}\nСообщение: {user_msg}",
                random_id=0
            )
        except Exception as e:
            print(f"❌ Ошибка уведомления: {e}")

    return answer, new_history

def main():
    while True:
        try:
            print("🔄 Подключаюсь к VK...")
            vk_session = VkApi(token=VK_TOKEN)
            longpoll = VkLongPoll(vk_session, wait=25)
            print("✅ Бот запущен (AI Router + жёсткие правила)")

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
                        VkApi(token=VK_TOKEN).get_api().messages.send(
                            user_id=uid, message=ans, random_id=0
                        )
                    except Exception as e:
                        print(f"❌ Ошибка: {e}")
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            time.sleep(15)

if __name__ == "__main__":
    main()
