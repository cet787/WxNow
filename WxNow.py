import requests
import threading

import json
import time
import serial
import serial.tools.list_ports


class Timer:

    def __init__(self, interval, callback=None):
        self.interval = interval
        self.callback = callback
        self._timer = None

    def start(self):
        if self._timer is not None:
            print(f'{self} timer is already started.')
            return
        self._timer = threading.Timer(self.interval, self._repeat)
        self._timer.start()

    def  _repeat(self):
        if self._timer is None:
            print(f'{self} timer not running')
            return
        self.callback()
        self._timer = threading.Timer(self.interval, self._repeat)
        self._timer.start()

    def stop(self):
        if self._timer is None:
            print(f'{self} timer not running')
            return
        self._timer.cancel()
        self._timer = None

class SerialDataManager:

    def __init__(self, city = 'fishers'):
        self.API_KEY = 'a48bfb300cb34ffeb4f132226251203'
        self.BASE_URL = 'http://api.weatherapi.com/v1/current.json'
        self.LOCATION = None
        self._weather = {}
        if city is None:
            self.get_location()
        else:
            self.LOCATION = city
        self.ser_text = '?|?|?|?|?|?|?'

    def update_weather(self):
        params = {
            'key': self.API_KEY,
            'q': self.LOCATION,
            'aqi': 'no'
        }

        response = requests.get(self.BASE_URL, params=params)

        if response.status_code == 200:
            self._weather = response.json()

        else:
            print(f'Error: Failed to load up to date weather, code: {response.status_code}')

    def print_weather_data(self):
        self._weather = self.get_weather(self.LOCATION)
        print(json.dumps(self._weather, indent=4))

    def get_str_temperature(self) -> str:
        if self._weather is not None:
            return self._weather['current']['temp_f']
        else:
            print('Error: No weather loaded, it is recommended that at least one update be called prior to called this method.')
            return '?'

    def get_str_condition_code(self) -> str:
        if self._weather is not None:
            return self._weather['current']['condition']['code']
        else:
            print('Error: No weather loaded, it is recommended that at least one update be called prior to called this method.')
            return '?'

    def get_str_condition_text(self) -> str:
        if self._weather is not None:
            return self._weather['current']['condition']['text']
        else:
            print('Error: No weather loaded, it is recommended that at least one update be called prior to called this method.')
            return '?'

    def get_str_wind_speed(self) -> str:
        if self._weather is not None:
            return self._weather['current']['wind_mph']
        else:
            print('Error: No weather loaded, it is recommended that at least one update be called prior to called this method.')
            return '?'

    def get_str_wind_dir(self) -> str:
        if self._weather is not None:
            return self._weather['current']['wind_dir']
        else:
            print('Error: No weather loaded, it is recommended that at least one update be called prior to called this method.')
            return '?'

    def get_str_wind_degree(self):
        if self._weather is not None:
            return self._weather['current']['wind_degree']
        else:
            print('Error: No weather loaded, it is recommended that at least one update be called prior to called this method.')
            return '?'

    def get_str_feelslike(self) -> str:
        if self._weather is not None:
            return self._weather['current']['feelslike_f']
        else:
            print('Error: No weather loaded, it is recommended that at least one update be called prior to called this method.')
            return '?'

    def get_weather(self, city=None) -> dict | None:
        params = {
            "key": self.API_KEY,
            "q": city,
            "aqi": 'no'
        }

        response = requests.get(self.BASE_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f'Error: {response.status_code}, {response.text}')
            return None

    @staticmethod
    def get_public_ip():
        public_ip = requests.get("https://api64.ipify.org?format=text").text
        return public_ip

    def get_location(self):
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        self.LOCATION = data['loc']
        print(self.LOCATION)

    def get_str_time(self) -> str:
        lt = time.localtime(time.time())
        day = '?'
        match lt.tm_wday:
            case 0:
                day = 'MON'
            case 1:
                day = 'TUE'
            case 2:
                day = 'WED'
            case 3:
                day = 'THU'
            case 4:
                day = 'FRI'
            case 5:
                day = 'SAT'
            case 6:
                day = 'SUN'

        hour = str(lt.tm_hour).rjust(2, '0')
        minute = str(lt.tm_min).rjust(2, '0')
        return f'{day}{hour}{minute}'

    @staticmethod
    def get_str_month_date() -> str:
        lt = time.localtime(time.time())
        month = '?'
        match lt.tm_mon:
            case 1:
                month = 'JAN'
            case 2:
                month = 'FEB'
            case 3:
                month = 'MAR'
            case 4:
                month = 'APR'
            case 5:
                month = 'MAY'
            case 6:
                month = 'JUN'
            case 7:
                month = 'JUL'
            case 8:
                month = 'AUG'
            case 9:
                month = 'SEP'
            case 10:
                month = 'OCT'
            case 11:
                month = 'NOV'
            case 12:
                month = 'DEC'

        date = lt.tm_mday
        return f'{month}{date}'

    def update_ser_text(self, weather_data=False):
        # Send str format v1.0
        # time|Month|Condition Code|temp|feelslike|wind|wind dir

        if weather_data:
            self.update_weather()

        time_str = self.get_str_time()
        date_str = self.get_str_month_date()
        condition_code_str = self.get_str_condition_code()
        temp_str = self.get_str_temperature()
        feelslike_str = self.get_str_feelslike()
        wind_speed_str = self.get_str_wind_speed()
        wind_dir_str = self.get_str_wind_dir()

        self.ser_text =  f'{time_str}|{date_str}|{condition_code_str}|{temp_str}|{feelslike_str}|{wind_speed_str}|{wind_dir_str}'

    def send_ser_text(self, ser):
        ser.write(self.ser_text.encode('utf-8'))

    def run(self):
        ports = {i: port.device for i, port in enumerate(list(serial.tools.list_ports.comports()))}
        for i, port in ports.items():
            print(f'{i}: {port}')
        print()
        port_index = input('Type number corresponding to the correct serial port, i.e. \'0\':')

        ser = None
        if port_index != 'None':
            try:
                port_index = int(port_index)
                port = ports[port_index]
                ser = serial.Serial(port, 115200)

            except ValueError:
                print(f'Error: {port_index} is not a valid port to open a serial connection.')

            except IndexError:
                print(f'Error: {port_index} is out of range max port, port must be 0 - {len(ports) - 1}')

            except Exception as e:
                print(f'Error: serial failed to initialize.')

        time_updates = Timer(15, self.update_ser_text)
        weather_updates = Timer(60, lambda: self.update_ser_text(weather_data=True))
        if ser is not None:
            ser_updates = Timer(5, lambda: self.send_ser_text(ser))
            ser_updates.start()

        self.update_weather()

        time_updates.start()
        weather_updates.start()

        last_ser_text = self.ser_text

        while True:
            if self.ser_text == last_ser_text:
                continue

            print(self.ser_text)
            last_ser_text = self.ser_text



SDM = SerialDataManager()
SDM.update_weather()
SDM.run()


