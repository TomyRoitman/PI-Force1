from enum import Enum

from car_utils.hardware import Component, PIMachine, InPinState


class Direction(Enum):
    """
    Motor spin direction
    """
    Forward = 1,
    Backward = 2


class Speed(Enum):
    """
    Motor speed level
    """
    Low = 1,
    High = 2


class State(Enum):
    """
    Motor state
    """
    Rotate = 1,
    Stop = 2


class ServoMotor(Component):
    """
    Represents a servo motor.
    """

    def __init__(self, id: str, machine: PIMachine, gpio_pins_dict, degree: float = 90):
        """
        Initialize a ServoMotor object.
        :param id: Motor id.
        :param machine: PIMachine
        :param gpio_pins_dict:  {<name>:<PinType>}
        :param degree:
        """
        self.id = id
        self.name = f"ServoMotor-{self.id}"
        self.machine = machine
        self.gpio_pins_dict = gpio_pins_dict
        super().__init__(self.name, self.machine, gpio_pins_dict.values())
        self.degree = degree % 180.0
        self.initial_degree = self.degree
        print(gpio_pins_dict)
        self.servo_pin_number = -1
        self.initialize_pins()

    def change_degree(self, degree_change: float):
        """
        Changes the degree of the motor by a given change_value (degree_change)
        """
        self.degree += degree_change
        if self.degree < 0 or self.degree > 180.0:
            self.degree = int(self.degree / 180.0) * 180.0
        self.__set_degree(self.degree)

    def reset(self):
        """
        Reset motor to initial degree
        """
        self.__set_degree(self.initial_degree)

    def initialize_pins(self):
        """
        Initialize pins used by motor
        """
        print("Initializing pins: ", self.gpio_pins_dict)
        for pin_type, pin_number in self.gpio_pins_dict.items():
            if pin_type == "pwm":
                self.initialize_pwm_pin(pin_number, self.__convert_degrees_to_duty_cycle(self.initial_degree))
                self.servo_pin_number = pin_number

    def __set_degree(self, angle: float):
        """
        Set a certain degree (angle) for the motor.
        :param angle:
        """
        self.update_pwm(self.servo_pin_number, self.__convert_degrees_to_duty_cycle(angle))

    def __convert_degrees_to_duty_cycle(self, angle: float):
        """
        Convert degrees to duty cycle values according to the frequency.
        Degrees are normalized for the range of 0.0-180.0 to the range of 500.0-2500.0
        :param angle: angle in degrees
        """
        return angle / 180.0 * 2000 + 500


class DCMotorController(Component):
    """
    Represents a DCMotor Controller.
    """

    def __init__(self, name: str, machine: PIMachine, gpio_pins_dict):
        """
        Initialize a DCMotorController objet.
        :param name: Controller name
        :param machine: PIMachine
        :param gpio_pins_dict: {pin_type: pin_number}
        """
        self.name = name
        self.machine = machine
        self.gpio_pins_dict = gpio_pins_dict
        super().__init__(self.name, self.machine, gpio_pins_dict.values())
        self.initialize_pins()

    def initialize_pins(self):
        """
        Initialize pins used by controller
        """
        for pin_type, pin_number in self.gpio_pins_dict.items():
            if pin_type == "en":
                self.initialize_en_pin(pin_number)
            elif pin_type == "in":
                self.initialize_in_pin(pin_number)


class DCMotor(Component):
    """
    Represents a DCMotor.
    """
    speed_pwm = {
        "LOW": 25,
        "MEDIUM": 50,
        "HIGH": 75,
        "MIN": 25,
        "MAX": 75
    }

    def __init__(self, name: str, machine: PIMachine, gpio_pins_dict):
        """
        Initialize a DCMotor object.
        :param name: Motor name
        :param machine: PIMachine
        :param gpio_pins_dict: {pin_type: pin_number}
        """
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

    def go_forward(self, speed: Speed = Speed.High):
        """
        Make motor spin forward
        :param speed: Set spin speed
        :return:
        """
        self.state = State.Rotate
        self.direction = Direction.Forward
        self.speed = speed
        self.update_in_pin(self.gpio_pins_dict["in1"], InPinState.HIGH)
        self.update_in_pin(self.gpio_pins_dict["in2"], InPinState.LOW)

    def go_backwards(self, speed: Speed = Speed.High):
        """
        Make motor spin backwards
        :param speed: Set spin speed
        :return:
        """
        self.state = State.Rotate
        self.direction = Direction.Backward
        self.speed = speed
        self.update_in_pin(self.gpio_pins_dict["in1"], InPinState.LOW)
        self.update_in_pin(self.gpio_pins_dict["in2"], InPinState.HIGH)

    def stop(self):
        """
        Make motor stop.
        """
        self.state = State.Rotate
        # self.direction = Direction
        # self.speed = speed
        self.update_in_pin(self.gpio_pins_dict["in1"], InPinState.HIGH)
        self.update_in_pin(self.gpio_pins_dict["in2"], InPinState.HIGH)

    def low_speed(self):
        """
        Set speed to low
        """
        self.update_pwm(self.gpio_pins_dict["en"], 25)

    def medium_speed(self):
        """
        Set speed to medium
        """
        self.update_pwm(self.gpio_pins_dict["en"], 50)

    def high_speed(self):
        """
        Set speed to high
        """
        self.update_pwm(self.gpio_pins_dict["en"], 75)

    def initialize_pins(self):
        """
        Initialize pins used by controller
        """
        for pin_type, pin_number in self.gpio_pins_dict.items():
            if "en" in pin_type:
                self.initialize_en_pin(pin_number)
            elif "in" in pin_type:
                self.initialize_in_pin(pin_number)
