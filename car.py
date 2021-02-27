from hardware import PIMachine
import threading
import json
from motor import DCMotor, ServoMotor, Speed, State

GPIO_PIN_DISTRIBUTION_PATH="gpio_pin_distribution.json"

class Car():

    def __init__(self):
        
        self.machine = PIMachine()

        self.__load_gpio_distribution()

        self.lock = threading.Lock()
        self.controllers = {}
        self.wheel_DC_motors = {}
        self.__initialize_wheel_controllers()
        self.__initialize_wheel_DC_motors()
        self.__initialize_servo_motors()

    def __initialize_wheel_controllers(self):
        DC_controllers = self.pin_distribution["DCControllers"]
        #print(DC_controllers)
        for controller_name, pins in DC_controllers.items():
            #print(DC_controllers[controller_name])
            self.controllers[controller_name] = DCMotorController(controller_name, self.machine, pins) # DC_controllers[controller_name]) #pins)
            #print(self.wheels[controller_name].__dict__)      
            print(f"Initialized controller \"{controller_name}\" with pins: {pins}")

    def __initialize_wheel_motors(self):
        wheel_DC_motors_dict = self.pin_distribution["WheelDCMotors"]
        for wheel_group in wheel_motors.keys():
            if not wheel_group in self.wheel_DC_motors:
                wheel_DC_motors[wheel_group] = {}
            for wheel_motor_name, pins in wheel_DC_motors[wheel_group]     
                self.wheel_DC_motors[wheel_group][wheel_motor_name] = DCMotor(wheel_motor_name, self.machine, pins)
                print(f"Initialized wheel DC motor \"{wheel_motor_name}\" with pins: {pins}")          
#print(DC_controllers)
    
    def __initialize_servo_motors(self):
            pass


    def __load_gpio_distribution(self):
        self.pin_distribution = json.load(open(GPIO_PIN_DISTRIBUTION_PATH))


def main():
    car = Car()


if __name__ == "__main__":
    main()
