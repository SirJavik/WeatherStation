import Adafruit_BMP.BMP085 as BMP085
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

class Barometer:
    def __init__(self):
        pass

    def run(self):
        sensor      = BMP085.BMP085()
        temp        = sensor.read_temperature()
        pressure    = sensor.read_pressure()
            

        print ('[Barometer] Temperature = {0:0.2f} °C'.format(temp))       # Print temperature
        print ('[Barometer] Pressure = {0:0.2f} Pa'.format(pressure)) # Print pressure
        return pressure, temp

class Humidity:
    
    def run(self):
        DHTPIN = 27
        MAX_UNCHANGE_COUNT = 100
        STATE_INIT_PULL_DOWN = 1
        STATE_INIT_PULL_UP = 2
        STATE_DATA_FIRST_PULL_DOWN = 3
        STATE_DATA_PULL_UP = 4
        STATE_DATA_PULL_DOWN = 5
        
        GPIO.setup(DHTPIN, GPIO.OUT)
        GPIO.output(DHTPIN, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(DHTPIN, GPIO.LOW)
        time.sleep(0.02)
        GPIO.setup(DHTPIN, GPIO.IN, GPIO.PUD_UP)

        unchanged_count = 0
        last = -1
        data = []
        while True:
            current = GPIO.input(DHTPIN)
            data.append(current)
            if last != current:
                unchanged_count = 0
                last = current
            else:
                unchanged_count += 1
                if unchanged_count > MAX_UNCHANGE_COUNT:
                    break

        state = STATE_INIT_PULL_DOWN

        lengths = []
        current_length = 0

        for current in data:
            current_length += 1

            if state == STATE_INIT_PULL_DOWN:
                if current == GPIO.LOW:
                    state = STATE_INIT_PULL_UP
                else:
                    continue
            if state == STATE_INIT_PULL_UP:
                if current == GPIO.HIGH:
                    state = STATE_DATA_FIRST_PULL_DOWN
                else:
                    continue
            if state == STATE_DATA_FIRST_PULL_DOWN:
                if current == GPIO.LOW:
                    state = STATE_DATA_PULL_UP
                else:
                    continue
            if state == STATE_DATA_PULL_UP:
                if current == GPIO.HIGH:
                    current_length = 0
                    state = STATE_DATA_PULL_DOWN
                else:
                    continue
            if state == STATE_DATA_PULL_DOWN:
                if current == GPIO.LOW:
                    lengths.append(current_length)
                    state = STATE_DATA_PULL_UP
                else:
                    continue
        if len(lengths) != 40:
            print ("[Humidity] Data not good, skip")
            return False

        shortest_pull_up = min(lengths)
        longest_pull_up = max(lengths)
        halfway = (longest_pull_up + shortest_pull_up) / 2
        bits = []
        the_bytes = []
        byte = 0

        for length in lengths:
            bit = 0
            if length > halfway:
                bit = 1
            bits.append(bit)
        for i in range(0, len(bits)):
            byte = byte << 1
            if (bits[i]):
                byte = byte | 1
            else:
                byte = byte | 0
            if ((i + 1) % 8 == 0):
                the_bytes.append(byte)
                byte = 0
        checksum = (the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3]) & 0xFF
        if the_bytes[4] != checksum:
            print ("[Humidity] Data not good, skip")
            return False

        print ("[Humidity] Humidity: %s %%,  Temperature: %s °C" % (the_bytes[0], the_bytes[2]))
        return the_bytes[0], the_bytes[2]

#def main():
#    print ("Raspberry Pi wiringPi DHT11 Temperature test program\n")
#    while True:
#        hum = Humidity()
#        result = hum.run()
#        if result:
#            humidity, temperature = result
#            time.sleep(1)
#
#def destroy():
#    GPIO.cleanup()
#
#if __name__ == '__main__':
#    try:
#        main()
#    except KeyboardInterrupt:
#        destroy() 

        
