from machine import I2C, Pin, Timer
import ssd1306

# 定义配置常量和初始化I2C及OLED
INA226_ADDRESS = 0x40
CONFIG_REG = bytearray([0x00, 0x7F, 0xFF])

# INA226 I2C引脚
ina226_scl_pin = Pin(9)  # 根据实际连接的SCL引脚选择
ina226_sda_pin = Pin(8)  # 根据实际连接的SDA引脚选择
i2c_ina226 = I2C(0, scl=ina226_scl_pin, sda=ina226_sda_pin, freq=400000)

# OLED I2C引脚
oled_scl_pin = Pin(7)  # 根据实际连接的SCL引脚选择
oled_sda_pin = Pin(6)  # 根据实际连接的SDA引脚选择
i2c_oled = I2C(1, scl=oled_scl_pin, sda=oled_sda_pin, freq=400000)

# OLED初始化
oled = ssd1306.SSD1306_I2C(128, 64, i2c_oled)

# INA226配置
i2c_ina226.writeto_mem(INA226_ADDRESS, 0x00, CONFIG_REG)

# 滑动平均权重
EXP_WEIGHT = 0.3
filtered_current_avg = None
filtered_voltage_avg = None

def read_sensor_data(retries=3):
    """尝试读取电流和电压数据，失败后重试."""
    for attempt in range(retries):
        try:
            current_raw = i2c_ina226.readfrom_mem(INA226_ADDRESS, 0x01, 2)
            voltage_raw = i2c_ina226.readfrom_mem(INA226_ADDRESS, 0x02, 2)
            current = (current_raw[0] << 8 | current_raw[1]) / 1000
            voltage = (voltage_raw[0] << 8 | voltage_raw[1]) * 1.25 / 1000
            return current, voltage
        except OSError as e:
            if attempt < retries - 1:  # 如果不是最后一次尝试，继续尝试
                continue
            else:
                print(f"Failed to read from INA226 after {retries} attempts: {e}")
                raise

def update_display(current, voltage, power):
    """更新OLED显示屏的内容."""
    oled.fill(0)
    oled.text(f"C: {current:.2f} mA", 0, 32)
    oled.text(f"V: {voltage:.2f} V", 0, 16)
    oled.text(f"P: {power:.2f} mW", 0, 48)
    oled.show()

def timer_callback(timer):
    global filtered_current_avg, filtered_voltage_avg
    try:
        current, voltage = read_sensor_data()
        # 计算指数滑动平均
        filtered_current_avg = EXP_WEIGHT * current if filtered_current_avg is None else EXP_WEIGHT * filtered_current_avg + (1 - EXP_WEIGHT) * current
        filtered_voltage_avg = EXP_WEIGHT * voltage if filtered_voltage_avg is None else EXP_WEIGHT * filtered_voltage_avg + (1 - EXP_WEIGHT) * voltage
        
        power = filtered_current_avg * filtered_voltage_avg * 1000
        update_display(filtered_current_avg, filtered_voltage_avg, power)
    except Exception as e:
        print(f"Error fetching INA226 data: {e}")
# 启动定时器
timer = Timer(-1)
timer.init(period=50, mode=Timer.PERIODIC, callback=timer_callback)

# 主循环
while True:
    pass

