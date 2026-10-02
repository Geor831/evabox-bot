import time
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

VK_TOKEN = "vk1.a.CZqAdRXB0TDo0FQ6n5_cQnJoCBowsrmDfcp5oblGusc0PUdQYzh08s6cO1BDC6sSVrHyyCy1ChCOIZj-OoHsrJlXlmNC6Ha0ZzhJ0pdRNMZIYcybjkGECKo8sOQkvzhTdfEJYaEMJJqV4Ma_nuNxGAqVcp3sVRhixwUF4Tab6pnyMxT3kIdyOwzfOl3-i2lwlt2EygdPsd_Xkah3p9zEhQ"

def main():
    print("🔄 Подключаюсь...")
    while True:
        try:
            vk_session = VkApi(token=VK_TOKEN)
            longpoll = VkLongPoll(vk_session, wait=200)
            vk = vk_session.get_api()
            print("✅ Бот запущен (минимальная версия)")
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    uid = event.user_id
                    text = event.text.strip()
                    print(f"📩 Получено от {uid}: {text}")
                    vk.messages.send(user_id=uid, message="Привет! Я работаю.", random_id=0)
        except Exception as e:
            print(f"⚠️ Ошибка: {e}. Перезапуск через 10 секунд...")
            time.sleep(10)

if __name__ == "__main__":
    main()
