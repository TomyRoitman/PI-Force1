from hardware import PIMachine
import threading
import json
from motor import DCMotorController, DCMotor, ServoMotor, Speed, State
import time

GPIO_PIN_DISTRIBUTION_PATH="gpio_pin_distribution.json"

class Car():

    def __init__(self):
        
        self.machine = PIMachine()

        self.__load_gpio_distribution()

        self.lock = threading.Lock()
        # self.controllers = {}
        self.wheel_DC_motors = {}
        # self.__initialize_wheel_controllers()
        self.__initialize_wheel_DC_motors()
        self.__initialize_servo_motors()

    def go_forward(self):
        for wheel_group, wheel_motors in self.wheel_DC_motors.items():
            for wheel_motor_name, wheel_motor_object in wheel_motors.items():
                wheel_motor_object.go_forward()
    def go_backwards(self):
        for wheel_group, wheel_motors in self.wheel_DC_motors.items():
            for wheel_motor_name, wheel_motor_object in wheel_motors.items():
                wheel_motor_object.go_backwards()
    def stop(self):
        for wheel_group, wheel_motors in self.wheel_DC_motors.items():
            for wheel_motor_name, wheel_motor_object in wheel_motors.items():
                wheel_motor_object.stop()
    def low(self):
        for wheel_group, wheel_motors in self.wheel_DC_motors.items():
            for wheel_motor_name, wheel_motor_object in wheel_motors.items():
                wheel_motor_object.low()
    def medium(self):
        for wheel_group, wheel_motors in self.wheel_DC_motors.items():
            for wheel_motor_name, wheel_motor_object in wheel_motors.items():
                wheel_motor_object.medium()
    
    def high(self):
        for wheel_group, wheel_motors in self.wheel_DC_motors.items():
            for wheel_motor_name, wheel_motor_object in wheel_motors.items():
                wheel_motor_object.high()

    def __initialize_wheel_controllers(self):
        DC_controllers = self.pin_distribution["DCControllers"]
        #print(DC_controllers)
        for controller_name, pins in DC_controllers.items():
            #print(DC_controllers[controller_name])
            self.controllers[controller_name] = DCMotorController(controller_name, self.machine, pins) # DC_controllers[controller_name]) #pins)
            #print(self.wheels[controller_name].__dict__)      
            print(f"Initialized controller \"{controller_name}\" with pins: {pins}")

    def __initialize_wheel_DC_motors(self):
        wheel_DC_motors_dict = self.pin_distribution["WheelDCMotors"]
        print("1", wheel_DC_motors_dict)
        for wheel_group, wheel_motors in wheel_DC_motors_dict.items():
            print("2", wheel_group)
            if not wheel_group in self.wheel_DC_motors:
                self.wheel_DC_motors[wheel_group] = {}
            print("2a", wheel_group, wheel_DC_motors_dict[wheel_group])
            for wheel_motor_name, pins in wheel_motors.items():     
                print("3", wheel_motor_name, pins)
                self.wheel_DC_motors[wheel_group][wheel_motor_name] = DCMotor(wheel_motor_name, self.machine, pins)
                print("4", f"Initialized wheel DC motor \"{wheel_group}-{wheel_motor_name}\" with pins: {pins}")          
#print(DC_controllers)
    
    def __initialize_servo_motors(self):
            pass


    def __load_gpio_distribution(self):
        self.pin_distribution = json.load(open(GPIO_PIN_DISTRIBUTION_PATH))


def main():
    car = Car()
    while True:
        query = input("\nf - forward, b - backward, s - stop, l - low, m - medium, h - high\n")
        if query == "f":
            car.go_forward()
        elif query == "b":
            car.go_backwards()
        elif query == "s":
            car.stop()
        elif query == "l":
            car.low()
        elif query == "m":
            car.medium()
        elif query == "h":
            car.high()
        else:
            print(f"Command {query} unknown, skipping")
    #time.sleep(5000)
    car.machine.clean_up()

if __name__ == "__main__":
    main()
