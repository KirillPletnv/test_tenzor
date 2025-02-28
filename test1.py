import requests
import datetime
import time

def raw_data():
    url = "https://yandex.com/time/sync.json?geo=213"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Ошибка при запросе к ресурсу: {response.status_code}")

def print_data(data):
    print("Данные ответа:")
    print(data)

def show_times(data):
    timestamp = data['time'] / 1000
    time_zone = data['clocks']['213']['name']
    offset = datetime.timezone(datetime.timedelta(hours=raw_data()['clocks']['213']['offset'] / 3600000))
    human_readable_time = datetime.datetime.fromtimestamp(timestamp, tz=offset).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Человекочитаемое время: {human_readable_time}")
    print(f"Временная зона: {time_zone}")

def time_delta(start_time, data):
    server_time = data['time'] / 1000  # Конвертируем миллисекунды в секунды
    delta = server_time - start_time
    return delta

def main():
    delts = []
    for _ in range(5):
        start_time = time.time()
        data = raw_data()
        delta = time_delta(start_time, data)
        delts.append(delta)
        print_data(data)
        show_times(data)
        print(f"Разница/дельта времени: {delta} секунд\n")
        time.sleep(1)

    avg_delta = sum(delts) / len(delts)
    print(f"Средняя разница/дельта времени: {avg_delta} секунд")

if __name__ == "__main__":
    main()