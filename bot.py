import time
import requests
import re
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from cdek import CdekClient
from cdek.apps.tariff import TariffCodeRequest

# ===== НАСТРОЙКИ =====
VK_TOKEN = "vk1.a.gB_E6NmXBEv0nRT58o_22HRpW5hhLvc7TC22VbE1M8KBZPgW7beJfO-DmSqnCNGIdVvQu17WHPKa5teVbQq3z93d-pneW6XkAmMdpNowUViS0P0enWa16qKXfA4HRRCvG74_OriEOAF6mtQeddpjDzDoooIAGWBxu84c-1Aj7wE9sGoOrOdVSS5NvnDSjfc0-QunLDoQdSsSgDFQxkIWgg"
MANAGER_VK_ID = 29279564
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
    {"name": "Ведро пластиковое пищевое 20 л с крышкой", "desc": "Б/У, из-под сиропа, идеальное состояние, без сколов, трещин и запаха. Толстый пластик (1 кг), герметичная крышка, пищевой пластик.", "price": 300.0, "weight": 800}
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

def get_city_code(city_name: str) -> int:
    city_lower = city_name.lower().strip()
    for name, code in CITY_CODES.items():
        if name in city_lower:
            return code
    try:
        client = CdekClient(CDEK_CLIENT_ID, CDEK_CLIENT_SECRET, timeout=60)
        response = client.search_cities(city_lower)
        if response and len(response) > 0:
            return response[0].code
    except Exception as e:
        print(f"⚠️ Ошибка поиска города: {e}")
    return None

def calculate_delivery(city_name: str, weight_grams: int) -> dict:
    city_code = get_city_code(city_name)
    if not city_code:
        return {"error": "Не удалось определить город"}
    try:
        client = CdekClient(CDEK_CLIENT_ID, CDEK_CLIENT_SECRET, timeout=60)
        request = TariffCodeRequest.init(tariff_code=136)
        request.set_city_codes(from_location=SENDER_CITY_CODE, to_location=city_code)
        request.set_package_weight(weight=weight_grams)
        tariff = client.tariff.calc(request)
        return {
            "price": tariff.delivery_sum,
            "days_min": tariff.period_min,
            "days_max": tariff.period_max
        }
    except Exception as e:
        print(f"⚠️ Ошибка расчёта доставки: {e}")
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
    print("✅ Бот запущен (с управлением через фразы менеджера)")

    dialogs = {}
    order_data = {}
    disabled_users = set()  # пользователи, для которых бот отключён

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            uid = event.user_id
            text = event.text.strip()
            if not text:
                continue

            # === ЕСЛИ ПИШЕТ МЕНЕДЖЕР ===
            if uid == MANAGER_VK_ID:
                # Получаем peer_id (кому адресовано сообщение)
                try:
                    msg_info = vk.messages.getById(message_ids=event.message_id)
                    if msg_info and 'items' in msg_info and len(msg_info['items']) > 0:
                        peer_id = msg_info['items'][0]['peer_id']
                    else:
                        # Если не удалось получить, пропускаем
                        print("⚠️ Не удалось определить peer_id для сообщения менеджера")
                        continue
                except Exception as e:
                    print(f"⚠️ Ошибка получения peer_id: {e}")
                    continue

                # Проверяем команды
                text_lower = text.lower()
                if "менеджер на связи" in text_lower or "я на связи" in text_lower or "на связи" in text_lower:
                    disabled_users.add(peer_id)
                    vk.messages.send(
                        user_id=MANAGER_VK_ID,
                        message=f"✅ Бот отключён для пользователя {peer_id}",
                        random_id=0
                    )
                    continue
                elif "ии агент на связи" in text_lower or "агент на связи" in text_lower:
                    disabled_users.discard(peer_id)
                    vk.messages.send(
                        user_id=MANAGER_VK_ID,
                        message=f"✅ Бот включён для пользователя {peer_id}",
                        random_id=0
                    )
                    continue
                # Если менеджер пишет что-то другое, бот пропускает (он не отвечает на сообщения менеджера)
                continue

            # === ЕСЛИ КЛИЕНТ В ОТКЛЮЧЁННЫХ ===
            if uid in disabled_users:
                print(f"⏸️ Бот отключён для {uid}")
                continue

            # Получаем имя клиента
            try:
                user_info = vk.users.get(user_id=uid)
                user_name = user_info[0]['first_name']
            except:
                user_name = "Клиент"

            # === ОБРАБОТКА ЗАПРОСА НА ДОСТАВКУ (с промежуточным ответом) ===
            city_found = extract_city(text)
            delivery_keywords = ["доставк", "привезти", "сдэк", "курьер", "отправк", "транспортн", "сколько", "цена"]
            is_delivery_question = any(w in text.lower() for w in delivery_keywords)

            if city_found and is_delivery_question:
                # 1. Отправляем промежуточный ответ
                vk.messages.send(
                    user_id=uid,
                    message="⏳ Сейчас посчитаю стоимость доставки от Владимира до вашего города...",
                    random_id=0
                )
                # 2. Определяем товар
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
                # 3. Рассчитываем доставку
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

            # === ОБЫЧНЫЙ ПРОЦЕСС ЗАКАЗА (без запроса доставки) ===
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
                    # Сразу отправим промежуточный ответ
                    vk.messages.send(
                        user_id=uid,
                        message="⏳ Сейчас посчитаю доставку...",
                        random_id=0
                    )
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
                else:
                    # Если не назван город, и это не запрос доставки, то переспрашиваем через ИИ
                    pass

            if uid in order_data and order_data[uid].get("city") and not order_data[uid].get("phone"):
                phone_found = extract_phone(text)
                if phone_found:
                    order_data[uid]["phone"] = phone_found
                    try:
                        vk.messages.send(
                            user_id=MANAGER_VK_ID,
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
                    # Если не похоже на телефон, переспрашиваем
                    if not any(w in text.lower() for w in ["да", "нет", "ок", "хорошо"]):
                        answer = "Для оформления заказа нужен ваш номер телефона. Напишите, пожалуйста."
                        vk.messages.send(user_id=uid, message=answer, random_id=0)
                        if uid not in dialogs:
                            dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                        dialogs[uid].append({"role": "assistant", "content": answer})
                        continue

            # === ОБЫЧНЫЙ ДИАЛОГ ЧЕРЕЗ ИИ ===
            if uid not in dialogs:
                dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]

            answer, new_history = ask_aitunnel(text, dialogs[uid])
            dialogs[uid] = new_history
            vk.messages.send(user_id=uid, message=answer, random_id=0)

if __name__ == "__main__":
    main()
