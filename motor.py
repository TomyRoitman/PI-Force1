from enum import Enum

from hardware import Component, PIMachine, InPinState


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
    def __init__(self, id: str, machine: PIMachine, gpio_pins_dict, degree: float = 90):
        self.id = id
        self.name = f"ServoMotor-{self.id}"
        self.machine = machine
        self.gpio_pins_dict = gpio_pins_dict
        super().__init__(self.name, self.machine, gpio_pins_dict.values())
        self.degree = degree % 180.0
        self.initial_degree = self.degree
        # self.gpio_pins[0]
        print(gpio_pins_dict)
        self.servo_pin_number = -1
        self.initialize_pins()
        #self.servo_pin_number = -1
    def change_degree(self, degree_change: float):
        """
        TODO: Change degree
        """
        self.degree += degree_change
        if self.degree < 0 or self. degree > 180.0:
            self.degree = int(self.degree / 180.0) * 180.0
        self.__set_degree(self.degree)

    def reset(self):
        self.__set_degree(self.initial_degree)

    def initialize_pins(self):
        print("Initializing pins: ", self.gpio_pins_dict)
        for pin_type, pin_number in self.gpio_pins_dict.items():
            if pin_type == "pwm":
                self.initialize_pwm_pin(pin_number, self.__convert_degrees_to_duty_cycle(self.initial_degree))
                self.servo_pin_number = pin_number

    def __set_degree(self, angle: float):
        self.update_pwm(self.servo_pin_number, self.__convert_degrees_to_duty_cycle(angle))

    def __convert_degrees_to_duty_cycle(self, angle: float):
        """
        Convert degrees to duty cycle values
        :param angle: angle in degrees
        :return:
        """
        return angle / 180.0 * 2000 + 500


class DCMotorController(Component):

    def __init__(self, name: str, machine: PIMachine, gpio_pins_dict):
        self.name = name
        self.machine = machine
        self.gpio_pins_dict = gpio_pins_dict
        super().__init__(self.name, self.machine, gpio_pins_dict.values())
        self.initialize_pins()

    def initialize_pins(self):
        for pin_type, pin_number in self.gpio_pins_dict.items():
            if pin_type == "en":
                self.initialize_en_pin(pin_number)
            elif pin_type == "in":
                self.initialize_in_pin(pin_number)


class DCMotor(Component):
    speed_pwm = {
        "LOW": 25,
        "MEDIUM": 50,
        "HIGH": 75,
        "MIN": 25,
        "MAX": 75
    }

    def __init__(self, name: str, machine: PIMachine, gpio_pins_dict):
        self.name = name
        self.machine = machine
        self.gpio_pins_dict = gpio_pins_dict
        # print(self.gpio_pins_dict)
        super().__init__(self.name, self.machine, gpio_pins_dict.values())
        self.direction = Direction.Forward
        self.speed = Speed.Low
        self.state = State.Stop
        # print(self.gpio_pins)
        self.initialize_pins()

    def go_forward(self, direction: Direction = Direction.Forward, speed: Speed = Speed.Low):
        self.state = State.Rotate
        self.direction = Direction
        self.speed = speed
        self.update_in_pin(self.gpio_pins_dict["in1"], InPinState.HIGH)
        self.update_in_pin(self.gpio_pins_dict["in2"], InPinState.LOW)

    def go_backwards(self, direction: Direction = Direction.Forward, speed: Speed = Speed.Low):
        self.state = State.Rotate
        self.direction = Direction
        self.speed = speed
        self.update_in_pin(self.gpio_pins_dict["in1"], InPinState.LOW)
        self.update_in_pin(self.gpio_pins_dict["in2"], InPinState.HIGH)

    def stop(self):
        self.state = State.Rotate
        # self.direction = Direction
        # self.speed = speed
        self.update_in_pin(self.gpio_pins_dict["in1"], InPinState.HIGH)
        self.update_in_pin(self.gpio_pins_dict["in2"], InPinState.HIGH)

    def low_speed(self):
        self.update_pwm(self.gpio_pins_dict["en"], 25)

    def medium_speed(self):
        self.update_pwm(self.gpio_pins_dict["en"], 50)

    def high_speed(self):
        self.update_pwm(self.gpio_pins_dict["en"], 75)

    def initialize_pins(self):
        for pin_type, pin_number in self.gpio_pins_dict.items():
            if "en" in pin_type:
                self.initialize_en_pin(pin_number)
            elif "in" in pin_type:
                self.initialize_in_pin(pin_number)

    # def stop(self):
    # self.state = State.Stop
