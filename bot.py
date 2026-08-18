import time
import requests
import re
import json
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

# ===== НАСТРОЙКИ =====
VK_TOKEN = "vk1.a.vedeEaKBa4UKyV0RYddcBqMts_JJrvNynhr8OPClZfx2l6JQVzrFM2v9fXIm74J0RWykxVmwIMxbrwVuZxnoDYkUh4FE9EVxz4d3btZ51dyjV4nUzHJ9Gph5juclIZaWRfq03hBfqW6L3Our9W_1PwJsp5udn-_nOTM2XV79CO16MWqPwmfKEON4dp3oPnVdz9bBIhEzRIjmlAEFLfDeNQ"
MANAGER_IDS = [29279564, 598512076]
AITUNNEL_API_KEY = "sk-aitunnel-EJz97YJpiOwnaObmGNjf6mU8cT2OdP8L"

# ===== НАСТРОЙКИ СДЭК =====
CDEK_CLIENT_ID = "FDF0yHIab572TjWg6Kuo5uIzY5jcyKQ2"
CDEK_CLIENT_SECRET = "B8UDRKFzfbMzMgZ9cwrOKsEwPodAloGN"
SENDER_CITY_CODE = 1177  # Владимир
# ===============================================

PRODUCTS = [
    {"name": "Короба 600×400×400", "desc": "Крупная коробка для габаритных грузов. Трёхслойный гофрокартон T23, самосборная, упаковка 10 шт.", "price": 70.0, "weight": 500, "length": 60, "width": 40, "height": 40},
    {"name": "Короба 600×400×200", "desc": "Удобная коробка 600×400×200 мм для плоских грузов. Трёхслойный картон T23, самосборная, упаковка 10 шт.", "price": 68.0, "weight": 400, "length": 60, "width": 40, "height": 20},
    {"name": "Короба 200×300×300", "desc": "Коробка 200×300×300 мм для небольших товаров. Трёхслойный гофрокартон T23, самосборная, 10 шт.", "price": 60.0, "weight": 400, "length": 20, "width": 30, "height": 30},
    {"name": "Короба 95×95×103", "desc": "Компактная коробка 95×95×103 мм для мелких предметов. Трёхслойный картон T23, самосборная, упаковка 10 шт.", "price": 22.0, "weight": 200, "length": 9.5, "width": 9.5, "height": 10.3},
    {"name": "Короба 50×50×225", "desc": "Узкая коробка 50×50×225 мм для длинных товаров. Трёхслойный гофрокартон T23, самосборная, 10 шт.", "price": 16.0, "weight": 200, "length": 5, "width": 5, "height": 22.5},
    {"name": "Короба 100×100×290", "desc": "Коробка 100×100×290 мм для средних по длине предметов. Трёхслойный картон T23, самосборная, упаковка 10 шт.", "price": 12.09, "weight": 200, "length": 10, "width": 10, "height": 29},
    {"name": "Короба 1040×165×45", "desc": "Длинная плоская коробка 1040×165×45 мм для крупных плоских грузов. Трёхслойный гофрокартон T23, самосборная, 10 шт.", "price": 29.04, "weight": 600, "length": 104, "width": 16.5, "height": 4.5},
    {"name": "Короба 110×110×335", "desc": "Коробка 110×110×335 мм для длинных тонких предметов. Трёхслойный картон T23, самосборная, упаковка 10 шт.", "price": 20.3, "weight": 300, "length": 11, "width": 11, "height": 33.5},
    {"name": "Короба 165×105×55", "desc": "Коробка 165×105×55 мм для компактных товаров. Трёхслойный гофрокартон T23, самосборная, 10 шт.", "price": 11.08, "weight": 200, "length": 16.5, "width": 10.5, "height": 5.5},
    {"name": "Короба 170×170×80", "desc": "Квадратная коробка 170×170×80 мм для небольших квадратных предметов. Трёхслойный картон T23, самосборная, упаковка 10 шт.", "price": 9.96, "weight": 200, "length": 17, "width": 17, "height": 8},
    {"name": "Короба 220×130×130*", "desc": "Коробка 220×130×130 мм для небольших товаров среднего размера. Трёхслойный гофрокартон T23, самосборная, 10 шт.", "price": 9.99, "weight": 200, "length": 22, "width": 13, "height": 13},
    {"name": "Короба 220×130×180", "desc": "Коробка 220×130×180 мм для компактных грузов. Трёхслойный картон T23, самосборная, упаковка 10 шт.", "price": 11.47, "weight": 200, "length": 22, "width": 13, "height": 18},
    {"name": "Короба 240×135×50", "desc": "Плоская коробка 240×135×50 мм для небольших плоских предметов. Трёхслойный гофрокартон T23, самосборная, 10 шт.", "price": 16.98, "weight": 300, "length": 24, "width": 13.5, "height": 5},
    {"name": "Короба 280×150×350", "desc": "Коробка 280×150×350 мм для средних габаритных товаров. Трёхслойный картон T23, самосборная, упаковка 10 шт.", "price": 23.41, "weight": 400, "length": 28, "width": 15, "height": 35},
    {"name": "Короба 300×200×300", "desc": "Коробка 300×200×300 мм для универсальных грузов. Трёхслойный гофрокартон T23, самосборная, 10 шт.", "price": 23.55, "weight": 400, "length": 30, "width": 20, "height": 30},
    {"name": "Короба 380×240×290", "desc": "Коробка 380×240×290 мм для крупных товаров. Трёхслойный картон T23, самосборная, упаковка 10 шт.", "price": 33.0, "weight": 500, "length": 38, "width": 24, "height": 29},
    {"name": "Короба 590×195×120", "desc": "Длинная коробка 590×195×120 мм для крупных длинных предметов. Трёхслойный гофрокартон T23, самосборная, 10 шт.", "price": 57.72, "weight": 500, "length": 59, "width": 19.5, "height": 12},
    {"name": "Короба 785×235×215", "desc": "Крупная коробка 785×235×215 мм для больших грузов. Трёхслойный картон T23, самосборная, упаковка 10 шт.", "price": 42.87, "weight": 600, "length": 78.5, "width": 23.5, "height": 21.5},
    {"name": "Ведро пластиковое пищевое 20 л с крышкой", "desc": "🪣 Универсальное пищевое ведро 20 л — идеально для хранения продуктов, заготовок, воды. Толстый пластик (1 кг), герметичная крышка, удобная ручка. Б/у из-под сиропа, состояние идеальное: без сколов, трещин и запаха.", "price": 300.0, "weight": 1100, "length": 35, "width": 35, "height": 40},
    {"name": "Набор эфирных масел PARLAB, 5 шт", "desc": "🌿 Натуральный набор 100% эфирных масел (чайное дерево, апельсин, мята, лаванда, иланг-иланг). В подарочной упаковке, объём 50 мл.", "price": 696.0, "weight": 400, "length": 20, "width": 15, "height": 5},
    {"name": "Прокладки для собак PitoMir, 30 шт", "desc": "🐾 Гипоаллергенные впитывающие прокладки для собак и кошек 30 шт. Дышащий материал, суперабсорбент, липкий слой.", "price": 432.0, "weight": 600, "length": 30, "width": 20, "height": 10},
    {"name": "Садовая дорожка модульная GUSEV GARDEN, 27 шт", "desc": "🌱 Садовая модульная дорожка 27 модулей (2.43 м²). Прочный пластик, устойчивый к погоде и нагрузкам. Легко собирается без инструментов.", "price": 2676.0, "weight": 5700, "length": 32, "width": 31, "height": 26},
    {"name": "Садовая дорожка модульная GUSEV GARDEN, 9 шт", "desc": "🌱 Садовая модульная дорожка 9 модулей (0.81 м²). Компактный вариант для небольших участков.", "price": 1177.0, "weight": 2000, "length": 32, "width": 32, "height": 9},
    {"name": "Скобы садовые с фиксаторами GUSEV GARDEN, 100 шт", "desc": "🧷 Надёжные садовые скобы из оцинкованной стали с пластиковыми фиксаторами, 100 шт. Заострённые концы легко входят в грунт.", "price": 670.0, "weight": 1820, "length": 23, "width": 18, "height": 10},
    {"name": "Заборчик садовый раздвижной декоративный GUSEV GARDEN", "desc": "🌳 Декоративный раздвижной заборчик из WPC (древесно-пластиковый композит). Высота 40 см, длина 90 см (раздвижной).", "price": 923.0, "weight": 400, "length": 45, "width": 23, "height": 3},
    {"name": "Печь походная отопительная для палатки и бани", "desc": "🔥 Дровяная печь из стали Aisi 439, компактная, с дымоходом, каменкой, быстросъёмными ножками. Идеальна для палаток, бань, зимней рыбалки.", "price": 18000.0, "weight": 23000, "length": 67, "width": 30, "height": 45}
]

