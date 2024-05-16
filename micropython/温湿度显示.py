from machine import Pin, I2C
import ssd1306
import time

# AHT21读取函数
def read_aht21(i2c):
    i2c.writeto(0x38, bytearray([0xAC, 0x33, 0x00]))
    time.sleep(0.1)  # 等待数据准备
    data = i2c.readfrom(0x38, 6)
    humidity = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4)) * 100 / 0x100000
    temperature = (((data[3] & 0xF) << 16) | (data[4] << 8) | data[5]) * 200 / 0x100000 - 50
    return temperature, humidity

# 初始化I2C
i2c_aht = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
i2c_ssd = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)

# 初始化SSD1306
oled = ssd1306.SSD1306_I2C(128, 64, i2c_ssd)

while True:
    temperature, humidity = read_aht21(i2c_aht)
    oled.fill(0)  # 清屏
    oled.text("Temp: {:.2f} C".format(temperature), 0, 0)
    oled.text("Humidity: {:.2f}%".format(humidity), 0, 10)
    oled.show()
    time.sleep(2)
