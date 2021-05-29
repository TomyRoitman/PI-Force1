import threading
from enum import Enum

import RPi.GPIO as GPIO
import pigpio as pigpio

START_PIN_INDEX = 2
END_PIN_INDEX = 27


class PinType(Enum):
    """
    Enum class to describe the type of each pin used by a hardware component.
    """
    EN = 1,
    IN = 2,
    PWM = 3


class InPinState(Enum):
    """
    Pin state describes the possible modes for a physical pin.
    """
    LOW = 1,
    HIGH = 2


class PinSlot:
    """
    Class that holds a pin.
    This is a singleton, and every pin can be acquired only once and used by one component at a time.
    """

    def __init__(self, acquired: bool = False, component_name: str = None):
        """
        Initalize PinSlot object
        :param acquired: Is the pin acquired
        :param component_name:
        """
        self.acquired = acquired
        self.component_name = component_name

    def is_acquired(self):
        """
        :return: If the pin is acquired
        """
        return self.acquired

    def get_component_name(self):
        """
        :return: Get the name of the component that acquired the pin.
        """
        return self.component_name

    def acquire_pin(self, component_name):
        """
        Try acquiring a pin.
        :param component_name: Name of component acquiring.
        :return: Whether action succeeded.
        """
        # TODO: Possible (consider): Check name and if the component_name is the same as the component which has
        #  acquired the pin, return True
        if self.acquired:
            return False
        self.acquired = True
        self.component_name = component_name
        return True

    def release_pin(self, component_name):
        """
        Try releasing a pin.
        :param component_name: Name of component releasing.
        :return: Whether action succeeded.
        """
        if not self.acquired or component_name != self.component_name:
            return False
        self.component_name = None
        self.acquired = False
        return True


class PIMachine:
    """
    Class that represents the PIMachine, and allowing the communication with all physical components.
    """

    def __init__(self):
        """
        Initialize PIMachine object
        """
        self.clean_up()
        self.gpio_pins = self.__create_gpio_pins_data_structure()
        self.pin_lock = threading.Lock()
        GPIO.setmode(GPIO.BCM)  # initialize machine

    def __create_gpio_pins_data_structure(self):
        """
        :return: Dictionary of the form {<pinIndex>: PinSlot_object}
        """
        return {i: PinSlot() for i in range(START_PIN_INDEX, END_PIN_INDEX)}

    def acquire_pins(self, component_name: str, *pin_numbers):
        """
        Trying to acquire pins. Returns True if all pins acquired correctly, False otherwise
        """
        return all([self.gpio_pins[pin].acquire_pin(component_name) for pin in pin_numbers])

    def release_pins(self, component_name: str, *pin_numbers):
        """
        Trying to release pins. Returns True if all pins released correctly, False otherwise
        """
        return all([self.gpio_pins[pin].release_pin(component_name) for pin in pin_numbers])

    def clean_up(self):
        """
        When shutting off machine, clean up all pins.
        """
        GPIO.cleanup()


class Component:
    """
    Represents a hardware component, such as DC_motor, Servo_motor, or any other components that usus gpio pins.
    GPIO = General Purpose Input/Output pins
    """

    def __init__(self, name: str, machine: PIMachine, gpio_pins=None, servo_frequency=50):
        """
        Initialize component object
        """
        self.pin_classification = {}
        self.name = name
        self.machine = machine
        self.gpio_pins = gpio_pins
        self.servo_frequency = servo_frequency
        self.p = None
        if not self.__acquire_pins():
            raise ValueError("Pins already taken")

    def __acquire_pins(self):
        """
        Acquire all pins needed for component operation
        :return: Whether operation succeeded
        """
        return self.machine.acquire_pins(self.name, *self.gpio_pins) if self.gpio_pins else False

    def initialize_en_pin(self, pin_num, frequency: float = 1000, duty_cycle: int = 75):
        """
        Initialize pin of type 'en'. en -> enable, pins that enable operation of component. For example, enable pin on
        a dc motor controller, would enable the operation of dc motors via the dc motor controller.
        :param pin_num: Index of pin
        :param frequency: Wave frequency
        :param duty_cycle: Translates to angle of motor.
        """
        print("[I] Initializing EN pin", pin_num, frequency, duty_cycle)
        GPIO.setup(pin_num, GPIO.OUT)
        self.p = GPIO.PWM(pin_num, frequency)
        self.p.start(duty_cycle)
        self.pin_classification[pin_num] = PinType.EN

    def initialize_in_pin(self, pin_num):
        """
        Initialize pin of type 'in'. This pin allows the transmission of direct signals from the machine to physical
        component.
        :param pin_num:
        """
        GPIO.setup(pin_num, GPIO.OUT)
        GPIO.output(pin_num, GPIO.LOW)
        self.pin_classification[pin_num] = PinType.IN

    def initialize_pwm_pin(self, pin_num, angle, frequency: float = 50):
        """
        Initialize pin of type 'pwm'.
        :param frequency: Wave frequency
        :param angle: Initial motor angle What angle to sta
        :param pin_num: PWM pin number
        """
        print("Initializing pwm pin", pin_num, angle)
        self.p = pigpio.pi('0.0.0.0', 8888)
        self.p.set_mode(pin_num, pigpio.OUTPUT)
        self.p.set_PWM_frequency(pin_num, frequency)
        self.p.set_servo_pulsewidth(pin_num, angle)
        self.pin_classification[pin_num] = PinType.PWM

    def update_pwm(self, pin_num, angle: float = 500):
        """
        Changes the angle of the motor.
        Angle is normalized to the range of 500 - 2500, according to the frequency.
        :param pin_num: Which pwm pin to update.
        :param angle: What angle to set the motor to.
        """
        if not PinType.PWM in self.pin_classification.values():
            raise ValueError(f"Pin {pin_num} is not registered as a PWM pin!")
        self.p.set_servo_pulsewidth(pin_num, angle)

    def stop_pwm(self, pin_num):
        """
        Stop the session with a pwm pin.
        :param pin_num: Which pwm pin to stop.
        """
        self.p.set_PWM_dutycycle(pin_num, 0)
        self.p.set_PWM_frequency(pin_num, 0)

    def update_in_pin(self, pin_num, pin_state: InPinState):
        """
        Update the state of an 'in' pin.
        :param pin_num: Which pwm pin to update.
        :param pin_state: What state to change the pin to.
        """
        if pin_num not in self.pin_classification.keys():
            raise ValueError(f"No pin is registered for slot {pin_num}!")
        if self.pin_classification[pin_num] != PinType.IN:
            raise ValueError(f"Pin slot isn't registered")

        if type(pin_state) is not InPinState:
            raise TypeError(f"pin_state param type: {type(pin_num)} is not InPinState")
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
