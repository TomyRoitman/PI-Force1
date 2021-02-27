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
        self.__initialize_DC_controllers()
        self.__initialize_DC_motors()
        self.__initialize_servo_motors()

    def __initialize_DC_controllers(self):
        DC_controllers = self.pin_distribution["DCControllers"]
        for controller_name, pins in DC_controllers.items():
            a = DCMotor(controller_name, self.machine, pins)
            print(a.__dict__)      
    
    def __initialize_DC_motors(self):
            DC_controllers = self.pin_distribution["DCMotors"]
            print(DC_controllers)
    
    def __initialize_servo_motors(self):
            pass


    def __load_gpio_distribution(self):
        self.pin_distribution = json.load(open(GPIO_PIN_DISTRIBUTION_PATH))


def main():
    car = Car()


if __name__ == "__main__":
    main()
