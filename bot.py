import time
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

VK_TOKEN = "vk1.a.gB_E6NmXBEv0nRT58o_22HRpW5hhLvc7TC22VbE1M8KBZPgW7beJfO-DmSqnCNGIdVvQu17WHPKa5teVbQq3z93d-pneW6XkAmMdpNowUViS0P0enWa16qKXfA4HRRCvG74_OriEOAF6mtQeddpjDzDoooIAGWBxu84c-1Aj7wE9sGoOrOdVSS5NvnDSjfc0-QunLDoQdSsSgDFQxkIWgg"

def main():
    vk_session = VkApi(token=VK_TOKEN)
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()
    print("✅ Бот запущен (тестовая версия)")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            uid = event.user_id
            msg = event.text.strip()
            if msg:
                vk.messages.send(user_id=uid, message="Я работаю! (тест)", random_id=0)

if __name__ == "__main__":
    main()
