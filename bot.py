import time
import requests
import re
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

# ===== НАСТРОЙКИ =====
VK_TOKEN = "vk1.a.vedeEaKBa4UKyV0RYddcBqMts_JJrvNynhr8OPClZfx2l6JQVzrFM2v9fXIm74J0RWykxVmwIMxbrwVuZxnoDYkUh4FE9EVxz4d3btZ51dyjV4nUzHJ9Gph5juclIZaWRfq03hBfqW6L3Our9W_1PwJsp5udn-_nOTM2XV79CO16MWqPwmfKEON4dp3oPnVdz9bBIhEzRIjmlAEFLfDeNQ"
MANAGER_IDS = [29279564, 598512076]
AITUNNEL_API_KEY = "sk-aitunnel-EJz97YJpiOwnaObmGNjf6mU8cT2OdP8L"

# ===== НАСТРОЙКИ СДЭК (уже вставлены) =====
CDEK_CLIENT_ID = "1lewXxGlFX3De0d3L6rPbjhzYPfrYvJK"
CDEK_CLIENT_SECRET = "pEpIoya912voraWeRAV2PdH18TrI1Fty"
SENDER_CITY_CODE = 1177  # Владимир
# ===============================================

# ===== ТОВАРЫ С ГАБАРИТАМИ =====
PRODUCTS = [
    {"name": "Короба 600×400×400", "desc": "Крупная коробка для габаритных грузов. Трёхслойный гофрокартон T23, самосборная, упаковка 10 шт. Надёжно защищает товар при переезде и хранении.", "price": 70.0, "weight": 500, "length": 60, "width": 40, "height": 40},
    {"name": "Короба 600×400×200", "desc": "Удобная коробка 600×400×200 мм для плоских грузов. Трёхслойный картон T23, самосборная, упаковка 10 шт. Прочная и лёгкая.", "price": 68.0, "weight": 400, "length": 60, "width": 40, "height": 20},
    {"name": "Короба 200×300×300", "desc": "Коробка 200×300×300 мм для небольших товаров. Трёхслойный гофрокартон T23, самосборная, 10 шт. в упаковке. Идеально для интернет-магазинов.", "price": 60.0, "weight": 400, "length": 20, "width": 30, "height": 30},
    {"name": "Короба 95×95×103", "desc": "Компактная коробка 95×95×103 мм для мелких предметов. Трёхслойный картон T23, самосборная, упаковка 10 шт. Надёжная упаковка для небольших заказов.", "price": 22.0, "weight": 200, "length": 9.5, "width": 9.5, "height": 10.3},
    {"name": "Короба 50×50×225", "desc": "Узкая коробка 50×50×225 мм для длинных товаров. Трёхслойный гофрокартон T23, самосборная, 10 шт. Отлично подходит для труб, светильников, профилей.", "price": 16.0, "weight": 200, "length": 5, "width": 5, "height": 22.5},
    {"name": "Короба 100×100×290", "desc": "Коробка 100×100×290 мм для средних по длине предметов. Трёхслойный картон T23, самосборная, упаковка 10 шт. Прочная и удобная.", "price": 12.09, "weight": 200, "length": 10, "width": 10, "height": 29},
    {"name": "Короба 1040×165×45", "desc": "Длинная плоская коробка 1040×165×45 мм для крупных плоских грузов. Трёхслойный гофрокартон T23, самосборная, 10 шт. Идеально для картин, зеркал, панелей.", "price": 29.04, "weight": 600, "length": 104, "width": 16.5, "height": 4.5},
    {"name": "Короба 110×110×335", "desc": "Коробка 110×110×335 мм для длинных тонких предметов. Трёхслойный картон T23, самосборная, упаковка 10 шт. Надёжно защищает содержимое.", "price": 20.3, "weight": 300, "length": 11, "width": 11, "height": 33.5},
    {"name": "Короба 165×105×55", "desc": "Коробка 165×105×55 мм для компактных товаров. Трёхслойный гофрокартон T23, самосборная, 10 шт. Удобна для хранения и пересылки.", "price": 11.08, "weight": 200, "length": 16.5, "width": 10.5, "height": 5.5},
    {"name": "Короба 170×170×80", "desc": "Квадратная коробка 170×170×80 мм для небольших квадратных предметов. Трёхслойный картон T23, самосборная, упаковка 10 шт. Прочная и аккуратная.", "price": 9.96, "weight": 200, "length": 17, "width": 17, "height": 8},
    {"name": "Короба 220×130×130*", "desc": "Коробка 220×130×130 мм для небольших товаров среднего размера. Трёхслойный гофрокартон T23, самосборная, 10 шт. Универсальная упаковка.", "price": 9.99, "weight": 200, "length": 22, "width": 13, "height": 13},
    {"name": "Короба 220×130×180", "desc": "Коробка 220×130×180 мм для компактных грузов. Трёхслойный картон T23, самосборная, упаковка 10 шт. Надёжно защищает товары при транспортировке.", "price": 11.47, "weight": 200, "length": 22, "width": 13, "height": 18},
    {"name": "Короба 240×135×50", "desc": "Плоская коробка 240×135×50 мм для небольших плоских предметов. Трёхслойный гофрокартон T23, самосборная, 10 шт. Удобна для писем, документов, фото.", "price": 16.98, "weight": 300, "length": 24, "width": 13.5, "height": 5},
    {"name": "Короба 280×150×350", "desc": "Коробка 280×150×350 мм для средних габаритных товаров. Трёхслойный картон T23, самосборная, упаковка 10 шт. Надёжная упаковка для интернет-заказов.", "price": 23.41, "weight": 400, "length": 28, "width": 15, "height": 35},
    {"name": "Короба 300×200×300", "desc": "Коробка 300×200×300 мм для универсальных грузов. Трёхслойный гофрокартон T23, самосборная, 10 шт. Отлично подходит для хранения и пересылки.", "price": 23.55, "weight": 400, "length": 30, "width": 20, "height": 30},
    {"name": "Короба 380×240×290", "desc": "Коробка 380×240×290 мм для крупных товаров. Трёхслойный картон T23, самосборная, упаковка 10 шт. Прочная конструкция для тяжелых грузов.", "price": 33.0, "weight": 500, "length": 38, "width": 24, "height": 29},
    {"name": "Короба 590×195×120", "desc": "Длинная коробка 590×195×120 мм для крупных длинных предметов. Трёхслойный гофрокартон T23, самосборная, 10 шт. Идеально для доставки габаритных товаров.", "price": 57.72, "weight": 500, "length": 59, "width": 19.5, "height": 12},
    {"name": "Короба 785×235×215", "desc": "Крупная коробка 785×235×215 мм для больших грузов. Трёхслойный картон T23, самосборная, упаковка 10 шт. Надёжная защита для крупногабаритных товаров.", "price": 42.87, "weight": 600, "length": 78.5, "width": 23.5, "height": 21.5},
    {"name": "Ведро пластиковое пищевое 20 л с крышкой", "desc": "🪣 Универсальное пищевое ведро 20 л — идеально для хранения продуктов, заготовок, воды. Толстый пластик (1 кг), герметичная крышка, удобная ручка. Б/у из-под сиропа, состояние идеальное: без сколов, трещин и запаха. Сертифицированный пищевой пластик. Не трескается на морозе.", "price": 300.0, "weight": 1100, "length": 35, "width": 35, "height": 40},
    {"name": "Набор эфирных масел PARLAB, 5 шт", "desc": "🌿 Натуральный набор 100% эфирных масел (чайное дерево, апельсин, мята, лаванда, иланг-иланг). В подарочной упаковке, объём 50 мл. Помогает снять стресс, улучшить сон, поднять настроение. Идеальный подарок для женщин и мужчин.", "price": 696.0, "weight": 400, "length": 20, "width": 15, "height": 5},
    {"name": "Прокладки для собак PitoMir, 30 шт", "desc": "🐾 Гипоаллергенные впитывающие прокладки для собак и кошек 30 шт. Дышащий материал, суперабсорбент, липкий слой для фиксации. Индивидуальная упаковка каждой прокладки. Идеальны для щенков, пожилых животных, в дорогу или для дома. Безопасно и гигиенично.", "price": 432.0, "weight": 600, "length": 30, "width": 20, "height": 10},
    {"name": "Садовая дорожка модульная GUSEV GARDEN, 27 шт", "desc": "🌱 Садовая модульная дорожка 27 модулей (2.43 м²). Прочный пластик, устойчивый к погоде и нагрузкам. Легко собирается без инструментов. Подходит для садовых дорожек, террас, балконов, детских площадок. Не гниёт, не выцветает, скрывает неровности земли. Антивандальное покрытие.", "price": 2676.0, "weight": 5700, "length": 32, "width": 31, "height": 26},
    {"name": "Садовая дорожка модульная GUSEV GARDEN, 9 шт", "desc": "🌱 Садовая модульная дорожка 9 модулей (0.81 м²). Компактный вариант для небольших участков, между грядками, у входа в теплицу. Те же преимущества: прочный пластик, устойчивость к погоде, лёгкий монтаж.", "price": 1177.0, "weight": 2000, "length": 32, "width": 32, "height": 9},
    {"name": "Скобы садовые с фиксаторами GUSEV GARDEN, 100 шт", "desc": "🧷 Надёжные садовые скобы из оцинкованной стали с пластиковыми фиксаторами, 100 шт. Заострённые концы легко входят в грунт, надёжно фиксируют агроткань, геотекстиль, спанбонд. Не ржавеют, долговечные. Идеально для грядок, теплиц, клумб.", "price": 670.0, "weight": 1820, "length": 23, "width": 18, "height": 10},
    {"name": "Заборчик садовый раздвижной декоративный GUSEV GARDEN", "desc": "🌳 Декоративный раздвижной заборчик из WPC (древесно-пластиковый композит). Высота 40 см, длина 90 см (раздвижной), колышки в комплекте. Лёгкий, прочный, не боится влаги и солнца. Ограждает клумбы, грядки, деревья. Красиво и функционально.", "price": 923.0, "weight": 400, "length": 45, "width": 23, "height": 3},
    {"name": "Печь походная отопительная для палатки и бани", "desc": "🔥 Дровяная печь из стали Aisi 439, компактная, с дымоходом, каменкой, быстросъёмными ножками. Идеальна для палаток, бань, зимней рыбалки, походов. Кирпичный стиль — долго сохраняет тепло. Можно готовить пищу. Сделано в России. Надёжная и мощная.", "price": 18000.0, "weight": 23000, "length": 67, "width": 30, "height": 45}
]

