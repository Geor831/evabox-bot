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

# ===== ФИКСИРОВАННЫЕ ЦЕНЫ ДОСТАВКИ =====
DELIVERY_PRICES = {
    "москва": 350,
    "самара": 430,          # ← твоя цена из договора
    "санкт-петербург": 450,
    "питер": 450,
    "владимир": 0,
    "новосибирск": 500,
    "екатеринбург": 480,
}
DEFAULT_DELIVERY_PRICE = None  # если None, пишем "рассчитает менеджер"
# ===============================================

PRODUCTS = [
    {"name": "Короба 600×400×400", "desc": "Крупная коробка для габаритных грузов. Трёхслойный гофрокартон T23, самосборная, упаковка 10 шт.", "price": 70.0},
    {"name": "Короба 600×400×200", "desc": "Удобная коробка 600×400×200 мм для плоских грузов.", "price": 68.0},
    {"name": "Короба 200×300×300", "desc": "Коробка 200×300×300 мм для небольших товаров.", "price": 60.0},
    {"name": "Короба 95×95×103", "desc": "Компактная коробка 95×95×103 мм для мелких предметов.", "price": 22.0},
    {"name": "Короба 50×50×225", "desc": "Узкая коробка 50×50×225 мм для длинных товаров.", "price": 16.0},
    {"name": "Короба 100×100×290", "desc": "Коробка 100×100×290 мм для средних по длине предметов.", "price": 12.09},
    {"name": "Короба 1040×165×45", "desc": "Длинная плоская коробка 1040×165×45 мм для крупных плоских грузов.", "price": 29.04},
    {"name": "Короба 110×110×335", "desc": "Коробка 110×110×335 мм для длинных тонких предметов.", "price": 20.3},
    {"name": "Короба 165×105×55", "desc": "Коробка 165×105×55 мм для компактных товаров.", "price": 11.08},
    {"name": "Короба 170×170×80", "desc": "Квадратная коробка 170×170×80 мм.", "price": 9.96},
    {"name": "Короба 220×130×130*", "desc": "Коробка 220×130×130 мм для небольших товаров среднего размера.", "price": 9.99},
    {"name": "Короба 220×130×180", "desc": "Коробка 220×130×180 мм для компактных грузов.", "price": 11.47},
    {"name": "Короба 240×135×50", "desc": "Плоская коробка 240×135×50 мм для небольших плоских предметов.", "price": 16.98},
    {"name": "Короба 280×150×350", "desc": "Коробка 280×150×350 мм для средних габаритных товаров.", "price": 23.41},
    {"name": "Короба 300×200×300", "desc": "Коробка 300×200×300 мм для универсальных грузов.", "price": 23.55},
    {"name": "Короба 380×240×290", "desc": "Коробка 380×240×290 мм для крупных товаров.", "price": 33.0},
    {"name": "Короба 590×195×120", "desc": "Длинная коробка 590×195×120 мм для крупных длинных предметов.", "price": 57.72},
    {"name": "Короба 785×235×215", "desc": "Крупная коробка 785×235×215 мм для больших грузов.", "price": 42.87},
    {"name": "Ведро пластиковое пищевое 20 л с крышкой", "desc": "🪣 Универсальное пищевое ведро 20 л — идеально для хранения продуктов, заготовок, воды. Толстый пластик (1 кг), герметичная крышка, удобная ручка. Б/у из-под сиропа, состояние идеальное.", "price": 300.0},
    {"name": "Набор эфирных масел PARLAB, 5 шт", "desc": "🌿 Натуральный набор 100% эфирных масел (чайное дерево, апельсин, мята, лаванда, иланг-иланг). В подарочной упаковке, объём 50 мл.", "price": 696.0},
    {"name": "Прокладки для собак PitoMir, 30 шт", "desc": "🐾 Гипоаллергенные впитывающие прокладки для собак и кошек 30 шт. Дышащий материал, суперабсорбент, липкий слой.", "price": 432.0},
    {"name": "Садовая дорожка модульная GUSEV GARDEN, 27 шт", "desc": "🌱 Садовая модульная дорожка 27 модулей (2.43 м²). Прочный пластик, устойчивый к погоде и нагрузкам. Легко собирается без инструментов.", "price": 2676.0},
    {"name": "Садовая дорожка модульная GUSEV GARDEN, 9 шт", "desc": "🌱 Садовая модульная дорожка 9 модулей (0.81 м²). Компактный вариант для небольших участков.", "price": 1177.0},
    {"name": "Скобы садовые с фиксаторами GUSEV GARDEN, 100 шт", "desc": "🧷 Надёжные садовые скобы из оцинкованной стали с пластиковыми фиксаторами, 100 шт. Заострённые концы легко входят в грунт.", "price": 670.0},
    {"name": "Заборчик садовый раздвижной декоративный GUSEV GARDEN", "desc": "🌳 Декоративный раздвижной заборчик из WPC (древесно-пластиковый композит). Высота 40 см, длина 90 см (раздвижной).", "price": 923.0},
    {"name": "Печь походная отопительная для палатки и бани", "desc": "🔥 Дровяная печь из стали Aisi 439, компактная, с дымоходом, каменкой, быстросъёмными ножками. Идеальна для палаток, бань, зимней рыбалки.", "price": 18000.0}
]

