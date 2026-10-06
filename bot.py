import time
import requests
import re
import json
import os
from datetime import datetime
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

# ===== НАСТРОЙКИ =====
VK_TOKEN = "vk1.a.SRkkuK9sN4N_GpwlKjdldoXI_xuqnKFJVS0KaUmxNfegvqc9Z5VxzYGT7vQrlji-zxZY-Nlr4FjQSzaWQzSuF48vGNkRekd9_Dll7HQJ5wQo9XmnT9f8RtFcCMPJ8P2pjfE7dlamNDuIqi6kwSdjHj3xeF00RoM522y8EbMDDMyoyiNUqa-5AmCuRuWgDwYyIVi5XggWWO7ogN_-C1B-AQ"
MANAGER_IDS = [29279564]
AITUNNEL_API_KEY = "sk-aitunnel-RQFsYV5hGsb1pHXjZdqhxp1RGLLhdi49"

CDEK_CLIENT_ID = "xa9kg2n25HvBQeRSLAbZ51NoGEX4k7xX"
CDEK_CLIENT_SECRET = "pfV81gBVIGK3WBSOzg6ybUQNGggp2Zp8"
SENDER_CITY_CODE = 1177
SENDER_CITY_NAME = "владимир"
SENDER_ADDRESS = "ул. Юбилейная, 58"
SENDER_PHONE = "+79056161515"

HISTORY_FILE = "dialogs.json"
# ===============================================

# ===== ТОВАРЫ =====
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
    {"name": "Ведро пластиковое пищевое 20 л с крышкой", "desc": "Б/У, из-под сиропа, идеальное состояние, без сколов, трещин и запаха. Толстый пластик (1 кг), герметичная крышка, пищевой пластик.", "price": 200.0, "weight": 1100, "length": 35, "width": 35, "height": 40},
    {"name": "Набор эфирных масел PARLAB, 5 шт", "desc": "100% эфирные масла (чайное дерево, апельсин, мята, лаванда, иланг-иланг). Подарочная упаковка, 50 мл, Россия.", "price": 696.0, "weight": 400, "length": 20, "width": 15, "height": 5},
    {"name": "Прокладки для собак PitoMir, 30 шт", "desc": "Впитывающие гипоаллергенные прокладки для собак и кошек. 30 шт.", "price": 432.0, "weight": 600, "length": 30, "width": 20, "height": 10},
    {"name": "Садовая дорожка модульная GUSEV GARDEN, 27 шт", "desc": "Модульное покрытие 2.43 м². Прочный пластик, устойчивый к погоде.", "price": 2676.0, "weight": 5700, "length": 32, "width": 31, "height": 26},
    {"name": "Садовая дорожка модульная GUSEV GARDEN, 9 шт", "desc": "Модульное покрытие 0.81 м². Компактный вариант.", "price": 1177.0, "weight": 2000, "length": 32, "width": 32, "height": 9},
    {"name": "Скобы садовые с фиксаторами GUSEV GARDEN, 100 шт", "desc": "Оцинкованная сталь + пластиковые фиксаторы, 100 шт.", "price": 670.0, "weight": 1820, "length": 23, "width": 18, "height": 10},
    {"name": "Заборчик садовый раздвижной декоративный GUSEV GARDEN", "desc": "WPC, высота 40 см, длина 90 см, колышки в комплекте.", "price": 923.0, "weight": 400, "length": 45, "width": 23, "height": 3},
    {"name": "Печь походная отопительная для палатки и бани", "desc": "Сталь Aisi 439, с дымоходом и каменкой, для палаток и бань.", "price": 18000.0, "weight": 23000, "length": 67, "width": 30, "height": 45},
]

PRODUCTS_LIST = "\n".join([f"- {p['name']}: {p['price']} ₽, вес ~{p['weight']}г" for p in PRODUCTS])

