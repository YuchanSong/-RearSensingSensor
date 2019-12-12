# Rear Sensor
import RPi.GPIO as GPIO #GPIO 사용을 위한 라이브러리 호출
import time #sleep 사용을 위한 리이브러리 호출

# LCD GPIO Define
LCD_RS = 23
LCD_E  = 26 
LCD_D4 = 17
LCD_D5 = 18
LCD_D6 = 27
LCD_D7 = 22

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

trig = 0
echo = 1
buzz = 13 #sound output

# Distance Measure
def get_ultrasonic_distance():
    GPIO.output(trig, False)
    time.sleep(0.1)
 
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)
 
    while GPIO.input(echo) == False :  
        pulse_start = time.time()
 
    while GPIO.input(echo) == True :   
        pulse_end = time.time()
 
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17000
    distance = round(distance, 2)

    return distance

def lcd_init():
  # Initialise display
  lcd_byte(0x33, LCD_CMD) # 110011 Initialise
  lcd_byte(0x32, LCD_CMD) # 110010 Initialise
  lcd_byte(0x06, LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C, LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28, LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01, LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

#LCD USE
def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_string(message, line):
  # Send string to display
  message = message.ljust(LCD_WIDTH," ")
  lcd_byte(line, LCD_CMD)
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def main():
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7

  GPIO.setup(trig, GPIO.OUT)
  GPIO.setup(echo, GPIO.IN)
  GPIO.setup(buzz, GPIO.OUT)

  # Initialise display
  lcd_init()

  cnt = 0
  BZ_int = 1
  p = GPIO.PWM(buzz, 500) #PWM
  p.start(100)
  
  while True:
    distance = get_ultrasonic_distance()

    if distance > 15:
        lcd_string("Rear Sensor", LCD_LINE_1)
        lcd_string("is running", LCD_LINE_2)
        for i in range(3):
            lcd_byte(0x08, LCD_CMD)
            time.sleep(0.5)
            lcd_byte(0x0c, LCD_CMD)
            time.sleep(0.5)
        p.ChangeDutyCycle(0)
        
    elif distance <= 15 and distance >= 5:
        lcd_string("Distance Warnings!", LCD_LINE_1)
        lcd_string("", LCD_LINE_2)
        print ("Distance : ", distance, "cm")
        print("Distance Warnings!")
        p.ChangeDutyCycle(50)
        time.sleep(0.1)
        p.ChangeDutyCycle(0)
        time.sleep(0.5)
        
    elif distance < 5:
        lcd_string("Crush Warnings!", LCD_LINE_1)
        lcd_string("", LCD_LINE_2)
        print ("Distance : ", distance, "cm")
        print("Crush Warnings!")
        p.ChangeDutyCycle(80)
              
    time.sleep(0.1)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_string("Good Bye!", LCD_LINE_1)
    lcd_string("", LCD_LINE_2)
    GPIO.cleanup()