PRODUCTS_LIST = "\n".join([f"- {p['name']}: {p['price']:.2f} ₽, вес ~{p['weight']}г, {p['desc']}" for p in PRODUCTS])

SYSTEM_PROMPT = (
    "Ты — продавец-консультант интернет-магазина EVA.store.\n"
    "Ты помогаешь клиентам с выбором и оформлением заказов.\n\n"
    "АССОРТИМЕНТ (цены, вес, описание):\n"
    f"{PRODUCTS_LIST}\n\n"
    "АЛГОРИТМ РАБОТЫ:\n"
    "- Если клиент хочет купить — узнай его город.\n"
    "- Когда клиент назвал город — рассчитай доставку и покажи итог (товар + доставка).\n"
    "- Затем спроси номер телефона.\n"
    "- Когда клиент дал телефон — сообщи, что заявка передана менеджеру.\n"
    "- Отвечай кратко, дружелюбно, используй техники продаж.\n"
    "- Если клиент не назвал город, а спросил про доставку — сначала узнай город."
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

def calculate_delivery(city_name: str, product: dict) -> dict:
    """
    Рассчитывает доставку с использованием габаритов и нескольких тарифов.
    Возвращает словарь с минимальной ценой и сроками.
    """
    city_code = get_city_code(city_name)
    if not city_code:
        return {"error": "Не удалось определить город"}

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
                continue
        except Exception as e:
            print(f"⚠️ Ошибка при тарифе {tariff}: {e}")
            continue

    if best_price is not None:
        return {
            "price": best_price,
            "days_min": best_days["min"],
            "days_max": best_days["max"]
        }
    else:
        return {"error": "Не удалось рассчитать доставку"}

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
        response = requests.post(url, headers=headers, json=data, timeout=60)
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            history.append({"role": "assistant", "content": answer})
            return answer, history
        else:
            return "❌ Ошибка AITunnel. Попробуйте позже.", history
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:100]}", history