SYSTEM_PROMPT = (
    "Ты — продавец-консультант интернет-магазина EVA.store.\n"
    "Ты помогаешь клиентам с выбором и оформлением заказов.\n\n"
    "У нас есть следующие товары (всегда используй эти nazvaniya и цены):\n"
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

def get_delivery_price(city_name: str) -> int:
    city_lower = city_name.lower().strip()
    for key, price in DELIVERY_PRICES.items():
        if key in city_lower:
            return price
    return DEFAULT_DELIVERY_PRICE

def calculate_delivery(city_name: str, product_name: str) -> dict:
    product = None
    for p in PRODUCTS:
        if p["name"].lower() == product_name.lower() or product_name.lower() in p["name"].lower():
            product = p
            break
    if not product:
        return {"error": f"Товар '{product_name}' не найден"}

    price = get_delivery_price(city_name)
    if price is None:
        return {"error": "Доставка будет рассчитана менеджером"}

    return {
        "price": price,
        "days_min": 2,
        "days_max": 4,
        "product_name": product["name"],
        "product_price": product["price"]
    }

def ask_aitunnel_with_tools(user_msg, history=None, tools=None):
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
    print("✅ Бот запущен (фиксированные тарифы)")

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
                            "description": "Название города клиента, например 'Москва'"
                        },
                        "product_name": {
                            "type": "string",
                            "description": "Точное название товара из списка"
                        }
                    },
                    "required": ["city_name", "product_name"]
                }
            }
        }
    ]

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

            response = ask_aitunnel_with_tools(text, dialogs[uid], tools)
            if response is None:
                vk.messages.send(user_id=uid, message="❌ Ошибка сервиса ИИ. Попробуйте позже.", random_id=0)
                continue

            msg = response["choices"][0]["message"]

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

                    result = calculate_delivery(city_name, product_name)
                    if "error" in result:
                        delivery_result = f"❌ {result['error']}"
                        total = None
                    else:
                        total = result["product_price"] + result["price"]
                        delivery_result = (
                            f"🚚 Доставка: {result['price']} ₽ (2-4 дня)\n"
                            f"💰 Итого: {total} ₽"
                        )
                        if uid not in order_data:
                            order_data[uid] = {}
                        order_data[uid]["city"] = city_name
                        order_data[uid]["product"] = product_name
                        order_data[uid]["product_price"] = result["product_price"]
                        order_data[uid]["delivery_price"] = result["price"]
                        order_data[uid]["total"] = total

                    function_response = {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": delivery_result
                    }
                    dialogs[uid].append(msg)
                    dialogs[uid].append(function_response)

                    second_response = ask_aitunnel_with_tools("", dialogs[uid], tools)
                    if second_response:
                        final_msg = second_response["choices"][0]["message"]
                        answer = final_msg.get("content", "✅ Доставка рассчитана. Укажите номер телефона для заказа.")
                        vk.messages.send(user_id=uid, message=answer, random_id=0)
                        if "content" in final_msg:
                            dialogs[uid].append({"role": "assistant", "content": final_msg["content"]})
                    else:
                        vk.messages.send(user_id=uid, message="❌ Ошибка обработки. Попробуйте позже.", random_id=0)
                else:
                    vk.messages.send(user_id=uid, message="❌ Неизвестная функция.", random_id=0)
                continue

            if "content" in msg:
                answer = msg["content"]
                vk.messages.send(user_id=uid, message=answer, random_id=0)
                dialogs[uid].append({"role": "assistant", "content": answer})
                if "телефон" in answer.lower() or "номер" in answer.lower():
                    if uid not in order_data:
                        order_data[uid] = {}
                    order_data[uid]["awaiting_phone"] = True

            if uid in order_data and order_data[uid].get("awaiting_phone"):
                phone_match = re.search(r'\+?\d[\d\s\-\(\)]{7,}\d', text)
                if phone_match:
                    phone = phone_match.group().strip()
                    city = order_data[uid].get("city", "не указан")
                    product = order_data[uid].get("product", "не указан")
                    total = order_data[uid].get("total", "не рассчитана")
                    delivery_info = ""
                    if order_data[uid].get("delivery_price") is not None:
                        delivery_info = f"Доставка: {order_data[uid]['delivery_price']} ₽, итого: {total} ₽"
                    else:
                        delivery_info = "Доставка будет рассчитана менеджером"

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
                    if uid in order_data:
                        del order_data[uid]

if __name__ == "__main__":
    main()
