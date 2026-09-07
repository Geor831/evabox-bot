import time
import requests
import re
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

# ===== НАСТРОЙКИ =====
VK_TOKEN = "vk1.a.gB_E6NmXBEv0nRT58o_22HRpW5hhLvc7TC22VbE1M8KBZPgW7beJfO-DmSqnCNGIdVvQu17WHPKa5teVbQq3z93d-pneW6XkAmMdpNowUViS0P0enWa16qKXfA4HRRCvG74_OriEOAF6mtQeddpjDzDoooIAGWBxu84c-1Aj7wE9sGoOrOdVSS5NvnDSjfc0-QunLDoQdSsSgDFQxkIWgg"
MANAGER_IDS = [29279564, 598512076]
AITUNNEL_API_KEY = "sk-aitunnel-EJz97YJpiOwnaObmGNjf6mU8cT2OdP8L"

# ===== НАСТРОЙКИ СДЭК =====
CDEK_CLIENT_ID = "xa9kg2n25HvBQeRSLAbZ51NoGEX4k7xX"
CDEK_CLIENT_SECRET = "pfV81gBVIGK3WBSOzg6ybUQNGggp2Zp8"
SENDER_CITY_CODE = 1177  # Владимир
SENDER_ADDRESS = "ул. Юбилейная, 58"
# ===============================================