SYSTEM_PROMPT = (
    "Ты — продавец-консультант интернет-магазина EVA.store.\n"
    "Ты помогаешь клиентам с выбором и оформлением заказов.\n\n"
    "У нас есть следующие товары (всегда используй эти названия и цены):\n"
    + "\n".join([f"- {p['name']}: {p['price']} ₽, {p['desc']}" for p in PRODUCTS]) +
    "\n\nАЛГОРИТМ РАБОТЫ:\n"
    "- Если клиент выражает желание купить или спрашивает цену/доставку, определи город и товар.\n"
    "- Для расчёта доставки вызови функцию calculate_delivery.\n"
    "- После расчёта спроси номер телефона.\n"
    "- Когда клиент дал телефон — сообщи, что заявка передана менеджеру.\n"
    "- Отвечай кратко, дружелюбно, используй техники продаж.\n"
    "- Если клиент спрашивает о товаре — дай информацию из списка выше.\n"
    "- Если клиент спрашивает про доставку, но не назвал город — сначала попроси назвать город."
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
        print(f"⚠️ Ошибка токена СДЭК: {response.status_code} {response.text[:200]}")
        return None
    except Exception as e:
        print(f"⚠️ Ошибка токена СДЭК: {e}")
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
        print(f"⚠️ Ошибка поиска города: {response.status_code} {response.text[:200]}")
    except Exception as e:
        print(f"⚠️ Ошибка поиска города: {e}")
    return None

def calculate_delivery(city_name: str, product_name: str) -> dict:
    """Функция, вызываемая ИИ для расчёта доставки"""
    # Находим товар по названию
    product = None
    for p in PRODUCTS:
        if p["name"].lower() == product_name.lower() or product_name.lower() in p["name"].lower():
            product = p
            break
    if not product:
        return {"error": f"Товар '{product_name}' не найден в ассортименте"}

    city_code = get_city_code(city_name)
    if not city_code:
        return {"error": f"Не удалось определить код города '{city_name}'"}

    token = get_cdek_token()
    if not token:
        return {"error": "Не удалось получить токен СДЭК"}

    package = {
        "weight": product.get("weight", 500),
    }
    if "length" in product and "width" in product and "height" in product:
        package["length"] = product["length"]
        package["width"] = product["width"]
        package["height"] = product["height"]

    tariffs = [136, 137, 138]
    best_price = None
    best_days = None
    last_error = None

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
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                if "tariff_codes" in data and len(data["tariff_codes"]) > 0:
                    tariff_info = data["tariff_codes"][0]
                    price = tariff_info.get("total_sum", 0)
                    if price > 0:
                        if best_price is None or price < best_price:
                            best_price = price
                            best_days = {
                                "min": tariff_info.get("period_min", 1),
                                "max": tariff_info.get("period_max", 3)
                            }
            else:
                last_error = f"СДЭК вернул {response.status_code}"
        except Exception as e:
            last_error = str(e)
            continue

    if best_price is not None:
        return {
            "price": best_price,
            "days_min": best_days["min"],
            "days_max": best_days["max"],
            "product_name": product["name"],
            "product_price": product["price"]
        }
    else:
        return {"error": last_error or "Не удалось рассчитать доставку"}

def ask_aitunnel_with_tools(user_msg, history=None, tools=None):
    """Вызов DeepSeek через AITunnel с поддержкой function calling"""
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
        "max_tokens": 600,
        "tools": tools,
        "tool_choice": "auto"
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ Ошибка AITunnel: {response.status_code} {response.text[:200]}")
            return None
    except Exception as e:
        print(f"⚠️ Ошибка запроса к AITunnel: {e}")
        return None

def main():
    print("🔄 Подключаюсь к VK...")
    vk_session = VkApi(token=VK_TOKEN)
    longpoll = VkLongPoll(vk_session, wait=90)
    vk = vk_session.get_api()
    print("✅ Бот запущен (function calling)")

    # Определяем доступные функции (tools) для ИИ
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate_delivery",
                "description": "Рассчитывает стоимость доставки для указанного города и товара. Используй эту функцию, когда клиент хочет купить товар и назвал город.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city_name": {
                            "type": "string",
                            "description": "Название города клиента, например 'Москва' или 'Санкт-Петербург'"
                        },
                        "product_name": {
                            "type": "string",
                            "description": "Точное название товара из списка, например 'Ведро пластиковое пищевое 20 л с крышкой'"
                        }
                    },
                    "required": ["city_name", "product_name"]
                }
            }
        }
    ]

    dialogs = {}           # история диалога
    order_data = {}        # временные данные по заказу
    pending_tool_calls = {} # ожидание вызова функции для подтверждения

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

            # Получаем историю диалога для пользователя
            if uid not in dialogs:
                dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]

            # Отправляем запрос к ИИ с возможностью вызова функций
            response = ask_aitunnel_with_tools(text, dialogs[uid], tools)
            if response is None:
                vk.messages.send(user_id=uid, message="❌ Ошибка сервиса ИИ. Попробуйте позже.", random_id=0)
                continue

            msg = response["choices"][0]["message"]

            # Если ИИ хочет вызвать функцию
            if "tool_calls" in msg and msg["tool_calls"]:
                tool_call = msg["tool_calls"][0]
                function_name = tool_call["function"]["name"]
                arguments = json.loads(tool_call["function"]["arguments"])

                if function_name == "calculate_delivery":
                    city_name = arguments.get("city_name")
                    product_name = arguments.get("product_name")
                    if not city_name or not product_name:
                        vk.messages.send(user_id=uid, message="❌ Не удалось определить город или товар. Уточните, пожалуйста.", random_id=0)
                        continue

                    # Выполняем расчёт доставки
                    result = calculate_delivery(city_name, product_name)
                    if "error" in result:
                        delivery_result = f"❌ {result['error']}"
                        total = None
                    else:
                        total = result["product_price"] + result["price"]
                        delivery_result = (
                            f"🚚 Доставка: {result['price']} ₽ ({result['days_min']}-{result['days_max']} дн.)\n"
                            f"💰 Итого: {total} ₽"
                        )
                        # Сохраняем данные в order_data
                        if uid not in order_data:
                            order_data[uid] = {}
                        order_data[uid]["city"] = city_name
                        order_data[uid]["product"] = product_name
                        order_data[uid]["product_price"] = result["product_price"]
                        order_data[uid]["delivery_price"] = result["price"]
                        order_data[uid]["total"] = total

                    # Добавляем результат функции в историю (для продолжения диалога)
                    function_response = {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": delivery_result
                    }
                    dialogs[uid].append(msg)  # добавляем сообщение ассистента с вызовом
                    dialogs[uid].append(function_response)

                    # Повторный запрос к ИИ с результатом функции
                    second_response = ask_aitunnel_with_tools("", dialogs[uid], tools)
                    if second_response:
                        final_msg = second_response["choices"][0]["message"]
                        answer = final_msg.get("content", "✅ Доставка рассчитана. Укажите номер телефона для заказа.")
                        vk.messages.send(user_id=uid, message=answer, random_id=0)
                        # Добавляем ответ в историю
                        if "content" in final_msg:
                            dialogs[uid].append({"role": "assistant", "content": final_msg["content"]})
                    else:
                        vk.messages.send(user_id=uid, message="❌ Ошибка обработки. Попробуйте позже.", random_id=0)
                else:
                    vk.messages.send(user_id=uid, message="❌ Неизвестная функция.", random_id=0)
                continue

            # Если ИИ просто ответил текстом (без вызова функции)
            if "content" in msg:
                answer = msg["content"]
                vk.messages.send(user_id=uid, message=answer, random_id=0)
                dialogs[uid].append({"role": "assistant", "content": answer})
                # Если в ответе просит телефон, запоминаем, что ожидаем телефон
                if "телефон" in answer.lower() or "номер" in answer.lower():
                    if uid not in order_data:
                        order_data[uid] = {}
                    order_data[uid]["awaiting_phone"] = True

            # Обработка ввода телефона (если бот его запросил)
            if uid in order_data and order_data[uid].get("awaiting_phone"):
                # Проверяем, похоже ли сообщение на телефон
                phone_match = re.search(r'\+?\d[\d\s\-\(\)]{7,}\d', text)
                if phone_match:
                    phone = phone_match.group().strip()
                    # Получаем сохранённые данные заказа
                    city = order_data[uid].get("city", "не указан")
                    product = order_data[uid].get("product", "не указан")
                    total = order_data[uid].get("total", "не рассчитана")
                    delivery_info = ""
                    if order_data[uid].get("delivery_price") is not None:
                        delivery_info = f"Доставка: {order_data[uid]['delivery_price']} ₽, итого: {total} ₽"
                    else:
                        delivery_info = "Доставка будет рассчитана менеджером"

                    # Отправляем заявку менеджерам
                    for manager_id in MANAGER_IDS:
                        try:
                            vk.messages.send(
                                user_id=manager_id,
                                message=(
                                    f"🛒 ЗАЯВКА от {user_name}!\n"
                                    f"Товар: {product}\n"
                                    f"Город: {city}\n"
                                    f"Телефон: {phone}\n"
                                    f"{delivery_info}"
                                ),
                                random_id=0
                            )
                        except:
                            pass
                    answer = "✅ Заявка оформлена! Менеджер свяжется с вами по указанному телефону. Спасибо! 😊"
                    vk.messages.send(user_id=uid, message=answer, random_id=0)
                    dialogs[uid].append({"role": "assistant", "content": answer})
                    # Очищаем данные заказа
                    if uid in order_data:
                        del order_data[uid]
                else:
                    # Если не похоже на телефон, но мы ждём телефон, можно переспросить
                    pass

if __name__ == "__main__":
    main()
