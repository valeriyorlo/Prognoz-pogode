import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
import requests


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Прогноз погоды")
        self.setGeometry(100, 100, 300, 200)

        self.city_label = QLabel("Введите название города:")
        self.city_entry = QLineEdit()
        self.get_weather_button = QPushButton("Узнать погоду")
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("font-size: 16px;")

        layout = QVBoxLayout()
        layout.addWidget(self.city_label)
        layout.addWidget(self.city_entry)
        layout.addWidget(self.get_weather_button)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

        self.get_weather_button.clicked.connect(self.get_weather)

    def get_weather(self):
        city = self.city_entry.text()
        api_key = "cecd2221704d21750cce88ce5b93deba"
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = base_url + "q=" + city + "&appid=" + api_key + "&units=metric"

        try:
            response = requests.get(complete_url)
            response.raise_for_status()  # Проверяем статус ответа
            data = response.json()

            main_data = data["main"]
            temperature = main_data["temp"]
            humidity = main_data["humidity"]
            weather_desc = data["weather"][0]["description"]

            self.result_label.setText(
                f"Погода в {city}:\nТемпература: {temperature}°C\nВлажность: {humidity}%\nОписание: {weather_desc}")
        except requests.exceptions.HTTPError as e:
            self.result_label.setText(
                "Ошибка при получении данных. Проверьте подключение к интернету и правильность ввода города.")
        except Exception as e:
            self.result_label.setText("Произошла ошибка: " + str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())