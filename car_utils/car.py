import json
import threading

from car_utils.hardware import PIMachine
from car_utils.motor import DCMotorController, DCMotor, ServoMotor

GPIO_PIN_DISTRIBUTION_PATH = "gpio_pin_distribution.json"


class Car():
    """
    Represents the entire car, and allows control over wheels and camera gyroscope.
    """
    def __init__(self, vertical_change_value: float = 2.0, horizontal_change_value: float = 2.0):
        """
        Initialize car object
        :param vertical_change_value: How many degrees to add or decrease when moving camera vertically.
        :param horizontal_change_value: How many degrees to add or decrease when moving camera horizontally.
        """
        self.machine = PIMachine()

        self.vertical_change_value = vertical_change_value
        self.horizontal_change_value = horizontal_change_value

        self.__load_gpio_distribution()

        self.lock = threading.Lock()
        self.wheel_DC_motors = {}
        self.gyroscope_servo_motors = {}
        self.__initialize_wheel_DC_motors()
        self.__initialize_servo_motors()

    def go_forward(self):
        """
        Make car go forward.
        """
        for wheel_group, wheel_motors in self.wheel_DC_motors.items():
            for wheel_motor_name, wheel_motor_object in wheel_motors.items():
                wheel_motor_object.go_forward()

    def go_backwards(self):
        """
        Make car go backwards.
        """
        for wheel_group, wheel_motors in self.wheel_DC_motors.items():
            for wheel_motor_name, wheel_motor_object in wheel_motors.items():
                wheel_motor_object.go_backwards()

    def stop(self):
        """
        Make the car stop.
        """
        for wheel_group, wheel_motors in self.wheel_DC_motors.items():
            for wheel_motor_name, wheel_motor_object in wheel_motors.items():
                wheel_motor_object.stop()

    def low(self):
        """
        Set car speed low.
        """
        for wheel_group, wheel_motors in self.wheel_DC_motors.items():
            for wheel_motor_name, wheel_motor_object in wheel_motors.items():
                wheel_motor_object.low_speed()

    def medium(self):
        """
        Set car speed medium.
        """
        for wheel_group, wheel_motors in self.wheel_DC_motors.items():
            for wheel_motor_name, wheel_motor_object in wheel_motors.items():
                wheel_motor_object.medium_speed()

    def high(self):
        """
        Set car speed high.
        """
        for wheel_group, wheel_motors in self.wheel_DC_motors.items():
            for wheel_motor_name, wheel_motor_object in wheel_motors.items():
                wheel_motor_object.high_speed()

    def turn_right(self):
        """
        Make car turn right.
        """
        for wheel_group, wheel_motors in self.wheel_DC_motors.items():
            for wheel_motor_name, wheel_motor_object in wheel_motors.items():
                if "left" in wheel_motor_name:
                    wheel_motor_object.go_forward()
                if "right" in wheel_motor_name:
                    wheel_motor_object.go_backwards()

    def turn_left(self):
        """
        Make car turn left.
        """
        for wheel_group, wheel_motors in self.wheel_DC_motors.items():
            for wheel_motor_name, wheel_motor_object in wheel_motors.items():
                if "left" in wheel_motor_name:
                    wheel_motor_object.go_backwards()
                if "right" in wheel_motor_name:
                    wheel_motor_object.go_forward()

    def move_camera_right(self):
        """
        Turn camera gyroscope right.
        """
        self.gyroscope_servo_motors["vertical"].change_degree(self.vertical_change_value)

    def move_camera_left(self):
        """
        Turn camera gyroscope left.
        """
        self.gyroscope_servo_motors["vertical"].change_degree(-1 * self.vertical_change_value)

    def move_camera_up(self):
        """
        Turn camera gyroscope up.
        """
        self.gyroscope_servo_motors["horizontal"].change_degree(self.horizontal_change_value)

    def move_camera_down(self):
        """
        Turn camera gyroscope down.
        """
        self.gyroscope_servo_motors["horizontal"].change_degree(-1 * self.horizontal_change_value)

    def reset_camera_position(self):
        """
        Reset camera gyroscope position to its initial position.
        """
        for name, motor in self.gyroscope_servo_motors.items():
            motor.reset()

    def __initialize_wheel_controllers(self):
        """
        Initialize the DCMotor controllers used to control the wheels DC motors.
        """
        DC_controllers = self.pin_distribution["DCControllers"]
        # print(DC_controllers)
        for controller_name, pins in DC_controllers.items():
            # print(DC_controllers[controller_name])
            self.controllers[controller_name] = DCMotorController(controller_name, self.machine,
                                                                  pins)  # DC_controllers[controller_name]) #pins)
            # print(self.wheels[controller_name].__dict__)
            print(f"Initialized controller \"{controller_name}\" with pins: {pins}")

    def __initialize_wheel_DC_motors(self):
        """
        Initialize the DCMotors used for the wheels.
        """
        wheel_DC_motors_dict = self.pin_distribution["WheelDCMotors"]
        print("1", wheel_DC_motors_dict)
        for wheel_group, wheel_motors in wheel_DC_motors_dict.items():
            print("2", wheel_group)
            if not wheel_group in self.wheel_DC_motors:
                self.wheel_DC_motors[wheel_group] = {}
            print("2a", wheel_group, wheel_DC_motors_dict[wheel_group])
            for wheel_motor_name, pins in wheel_motors.items():
                print("3", wheel_motor_name, pins)
                self.wheel_DC_motors[wheel_group][wheel_motor_name] = DCMotor(wheel_motor_name, self.machine, pins)
                print("4", f"Initialized wheel DC motor \"{wheel_group}-{wheel_motor_name}\" with pins: {pins}")
            # print(DC_controllers)

    def __initialize_servo_motors(self):
        """
        Initialize the ServoMotors used for the camera gyroscope.
        """
        print("\n\n\n\---- initializing servo motors ----\n\n\n")
        gyroscope_servo_motors_dict = self.pin_distribution["GyroscopeServoMotors"]
        print("\n\n\n1", gyroscope_servo_motors_dict)
        for motor_name, pins in gyroscope_servo_motors_dict.items():
            print("Servo motor info: ", motor_name, pins)
            self.gyroscope_servo_motors[motor_name] = ServoMotor(motor_name, self.machine, pins, 90)

    def __load_gpio_distribution(self):
        """
        Load from a json file the mapping of the gpio pins used for the car. Mapping is done by component type,
        component name, pin type and pin index.
        """
        self.pin_distribution = json.load(open(GPIO_PIN_DISTRIBUTION_PATH))


def main():
    car = Car()
    while True:
        query = input("""
        \nf - forward
        \nb - backwards
        \ns - stop
        \nl - low
        \nm - medium
        \nh - high
        \ntr - turn right
        \ntl - turn left
        \nq - quit\n""")
        if query == "f":
            car.go_forward()
        elif query == "b":
            car.go_backwards()
        elif query == "s":
            car.stop()
        elif query == "l":
            car.low()
        elif query == "m":
            car.medium()
        elif query == "h":
            car.high()
        elif query == "tr":
            car.turn_right()
        elif query == "tl":
            car.turn_left()
        elif query == "q":
            break
        else:
            print(f"Command {query} unknown, skipping")
    # time.sleep(5000)
    car.machine.clean_up()


if __name__ == "__main__":
    main()