SYSTEM_PROMPT = (
    "Ты — продавец-консультант интернет-магазина EVA.store.\n"
    "Ты ведёшь полноценный диалог, помнишь историю и понимаешь свободную речь.\n"
    "Твоя цель — убедить клиента купить товар. Не сравнивай нас с конкурентами.\n\n"
    "АССОРТИМЕНТ:\n"
    f"{PRODUCTS_LIST}\n\n"
    "ТЕХНИКИ УБЕЖДЕНИЯ:\n"
    "- Выявляй потребность: 'Для чего вам нужен товар?'\n"
    "- Говори о выгоде: 'не треснет на морозе', 'прослужит годы'.\n"
    "- Приводи примеры: 'Наши клиенты берут эти вёдра для засолки.'\n"
    "- Работай с возражениями: 'Дорого? Посчитаем: 40 ₽ в год.'\n"
    "- Закрывай сделку: 'Оформляем?', 'Сколько штук?'\n"
    "- Во Владимире доставка бесплатная.\n"
    "- Всегда проси телефон для оформления.\n"
    "- Отвечай кратко, дружелюбно, с эмодзи."
)

CITY_CODES = {
    "москва": 44, "владимир": 1177, "санкт-петербург": 2, "питер": 2,
    "новосибирск": 137, "екатеринбург": 270, "самара": 435,
    "казань": 43, "нижний новгород": 38, "краснодар": 26,
    "ростов-на-дону": 13, "уфа": 122, "пермь": 124,
    "воронеж": 10, "волгоград": 9,
}

TARIFF_NAMES = {
    136: "Посылка склад-склад",
    137: "Посылка склад-дверь",
    138: "Экономичная посылка склад-дверь",
    139: "Экономичная посылка склад-склад",
    140: "Посылка склад-постамат",
    141: "Экономичная посылка склад-постамат",
}

# ===== СОХРАНЕНИЕ ИСТОРИИ =====
def save_dialogs(dialogs):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(dialogs, f, ensure_ascii=False, indent=2)
    except:
        pass

def load_dialogs():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

