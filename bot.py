import time
import requests
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from cdek import CdekClient
from cdek.apps.tariff import TariffCodeRequest

# ===== НАСТРОЙКИ =====
VK_TOKEN = "vk1.a.gB_E6NmXBEv0nRT58o_22HRpW5hhLvc7TC22VbE1M8KBZPgW7beJfO-DmSqnCNGIdVvQu17WHPKa5teVbQq3z93d-pneW6XkAmMdpNowUViS0P0enWa16qKXfA4HRRCvG74_OriEOAF6mtQeddpjDzDoooIAGWBxu84c-1Aj7wE9sGoOrOdVSS5NvnDSjfc0-QunLDoQdSsSgDFQxkIWgg"
MANAGER_VK_ID = 29279564
AITUNNEL_API_KEY = "sk-aitunnel-EJz97YJpiOwnaObmGNjf6mU8cT2OdP8L"

# ===== НАСТРОЙКИ СДЭК (ваши ключи) =====
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

# Простые коды городов (можно расширять)
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
    "Твоя цель — продавать и строить доверие.\n\n"
    "ТОВАРЫ (с точными ценами и весом в граммах):\n"
    f"{PRODUCTS_LIST}\n\n"
    "ЛОГИКА ЗАКАЗА:\n"
    "1. Если клиент говорит о покупке ('хочу купить', 'оформить', 'заказ', 'покупаю'), спроси город.\n"
    "2. После получения города скажи: 'Сейчас посчитаю стоимость доставки от Владимира до вашего города...'\n"
    "3. Покажи итог: 'Товар — X ₽, доставка — Y ₽, итого — Z ₽'.\n"
    "4. Спроси номер телефона для связи: 'Для оформления заказа нужен ваш номер телефона.'\n"
    "5. После получения телефона подтверди заявку и сообщи, что менеджер свяжется.\n"
    "6. ВСЕГДА запоминай город и телефон в истории диалога.\n\n"
    "ИСПОЛЬЗУЙ ТЕХНИКИ ПРОДАЖ:\n"
    "- Установление контакта, выявление потребностей (SPIN)\n"
    "- Презентация по ХПВ, работа с возражениями (AIDA)\n"
    "- Апселл и кросс-селл, якорение цены\n"
    "- Социальное доказательство, сторителлинг\n"
    "- Follow-up, сбор контакта, распознавание эмоций\n"
    "- Стимул за отзыв (скидка 10% на следующую покупку)\n\n"
    "ОБЩИЕ ПРАВИЛА:\n"
    "- Отвечай кратко, по делу, дружелюбно.\n"
    "- Помни историю диалога.\n"
    "- Используй эмодзи (😊, 👍, 📦).\n"
    "- Если клиент пишет 'покупаю' — передай заявку менеджеру."
)

# === ФУНКЦИИ СДЭК ===
def get_city_code(city_name: str) -> int:
    """Находит код города СДЭК по названию (сначала в словаре, затем через API)"""
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
    """Рассчитывает стоимость и срок доставки через СДЭК"""
    city_code = get_city_code(city_name)
    if not city_code:
        return {"error": "Не удалось определить город"}

    try:
        client = CdekClient(CDEK_CLIENT_ID, CDEK_CLIENT_SECRET)
        request = TariffCodeRequest.init(tariff_code=136)  # 136 — склад-склад
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

# === ФУНКЦИЯ ВЫЗОВА AITUNNEL ===
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

