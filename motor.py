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
    def __init__(self, id: str, degree=0, machine: PIMachine, gpio_pins):
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
    def __init__(self, id: str, machine: PIMachine, gpio_pins):
        self.id = id
        self.name = f"DCMotor-{self.id}"
        self.machine = machine
        self.gpio_pins = gpio_pins
        super().__init__(self.name, self.machine, gpio_pins)
        self.direction = Direction.Forward
        self.speed = Low
        self.state = State.Stop

    def rotate(self, direction: Direction=Direction.Forward, speed: Speed=Speed.Low):
        self.state = State.Rotate
        self.direction = Direction
        self.speed = speed
    
    def stop(self):
        self.state = State.Stop
