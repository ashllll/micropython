from machine import Pin, I2C, freq
import ssd1306
import time

# 设定主频
machine.freq(270000000)

# I2C配置参数
I2C_SHT_CONFIG = {
    "scl": Pin(9),
    "sda": Pin(8),
    "freq": 400000
}
I2C_SSD_CONFIG = {
    "scl": Pin(15),
    "sda": Pin(14),
    "freq": 400000
}

# 创建I2C对象
i2c_sht = I2C(0, **I2C_SHT_CONFIG)
i2c_ssd = I2C(1, **I2C_SSD_CONFIG)

# SHT40的I2C地址和测量命令
SHT40_ADDR = 0x44  
MEASUREMENT_COMMAND = bytearray([0xFD])

# 温湿度数据缓冲区及索引
BUFFER_SIZE = 20
temp_history = [0] * BUFFER_SIZE
hum_history = [0] * BUFFER_SIZE
history_index = 0

def read_sht40(i2c, address=SHT40_ADDR, command=MEASUREMENT_COMMAND):
    try:
        # 发送测量命令
        i2c.writeto(address, command)
        time.sleep(1)  # 等待测量完成

        # 读取数据
        data = i2c.readfrom(address, 6)
        if len(data) != 6:
            raise ValueError("Failed to read data from SHT40")

        # 解析数据
        temp_raw = data[0] << 8 | data[1]
        temperature = -45 + (175 * temp_raw / 65535.0)
        hum_raw = data[3] << 8 | data[4]
        humidity = 100 * (hum_raw / 65535.0)

        return temperature, humidity
    except Exception as e:
        print(f"Error reading from SHT40: {e}")
        return None, None

# 初始化SSD1306
oled = ssd1306.SSD1306_I2C(128, 64, i2c_ssd)

while True:
    temperature, humidity = read_sht40(i2c_sht)
    if temperature is not None and humidity is not None:
        # 更新历史数据
        temp_history[history_index] = temperature
        hum_history[history_index] = humidity
        history_index = (history_index + 1) % BUFFER_SIZE

        oled.fill(0)

        # 显示文字信息
        oled.text(f"Temp: {temperature:.2f} C", 0, 0)
        oled.text(f"Humidity: {humidity:.2f}%", 0, 10)

        # 绘制温度曲线
        y_start = 30
        for i in range(BUFFER_SIZE):
            x = i * 6
            y = int((1 - temp_history[i] / 50) * (64 - y_start)) + y_start
            if i > 0:
                oled.line(x - 6, prev_y, x, y, 1)
            prev_y = y

        # 绘制湿度曲线
        y_start = 50
        for i in range(BUFFER_SIZE):
            x = i * 6
            y = int((1 - hum_history[i] / 100) * (64 - y_start)) + y_start
            if i > 0:
                oled.line(x - 6, prev_y, x, y, 1)
            prev_y = y

        oled.show()

    time.sleep(2)