from enum import Enum
import threading
import functools

START_PIN_INDEX = 2
END_PIN_INDEX = 27

class Pin:

    def __init__(acquired=False: bool, component_name=None: str):
        self.acquired=acquired
        self.component_name=component_name

    def is_acquired(self):
        return self.acquired

    def get_component_name(self):
        return self.component_name
    
    def acquire_pin(self, component_name):
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

        self.gpio_pins = self.__create_gpio_pins_data_structure()
        self.pin_lock = threading.Lock()

    def __create_gpio_pins_data_structure(self):
        return {i: Pin() for i in range(START_PIN_INDEX, END_PIN_INDEX)}
    
    def acquire_pins(self,  component_name: str, *pin_numbers):
        
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
        pass


class Component:

    def __init__(self, name: str, machine: PIMachine, gpio_pins=None):
        self.name = name
        self.machine=machine
        self.gpio_pins = gpio_pins

    def acquire_pins(self):
        return self.machine.acquire_pins(self.name, *self.gpio_pins) if self.gpio_pins else False

