import machine
import network
import socket
import ssd1306
import time
import _thread
from machine import Pin, I2C

# 将配置信息放在一个文件中，这里直接定义为变量，实际使用时应从文件中读取
SSID = 'YOUR_WIFI_SSID'
PASSWORD = 'YOUR_WIFI_PASSWORD'
I2C_CONFIG = {
    "scl": Pin(9),
    "sda": Pin(8),
    "freq": 400000
}

# 连接到Wi-Fi的函数
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print('WiFi Connected. IP:', wlan.ifconfig()[0])

# I2C配置和设备初始化
def init_i2c():
    i2c = I2C(0, **I2C_CONFIG)
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)  # 假设OLED和SHT40共用一个I2C
    return oled

# 读取SHT40数据的函数（假设）
def read_sht40():
    # 发送测量命令、读取数据、解析数据
    # 返回模拟的温湿度值
    return 25.0, 50.0  # 模拟温度和湿度值

# 历史数据存储
BUFFER_SIZE = 20
temp_history = [0] * BUFFER_SIZE
hum_history = [0] * BUFFER_SIZE

# Web页面生成
def web_page(temp_history, hum_history):
    data_points = '<ul>'
    for i in range(BUFFER_SIZE):
        data_points += f'<li>Temperature: {temp_history[i]:.2f} C, Humidity: {hum_history[i]:.2f}%</li>'
    data_points += '</ul>'
    return """<!DOCTYPE html><html>
<head><title>Pico W Temp and Humidity</title></head>
<body><h1>Temperature and Humidity Data</h1>{}</body></html>""".format(data_points)

# Web服务器线程函数
def start_web_server(oled, temp_history, hum_history):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        request = conn.recv(1024)
        response = web_page(temp_history, hum_history)
        conn.send('HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\nContent-Length: {}\n\n'.format(len(response)))
        conn.sendall(response)
        conn.close()

# 主循环函数
def main_loop(oled):
    while True:
        try:
            temperature, humidity = read_sht40()
        except Exception as e:
            print("Error reading SHT40: ", e)
            continue  # 如果读取失败，则尝试下一次读取

        try:
            update_history(temperature, humidity)
            oled.fill(0)
            oled.text(f"Temp: {temperature:.2f} C", 0, 0)
            oled.text(f"Hum: {humidity:.2f}%", 0, 10)
            oled.show()
        except Exception as e:
            print("Error updating OLED: ", e)

        time.sleep(2)

# 更新历史数据的线程安全函数
def update_history(temperature, humidity):
    global temp_history, hum_history, history_index
    with lock:
        temp_history[history_index] = temperature
        hum_history[history_index] = humidity
        history_index = (history_index + 1) % BUFFER_SIZE

# 锁对象，用于线程安全
lock = _thread.allocate_lock()

# 主程序
def main():
    connect_to_wifi()
    oled = init_i2c()
    _thread.start_new_thread(start_web_server, (oled, temp_history, hum_history))
    main_loop(oled)

if __name__ == "__main__":
    main()