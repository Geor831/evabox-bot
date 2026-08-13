import time
import requests
import re
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

# ===== НАСТРОЙКИ =====
VK_TOKEN = "vk1.a.gB_E6NmXBEv0nRT58o_22HRpW5hhLvc7TC22VbE1M8KBZPgW7beJfO-DmSqnCNGIdVvQu17WHPKa5teVbQq3z93d-pneW6XkAmMdpNowUViS0P0enWa16qKXfA4HRRCvG74_OriEOAF6mtQeddpjDzDoooIAGWBxu84c-1Aj7wE9sGoOrOdVSS5NvnDSjfc0-QunLDoQdSsSgDFQxkIWgg"
MANAGER_IDS = [29279564, 598512076]
AITUNNEL_API_KEY = "sk-aitunnel-EJz97YJpiOwnaObmGNjf6mU8cT2OdP8L"
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

PRODUCTS_LIST = "\n".join([f"- {p['name']}: {p['price']:.2f} ₽, вес ~{p['weight']}г, {p['desc']}" for p in PRODUCTS])

SYSTEM_PROMPT = (
    "Ты — продавец-консультант интернет-магазина EVA.store.\n"
    "Ты помогаешь клиентам с выбором и оформлением заказов.\n\n"
    "АССОРТИМЕНТ (цены, вес, описание):\n"
    f"{PRODUCTS_LIST}\n\n"
    "АЛГОРИТМ РАБОТЫ:\n"
    "- Если клиент хочет купить — узнай его город.\n"
    "- Когда клиент назвал город — спроси номер телефона.\n"
    "- Когда клиент дал телефон — сообщи, что заявка передана менеджеру.\n"
    "- Отвечай кратко, дружелюбно, используй техники продаж.\n"
    "- Если клиент спрашивает о товаре — дай информацию из списка выше."
)

CITY_CODES = {
    "москва": 44,
    "владимир": 1177,
    "санкт-петербург": 2,
    "питер": 2,
    "новосибирск": 137,
    "екатеринбург": 270,
}

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
    print("✅ Бот запущен (старый токен, без СДЭК)")

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
                if uid not in order_data:
                    order_data[uid] = {}
                order_data[uid]["city"] = city_found

            if phone_found:
                if uid not in order_data:
                    order_data[uid] = {}
                order_data[uid]["phone"] = phone_found

            if uid in order_data and order_data[uid].get("city") and order_data[uid].get("phone"):
                city = order_data[uid]["city"]
                phone = order_data[uid]["phone"]
                product_name = "не указан"
                for p in PRODUCTS:
                    if p["name"].lower() in text.lower():
                        product_name = p["name"]
                        break
                for manager_id in MANAGER_IDS:
                    try:
                        vk.messages.send(
                            user_id=manager_id,
                            message=(
                                f"🛒 ЗАЯВКА от {user_name}!\n"
                                f"Товар: {product_name}\n"
                                f"Город: {city}\n"
                                f"Телефон: {phone}"
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
