import time
import re
import os
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from openai import OpenAI

# ===== НАСТРОЙКИ =====
VK_TOKEN = "vk1.a.gB_E6NmXBEv0nRT58o_22HRpW5hhLvc7TC22VbE1M8KBZPgW7beJfO-DmSqnCNGIdVvQu17WHPKa5teVbQq3z93d-pneW6XkAmMdpNowUViS0P0enWa16qKXfA4HRRCvG74_OriEOAF6mtQeddpjDzDoooIAGWBxu84c-1Aj7wE9sGoOrOdVSS5NvnDSjfc0-QunLDoQdSsSgDFQxkIWgg"
MANAGER_VK_ID = 29279564
CLOUD_API_KEY = "NGFjYmFiNjItZDUwNi00MzJkLTg1YzItOGZkZTRjNjhkZGQ3.b58402e737860e9931736d464b783c41"
# ===============================================

# Инициализация клиента Cloud.ru (OpenAI-совместимый)
client = OpenAI(
    api_key=CLOUD_API_KEY,
    base_url="https://foundation-models.api.cloud.ru/v1"
)

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

# Формируем системный промпт со списком товаров
PRODUCTS_TEXT = "\n".join([f"- {p['name']}: {p['price']:.2f} ₽, {p['desc']}" for p in PRODUCTS])

SYSTEM_PROMPT = (
    "Ты — консультант интернет-магазина EVA.store.\n"
    "У нас есть следующие товары:\n"
    f"{PRODUCTS_TEXT}\n"
    "Если клиент спрашивает о цене, наличии или характеристиках — отвечай, используя информацию из этого списка.\n"
    "Если клиент пишет 'покупаю', 'заказываю', 'беру' — скажи, что заявка передана менеджеру.\n"
    "Отвечай кратко, дружелюбно, по делу."
)

# ===== ЖЁСТКИЕ ПРАВИЛА (без AI) =====
def get_bucket_answer(question):
    q = question.lower().replace("ё", "е")
    if any(word in q for word in ["откуда", "состояни", "нов", "б/у", "объявл"]) and "ведр" in q:
        return "Вёдра Б/У, из-под сиропа, в идеальном состоянии. Без сколов, трещин и запаха. Пищевой пластик, герметичная крышка. Цена 150 ₽ за штуку."
    if any(word in q for word in ["где использовать", "для чего", "применение", "использовать", "можно использовать"]) and "ведр" in q:
        return "Вёдра подходят для хранения сыпучих продуктов, воды, жидкостей, для заготовок (соления, варенья), а также для технических нужд."
    if "сколько" in q and "ведр" in q:
        return "Цена: 150 ₽ за штуку."
    if "размер" in q and "ведр" in q:
        return "Объём ведра — 20 литров, крышка в комплекте."
    return None

# ===== УЛУЧШЕННЫЙ ПОИСК ПО ТОВАРАМ (fallback) =====
def normalize(text):
    text = text.lower().strip()
    text = re.sub(r'[xх*]', '×', text)
    text = text.replace(' ', '')
    return text

def extract_numbers(text):
    return list(map(int, re.findall(r'\d+', text)))

def search_products(query):
    q = normalize(query)
    results = []
    for p in PRODUCTS:
        if q in normalize(p["name"]) or q in normalize(p["desc"]):
            results.append(p)
    if not results:
        numbers = extract_numbers(query)
        if len(numbers) >= 3:
            for p in PRODUCTS:
                if all(str(n) in p["name"] for n in numbers[:3]):
                    results.append(p)
                    break
    return results

def fallback_answer(query):
    results = search_products(query)
    if results:
        p = results[0]
        return f"{p['name']} — {p['desc']}\nЦена: {p['price']:.2f} ₽"
    return "🤔 Не нашёл таких товаров. Попробуйте уточнить размер (например, 600×400×400) или напишите «вёдра»."

