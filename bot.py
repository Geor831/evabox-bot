import time
import requests
import re
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

VK_TOKEN = "vk1.a.vedeEaKBa4UKyV0RYddcBqMts_JJrvNynhr8OPClZfx2l6JQVzrFM2v9fXIm74J0RWykxVmwIMxbrwVuZxnoDYkUh4FE9EVxz4d3btZ51dyjV4nUzHJ9Gph5juclIZaWRfq03hBfqW6L3Our9W_1PwJsp5udn-_nOTM2XV79CO16MWqPwmfKEON4dp3oPnVdz9bBIhEzRIjmlAEFLfDeNQ"
MANAGER_IDS = [29279564, 598512076]
AITUNNEL_API_KEY = "sk-aitunnel-EJz97YJpiOwnaObmGNjf6mU8cT2OdP8L"

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
    {"name": "Ведро пластиковое пищевое 20 л с крышкой", "desc": "🪣 Универсальное пищевое ведро 20 л — идеально для хранения продуктов, заготовок, воды. Толстый пластик, герметичная крышка, удобная ручка. Б/у из-под сиропа, состояние идеальное.", "price": 300.0}
]

def ask_aitunnel(user_msg, history=None):
    if history is None:
        history = [{"role": "system", "content": "Ты — продавец-консультант интернет-магазина EVA.store. Отвечай кратко, дружелюбно, по делу."}]
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
    print("✅ Бот запущен (стабильная версия без СДЭК)")

    dialogs = {}

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            uid = event.user_id
            text = event.text.strip()
            if not text:
                continue

            # Определяем товар
            product = None
            for p in PRODUCTS:
                if p["name"].lower() in text.lower():
                    product = p
                    break
            if not product:
                product = PRODUCTS[-1]  # по умолчанию ведро

            # Если есть намёк на покупку
            if any(w in text.lower() for w in ["купить", "заказать", "беру", "покупаю", "хочу"]):
                # Спрашиваем город
                answer = f"Отлично! Для расчёта доставки скажите, из какого вы города?"
                vk.messages.send(user_id=uid, message=answer, random_id=0)
                if uid not in dialogs:
                    dialogs[uid] = [{"role": "system", "content": "Ты — продавец-консультант EVA.store."}]
                dialogs[uid].append({"role": "assistant", "content": answer})
                continue

            # Проверяем, есть ли город в тексте
            city_found = None
            cities = ["москва", "владимир", "санкт-петербург", "питер", "новосибирск", "екатеринбург"]
            for city in cities:
                if city in text.lower():
                    city_found = city
                    break

            if city_found:
                # Ищем телефон в тексте
                phone_match = re.search(r'\+?\d[\d\s\-\(\)]{7,}\d', text)
                if phone_match:
                    phone = phone_match.group().strip()
                    # Отправляем заявку менеджерам
                    for manager_id in MANAGER_IDS:
                        try:
                            vk.messages.send(
                                user_id=manager_id,
                                message=(
                                    f"🛒 ЗАЯВКА!\n"
                                    f"Товар: {product['name']}\n"
                                    f"Город: {city_found}\n"
                                    f"Телефон: {phone}\n"
                                    f"Цена: {product['price']} ₽"
                                ),
                                random_id=0
                            )
                        except:
                            pass
                    answer = "✅ Заявка оформлена! Менеджер свяжется с вами по указанному телефону. Спасибо! 😊"
                    vk.messages.send(user_id=uid, message=answer, random_id=0)
                    if uid not in dialogs:
                        dialogs[uid] = [{"role": "system", "content": "Ты — продавец-консультант EVA.store."}]
                    dialogs[uid].append({"role": "assistant", "content": answer})
                else:
                    # Город есть, но телефона нет — просим телефон
                    answer = f"Отлично! Доставка до {city_found.capitalize()} возможна. Для оформления заказа нужен ваш номер телефона."
                    vk.messages.send(user_id=uid, message=answer, random_id=0)
                    if uid not in dialogs:
                        dialogs[uid] = [{"role": "system", "content": "Ты — продавец-консультант EVA.store."}]
                    dialogs[uid].append({"role": "assistant", "content": answer})
                continue

            # Обычный диалог
            if uid not in dialogs:
                dialogs[uid] = [{"role": "system", "content": "Ты — продавец-консультант EVA.store. Отвечай кратко, дружелюбно, по делу."}]

            answer, new_history = ask_aitunnel(text, dialogs[uid])
            dialogs[uid] = new_history
            vk.messages.send(user_id=uid, message=answer, random_id=0)

if __name__ == "__main__":
    main()
