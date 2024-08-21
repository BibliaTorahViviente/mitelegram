import os
import requests
from td.client import Client
from td.api import functions, types

class TorahVivienteClient(Client):
    def __init__(self, api_id, api_hash, database_directory):
        super().__init__(api_id, api_hash, database_directory)
        self.authorized = False

    def login(self, phone_number):
        try:
            result = self.send(functions.auth.SendCode(
                phone_number=phone_number,
                settings=types.PhoneNumberSettings(
                    allow_flash_call=False,
                    allow_sms=True,
                    allow_voice_call=True
                )
            ))
            auth_code = input("Please enter the authentication code: ")
            result = self.send(functions.auth.CheckCode(
                phone_number=phone_number,
                code=auth_code
            ))
            if result._ == "auth.authorization":
                self.authorized = True
                print("Authentication successful!")
            else:
                print("Authentication failed!")
        except Exception as e:
            print(f"An error occurred during authentication: {e}")

    def get_torah_reading(self, date):
        try:
            response = requests.get(f"https://api.torahviviente.com/reading?date={date}")
            if response.status_code == 200:
                return response.json().get('reading')
            else:
                return "No Torah reading found for this date."
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching Torah reading: {e}")
            return None

    def send_daily_notification(self, chat_id, date):
        torah_reading = self.get_torah_reading(date)
        if torah_reading:
            message = f"Today's Torah reading:\n{torah_reading}"
            try:
                self.send(functions.messages.SendMessage(
                    chat_id=chat_id,
                    text=message
                ))
                print(f"Message sent to {chat_id}")
            except Exception as e:
                print(f"An error occurred while sending the message: {e}")
        else:
            print("Failed to retrieve Torah reading, message not sent.")

# Función principal para ejecutar el cliente
def main():
    client = TorahVivienteClient(
        api_id=os.getenv("API_ID"),
        api_hash=os.getenv("API_HASH"),
        database_directory="./tdlib_database"
    )
    client.login("+1234567890")
    # Enviar la notificación diaria para la fecha actual
    from datetime import datetime
    today = datetime.today().strftime('%Y-%m-%d')
    client.send_daily_notification(chat_id="@your_torah_viviente_channel", date=today)

if __name__ == "__main__":
    main()
