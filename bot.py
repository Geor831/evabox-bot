import time
import requests
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

# ===== НАСТРОЙКИ =====
VK_TOKEN = "vk1.a.gB_E6NmXBEv0nRT58o_22HRpW5hhLvc7TC22VbE1M8KBZPgW7beJfO-DmSqnCNGIdVvQu17WHPKa5teVbQq3z93d-pneW6XkAmMdpNowUViS0P0enWa16qKXfA4HRRCvG74_OriEOAF6mtQeddpjDzDoooIAGWBxu84c-1Aj7wE9sGoOrOdVSS5NvnDSjfc0-QunLDoQdSsSgDFQxkIWgg"
MANAGER_VK_ID = 29279564
AITUNNEL_API_KEY = "sk-aitunnel-EJz97YJpiOwnaObmGNjf6mU8cT2OdP8L"
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
    {"name": "Ведро пластиковое пищевое 20 л с крышкой", "desc": "Б/У, из-под сиропа, идеальное состояние, без сколов, трещин и запаха. Толстый пластик (1 кг), герметичная крышка, пищевой пластик.", "price": 300.0}
]

PRODUCTS_LIST = "\n".join([f"- {p['name']}: {p['price']:.2f} ₽, {p['desc']}" for p in PRODUCTS])

SYSTEM_PROMPT = (
    "Ты — профессиональный продавец-консультант интернет-магазина EVA.store.\n"
    "Твоя цель — продавать и строить доверие с клиентом.\n"
    "Ты работаешь в ВК и общаешься с покупателями.\n\n"
    "ТОВАРЫ (с точными ценами):\n"
    f"{PRODUCTS_LIST}\n\n"
    "ТЫ ОБЯЗАН ИСПОЛЬЗОВАТЬ ЭТИ ТЕХНИКИ ПРОДАЖ:\n"
    "- Установление контакта\n"
    "- Выявление потребностей (SPIN)\n"
    "- Презентация по ХПВ\n"
    "- Работа с возражениями (AIDA)\n"
    "- Апселл и кросс-селл\n"
    "- Якорение цены\n"
    "- Социальное доказательство\n"
    "- Сторителлинг\n"
    "- Создание дефицита\n"
    "- Накрытие стола\n"
    "- Бесплатная консультация\n"
    "- Follow-up после заказа\n"
    "- Привязка к датам\n"
    "- Закрытие сделки\n"
    "- Сбор контакта\n"
    "- Распознавание эмоций\n"
    "- Стимул за отзыв (скидка 10% на следующую покупку)\n\n"
    "ОБЩИЕ ПРАВИЛА:\n"
    "- Отвечай кратко, по делу, дружелюбно.\n"
    "- Помни историю диалога.\n"
    "- Используй эмодзи для тёплого тона (😊, 👍, 📦).\n"
    "- Если клиент пишет 'покупаю' — передай заявку менеджеру."
)

def ask_aitunnel(user_msg, history=None):
    if history is None:
        history = [{"role": "system", "content": SYSTEM_PROMPT}]
    history.append({"role": "user", "content": user_msg})

    url = "https://api.aitunnel.ru/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AITUNNEL_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": history,
        "temperature": 0.8,
        "max_tokens": 600
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            history.append({"role": "assistant", "content": answer})
            return answer, history
        else:
            return "❌ Ошибка AITunnel. Попробуйте позже.", history
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:100]}", history

def main():
    print("🔄 Подключаюсь к VK...")
    vk_session = VkApi(token=VK_TOKEN)
    longpoll = VkLongPoll(vk_session, wait=25)
    print("✅ Бот запущен (с автоопределением менеджера)")

    dialogs = {}
    last_message_from_manager = {}  # {user_id: time}

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            uid = event.user_id
            text = event.text.strip()
            if not text:
                continue

            # ===== ЕСЛИ ПИШЕТ МЕНЕДЖЕР =====
            if uid == MANAGER_VK_ID:
                for user_id in dialogs.keys():
                    last_message_from_manager[user_id] = time.time()
                continue

            # ===== КЛИЕНТ ПИШЕТ =====
            manager_recent = last_message_from_manager.get(uid, 0)
            time_since_manager = time.time() - manager_recent

            if time_since_manager < 7200:  # 2 часа
                print(f"⏸️ Бот молчит (менеджер в диалоге) для {uid}")
                continue

            try:
                user_info = vk_session.get_api().users.get(user_id=uid)
                user_name = user_info[0]['first_name']
            except:
                user_name = "Клиент"

            if any(w in text.lower() for w in ["покупаю", "заказываю", "беру", "оформляю"]):
                try:
                    vk = VkApi(token=VK_TOKEN).get_api()
                    vk.messages.send(
                        user_id=MANAGER_VK_ID,
                        message=f"🛒 ЗАЯВКА от {user_name}!\nСообщение: {text}",
                        random_id=0
                    )
                except:
                    pass

            if uid not in dialogs:
                dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]

            answer, new_history = ask_aitunnel(text, dialogs[uid])
            dialogs[uid] = new_history

            vk_session.get_api().messages.send(
                user_id=uid, message=answer, random_id=0
            )

if __name__ == "__main__":
    main()