PRODUCTS = [
    {"name": "Короба 600×400×400", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 70.0, "weight": 500, "length": 60, "width": 40, "height": 40},
    {"name": "Короба 600×400×200", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 68.0, "weight": 400, "length": 60, "width": 40, "height": 20},
    {"name": "Короба 200×300×300", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 60.0, "weight": 400, "length": 20, "width": 30, "height": 30},
    {"name": "Короба 95×95×103", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 22.0, "weight": 200, "length": 9.5, "width": 9.5, "height": 10.3},
    {"name": "Короба 50×50×225", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 16.0, "weight": 200, "length": 5, "width": 5, "height": 22.5},
    {"name": "Короба 100×100×290", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 12.09, "weight": 200, "length": 10, "width": 10, "height": 29},
    {"name": "Короба 1040×165×45", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 29.04, "weight": 600, "length": 104, "width": 16.5, "height": 4.5},
    {"name": "Короба 110×110×335", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 20.3, "weight": 300, "length": 11, "width": 11, "height": 33.5},
    {"name": "Короба 165×105×55", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 11.08, "weight": 200, "length": 16.5, "width": 10.5, "height": 5.5},
    {"name": "Короба 170×170×80", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 9.96, "weight": 200, "length": 17, "width": 17, "height": 8},
    {"name": "Короба 220×130×130*", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 9.99, "weight": 200, "length": 22, "width": 13, "height": 13},
    {"name": "Короба 220×130×180", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 11.47, "weight": 200, "length": 22, "width": 13, "height": 18},
    {"name": "Короба 240×135×50", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 16.98, "weight": 300, "length": 24, "width": 13.5, "height": 5},
    {"name": "Короба 280×150×350", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 23.41, "weight": 400, "length": 28, "width": 15, "height": 35},
    {"name": "Короба 300×200×300", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 23.55, "weight": 400, "length": 30, "width": 20, "height": 30},
    {"name": "Короба 380×240×290", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 33.0, "weight": 500, "length": 38, "width": 24, "height": 29},
    {"name": "Короба 590×195×120", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 57.72, "weight": 500, "length": 59, "width": 19.5, "height": 12},
    {"name": "Короба 785×235×215", "desc": "Новые, трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 42.87, "weight": 600, "length": 78.5, "width": 23.5, "height": 21.5},
    {"name": "Ведро пластиковое пищевое 20 л с крышкой", "desc": "Б/У, из-под сиропа, идеальное состояние, без сколов, трещин и запаха. Толстый пластик (1 кг), герметичная крышка, пищевой пластик.", "price": 300.0, "weight": 1100, "length": 35, "width": 35, "height": 40},
]

SYSTEM_PROMPT = (
    "Ты — продавец-консультант интернет-магазина EVA.store.\n"
    "Ты помогаешь клиентам с выбором и оформлением заказов.\n\n"
    "У нас есть следующие товары (всегда используй эти названия и цены):\n"
    + "\n".join([f"- {p['name']}: {p['price']} ₽, вес ~{p['weight']}г" for p in PRODUCTS]) +
    "\n\nАЛГОРИТМ РАБОТЫ:\n"
    "- Если клиент хочет купить — узнай его город, количество и товар.\n"
    "- Затем рассчитай стоимость товара и доставки.\n"
    "- Спроси номер телефона для оформления заказа.\n"
    "- Когда клиент дал телефон — сообщи, что заявка передана менеджеру.\n"
    "- Отвечай кратко, дружелюбно."
)

CITY_CODES = {
    "москва": 44,
    "владимир": 1177,
    "санкт-петербург": 2,
    "питер": 2,
    "новосибирск": 137,
    "екатеринбург": 270,
}

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
    except:
        return None

def get_city_code(city_name):
    city_lower = city_name.lower().strip()
    for name, code in CITY_CODES.items():
        if name in city_lower:
            return code
    return None

def calculate_delivery(city_name, product):
    # Для Владимира — самовывоз, 0 ₽
    if "владимир" in city_name.lower():
        return {"price": 0, "days_min": 0, "days_max": 0}

    city_code = get_city_code(city_name)
    if not city_code:
        return {"error": "Не удалось определить город"}

    token = get_cdek_token()
    if not token:
        return {"error": "Не удалось получить токен СДЭК"}

    package = {"weight": product.get("weight", 500)}
    if "length" in product and "width" in product and "height" in product:
        package["length"] = product["length"]
        package["width"] = product["width"]
        package["height"] = product["height"]

    tariffs = [136, 137, 138]
    best_price = None
    best_days = None

    for tariff in tariffs:
        try:
            response = requests.post(
                "https://api.cdek.ru/v2/calculator/tariff",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={
                    "from_location": {"code": SENDER_CITY_CODE},
                    "to_location": {"code": city_code},
                    "packages": [package],
                    "tariff_codes": [tariff]
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if "tariff_codes" in data and len(data["tariff_codes"]) > 0:
                    tariff_info = data["tariff_codes"][0]
                    price = tariff_info.get("total_sum", 0)
                    if price > 0 and (best_price is None or price < best_price):
                        best_price = price
                        best_days = {
                            "min": tariff_info.get("period_min", 2),
                            "max": tariff_info.get("period_max", 4)
                        }
        except:
            continue

    if best_price is not None:
        return {"price": best_price, "days_min": best_days["min"], "days_max": best_days["max"]}
    else:
        return {"error": "Не удалось рассчитать доставку"}

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
        "temperature": 0.7,
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
    except:
        return "❌ Ошибка. Попробуйте позже.", history

def main():
    print("🔄 Подключаюсь к VK...")
    vk_session = VkApi(token=VK_TOKEN)
    longpoll = VkLongPoll(vk_session, wait=90)
    vk = vk_session.get_api()
    print("✅ Бот запущен (с доставкой 0 для Владимира)")

    dialogs = {}
    order_data = {}

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            uid = event.user_id
            text = event.text.strip()
            if not text:
                continue

            try:
                user_info = vk.users.get(user_id=uid)
                user_name = user_info[0]['first_name']
            except:
                user_name = "Клиент"

            if uid not in dialogs:
                dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]

            buy_keywords = ["купить", "заказать", "беру", "покупаю", "хочу"]
            if any(w in text.lower() for w in buy_keywords):
                product = None
                for p in PRODUCTS:
                    if p["name"].lower() in text.lower():
                        product = p
                        break
                if not product:
                    product = PRODUCTS[-1]

                city_found = None
                for city in CITY_CODES.keys():
                    if city in text.lower():
                        city_found = city
                        break

                phone_match = re.search(r'\+?\d[\d\s\-\(\)]{7,}\d', text)

                if city_found and phone_match:
                    phone = phone_match.group().strip()
                    delivery = calculate_delivery(city_found, product)
                    if "error" in delivery:
                        delivery_text = f"❌ {delivery['error']}"
                        total = None
                    else:
                        total = product["price"] + delivery["price"]
                        if delivery["price"] == 0:
                            delivery_text = "Самовывоз (0 ₽)"
                        else:
                            delivery_text = f"Доставка: {delivery['price']} ₽"

                    answer = (
                        f"📦 {product['name']} — {product['price']} ₽\n"
                        f"🚚 {delivery_text}\n"
                        f"💰 Итого: {total} ₽\n\n"
                        f"✅ Заявка оформлена! Менеджер свяжется с вами по указанному телефону.\n"
                        f"Спасибо за покупку! 😊"
                    )
                    vk.messages.send(user_id=uid, message=answer, random_id=0)
                    dialogs[uid].append({"role": "assistant", "content": answer})

                    for manager_id in MANAGER_IDS:
                        try:
                            vk.messages.send(
                                user_id=manager_id,
                                message=(
                                    f"🛒 ЗАЯВКА от {user_name}!\n"
                                    f"Товар: {product['name']}\n"
                                    f"Город: {city_found}\n"
                                    f"Телефон: {phone}\n"
                                    f"Доставка: {delivery.get('price', 'не рассчитана')} ₽\n"
                                    f"Итого: {total} ₽"
                                ),
                                random_id=0
                            )
                        except:
                            pass
                    continue

                elif city_found and not phone_match:
                    delivery = calculate_delivery(city_found, product)
                    if "error" in delivery:
                        delivery_text = f"❌ {delivery['error']}"
                        total = None
                    else:
                        total = product["price"] + delivery["price"]
                        if delivery["price"] == 0:
                            delivery_text = "Самовывоз (0 ₽)"
                        else:
                            delivery_text = f"Доставка: {delivery['price']} ₽"

                    answer = (
                        f"📦 {product['name']} — {product['price']} ₽\n"
                        f"🚚 {delivery_text}\n"
                        f"💰 Итого: {total} ₽\n\n"
                        f"Для оформления заказа нужен ваш номер телефона."
                    )
                    vk.messages.send(user_id=uid, message=answer, random_id=0)
                    dialogs[uid].append({"role": "assistant", "content": answer})
                    if uid not in order_data:
                        order_data[uid] = {}
                    order_data[uid]["city"] = city_found
                    order_data[uid]["product"] = product
                    order_data[uid]["delivery_price"] = delivery.get("price")
                    order_data[uid]["total"] = total
                    continue

                elif not city_found:
                    answer = "Для расчёта доставки скажите, из какого вы города?"
                    vk.messages.send(user_id=uid, message=answer, random_id=0)
                    dialogs[uid].append({"role": "assistant", "content": answer})
                    continue

            if uid in order_data and not order_data[uid].get("phone"):
                phone_match = re.search(r'\+?\d[\d\s\-\(\)]{7,}\d', text)
                if phone_match:
                    phone = phone_match.group().strip()
                    order_data[uid]["phone"] = phone
                    city = order_data[uid].get("city")
                    product = order_data[uid].get("product")
                    delivery_price = order_data[uid].get("delivery_price")
                    total = order_data[uid].get("total")

                    if city and product:
                        answer = (
                            f"📦 {product['name']} — {product['price']} ₽\n"
                            f"🚚 Доставка: {delivery_price} ₽\n"
                            f"💰 Итого: {total} ₽\n\n"
                            f"✅ Заявка оформлена! Менеджер свяжется с вами по указанному телефону.\n"
                            f"Спасибо за покупку! 😊"
                        )
                        vk.messages.send(user_id=uid, message=answer, random_id=0)
                        dialogs[uid].append({"role": "assistant", "content": answer})

                        for manager_id in MANAGER_IDS:
                            try:
                                vk.messages.send(
                                    user_id=manager_id,
                                    message=(
                                        f"🛒 ЗАЯВКА от {user_name}!\n"
                                        f"Товар: {product['name']}\n"
                                        f"Город: {city}\n"
                                        f"Телефон: {phone}\n"
                                        f"Доставка: {delivery_price} ₽\n"
                                        f"Итого: {total} ₽"
                                    ),
                                    random_id=0
                                )
                            except:
                                pass
                        del order_data[uid]
                        continue

            if uid not in dialogs:
                dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]

            answer, new_history = ask_aitunnel(text, dialogs[uid])
            dialogs[uid] = new_history
            vk.messages.send(user_id=uid, message=answer, random_id=0)

if __name__ == "__main__":
    main()