# ===== ВЫЗОВ CLOUD.RU ЧЕРЕЗ OPENAI SDK =====
def ask_cloud(user_msg, history=None):
    if history is None:
        history = [{"role": "system", "content": SYSTEM_PROMPT}]
    history.append({"role": "user", "content": user_msg})

    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V4-Flash",
            messages=history,
            temperature=0.7,
            max_tokens=1000,
            timeout=10  # таймаут в секундах
        )
        answer = response.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        return answer, history
    except Exception as e:
        error_msg = str(e)
        # Если ошибка содержит код статуса, покажем её
        if "401" in error_msg:
            return "❌ Ошибка Cloud.ru: неверный ключ API.", history
        elif "402" in error_msg or "Payment Required" in error_msg:
            return "❌ Ошибка Cloud.ru: недостаточно средств на балансе.", history
        elif "404" in error_msg:
            return "❌ Ошибка Cloud.ru: модель не найдена. Проверьте название модели.", history
        elif "timeout" in error_msg.lower():
            return "⏱️ Превышено время ожидания ответа от Cloud.ru. Попробуйте позже.", history
        else:
            return f"❌ Ошибка Cloud.ru: {error_msg[:200]}", history

# ===== ОСНОВНОЙ ОБРАБОТЧИК =====
def run_agent(user_msg, history=None):
    msg_lower = user_msg.lower().replace("ё", "е")

    # Жёсткие правила
    bucket_ans = get_bucket_answer(msg_lower)
    if bucket_ans:
        return bucket_ans, history

    if msg_lower in ["привет", "здравствуйте", "добрый день", "доброе утро"]:
        return "Здравствуйте! Я бот-консультант. Напишите, что вас интересует: коробки (укажите размер) или вёдра.", history

    if "откуда" in msg_lower and "коробк" in msg_lower:
        return "Коробки новые, из трёхслойного гофрокартона T23, самосборные, упаковка по 10 штук.", history

    # Проверка на покупку
    is_purchase = any(w in msg_lower for w in ["покупаю", "заказываю", "беру", "оформляю"])
    if is_purchase:
        product_found = "неизвестный товар"
        for p in PRODUCTS:
            if p["name"].lower() in msg_lower:
                product_found = p["name"]
                break
        try:
            vk = VkApi(token=VK_TOKEN).get_api()
            vk.messages.send(
                user_id=MANAGER_VK_ID,
                message=f"🛒 ЗАЯВКА!\nТовар: {product_found}\nСообщение: {user_msg}",
                random_id=0
            )
        except:
            pass

    # Вызов Cloud.ru через OpenAI SDK
    ai_answer, new_history = ask_cloud(user_msg, history)
    # Если ответ начинается с "❌" или "⏱️" — это ошибка, показываем пользователю
    if ai_answer.startswith("❌") or ai_answer.startswith("⏱️"):
        return ai_answer, new_history
    # Если ответ получен — возвращаем его
    if ai_answer is not None and ai_answer.strip():
        return ai_answer, new_history

    # Если Cloud.ru не ответил — fallback
    return fallback_answer(user_msg), history

def main():
    while True:
        try:
            print("🔄 Подключаюсь к VK...")
            vk_session = VkApi(token=VK_TOKEN)
            longpoll = VkLongPoll(vk_session, wait=25)
            print("✅ Бот запущен (Cloud.ru OpenAI SDK + fallback)")

            dialogs = {}
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    uid = event.user_id
                    text = event.text.strip()
                    if not text:
                        continue
                    if uid not in dialogs:
                        dialogs[uid] = []
                    try:
                        ans, new_hist = run_agent(text, dialogs[uid])
                        dialogs[uid] = new_hist
                        VkApi(token=VK_TOKEN).get_api().messages.send(
                            user_id=uid, message=ans, random_id=0
                        )
                    except Exception as e:
                        print(f"❌ Ошибка при обработке: {e}")
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            time.sleep(15)

if __name__ == "__main__":
    main()