def main():
    print("🔄 Подключаюсь к VK...")
    vk_session = VkApi(token=VK_TOKEN)
    longpoll = VkLongPoll(vk_session, wait=90)
    vk = vk_session.get_api()
    print("✅ Бот запущен (с СДЭК и габаритами)")

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

            city_found = extract_city(text)
            phone_found = extract_phone(text)

            if city_found:
                product = None
                for p in PRODUCTS:
                    if p["name"].lower() in text.lower() or any(w in text.lower() for w in ["ведр", "короб"]):
                        product = p
                        break
                if not product:
                    product = PRODUCTS[0]

                result = calculate_delivery(city_found, product)
                if "error" in result:
                    delivery_text = f"❌ {result['error']}"
                    total = None
                else:
                    total = product["price"] + result["price"]
                    delivery_text = (
                        f"🚚 Доставка: {result['price']} ₽ ({result['days_min']}-{result['days_max']} дн.)\n"
                        f"💰 Итого: {total} ₽"
                    )
                if uid not in order_data:
                    order_data[uid] = {}
                order_data[uid]["city"] = city_found
                order_data[uid]["product"] = product
                order_data[uid]["delivery"] = result
                order_data[uid]["total"] = total

                answer = (
                    f"📦 {product['name']} — {product['price']} ₽\n"
                    f"{delivery_text}\n\n"
                    f"Для оформления заказа нужен ваш номер телефона. Напишите его, пожалуйста."
                )
                vk.messages.send(user_id=uid, message=answer, random_id=0)
                if uid not in dialogs:
                    dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                dialogs[uid].append({"role": "assistant", "content": answer})
                continue

            if phone_found and uid in order_data and order_data[uid].get("city"):
                city = order_data[uid]["city"]
                product = order_data[uid]["product"]
                total = order_data[uid].get("total")
                delivery = order_data[uid].get("delivery")
                delivery_info = ""
                if delivery and "error" not in delivery and total is not None:
                    delivery_info = f"Доставка: {delivery['price']} ₽, итого: {total} ₽"
                else:
                    delivery_info = "Доставка будет рассчитана менеджером"

                for manager_id in MANAGER_IDS:
                    try:
                        vk.messages.send(
                            user_id=manager_id,
                            message=(
                                f"🛒 ЗАЯВКА от {user_name}!\n"
                                f"Товар: {product['name']}\n"
                                f"Город: {city}\n"
                                f"Телефон: {phone_found}\n"
                                f"{delivery_info}"
                            ),
                            random_id=0
                        )
                    except:
                        pass
                answer = "✅ Заявка оформлена! Менеджер свяжется с вами по указанному телефону. Спасибо! 😊"
                vk.messages.send(user_id=uid, message=answer, random_id=0)
                if uid not in dialogs:
                    dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]
                dialogs[uid].append({"role": "assistant", "content": answer})
                del order_data[uid]
                continue

            if uid not in dialogs:
                dialogs[uid] = [{"role": "system", "content": SYSTEM_PROMPT}]

            answer, new_history = ask_aitunnel(text, dialogs[uid])
            dialogs[uid] = new_history
            vk.messages.send(user_id=uid, message=answer, random_id=0)

if __name__ == "__main__":
    main()
