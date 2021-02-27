from hardware import Component, PIMachine
from enum import Enum

class Direction(Enum):
    Forward = 1,
    Backward = 2

class Speed(Enum):
    Low = 1,
    High = 2

class State(Enum):
    Rotate = 1,
    Stop = 2

class ServoMotor(Component):
    def __init__(self, id: str, machine: PIMachine, gpio_pins, degree:float=0):
        self.id = id
        self.name = f"ServoMotor-{self.id}"
        self.machine = machine
        self.gpio_pins = gpio_pins
        super().__init__(self.name, self.machine, gpio_pins)
        self.degree= degree

    def change_degree(self, degree: float):
        """
        TODO: Change degree
        """
        self.degree = degree
    
class DCMotor(Component):

    speed_pwm = {
	"LOW": 25, 
	"MEDIUM": 50, 
	"HIGH": 75, 
	"MIN": 25, 
	"MAX": 75 
    }

    def __init__(self, name: str, machine: PIMachine, gpio_pins):
        self.name = name
        self.machine = machine
        self.gpio_pins_dict = gpio_pins
        print(self.gpio_pins_dict)
        super().__init__(self.name, self.machine, gpio_pins.values())
        self.direction = Direction.Forward
        self.speed = Speed.Low
        self.state = State.Stop
        #print(self.gpio_pins)
        self.initialize_pins()


    def rotate(self, direction: Direction=Direction.Forward, speed: Speed=Speed.Low):
        self.state = State.Rotate
        self.direction = Direction
        self.speed = speed

    def initialize_pins(self):
        for pin_type, pin_number in self.gpio_pins_dict.items():
            if pin_type == "en":
                self.initialize_en_pin(pin_number)
            elif pin_type == "in":
                self.initialize_in_pin(pin_number)


    def stop(self):
        self.state = State.Stop

    
