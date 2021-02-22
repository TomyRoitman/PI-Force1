from hardware import PIMachine
import threading
import json


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
        print(DC_controllers)
    
    def __initialize_DC_motors(self):
            pass
    
    def __initialize_servo_motors(self):
            pass


    def __load_gpio_distribution(self):
        self.pin_distribution = json.load(open(GPIO_PIN_DISTRIBUTION_PATH))


def main():
    pass

if __name__ == "__main__":
    main()