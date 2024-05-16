from machine import Pin, PWM, I2C, ADC
import ssd1306
import utime as time

class HardwareController:
    def __init__(self, i2c_scl_pin, i2c_sda_pin, pwm_pin, adc_pin):
        try:
            # 初始化I2C用于SSD1306 OLED
            self.i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
            self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c)

            # 设置PWM
            self.pwm_led = PWM(Pin(0))  
            self.pwm_led.freq(25000)  

            # 初始化ADC
            self.adc = ADC(Pin(26))  
        except Exception as e:
            print(f"Hardware initialization failed: {e}")

    def display_pwm_wave(self, duty_cycle):
        try:
            self.oled.fill(0)
            width = self.oled.width
            progress_width = int(width * (duty_cycle / 100))
            progress_height = 40

            for y in range(self.oled.height - progress_height, self.oled.height):
                for x in range(progress_width):
                    self.oled.pixel(x, y, 1)

            self.oled.text('POWER', 20, 0)
            self.oled.text(f'{duty_cycle}%', 80, 0)
            self.oled.show()
        except Exception as e:
            print(f"Display update failed: {e}")

    def adjust_pwm_duty(self):
        try:
            adc_value = self.adc.read_u16()
            # 将ADC值映射到10%到100%的占空比范围内，考虑了ADC满量程可能不为65535的情况
            duty_cycle = int((adc_value / 65535) * 90 + 10)
            self.pwm_led.duty_u16(int((adc_value / 65535) * 65535))
            self.display_pwm_wave(duty_cycle)
        except Exception as e:
            print(f"PWM adjustment failed: {e}")

if __name__ == "__main__":
   fancontroller = HardwareController(15, 14, 0, 26)
    
while True:
        fancontroller.adjust_pwm_duty()
        time.sleep(0.1) # 降低CPU占用率             