# ===== СДЭК =====
def get_cdek_token():
    try:
        response = requests.post(
            "https://api.cdek.ru/v2/oauth/token",
            params={"grant_type": "client_credentials", "client_id": CDEK_CLIENT_ID, "client_secret": CDEK_CLIENT_SECRET},
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
    if SENDER_CITY_NAME in city_name.lower():
        return {"price": 0, "days_min": 0, "days_max": 0, "tariff_name": "Самовывоз (Владимир)"}

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

    best_price = None
    best_days = None
    best_tariff = None

    for tariff in [136, 137, 138]:
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
                    info = data["tariff_codes"][0]
                    price = info.get("total_sum", 0)
                    if price > 0 and (best_price is None or price < best_price):
                        best_price = price
                        best_days = {"min": info.get("period_min", 2), "max": info.get("period_max", 4)}
                        best_tariff = tariff
        except:
            continue

    if best_price is not None:
        return {
            "price": best_price,
            "days_min": best_days["min"],
            "days_max": best_days["max"],
            "tariff_code": best_tariff,
            "tariff_name": TARIFF_NAMES.get(best_tariff, f"Тариф {best_tariff}")
        }
    else:
        return {"error": "Не удалось рассчитать доставку"}

def create_cdek_order(city_name, product, phone, client_name, quantity=1):
    if SENDER_CITY_NAME in city_name.lower():
        return {"success": True, "track_number": "Самовывоз (Владимир)"}

    city_code = get_city_code(city_name)
    if not city_code:
        return {"error": "Не удалось определить город"}

    token = get_cdek_token()
    if not token:
        return {"error": "Не удалось получить токен СДЭК"}

    total_weight = product["weight"] * quantity
    package = {"weight": total_weight}
    if "length" in product and "width" in product and "height" in product:
        package["length"] = product["length"]
        package["width"] = product["width"]
        package["height"] = product["height"]

    order_data = {
        "type": 1, "number": f"EVA-{int(time.time())}", "tariff_code": 136,
        "comment": f"Заказ от {client_name}, товар: {product['name']}",
        "sender": {"name": "EVA.store", "phone": SENDER_PHONE, "address": SENDER_ADDRESS},
        "recipient": {
            "name": client_name, "phone": phone,
            "address": {"city_code": city_code, "street": "ул. Центральная", "house": "1"}
        },
        "packages": [package]
    }

    try:
        response = requests.post(
            "https://api.cdek.ru/v2/orders",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=order_data, timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            if "entity" in data and "uuid" in data["entity"]:
                return {"success": True, "track_number": data["entity"].get("track_number", "будет позже")}
            return {"error": f"Ошибка: {data.get('errors', '')}"}
        return {"error": f"Ошибка СДЭК: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# ===== ИИ =====
def ask_aitunnel(user_msg, history=None):
    if history is None:
        history = [{"role": "system", "content": SYSTEM_PROMPT}]
    history.append({"role": "user", "content": user_msg})
    url = "https://api.aitunnel.ru/v1/chat/completions"
    headers = {"Authorization": f"Bearer {AITUNNEL_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "deepseek-chat", "messages": history, "temperature": 0.7, "max_tokens": 600}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            history.append({"role": "assistant", "content": answer})
            return answer, history
        return "❌ Ошибка AITunnel.", history
    except:
        return "❌ Ошибка.", history

# ===== ОСНОВНОЙ ЦИКЛ =====
def main():
    print("🔄 Подключаюсь к VK...")
    while True:
        try:
            vk_session = VkApi(token=VK_TOKEN)
            longpoll = VkLongPoll(vk_session, wait=200)
            vk = vk_session.get_api()
            print("✅ Бот запущен")

            dialogs = load_dialogs()
            order_data = {}

            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    uid = event.user_id
                    text = event.text.strip()
                    if not text:
                        continue

                    # === ИГНОРИРУЕМ МЕНЕДЖЕРОВ ===
                    if uid in MANAGER_IDS:
                        continue

                    try:
                        user_info = vk.users.get(user_id=uid)
                        user_name = user_info[0]['first_name']
                    except:
                        user_name = "Клиент"

                    if str(uid) not in dialogs:
                        dialogs[str(uid)] = [{"role": "system", "content": SYSTEM_PROMPT}]

                    # === ОБРАБОТКА ЗАКАЗА ===
                    buy_keywords = ["купить", "заказать", "беру", "покупаю", "хочу", "оформить", "прикупить", "взять", "надо", "нужно"]
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
                                    delivery_text = (
                                        f"Доставка: {delivery['price']} ₽ "
                                        f"({delivery.get('tariff_name', 'тариф СДЭК')}, "
                                        f"{delivery['days_min']}-{delivery['days_max']} дн.)"
                                    )

                            order_result = create_cdek_order(city_found, product, phone, user_name, 1)
                            order_msg = f"✅ Заказ создан! Трек: {order_result['track_number']}" if "error" not in order_result else f"⚠️ {order_result['error']}"

                            answer = (
                                f"📦 {product['name']} — {product['price']} ₽\n"
                                f"🚚 {delivery_text}\n"
                                f"💰 Итого: {total} ₽\n\n"
                                f"{order_msg}\n"
                                f"Менеджер свяжется с вами. Спасибо! 😊"
                            )
                            vk.messages.send(user_id=uid, message=answer, random_id=0)
                            dialogs[str(uid)].append({"role": "assistant", "content": answer})

                            dims = f"{product.get('length', '?')}×{product.get('width', '?')}×{product.get('height', '?')} см"
                            total_weight = product["weight"]
                            for manager_id in MANAGER_IDS:
                                try:
                                    vk.messages.send(
                                        user_id=manager_id,
                                        message=(
                                            f"🛒 ДЕТАЛЬНАЯ ЗАЯВКА\n"
                                            f"━━━━━━━━━━━━━━━━━━━━\n"
                                            f"👤 Клиент: {user_name}\n"
                                            f"📞 Телефон: {phone}\n"
                                            f"📍 Город: {city_found}\n"
                                            f"━━━━━━━━━━━━━━━━━━━━\n"
                                            f"📦 ТОВАР: {product['name']}\n"
                                            f"  • 1 шт., {total_weight} г, {dims}\n"
                                            f"🚚 Доставка: {delivery.get('price', '?')} ₽ ({delivery.get('tariff_name', '?')})\n"
                                            f"💰 Итого: {total} ₽\n"
                                            f"📦 Сдать в ПВЗ: 1 шт., {dims}, {total_weight} г\n"
                                            f"{order_msg}"
                                        ),
                                        random_id=0
                                    )
                                except:
                                    pass

                            save_dialogs(dialogs)
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
                                    delivery_text = (
                                        f"Доставка: {delivery['price']} ₽ "
                                        f"({delivery.get('tariff_name', 'тариф СДЭК')}, "
                                        f"{delivery['days_min']}-{delivery['days_max']} дн.)"
                                    )

                            answer = (
                                f"📦 {product['name']} — {product['price']} ₽\n"
                                f"🚚 {delivery_text}\n"
                                f"💰 Итого: {total} ₽\n\n"
                                f"Для оформления заказа нужен ваш номер телефона."
                            )
                            vk.messages.send(user_id=uid, message=answer, random_id=0)
                            dialogs[str(uid)].append({"role": "assistant", "content": answer})
                            order_data[uid] = {
                                "city": city_found,
                                "product": product,
                                "delivery_price": delivery.get("price"),
                                "total": total
                            }
                            save_dialogs(dialogs)
                            continue

                        elif not city_found:
                            answer = "Для расчёта доставки скажите, из какого вы города?"
                            vk.messages.send(user_id=uid, message=answer, random_id=0)
                            dialogs[str(uid)].append({"role": "assistant", "content": answer})
                            save_dialogs(dialogs)
                            continue

                    # === ВВОД ТЕЛЕФОНА ===
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
                                delivery = calculate_delivery(city, product)
                                order_result = create_cdek_order(city, product, phone, user_name, 1)
                                order_msg = f"✅ Заказ создан! Трек: {order_result['track_number']}" if "error" not in order_result else f"⚠️ {order_result['error']}"

                                answer = (
                                    f"📦 {product['name']} — {product['price']} ₽\n"
                                    f"🚚 Доставка: {delivery_price} ₽ ({delivery.get('tariff_name', 'тариф СДЭК')})\n"
                                    f"💰 Итого: {total} ₽\n\n"
                                    f"{order_msg}\n"
                                    f"Менеджер свяжется с вами. Спасибо! 😊"
                                )
                                vk.messages.send(user_id=uid, message=answer, random_id=0)
                                dialogs[str(uid)].append({"role": "assistant", "content": answer})

                                dims = f"{product.get('length', '?')}×{product.get('width', '?')}×{product.get('height', '?')} см"
                                total_weight = product["weight"]
                                for manager_id in MANAGER_IDS:
                                    try:
                                        vk.messages.send(
                                            user_id=manager_id,
                                            message=(
                                                f"🛒 ДЕТАЛЬНАЯ ЗАЯВКА\n"
                                                f"━━━━━━━━━━━━━━━━━━━━\n"
                                                f"👤 Клиент: {user_name}\n"
                                                f"📞 Телефон: {phone}\n"
                                                f"📍 Город: {city}\n"
                                                f"━━━━━━━━━━━━━━━━━━━━\n"
                                                f"📦 ТОВАР: {product['name']}\n"
                                                f"  • 1 шт., {total_weight} г, {dims}\n"
                                                f"🚚 Доставка: {delivery_price} ₽ ({delivery.get('tariff_name', '?')})\n"
                                                f"💰 Итого: {total} ₽\n"
                                                f"📦 Сдать в ПВЗ: 1 шт., {dims}, {total_weight} г\n"
                                                f"{order_msg}"
                                            ),
                                            random_id=0
                                        )
                                    except:
                                        pass

                                del order_data[uid]
                                save_dialogs(dialogs)
                                continue

                    # === ОБЫЧНЫЙ ДИАЛОГ ===
                    answer, new_history = ask_aitunnel(text, dialogs[str(uid)])
                    dialogs[str(uid)] = new_history
                    vk.messages.send(user_id=uid, message=answer, random_id=0)
                    save_dialogs(dialogs)

        except Exception as e:
            print(f"⚠️ Ошибка: {e}. Перезапуск через 10 секунд...")
            time.sleep(10)

if __name__ == "__main__":
    main()
