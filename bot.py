import time
import requests
import re
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

VK_TOKEN = "vk1.a.gB_E6NmXBEv0nRT58o_22HRpW5hhLvc7TC22VbE1M8KBZPgW7beJfO-DmSqnCNGIdVvQu17WHPKa5teVbQq3z93d-pneW6XkAmMdpNowUViS0P0enWa16qKXfA4HRRCvG74_OriEOAF6mtQeddpjDzDoooIAGWBxu84c-1Aj7wE9sGoOrOdVSS5NvnDSjfc0-QunLDoQdSsSgDFQxkIWgg"
MANAGER_VK_ID = 598512076

PRODUCTS = [
    {"name": "Короба 600×400×400", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 70.0},
    {"name": "Короба 600×400×200", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 68.0},
    {"name": "Короба 200×300×300", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 60.0},
    {"name": "Короба 95×95×103", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 22.0},
    {"name": "Короба 50×50×225", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 16.0},
    {"name": "Короба 100×100×290", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 12.09},
    {"name": "Короба 1040×165×45", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 29.04},
    {"name": "Короба 110×110×335", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 20.3},
    {"name": "Короба 165×105×55", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 11.08},
    {"name": "Короба 170×170×80", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 9.96},
    {"name": "Короба 220×130×130*", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 9.99},
    {"name": "Короба 220×130×180", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 11.47},
    {"name": "Короба 240×135×50", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 16.98},
    {"name": "Короба 280×150×350", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 23.41},
    {"name": "Короба 300×200×300", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 23.55},
    {"name": "Короба 380×240×290", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 33.0},
    {"name": "Короба 590×195×120", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 57.72},
    {"name": "Короба 785×235×215", "desc": "Трёхслойный гофрокартон T23, упаковка 10 шт.", "price": 42.87},
]

def normalize(text):
    text = text.lower().strip()
    text = re.sub(r'[xх*]', '×', text)
    text = text.replace(' ', '')
    return text

def search_products(query):
    q = normalize(query)
    results = []
    for p in PRODUCTS:
        name_clean = normalize(p["name"])
        desc_clean = normalize(p["desc"])
        if q in name_clean or q in desc_clean:
            results.append(f"{p['name']} — {p['desc']}\nЦена: {p['price']:.2f} ₽ (в наличии)")
    return results

def main():
    vk_session = VkApi(token=VK_TOKEN)
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()
    print("✅ Бот запущен (полная версия с товарами и нормализацией)")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            uid = event.user_id
            msg = event.text.strip()

            # Проверяем намерение купить
            if any(word in msg.lower() for word in ["покупаю", "заказываю", "беру", "оформляю"]):
                product_found = "неизвестный товар"
                for p in PRODUCTS:
                    if p["name"].lower() in msg.lower():
                        product_found = p["name"]
                        break
                try:
                    vk.messages.send(
                        user_id=MANAGER_VK_ID,
                        message=f"🛒 НОВАЯ ЗАЯВКА!\nТовар: {product_found}\nСообщение: {msg}",
                        random_id=0
                    )
                except:
                    pass
                vk.messages.send(user_id=uid, message="✅ Заявка передана менеджеру, с вами свяжутся!", random_id=0)
                continue

            # Поиск товаров
            found = search_products(msg)
            if found:
                answer = "\n\n".join(found[:5])
                if len(found) > 5:
                    answer += "\n\n🔍 Найдено больше позиций, уточните размер."
            else:
                answer = "🤔 Не нашёл таких коробок. Попробуйте уточнить размер (например, 600×400×400)."
            vk.messages.send(user_id=uid, message=answer, random_id=0)

if __name__ == "__main__":
    main()
