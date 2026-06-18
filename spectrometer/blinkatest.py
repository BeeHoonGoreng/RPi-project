import board
import digitalio
import busio
 
print("Hello blinka!")

# Try to great a Digital input
try:
    pin = digitalio.DigitalInOut(board.D4)
    print("GPIO (Digital IO) ok!")
except Exception as e:
    print(f"GPIO failed: {e}")
    
# Try to create an I2C device
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    print("I2C ok!")
except Exception as e:
    print(f"I2C failed: {e}")
    
# Try to create an SPI device
try:
    spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
    print("SPI ok!")
except Exception as e:
    print(f"SPI failed: {e}")

print("done!")