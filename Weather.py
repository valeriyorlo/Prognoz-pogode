from datetime import datetime
import json
import sys
import requests
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QApplication, QLabel, QLineEdit, QListWidget, QMainWindow,
                             QPushButton, QSpinBox, QWidget, QMessageBox, QVBoxLayout, QScrollArea)

from localization import localize_weather_condition


API_KEY = "19312cbf23144a9cbb9165847241106"


class FavoriteCityItem(QtWidgets.QWidget):
    def __init__(self, city_name, list_widget, main_window, parent=None):
        super().__init__(parent)
        self.list_widget = list_widget
        self.main_window = main_window
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.city_label = QtWidgets.QLabel(city_name)
        self.city_label.setFont(QFont("Verdana", 10))
        self.layout.addWidget(self.city_label)

        self.remove_button = QtWidgets.QPushButton('X', self)
        self.remove_button.setFont(QFont("Verdana", 10, QFont.Bold))
        self.remove_button.setFixedSize(40, 40)
        self.remove_button.setStyleSheet("""
            QPushButton {
                background-color: #d9534f; 
                color: white;
                border: 1px solid #cccccc; 
                border-radius: 4px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #e06b6b;
            }
            QPushButton:pressed {
                background-color: #c9302c;
            }
        """)  # Стиль кнопки удаления
        self.remove_button.clicked.connect(self.remove_city)
        self.layout.addWidget(self.remove_button)

    def remove_city(self):
        item = self.list_widget.takeItem(self.list_widget.row(self.list_widget.currentItem()))
        del item
        self.main_window.save_favorites()

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = "Прогноз погоды"
        self.forecast_data = None
        self.forecast_window = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(640, 500)
        self.setWindowIcon(QIcon('weather.ico'))

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
                padding: 2px;
            }
            QLabel#TitleLabel {
                color: #5c94fc;
                font-size: 24px;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding-left: 8px;
                padding-right: 8px;
                height: 25px;
            }
            QSpinBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding-left: 8px;
                padding-right: 8px;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #5c94fc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 15px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #6ca0ff;
            }
            QPushButton:pressed {
                background-color: #4a82e4;
            }
            QMessageBox {
                background-color: #ffffff;
            }
        """)

        self.favorite_cities_list = QListWidget(self)
        self.favorite_cities_list.setGeometry(50, 350, 540, 80)
        self.favorite_cities_list.setStyleSheet("""
                    QListWidget {
                        border: 1px solid #cccccc;
                        border-radius: 4px;
                    }
                """)

        self.label = QLabel('Добро пожаловать',self)
        self.label.setFont(QFont("Verdana", 16, QFont.Bold))
        self.label.adjustSize()
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.move((self.width() - self.label.width()) // 2, 30)

        self.label2 = QLabel('Прогноз погоды', self)
        self.label2.setObjectName("TitleLabel")
        self.label2.setFont(QFont("Verdana", 18, QFont.Bold))
        self.label2.setFixedWidth(320)
        self.label2.setAlignment(QtCore.Qt.AlignCenter)
        self.label2.move(160, 90)

        self.label3 = QLabel('Название города', self)
        self.label3.setFont(QFont("Verdana", 12))
        self.label3.setFixedWidth(240)
        self.label3.setAlignment(QtCore.Qt.AlignRight)
        self.label3.move(60, 180)

        self.label4 = QLabel('Дней для прогноза', self)
        self.label4.setFont(QFont("Verdana", 12))
        self.label4.setFixedWidth(240)
        self.label4.setAlignment(QtCore.Qt.AlignRight)
        self.label4.move(60, 240)

        self.city_name = QLineEdit(self)
        self.city_name.setFixedSize(165, 40)
        self.city_name.move(320, 180)

        self.num_days = QSpinBox(self)
        self.num_days.setRange(1, 5)
        self.num_days.setStyleSheet('QComboBox {background-color: white;}')
        self.num_days.resize(160, 25)
        self.num_days.move(320, 240)

        self.add_to_favorites_button = QPushButton('+', self)
        self.add_to_favorites_button.setFont(QFont("Verdana", 10, QFont.Bold))
        self.add_to_favorites_button.setFixedSize(40, 40)
        self.add_to_favorites_button.move(self.city_name.x() + self.city_name.width() + 10,
                                          self.city_name.y())
        self.add_to_favorites_button.setStyleSheet(
            "QPushButton {"
            "background-color: #28a745; color: white;"
            "border: 1px solid #cccccc; border-radius: 4px;"
            "padding: 0px;"  
            "}"
            "QPushButton:hover { background-color: #32cd32; }"
            "QPushButton:pressed { background-color: #228b22; }"
        )
        self.add_to_favorites_button.clicked.connect(self.add_to_favorites)

        self.favorite_cities_list = QListWidget(self)
        self.favorite_cities_list.setGeometry(50, 350, 540, 80)
        self.favorite_cities_list.setStyleSheet("""
                            QListWidget {
                                border: 1px solid #cccccc;
                                border-radius: 4px;
                            }
                        """)
        self.favorite_cities_list.itemClicked.connect(self.display_weather_for_selected_city)

        self.button1 = QPushButton('Найти город', self)
        self.button1.setFont(QFont("Verdana", 10, QFont.Bold))
        self.button1.resize(220, 50)
        self.button1.move(50, 280)
        self.button1.clicked.connect(self.get_forecast)

        self.button2 = QPushButton('Показать прогноз', self)
        self.button2.setFont(QFont("Verdana", 10, QFont.Bold))
        self.button2.resize(220, 50)
        self.button2.move(370, 280)
        self.button2.clicked.connect(self.open_forecast)

        self.button3 = QPushButton('Выйти', self)
        self.button3.setFont(QFont("Verdana", 10, QFont.Bold))
        self.button3.resize(220, 50)
        self.button3.setStyleSheet("background-color: #d9534f; color: white;")
        self.button3.move((self.width() - self.button3.width()) // 2, 440)
        self.button3.clicked.connect(QCoreApplication.instance().quit)

        self.load_favorites()
        self.show()

    def add_to_favorites(self):
        city = self.city_name.text().strip()
        if city and city not in self.get_favorite_cities():
            if self.forecast_data and city.lower() == self.forecast_data['location']['name'].lower():

                city_item = FavoriteCityItem(city, self.favorite_cities_list, self)
                city_widget_item = QtWidgets.QListWidgetItem(self.favorite_cities_list)
                city_widget_item.setSizeHint(city_item.sizeHint())
                self.favorite_cities_list.addItem(city_widget_item)
                self.favorite_cities_list.setItemWidget(city_widget_item, city_item)
                self.save_favorites()
            else:
                QMessageBox.warning(self, 'Ошибка',
                                    'Город не найден в API погоды. Проверьте название и попробуйте снова.')

    def save_favorites(self):
        favorites = []
        for index in range(self.favorite_cities_list.count()):
            item = self.favorite_cities_list.item(index)
            widget = self.favorite_cities_list.itemWidget(item)
            favorites.append(widget.city_label.text())
        with open('favorites.json', 'w') as file:
            json.dump(favorites, file)

    def load_favorites(self):
        try:
            with open('favorites.json', 'r') as file:
                favorites = json.load(file)
                for city_name in favorites:

                    city_item = FavoriteCityItem(city_name, self.favorite_cities_list, self)
                    city_widget_item = QtWidgets.QListWidgetItem(self.favorite_cities_list)
                    city_widget_item.setSizeHint(city_item.sizeHint())
                    self.favorite_cities_list.addItem(city_widget_item)
                    self.favorite_cities_list.setItemWidget(city_widget_item, city_item)
        except FileNotFoundError:
            with open('favorites.json', 'w') as file:
                json.dump([], file)
        except json.JSONDecodeError as e:
            print("Ошибка чтения файла избранных: ", e)
            QMessageBox.warning(self, 'Ошибка', 'Не удалось загрузить список избранных городов.')

    def display_weather_for_selected_city(self, item):
        widget = self.favorite_cities_list.itemWidget(item)
        if widget:
            city = widget.city_label.text()
            print(f"Выбранный город: {city}")
            if city:
                self.get_forecast_for_city(city)
            else:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось определить выбранный город.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Не удалось получить виджет для выбранного города.')
    def get_forecast_for_city(self, city):
        url = "http://api.weatherapi.com/v1/forecast.json"
        querystring = {
            "key": API_KEY,
            "q": city.strip(),
            "days": 2,  # Получаем прогноз на сегодня и завтра
            "aqi": "no",
            "alerts": "no",
            "lang": "ru",
        }

        try:
            response = requests.get(url, params=querystring)
            if response.status_code == 200:
                data = response.json()
                if "forecast" in data and len(data["forecast"]["forecastday"]) > 1:
                    tomorrow_forecast = data['forecast']['forecastday'][1]
                    self.show_weather(tomorrow_forecast)
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Прогноз погоды доступен только на сегодняшний день.')
            else:
                error_message = f"Ошибка сервера: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        error_message += f"\nСообщение: {error_data.get('error', {}).get('message', 'Нет деталей')}"
                    except json.JSONDecodeError:
                        error_message += f"\nНевозможно декодировать ответ сервера: {response.text}"
                QMessageBox.warning(self, 'Ошибка', error_message)
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, 'Ошибка', f'Произошла ошибка при запросе к серверу: {e}')
    def show_weather(self, forecast):
        date = forecast['date']
        conditions = forecast['day']['condition']['text']
        min_temp = forecast['day']['mintemp_c']
        max_temp = forecast['day']['maxtemp_c']
        QMessageBox.information(self, 'Прогноз погоды',
                                f"Дата: {date}\n"
                                f"Погода: {conditions}\n"
                                f"Мин. температура: {min_temp} °C\n"
                                f"Макс. температура: {max_temp} °C")
    def get_favorite_cities(self):
        favorites = []
        for index in range(self.favorite_cities_list.count()):
            item = self.favorite_cities_list.item(index)
            widget = self.favorite_cities_list.itemWidget(item)
            favorites.append(widget.city_label.text())
        return favorites

    def get_forecast(self):
        url = "http://api.weatherapi.com/v1/forecast.json"
        city = str(self.city_name.text()).strip()
        days = self.num_days.value()

        if not city:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, введите название города.')
            return

        querystring = {
            "key": API_KEY,
            "q": city,
            "days": days,
            "aqi": "no",
            "alerts": "no",
            "lang": "ru",
        }

        try:
            response = requests.get(url, params=querystring)
            data = response.json()

            if response.status_code == 200 and "location" in data:
                self.forecast_data = data
                QMessageBox.information(self, 'Информация',
                                        f'Прогноз погоды на {days} дней для города {city} успешно получен.')
            else:
                error_message = data.get("error", {}).get("message", "Ошибка получения данных.")
                if error_message == "No matching location found.":
                    error_message = "Указанное местоположение не найдено."
                QMessageBox.warning(self, 'Ошибка', error_message)
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, 'Ошибка', f'Произошла ошибка при запросе к серверу: {e}')

    def open_forecast(self):
        if self.forecast_data and 'forecast' in self.forecast_data and 'forecastday' in self.forecast_data['forecast']:
            self.forecast_window = ForecastWindow()  # Сохраняем ссылку на окно прогноза
            self.forecast_window.show_forecast(self.forecast_data)
            self.forecast_window.show()
        else:
            QMessageBox.information(self, 'Информация',
                                    'Прогноз погоды не найден. Пожалуйста, сначала получите прогноз.')


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()


class ForecastWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Прогноз погоды")
        self.setWindowIcon(QIcon('weather.ico'))
        self.setFixedSize(600, 400)
        self.initUI()

    def initUI(self):
        self.scroll_area = QScrollArea(self)
        self.content_widget = QWidget()
        self.layout = QVBoxLayout(self.content_widget)
        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setWidgetResizable(True)
        self.layout_scroll = QVBoxLayout(self)
        self.layout_scroll.addWidget(self.scroll_area)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

    def show_forecast(self, forecast_data):
        for day in forecast_data['forecast']['forecastday']:
            date = day['date']
            conditions = day['day']['condition']['text']
            localized_conditions = localize_weather_condition(conditions)
            min_temp = day['day']['mintemp_c']
            max_temp = day['day']['maxtemp_c']
            humidity = day['day']['avghumidity']

            try:
                sunrise_time = datetime.strptime(day['astro']['sunrise'], '%I:%M %p').strftime('%H:%M')
                sunset_time = datetime.strptime(day['astro']['sunset'], '%I:%M %p').strftime('%H:%M')
            except ValueError as ve:
                print(f"Ошибка преобразования времени: {ve}")
                sunrise_time = "Недоступно"
                sunset_time = "Недоступно"

            forecast_text = (f"<h3>{date}</h3>"
                             f"<p>Погода: {localized_conditions}</p>"
                             f"<p>Мин. температура: {min_temp} °C</p>"
                             f"<p>Макс. температура: {max_temp} °C</p>"
                             f"<p>Влажность: {humidity}%</p>"
                             f"<p>Восход солнца: {sunrise_time}</p>"
                             f"<p>Закат солнца: {sunset_time}</p>")

            frame = QtWidgets.QFrame(self.content_widget)
            frame_layout = QVBoxLayout(frame)
            frame.setStyleSheet("""
               QFrame {
                   background-color: #ffffff;
                   border-radius: 15px;
                   padding: 20px;
                   margin-bottom: 20px;
                   box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
               }
               QLabel {
                   font-size: 16px;
               }
           """)
            forecast_label = QLabel(forecast_text)
            forecast_label.setWordWrap(True)
            forecast_label.setAlignment(QtCore.Qt.AlignCenter)
            frame_layout.addWidget(forecast_label)
            self.layout.addWidget(frame)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())