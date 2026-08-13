import time
import requests
import re
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

# ===== НАСТРОЙКИ =====
VK_TOKEN = "vk1.a.vedeEaKBa4UKyV0RYddcBqMts_JJrvNynhr8OPClZfx2l6JQVzrFM2v9fXIm74J0RWykxVmwIMxbrwVuZxnoDYkUh4FE9EVxz4d3btZ51dyjV4nUzHJ9Gph5juclIZaWRfq03hBfqW6L3Our9W_1PwJsp5udn-_nOTM2XV79CO16MWqPwmfKEON4dp3oPnVdz9bBIhEzRIjmlAEFLfDeNQ"
MANAGER_IDS = [29279564, 598512076]
AITUNNEL_API_KEY = "sk-aitunnel-EJz97YJpiOwnaObmGNjf6mU8cT2OdP8L"

# ===== НАСТРОЙКИ СДЭК =====
CDEK_CLIENT_ID = "1lewXxGlFX3De0d3L6rPbjhzYPfrYvJK"
CDEK_CLIENT_SECRET = "pEpIoya912voraWeRAV2PdH18TrI1Fty"
SENDER_CITY_CODE = 1177  # Владимир
# ===============================================

PRODUCTS = [
    {"name": "Короба 600×400×400", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 70.0, "weight": 500},
    {"name": "Короба 600×400×200", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 68.0, "weight": 400},
    {"name": "Короба 200×300×300", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 60.0, "weight": 400},
    {"name": "Короба 95×95×103", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 22.0, "weight": 200},
    {"name": "Короба 50×50×225", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 16.0, "weight": 200},
    {"name": "Короба 100×100×290", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 12.09, "weight": 200},
    {"name": "Короба 1040×165×45", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 29.04, "weight": 600},
    {"name": "Короба 110×110×335", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 20.3, "weight": 300},
    {"name": "Короба 165×105×55", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 11.08, "weight": 200},
    {"name": "Короба 170×170×80", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 9.96, "weight": 200},
    {"name": "Короба 220×130×130*", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 9.99, "weight": 200},
    {"name": "Короба 220×130×180", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 11.47, "weight": 200},
    {"name": "Короба 240×135×50", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 16.98, "weight": 300},
    {"name": "Короба 280×150×350", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 23.41, "weight": 400},
    {"name": "Короба 300×200×300", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 23.55, "weight": 400},
    {"name": "Короба 380×240×290", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 33.0, "weight": 500},
    {"name": "Короба 590×195×120", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 57.72, "weight": 500},
    {"name": "Короба 785×235×215", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 42.87, "weight": 600},
    {"name": "Ведро пластиковое пищевое 20 л с крышкой", "desc": "Б/У, из-под сиропа, идеальное состояние, без сколов, трещин и запаха. Толстый пластик (1 кг), герметичная крышка, пищевой пластик.", "price": 300.0, "weight": 1100},
    {"name": "Набор эфирных масел PARLAB, 5 шт", "desc": "100% эфирные масла (чайное дерево, апельсин, мята, лаванда, иланг-иланг). Подарочная упаковка, 50 мл, Россия.", "price": 696.0, "weight": 400},
    {"name": "Прокладки для собак PitoMir, 30 шт", "desc": "Впитывающие гипоаллергенные прокладки для собак и кошек. Дышащие, на липком слое, суперабсорбент. 30 шт.", "price": 432.0, "weight": 600},
    {"name": "Садовая дорожка модульная GUSEV GARDEN, 27 шт", "desc": "Модульное пластиковое покрытие для садовых дорожек, террас, балконов, детских площадок. Прочный, устойчивый к погоде, легко укладывается. Площадь 2.43 м², Россия.", "price": 2676.0, "weight": 5700},
    {"name": "Садовая дорожка модульная GUSEV GARDEN, 9 шт", "desc": "Модульное пластиковое покрытие для садовых дорожек, террас, балконов, детских площадок. Прочный, устойчивый к погоде, легко укладывается. Площадь 0.81 м², Россия.", "price": 1177.0, "weight": 2000},
    {"name": "Скобы садовые с фиксаторами GUSEV GARDEN, 100 шт", "desc": "Садовые скобы из оцинкованной стали с фиксаторами для крепления агроткани, геотекстиля, спанбонда. Надёжное крепление, долговечные. 100 шт. Россия.", "price": 670.0, "weight": 1820},
    {"name": "Заборчик садовый раздвижной декоративный GUSEV GARDEN", "desc": "Раздвижной садовый заборчик для клумб, грядок и ограждения растений. Материал WPC (древесно-пластиковый композит), высота 40 см, длина 90 см, колышки в комплекте. Устойчив к погоде, долговечный. Россия.", "price": 923.0, "weight": 400},
    {"name": "Печь походная отопительная для палатки и бани", "desc": "Дровяная печь для палаток, бань, походов. Сталь Aisi 439, компактная, с дымоходом, каменкой, быстросъёмными ножками. Вес 23 кг, Россия.", "price": 18000.0, "weight": 23000}
]

