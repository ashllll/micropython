from machine import Pin, I2C,freq
import ssd1306
import time

machine.freq(270000000)


# 初始化I2C
i2c_sht = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
i2c_ssd = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)

# SHT40的I2C地址（需要根据数据手册确认）
SHT40_ADDR = 0x44  # 假设地址与SHT3x相同

def read_sht40(i2c):
    # 发送测量命令（根据SHT40的数据手册更新）
    i2c.writeto(SHT40_ADDR, bytearray([0xFD]))  # 假设0xFD是高重复性测量命令
    time.sleep(1)  # 根据SHT40手册调整等待时间
    data = i2c.readfrom(SHT40_ADDR, 6)  # 读取温湿度数据

    # 解析温度和湿度（假设数据格式与SHT3x相同）
    temp_raw = data[0] << 8 | data[1]
    temperature = -45 + (175 * temp_raw / 65535.0)
    hum_raw = data[3] << 8 | data[4]
    humidity = 100 * (hum_raw / 65535.0)

    return temperature, humidity

# 初始化SSD1306
oled = ssd1306.SSD1306_I2C(128, 64, i2c_ssd)

while True:
    temperature, humidity = read_sht40(i2c_sht)
    oled.fill(0)
    oled.text("Temp: {:.2f} C".format(temperature), 0, 0)
    oled.text("Humidity: {:.2f}%".format(humidity), 0, 10)
    oled.show()
    time.sleep(2)