weather_conditions_localization = {
    "Sunny": "Солнечно",
    "Clear": "Ясно",
    "Cloudy": "Облачно",
    "Overcast": "Пасмурно",
    "Mist": "Туман",
    "Patchy rain nearby": "Возможен небольшой дождь",
    "Patchy rain": "Небольшой дождь",
    "Patchy snow nearby": "Возможен небольшой снег",
    "Patchy snow": "Небольшой снег",
    "Patchy sleet nearby": "Возможен дождь со снегом",
    "Partly Cloudy": "Переменная облачность",
    "Patchy freezing drizzle possible": "Возможен изморозь",
    "Thundery outbreaks possible": "Возможны грозы",
    "Blowing snow": "Снегопад",
    "Blizzard": "Метель",
    "Fog": "Туман",
    "Freezing fog": "Ледяной туман",
    "Patchy light drizzle": "Легкий моросящий дождь",
    "Moderate rain": "Умеренный дождь",
    "Light rain": "Небольшой дождь",
    "Heavy rain": "Ливень",

    # Добавьте другие погодные условия по необходимости
}

def localize_weather_condition(condition):
    return weather_conditions_localization.get(condition, condition)