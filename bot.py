import time
import requests
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

VK_TOKEN = "vk1.a.gB_E6NmXBEv0nRT58o_22HRpW5hhLvc7TC22VbE1M8KBZPgW7beJfO-DmSqnCNGIdVvQu17WHPKa5teVbQq3z93d-pneW6XkAmMdpNowUViS0P0enWa16qKXfA4HRRCvG74_OriEOAF6mtQeddpjDzDoooIAGWBxu84c-1Aj7wE9sGoOrOdVSS5NvnDSjfc0-QunLDoQdSsSgDFQxkIWgg"
AITUNNEL_API_KEY = "sk-aitunnel-EJz97YJpiOwnaObmGNjf6mU8cT2OdP8L"

def ask_aitunnel(user_msg, history=None):
    if history is None:
        history = [{"role": "system", "content": "Ты — ИИ-ассистент EVA.store. Отвечай кратко, дружелюбно."}]
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
        "max_tokens": 300
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            history.append({"role": "assistant", "content": answer})
            return answer, history
        else:
            return "❌ Ошибка AITunnel", history
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:100]}", history

def main():
    print("🔄 Подключаюсь к VK...")
    vk_session = VkApi(token=VK_TOKEN)
    longpoll = VkLongPoll(vk_session, wait=25)
    vk = vk_session.get_api()
    print("✅ Бот запущен (диагностическая версия)")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            uid = event.user_id
            text = event.text.strip()
            if not text:
                continue
            # Просто отправляем запрос в AITunnel и отвечаем
            answer, _ = ask_aitunnel(text, None)
            vk.messages.send(user_id=uid, message=answer, random_id=0)

if __name__ == "__main__":
    main()
