import threading
from enum import Enum

import RPi.GPIO as GPIO

START_PIN_INDEX = 2
END_PIN_INDEX = 27


class PinType(Enum):
    EN = 1,
    IN = 2,
    PWM = 3


class InPinState(Enum):
    LOW = 1,
    HIGH = 2


class PinSlot:

    def __init__(self, acquired: bool = False, component_name: str = None):
        self.acquired = acquired
        self.component_name = component_name

    def is_acquired(self):
        return self.acquired

    def get_component_name(self):
        return self.component_name

    def acquire_pin(self, component_name):
        # TODO: Possible (consider): Check name and if the component_name is the same as the component which has acquired the pin, return True
        if self.acquired:
            return False
        self.acquired = True
        self.component_name = component_name
        return True

    def release_pin(self, component_name):
        if not self.acquired or component_name != self.component_name:
            return False
        self.component_name = None
        self.acquired = False
        return True


class PIMachine:

    def __init__(self):
        self.clean_up()
        self.gpio_pins = self.__create_gpio_pins_data_structure()
        self.pin_lock = threading.Lock()
        GPIO.setmode(GPIO.BCM)  # initialize machine

    def __create_gpio_pins_data_structure(self):
        return {i: PinSlot() for i in range(START_PIN_INDEX, END_PIN_INDEX)}

    def acquire_pins(self, component_name: str, *pin_numbers):
        return all([self.gpio_pins[pin].acquire_pin(component_name) for pin in pin_numbers])

        # already_acquired = [pin for pin in pins if self.gpio_pins[pin].is_acquired() and self.gpio_pins[pin].get_component_name() != component_name]

        # if already_acquired:
        #     raise ValueError(f"Pins {", ".join([pin for pin in already_acquired])} are already acquired.")

        # for pin in pin_numbers: self.gpio_pins[pin].acquire_pin(component_name)

        # return True

    def release_pins(self, component_name: str, *pin_numbers):
        """
        Trying to release pins. Returns True if all pins released correctly, False otherwise
        """
        return all([self.gpio_pins[pin].release_pin(component_name) for pin in pin_numbers])

    def clean_up(self):
        GPIO.cleanup()


class Component:

    def __init__(self, name: str, machine: PIMachine, gpio_pins=None, servo_frequency=50):
        self.name = name
        self.machine = machine
        self.gpio_pins = gpio_pins
        self.servo_frequency = servo_frequency
        self.p = None
        if not self.__acquire_pins():
            raise ValueError("Pins already taken")
        self.pin_classification = {}

    def __acquire_pins(self):
        return self.machine.acquire_pins(self.name, *self.gpio_pins) if self.gpio_pins else False

    def initialize_en_pin(self, pin_num, frequency: float = 1000, duty_cicle: int = 75):
        GPIO.setup(pin_num, GPIO.OUT)
        self.p = GPIO.PWM(pin_num, frequency)
        self.p.start(duty_cicle)
        self.pin_classification[pin_num] = PinType.EN

    def initialize_in_pin(self, pin_num):
        GPIO.setup(pin_num, GPIO.OUT)
        GPIO.output(pin_num, GPIO.LOW)
        self.pin_classification[pin_num] = PinType.IN

    def initialize_pwm_pin(self, pin_num, angle):
        """
        Initialize as pwm then handle as en
        :param angle: Initial motor angle
        :param pin_num: PWM pin number
        :return:
        """
        self.initialize_en_pin(pin_num, self.servo_frequency, angle)

    def update_pwm(self, pwm_value):
        if not PinType.EN in self.pin_classification.values():
            raise ValueError(f"PWM/En pin is not registered!")
        self.p.ChangeDutyCycle(pwm_value)

    def stop_pwm(self):
        self.p.stop()

    def update_in_pin(self, pin_num, pin_state: InPinState):
        if pin_num not in self.pin_classification.keys():
            raise ValueError(f"No pin is registered for slot {pin_num}!")
        if self.pin_classification[pin_num] != PinType.IN:
            raise ValueError(f"Pin slot isn't registered")

        if type(pin_state) is not InPinState:
            raise TypeError("Pin state type is not InPinState")
        if pin_state == InPinState.LOW:
            GPIO.output(pin_num, GPIO.LOW)
        elif pin_state == InPinState.HIGH:
            GPIO.output(pin_num, GPIO.HIGH)
        else:
            raise ValueError(f"Pin state {pin_state} unknown")


if __name__ == "__main__":
    machine = PIMachine()
    comp1 = Component("a", machine, [2, 3])
    print(comp1.__dict__)
    comp1 = Component("b", machine, [2, 3])
    print(comp1.__dict__)
