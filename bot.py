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

SYSTEM_PROMPT = (
    "Ты — профессиональный продавец-консультант интернет-магазина EVA.store.\n"
    "Твоя задача — вести естественный диалог и помочь клиенту купить товар.\n\n"
    "ТОВАРЫ (с точными ценами и весом):\n"
    f"{PRODUCTS_LIST}\n\n"
    "ЛОГИКА ПРОДАЖ:\n"
    "- Если клиент выражает желание купить (например, 'хочу купить', 'сколько стоят', 'беру', 'думаю приобрести', 'интересуют', 'нужны'), ты ДОЛЖЕН спросить город, чтобы рассчитать доставку.\n"
    "- Когда клиент называет город, ты должен запомнить его и рассчитать стоимость доставки. Для этого в ответе ты можешь написать: 'Сейчас посчитаю доставку...' и затем показать итоговую цену (товар + доставка).\n"
    "- После расчёта доставки спроси номер телефона для оформления заказа.\n"
    "- Когда клиент дал номер телефона, скажи, что заявка передана менеджеру.\n"
    "- Если клиент спрашивает про доставку ('доставка', 'привезти', 'сдэк'), а ты ещё не спросил город — спроси город.\n"
    "- Используй все техники продаж: выявляй потребности, работай с возражениями, предлагай сопутствующие товары, создавай дефицит, давай социальное доказательство, рассказывай истории.\n"
    "- Отвечай кратко, дружелюбно, используй эмодзи (😊, 👍, 📦).\n"
    "- Помни историю диалога и не теряй контекст."
)

def get_city_code(city_name: str) -> int:
    city_lower = city_name.lower().strip()
    for name, code in CITY_CODES.items():
        if name in city_lower:
            return code
    try:
        client = CdekClient(CDEK_CLIENT_ID, CDEK_CLIENT_SECRET)
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
        client = CdekClient(CDEK_CLIENT_ID, CDEK_CLIENT_SECRET)
        request = TariffCodeRequest.init(tariff_code=136)
        request.set_city_codes(from_location=SENDER_CITY_CODE, to_location=city_code)
        request.set_package_weight(weight=weight_grams)
        tariff = client.tariff.calc(request)
        return {
            "price": tariff.delivery_sum,
            "currency": tariff.currency,
            "days_min": tariff.period_min,
            "days_max": tariff.period_max
        }
    except Exception as e:
        print(f"⚠️ Ошибка расчёта доставки: {e}")
        return {"error": str(e)}

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

def has_buy_intent(text: str) -> bool:
    """Проверяет, есть ли в тексте намерение купить"""
    keywords = [
        "купить", "заказать", "беру", "покупаю", "оформить", "заказ",
        "приобрести", "хочу", "нужны", "интересует", "интересуют",
        "возьму", "возьмём", "приобрету", "заберу"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)

