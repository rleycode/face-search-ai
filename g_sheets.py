import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

class GoogleLogger:
    def __init__(self, key_file: str, sheet_name: str):

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(key_file, scope)
            self.client = gspread.authorize(creds)

            self.sheet = self.client.open(sheet_name).sheet1
            print("✅ Подключение к Google Таблице успешно!")
        except Exception as e:
            print(f"❌ Ошибка Google: {e}")
            self.sheet = None

    def log_new_face(self, face_id: int, status: str = "Success"):
        if not self.sheet:
            return
        

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        

        row = [timestamp, str(face_id), status]

        try:
            self.sheet.append_row(row)
            print(f"📝 Лог записан в таблицу: {row}")
        except Exception as e:
            print(f"❌ Не удалось записать лог: {e}")


if __name__ == "__main__":

    logger = GoogleLogger("google_creds.json", "face") 
    logger.log_new_face(123456789)