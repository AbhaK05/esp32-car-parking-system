from machine import SoftI2C, Pin, PWM
from i2c_lcd import I2cLcd
import time

# Initialize I2C and LCD
i2c = SoftI2C(scl=Pin(18), sda=Pin(19))
lcd = I2cLcd(i2c, 0x27, 2, 16)

# IR Sensors
ir_toll = Pin(23, Pin.IN)  # IR sensor at toll gate
ir_counter = Pin(22, Pin.IN)  # IR sensor at parking slots

# Buzzer
buzzer = Pin(4, Pin.OUT)  # GPIO 4 for the buzzer

# Initialize the PWM signal for the servo motor (50Hz for SG90 servo)
servo = PWM(Pin(15), freq=50)  # Use GPIO 15 for the servo

def set_servo_angle(angle):
    """Sets the servo motor to the specified angle (0-180 degrees)."""
    duty = int((angle / 180) * 75 + 40)  # Adjust duty cycle for SG90 (0 degrees -> 40, 180 degrees -> 115)
    print(f"Setting servo to {angle} degrees, duty cycle: {duty}")
    servo.duty(duty)

# Variables
car_count = 0  # Track number of cars currently in the parking lot
max_cars = 2  # Maximum number of parking spots
newcar = 0  # Flag to track if a new car is attempting to enter
leaving = False  # Flag to track if a car is leaving

while True:
    # Check if car is at toll gate (car detected)
    if ir_toll.value() == 0 and not leaving:  # Low means car detected, only for entering
        lcd.clear()
        lcd.putstr("Car Detected")
        buzzer.on()

        if car_count < max_cars:  # Check if there is space for the car
            set_servo_angle(90)  # Open toll gate (90 degrees)
            newcar = 1  # A new car is attempting to enter
            time.sleep(5)  # Keep the gate open for 5 seconds
            set_servo_angle(0)  # Close toll gate (0 degrees)
            print("Car is allowed in.")
        else:
            lcd.clear()
            lcd.putstr("No Parking Space")
            time.sleep(2)  # Show the message for 2 seconds
            print("Car is not allowed in.")

        buzzer.off()

    # Adding a short delay to avoid checking ir_counter too often
    time.sleep(0.1)

    # Check if car passes through the counter (entering parking or leaving)
    if ir_counter.value() == 0:  # Low means car detected at counter
        # Ensure the trigger is not caused by a "bounce" or noise
        time.sleep(0.2)  # Debounce delay to ensure stable reading

        if newcar == 1:  # New car is entering
            car_count += 1
            newcar = 0  # Reset newcar flag after the car has entered
            lcd.clear()
            lcd.putstr(f"Car Entered: {car_count}")
            time.sleep(2)  # To avoid multiple triggers for the same car
            print("Car is detected by the counter.")
        else:  # If no new car is entering, it must be a car leaving
            if car_count > 0:  # Ensure there is a car to exit
                leaving = True  # Set leaving flag to avoid toll triggering
                set_servo_angle(90)  # Open toll gate for exit
                time.sleep(5)  # Keep the gate open for 5 seconds
                set_servo_angle(0)  # Close toll gate
                car_count -= 1
                lcd.clear()
                lcd.putstr(f"Car Left: {car_count}")
                time.sleep(2)  # To avoid multiple triggers for the same car
                leaving = False  # Reset leaving flag after the car exits
                print("Car is detected leaving.")