CITY_CODES = {
    "москва": 44,
    "владимир": 1177,
    "санкт-петербург": 2,
    "питер": 2,
    "новосибирск": 137,
    "екатеринбург": 270,
}

PRODUCTS_LIST = "\n".join([f"- {p['name']}: {p['price']:.2f} ₽, вес ~{p['weight']}г, {p['desc']}" for p in PRODUCTS])

def get_cdek_token():
    try:
        response = requests.post(
            "https://api.cdek.ru/v2/oauth/token",
            params={
                "grant_type": "client_credentials",
                "client_id": CDEK_CLIENT_ID,
                "client_secret": CDEK_CLIENT_SECRET
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        return None
    except Exception as e:
        print(f"⚠️ Ошибка получения токена СДЭК: {e}")
        return None

def get_city_code(city_name: str) -> int:
    city_lower = city_name.lower().strip()
    for name, code in CITY_CODES.items():
        if name in city_lower:
            return code
    token = get_cdek_token()
    if not token:
        return None
    try:
        response = requests.get(
            "https://api.cdek.ru/v2/city",
            params={"q": city_lower},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        if response.status_code == 200:
            cities = response.json()
            if cities and len(cities) > 0:
                return cities[0]["code"]
    except Exception as e:
        print(f"⚠️ Ошибка поиска города: {e}")
    return None

def calculate_delivery(city_name: str, weight_grams: int) -> dict:
    city_code = get_city_code(city_name)
    if not city_code:
        return {"error": "Не удалось определить город"}
    token = get_cdek_token()
    if not token:
        return {"error": "Не удалось получить токен СДЭК"}
    try:
        response = requests.post(
            "https://api.cdek.ru/v2/calculator/tariff",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "from_location": {"code": SENDER_CITY_CODE},
                "to_location": {"code": city_code},
                "packages": [{"weight": weight_grams}],
                "tariff_codes": [136]
            },
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            if "tariff_codes" in data and len(data["tariff_codes"]) > 0:
                tariff = data["tariff_codes"][0]
                return {
                    "price": tariff.get("total_sum", 0),
                    "days_min": tariff.get("period_min", 1),
                    "days_max": tariff.get("period_max", 3)
                }
        return {"error": f"Ошибка СДЭК: {response.status_code} {response.text[:200]}"}
    except Exception as e:
        return {"error": str(e)}

def extract_city(text: str) -> str:
    text_lower = text.lower()
    for city in CITY_CODES.keys():
        if city in text_lower:
            return city
    return None

def extract_phone(text: str) -> str:
    phone = re.search(r'\+?\d[\d\s\-\(\)]{7,}\d', text)
    if phone:
        return phone.group().strip()
    return None

def ask_aitunnel(user_msg, history=None):
    if history is None:
        history = [{"role": "system", "content": "Ты — продавец-консультант EVA.store. Отвечай кратко, дружелюбно, используй техники продаж."}]
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
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            history.append({"role": "assistant", "content": answer})
            return answer, history
        else:
            return "❌ Ошибка AITunnel. Попробуйте позже.", history
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:100]}", history

SYSTEM_PROMPT = (
    "Ты — продавец-консультант интернет-магазина EVA.store.\n"
    "Ты помогаешь клиентам с выбором и оформлением заказов.\n\n"
    "ТОВАРЫ (с ценами и весом в граммах):\n"
    f"{PRODUCTS_LIST}\n\n"
    "АЛГОРИТМ РАБОТЫ (ты должен его соблюдать):\n"
    "1. Если клиент хочет купить — узнай его город.\n"
    "2. Когда клиент назвал город — рассчитай доставку и покажи итог (товар + доставка).\n"
    "3. После расчёта спроси номер телефона.\n"
    "4. Когда клиент дал телефон — сообщи, что заявка передана менеджеру.\n"
    "5. Если клиент спрашивает про доставку в любой момент — пересчитай и покажи сумму.\n"
    "Никогда не передавай заявку без расчёта доставки и без телефона.\n\n"
    "Используй техники продаж: выявляй потребности, работай с возражениями, предлагай доп. товары.\n"
    "Отвечай кратко, дружелюбно, с эмодзи."
)

def main():
    print("🔄 Подключаюсь к VK...")
    vk_session = VkApi(token=VK_TOKEN)
    longpoll = VkLongPoll(vk_session, wait=90)
    vk = vk_session.get_api()
    print("✅ Бот запущен (финальная версия)")

    dialogs = {}
    order_data = {}
    disabled_users = set()

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            uid = event.user_id
            text = event.text.strip()
            if not text:
                continue

            # ===== УПРАВЛЕНИЕ ЧЕРЕЗ ФРАЗЫ МЕНЕДЖЕРА (отключено) =====
            # Пока отключаем, чтобы не мешало тестированию

            # ===== ЕСЛИ КЛИЕНТ В ОТКЛЮЧЁННЫХ =====
            if uid in disabled_users:
                print(f"⏸️ Бот отключён для {uid}")
                continue

            # ===== ПОЛУЧАЕМ ИМЯ КЛИЕНТА =====
            try:
                user_info = vk.users.get(user_id=uid)
                user_name = user_info[0]['first_name']
            except:
                user_name = "Клиент"

            # ===== ЗАПРОС НА ДОСТАВКУ (с промежуточным ответом) =====
            city_found = extract_city(text)
            delivery_keywords = ["доставк", "привезти", "сдэк", "курьер", "отправк", "транспортн", "сколько", "цена"]
            is_delivery_question = any(w in text.lower() for w in delivery_keywords)

            if city_found and is_delivery_question:
                vk.messages.send(user_id=uid, message="⏳ Сейчас посчитаю стоимость доставки от Владимира до вашего города...", random_id=0)
                product = None
                if uid in order_data and order_data[uid].get("product"):
                    product = order_data[uid]["product"]
                else:
                    if uid in dialogs:
                        for msg in reversed(dialogs[uid]):
                            if msg["role"] == "user":
                                for p in PRODUCTS:
                                    if p["name"].lower() in msg["content"].lower() or any(w in msg["content"].lower() for w in ["ведр", "короб"]):
                                        product = p
                                        break
                                if product:
                                    break
                    if not product:
                        product = PRODUCTS[-1]
                result = calculate_delivery(city_found, product["weight"])
                if "error" in result:
                    answer = f"❌ Не удалось рассчитать доставку: {result['error']}"
                else:
                    total = product["price"] + result["price"]
                    if uid not in order_data:
                        order_data[uid] = {}
                    order_data[uid]["city"] = city_found
                    order_data[uid]["product"] = product
                    order_data[uid]["delivery_price"] = result["price"]
                    order_data[uid]["total"] = total
                    order_data[uid]["delivery_days"] = f"{result['days_min']}-{result['days_max']}"
                    order_data[uid]["phone"] = None
                    answer = (
                        f"✅ Доставка от Владимира до {city_found.capitalize()}:\n"
                        f"📦 Товар: {product['name']} — {product['price']:.2f} ₽\n"
                        f"🚚 Доставка: {result['price']:.2f} ₽ ({result['days_min']}-{result['days_max']} дн.)\n"
                        f"💰 Итого: {total:.2f} ₽\n\n"
                        f"Для оформления заказа нужен ваш номер телефона. Напишите его, пожалуйста."
                    )
                vk.messages.send(user_id=uid, message=answer, random_id=0)
                if uid not in dialogs:
                    dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                dialogs[uid].append({"role": "assistant", "content": answer})
                continue

            # ===== ОБЫЧНЫЙ ЗАКАЗ =====
            if uid not in order_data or not order_data[uid].get("city"):
                buy_keywords = ["купить", "заказать", "беру", "покупаю", "оформить", "заказ", "приобрести", "хочу", "нужны", "интересует"]
                if any(w in text.lower() for w in buy_keywords) or any(p["name"].lower() in text.lower() for p in PRODUCTS):
                    if uid not in order_data:
                        order_data[uid] = {"city": None, "phone": None, "product": None, "delivery_price": 0, "total": 0, "delivery_days": ""}
                    product = None
                    for p in PRODUCTS:
                        if p["name"].lower() in text.lower() or any(w in text.lower() for w in ["ведр", "короб"]):
                            product = p
                            break
                    if not product:
                        product = PRODUCTS[-1]
                    order_data[uid]["product"] = product
                    answer = "Отлично! Для расчёта доставки скажите, из какого вы города?"
                    vk.messages.send(user_id=uid, message=answer, random_id=0)
                    if uid not in dialogs:
                        dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                    dialogs[uid].append({"role": "assistant", "content": answer})
                    continue

            if uid in order_data and not order_data[uid].get("city"):
                city_found = extract_city(text)
                if city_found:
                    order_data[uid]["city"] = city_found
                    product = order_data[uid]["product"]
                    vk.messages.send(user_id=uid, message="⏳ Сейчас посчитаю доставку...", random_id=0)
                    result = calculate_delivery(city_found, product["weight"])
                    if "error" in result:
                        answer = f"❌ Не удалось рассчитать доставку: {result['error']}"
                    else:
                        total = product["price"] + result["price"]
                        order_data[uid]["delivery_price"] = result["price"]
                        order_data[uid]["total"] = total
                        order_data[uid]["delivery_days"] = f"{result['days_min']}-{result['days_max']}"
                        answer = (
                            f"✅ Доставка от Владимира до {city_found.capitalize()}:\n"
                            f"📦 Товар: {product['name']} — {product['price']:.2f} ₽\n"
                            f"🚚 Доставка: {result['price']:.2f} ₽ ({result['days_min']}-{result['days_max']} дн.)\n"
                            f"💰 Итого: {total:.2f} ₽\n\n"
                            f"Для оформления заказа нужен ваш номер телефона. Напишите его, пожалуйста."
                        )
                    vk.messages.send(user_id=uid, message=answer, random_id=0)
                    if uid not in dialogs:
                        dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                    dialogs[uid].append({"role": "assistant", "content": answer})
                    continue

            if uid in order_data and order_data[uid].get("city") and not order_data[uid].get("phone"):
                phone_found = extract_phone(text)
                if phone_found:
                    order_data[uid]["phone"] = phone_found
                    for manager_id in MANAGER_IDS:
                        try:
                            vk.messages.send(
                                user_id=manager_id,
                                message=(
                                    f"🛒 ЗАЯВКА от {user_name}!\n"
                                    f"Товар: {order_data[uid]['product']['name']}\n"
                                    f"Город: {order_data[uid]['city']}\n"
                                    f"Телефон: {phone_found}\n"
                                    f"Доставка: {order_data[uid].get('delivery_price', 0):.2f} ₽ ({order_data[uid].get('delivery_days', '')} дн.)\n"
                                    f"Итоговая сумма: {order_data[uid].get('total', 0):.2f} ₽"
                                ),
                                random_id=0
                            )
                        except:
                            pass
                    answer = "✅ Заявка оформлена! Менеджер свяжется с вами по указанному телефону. Спасибо за покупку! 😊"
                    vk.messages.send(user_id=uid, message=answer, random_id=0)
                    if uid not in dialogs:
                        dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                    dialogs[uid].append({"role": "assistant", "content": answer})
                    del order_data[uid]
                    continue
                else:
                    if not any(w in text.lower() for w in ["да", "нет", "ок", "хорошо"]):
                        answer = "Для оформления заказа нужен ваш номер телефона. Напишите, пожалуйста."
                        vk.messages.send(user_id=uid, message=answer, random_id=0)
                        if uid not in dialogs:
                            dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                        dialogs[uid].append({"role": "assistant", "content": answer})
                        continue

            # === ОБЫЧНЫЙ ДИАЛОГ ===
            if uid not in dialogs:
                dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]

            answer, new_history = ask_aitunnel(text, dialogs[uid])
            dialogs[uid] = new_history
            vk.messages.send(user_id=uid, message=answer, random_id=0)

if __name__ == "__main__":
    main()