# === ОСНОВНАЯ ЛОГИКА ===
def main():
    print("🔄 Подключаюсь к VK...")
    vk_session = VkApi(token=VK_TOKEN)
    longpoll = VkLongPoll(vk_session, wait=25)
    print("✅ Бот запущен (с доставкой СДЭК и сбором телефона)")

    dialogs = {}          # история диалога
    order_data = {}       # временное хранение данных заказа (город, телефон)
    last_message_from_manager = {}

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            uid = event.user_id
            text = event.text.strip()
            if not text:
                continue

            # === ЕСЛИ ПИШЕТ МЕНЕДЖЕР ===
            if uid == MANAGER_VK_ID:
                for user_id in dialogs.keys():
                    last_message_from_manager[user_id] = time.time()
                continue

            # === ЕСЛИ МЕНЕДЖЕР В ДИАЛОГЕ (2 часа) ===
            manager_recent = last_message_from_manager.get(uid, 0)
            if time.time() - manager_recent < 7200:
                print(f"⏸️ Бот молчит (менеджер в диалоге) для {uid}")
                continue

            # === ПОЛУЧАЕМ ИМЯ КЛИЕНТА ===
            try:
                user_info = vk_session.get_api().users.get(user_id=uid)
                user_name = user_info[0]['first_name']
            except:
                user_name = "Клиент"

            # === ЛОГИКА ЗАКАЗА ===
            # Проверяем, есть ли намерение купить
            if any(w in text.lower() for w in ["покупаю", "заказываю", "беру", "оформляю", "хочу купить", "заказ"]):
                # Проверяем, есть ли уже город в сохранённых данных
                if uid not in order_data:
                    order_data[uid] = {}

                city = order_data[uid].get("city")
                phone = order_data[uid].get("phone")

                # Если город ещё не указан, спрашиваем
                if not city:
                    answer = "Для расчёта доставки укажите ваш город (например, Москва). Откуда вы?"
                    vk_session.get_api().messages.send(user_id=uid, message=answer, random_id=0)
                    # Сохраняем запрос в историю
                    if uid not in dialogs:
                        dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                    dialogs[uid].append({"role": "assistant", "content": answer})
                    continue

                # Если город есть, но телефон ещё не указан
                if not phone:
                    # Определяем товар (последний упомянутый)
                    product = None
                    for p in PRODUCTS:
                        if p["name"].lower() in text.lower() or any(w in text.lower() for w in ["ведр", "короб"]):
                            product = p
                            break
                    if not product:
                        product = PRODUCTS[-1]  # по умолчанию вёдра

                    # Рассчитываем доставку
                    result = calculate_delivery(city, product["weight"])
                    if "error" in result:
                        answer = f"❌ Не удалось рассчитать доставку: {result['error']}"
                    else:
                        total_price = product["price"] + result["price"]
                        answer = (
                            f"✅ Рассчитал доставку от Владимира до {city.capitalize()}:\n"
                            f"📦 Товар: {product['name']} — {product['price']:.2f} ₽\n"
                            f"🚚 Доставка: {result['price']:.2f} ₽ ({result['days_min']}-{result['days_max']} дн.)\n"
                            f"💰 Итого: {total_price:.2f} ₽\n\n"
                            f"Для оформления заказа нужен ваш номер телефона. Напишите, пожалуйста."
                        )
                        # Сохраняем данные о товаре и сумме для последующей отправки менеджеру
                        order_data[uid]["product"] = product
                        order_data[uid]["total"] = total_price
                        order_data[uid]["delivery"] = result["price"]
                        order_data[uid]["days"] = f"{result['days_min']}-{result['days_max']}"

                    vk_session.get_api().messages.send(user_id=uid, message=answer, random_id=0)
                    if uid not in dialogs:
                        dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                    dialogs[uid].append({"role": "assistant", "content": answer})
                    continue

                # Если есть и город, и телефон — отправляем заявку менеджеру и завершаем
                product = order_data[uid].get("product")
                total = order_data[uid].get("total")
                delivery_price = order_data[uid].get("delivery")
                days = order_data[uid].get("days")

                if product and total:
                    # Отправляем уведомление менеджеру
                    try:
                        vk = VkApi(token=VK_TOKEN).get_api()
                        vk.messages.send(
                            user_id=MANAGER_VK_ID,
                            message=(
                                f"🛒 ЗАЯВКА от {user_name}!\n"
                                f"Товар: {product['name']}\n"
                                f"Количество: уточнить\n"
                                f"Город: {city}\n"
                                f"Телефон: {phone}\n"
                                f"Доставка: {delivery_price:.2f} ₽ ({days} дн.)\n"
                                f"Итоговая сумма: {total:.2f} ₽"
                            ),
                            random_id=0
                        )
                    except:
                        pass

                    answer = (
                        f"✅ Заявка оформлена!\n"
                        f"Менеджер свяжется с вами по номеру {phone} в ближайшее время.\n"
                        f"Спасибо за покупку! 😊"
                    )
                    vk_session.get_api().messages.send(user_id=uid, message=answer, random_id=0)
                    # Очищаем данные заказа после оформления
                    order_data.pop(uid, None)
                    if uid not in dialogs:
                        dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                    dialogs[uid].append({"role": "assistant", "content": answer})
                    continue

            # === ОБРАБОТКА ВВОДА ГОРОДА ИЛИ ТЕЛЕФОНА (если мы ждём эти данные) ===
            if uid in order_data:
                # Если мы ждём город
                if not order_data[uid].get("city") and not any(w in text.lower() for w in ["покупаю", "заказываю", "беру", "оформляю", "хочу купить", "заказ"]):
                    # Считаем, что это ввод города
                    city = text.strip()
                    # Проверяем, что это похоже на город (не слишком коротко)
                    if len(city) > 1:
                        order_data[uid]["city"] = city
                        # Город сохранён, теперь повторно инициируем расчёт
                        # Можно просто вернуть, чтобы на следующем цикле бот обработал как заказ
                        # Но лучше сразу продолжить обработку, используя флаг
                        pass
                # Если мы ждём телефон
                elif not order_data[uid].get("phone") and order_data[uid].get("city"):
                    # Проверяем, что это похоже на телефон (содержит цифры)
                    if any(char.isdigit() for char in text):
                        order_data[uid]["phone"] = text.strip()
                        # Теперь у нас есть всё — можно отправить заявку
                        # Устанавливаем флаг, чтобы бот обработал это как заказ
                        # Но проще вызвать логику заказа повторно с флагом
                        # Мы можем просто продолжить цикл, а на следующей итерации
                        # обработать как заказ
                        continue

            # === ОБЫЧНЫЙ ДИАЛОГ (если нет специальных флагов) ===
            if uid not in dialogs:
                dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]

            answer, new_history = ask_aitunnel(text, dialogs[uid])
            dialogs[uid] = new_history

            vk_session.get_api().messages.send(
                user_id=uid, message=answer, random_id=0
            )

if __name__ == "__main__":
    main()