def main():
    print("🔄 Подключаюсь к VK...")
    vk_session = VkApi(token=VK_TOKEN)
    longpoll = VkLongPoll(vk_session, wait=25)
    print("✅ Бот запущен (с расширенными триггерами)")

    dialogs = {}
    pending_orders = {}
    last_message_from_manager = {}

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            uid = event.user_id
            text = event.text.strip()
            if not text:
                continue

            # Менеджер пишет — запоминаем
            if uid == MANAGER_VK_ID:
                for user_id in dialogs.keys():
                    last_message_from_manager[user_id] = time.time()
                continue

            # Если менеджер в диалоге — бот молчит
            manager_recent = last_message_from_manager.get(uid, 0)
            if time.time() - manager_recent < 7200:
                print(f"⏸️ Бот молчит (менеджер в диалоге) для {uid}")
                continue

            # Получаем имя клиента
            try:
                user_info = vk_session.get_api().users.get(user_id=uid)
                user_name = user_info[0]['first_name']
            except:
                user_name = "Клиент"

            # === ОБРАБОТКА ЗАКАЗА ===
            order = pending_orders.get(uid, {})
            city = order.get("city")
            phone = order.get("phone")
            product = order.get("product")

            # Если заказ не начат и есть намерение купить или упоминание товара
            if not order and (has_buy_intent(text) or any(p["name"].lower() in text.lower() for p in PRODUCTS)):
                pending_orders[uid] = {"city": None, "phone": None, "product": None}
                order = pending_orders[uid]
                # Определяем товар
                for p in PRODUCTS:
                    if p["name"].lower() in text.lower() or any(w in text.lower() for w in ["ведр", "короб"]):
                        order["product"] = p
                        break
                if not order["product"]:
                    order["product"] = PRODUCTS[-1]  # по умолчанию вёдра
                # Спрашиваем город
                answer = "Отлично! Для расчёта доставки скажите, из какого вы города?"
                vk_session.get_api().messages.send(user_id=uid, message=answer, random_id=0)
                if uid not in dialogs:
                    dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                dialogs[uid].append({"role": "assistant", "content": answer})
                continue

            # Если заказ начат, но город не указан — пытаемся извлечь или спрашиваем
            if order and not city:
                # Проверяем, есть ли город в тексте
                city_found = extract_city(text)
                if city_found:
                    order["city"] = city_found
                    # Рассчитываем доставку
                    weight = order["product"]["weight"]
                    result = calculate_delivery(city_found, weight)
                    if "error" in result:
                        answer = f"❌ Не удалось рассчитать доставку: {result['error']}"
                    else:
                        total = order["product"]["price"] + result["price"]
                        answer = (
                            f"✅ Доставка от Владимира до {city_found.capitalize()}:\n"
                            f"📦 Товар: {order['product']['name']} — {order['product']['price']:.2f} ₽\n"
                            f"🚚 Доставка: {result['price']:.2f} ₽ ({result['days_min']}-{result['days_max']} дн.)\n"
                            f"💰 Итого: {total:.2f} ₽\n\n"
                            f"Для оформления заказа нужен ваш номер телефона. Напишите его, пожалуйста."
                        )
                        order["total"] = total
                        order["delivery_price"] = result["price"]
                        order["delivery_days"] = f"{result['days_min']}-{result['days_max']}"
                    vk_session.get_api().messages.send(user_id=uid, message=answer, random_id=0)
                    if uid not in dialogs:
                        dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                    dialogs[uid].append({"role": "assistant", "content": answer})
                    continue
                else:
                    # Если город не найден, но есть вопрос про доставку — переспрашиваем
                    if "доставк" in text.lower() or "привезти" in text.lower() or "сдэк" in text.lower():
                        answer = "Для расчёта доставки мне нужен ваш город. Скажите, откуда вы?"
                    else:
                        answer = "Из какого вы города? Это нужно для расчёта доставки."
                    vk_session.get_api().messages.send(user_id=uid, message=answer, random_id=0)
                    if uid not in dialogs:
                        dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                    dialogs[uid].append({"role": "assistant", "content": answer})
                    continue

            # Если заказ начат, город есть, но нет телефона
            if order and city and not phone:
                phone_found = extract_phone(text)
                if phone_found:
                    order["phone"] = phone_found
                    # Отправляем уведомление менеджеру
                    try:
                        vk = VkApi(token=VK_TOKEN).get_api()
                        vk.messages.send(
                            user_id=MANAGER_VK_ID,
                            message=(
                                f"🛒 ЗАЯВКА от {user_name}!\n"
                                f"Товар: {order['product']['name']}\n"
                                f"Город: {city}\n"
                                f"Телефон: {phone_found}\n"
                                f"Доставка: {order.get('delivery_price', 0):.2f} ₽ ({order.get('delivery_days', '')} дн.)\n"
                                f"Итоговая сумма: {order.get('total', 0):.2f} ₽"
                            ),
                            random_id=0
                        )
                    except:
                        pass
                    answer = "✅ Заявка оформлена! Менеджер свяжется с вами по указанному телефону. Спасибо за покупку! 😊"
                    vk_session.get_api().messages.send(user_id=uid, message=answer, random_id=0)
                    if uid not in dialogs:
                        dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                    dialogs[uid].append({"role": "assistant", "content": answer})
                    del pending_orders[uid]
                    continue
                else:
                    # Если телефон не найден, переспрашиваем
                    answer = "Для оформления заказа нужен ваш номер телефона. Напишите, пожалуйста."
                    vk_session.get_api().messages.send(user_id=uid, message=answer, random_id=0)
                    if uid not in dialogs:
                        dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                    dialogs[uid].append({"role": "assistant", "content": answer})
                    continue

            # === ОБЫЧНЫЙ ДИАЛОГ ===
            if uid not in dialogs:
                dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]

            answer, new_history = ask_aitunnel(text, dialogs[uid])
            dialogs[uid] = new_history

            vk_session.get_api().messages.send(
                user_id=uid, message=answer, random_id=0
            )

if __name__ == "__main__":
    main()
