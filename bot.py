import time
import requests
import re
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
    {"name": "Ведро пластиковое пищевое 20 л с крышкой", "desc": "Б/У, из-под сиропа, идеальное состояние, без сколов, трещин и запаха. Толстый пластик (1 кг), герметичная крышка, пищевой пластик.", "price": 150.0}
]

# ===== ЖЁСТКИЕ ПРАВИЛА (без AI) =====
def get_bucket_answer(question):
    q = question.lower().replace("ё", "е")
    if "откуда" in q and "ведр" in q:
        return "Вёдра Б/У, из-под сиропа, в идеальном состоянии."
    if "состояни" in q and "ведр" in q:
        return "Вёдра Б/У, в идеальном состоянии — без дефектов и запаха."
    if "нов" in q and "ведр" in q:
        return "Вёдра не новые, они Б/У (из-под сиропа), состояние отличное. Цена — 150 ₽."
    if "б/у" in q and "ведр" in q:
        return "Да, вёдра Б/У, из-под сиропа, состояние идеальное."
    if "сколько" in q and "ведр" in q:
        return "Цена: 150 ₽ за штуку."
    if "размер" in q and "ведр" in q:
        return "Объём ведра — 20 литров, крышка в комплекте."
    if any(word in q for word in ["где использовать", "для чего", "применение"]) and "ведр" in q:
        return "Вёдра подходят для хранения сыпучих продуктов, воды, для заготовок и технических нужд."
    return None

# ===== ПОИСК ПО ТОВАРАМ (fallback) =====
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
    return "🤔 Не нашёл таких товаров. Напишите размер (например, 600×400×400) или спросите про вёдра."

# ===== ВЫЗОВ AITUNNEL =====
def ask_aitunnel(user_msg, history=None):
    if history is None:
        history = [{"role": "system", "content": "Ты — консультант интернет-магазина EVA.store. Отвечай кратко и по делу."}]
    history.append({"role": "user", "content": user_msg})

    url = "https://api.aitunnel.ru/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AITUNNEL_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": history,
        "temperature": 0.7,
        "max_tokens": 1000
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            history.append({"role": "assistant", "content": answer})
            return answer, history
        else:
            return f"❌ Ошибка AITunnel (код {response.status_code}): {response.text[:200]}", history
    except requests.exceptions.Timeout:
        return None, history
    except Exception as e:
        return None, history

# ===== ОСНОВНОЙ ОБРАБОТЧИК =====
def run_agent(user_msg, history=None):
    msg_lower = user_msg.lower().replace("ё", "е")

    bucket_ans = get_bucket_answer(msg_lower)
    if bucket_ans:
        return bucket_ans, history

    if msg_lower in ["привет", "здравствуйте", "добрый день", "доброе утро"]:
        return "Здравствуйте! Я бот-консультант. Напишите размер коробки (например, 600×400×400) или спросите про вёдра.", history

    if "откуда" in msg_lower and "коробк" in msg_lower:
        return "Коробки новые, из трёхслойного гофрокартона T23, самосборные, упаковка по 10 штук.", history

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

    ai_answer, new_history = ask_aitunnel(user_msg, history)
    if ai_answer is not None:
        return ai_answer, new_history

    return fallback_answer(user_msg), history

def main():
    while True:
        try:
            print("🔄 Подключаюсь к VK...")
            vk_session = VkApi(token=VK_TOKEN)
            longpoll = VkLongPoll(vk_session, wait=25)
            print("✅ Бот запущен (AITunnel + fallback)")

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
