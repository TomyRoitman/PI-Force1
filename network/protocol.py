from enum import Enum


class PICommunication:
    msg_code_size = 4
    msg_size_header_size = 8
    msg_header_size = msg_code_size + msg_size_header_size

    class MessageCode(Enum):
        INITIALIZE_CAMERAS = "ICMS"  # = Choose camera to stream
        DISCONNECT = "DISC"  # = Disconnect
        ERROR = "ERRO"  # = Error
        HIGH_SPEED = "HIGH"  # = Set high speed
        INITIALIZE = "INIT"  # = Initialize
        LOW_SPEED = "LOWS"  # = Set low speed
        MEDIUM_SPEED = "MEDS"  # = Set medium speed
        MOVE_FORWARD = "FRWD"  # = Move forward
        MOVE_BACKWARDS = "BACK"  # = Move backwards
        STOP = "STOP"  # = Stop the car
        TURN_RIGHT = "TRRI"  # = Turn right
        TURN_LEFT = "TRLE"  # = Turn left
        CAMERA_RIGHT = "CAMR"
        CAMERA_LEFT = "CAML"
        CAMERA_UP = "CAMU"
        CAMERA_DOWN = "CAMD"
        TOGGLE_DEPTH_MAP = "DPTH"
        TOGGLE_OBJECT_DETECTION = "OBJD"
        TOGGLE_DISTANCE = "DIST"
        RESET_CAMERA_POSITION = "RCAM"

    @staticmethod
    def initialize_cameras():
        return PICommunication.__format_message(PICommunication.MessageCode.INITIALIZE_CAMERAS)

    @staticmethod
    def move_forward():
        return PICommunication.__format_message(PICommunication.MessageCode.MOVE_FORWARD, b"")

    @staticmethod
    def move_backwards():
        return PICommunication.__format_message(PICommunication.MessageCode.MOVE_BACKWARDS, b"")

    @staticmethod
    def stop():
        return PICommunication.__format_message(PICommunication.MessageCode.STOP, b"")

    @staticmethod
    def set_high_speed():
        return PICommunication.__format_message(PICommunication.MessageCode.HIGH_SPEED, b"")

    @staticmethod
    def set_medium_speed():
        return PICommunication.__format_message(PICommunication.MessageCode.MEDIUM_SPEED, b"")

    @staticmethod
    def set_low_speed():
        return PICommunication.__format_message(PICommunication.MessageCode.LOW_SPEED, b"")

    @staticmethod
    def turn_right(duration: float = 0):
        return PICommunication.__format_message(PICommunication.MessageCode.TURN_RIGHT, str(duration).encode())

    @staticmethod
    def turn_left(duration: float = 0):
        return PICommunication.__format_message(PICommunication.MessageCode.TURN_LEFT, str(duration).encode())

    @staticmethod
    def move_camera_up():
        return PICommunication.__format_message(PICommunication.MessageCode.CAMERA_UP)

    @staticmethod
    def move_camera_down():
        return PICommunication.__format_message(PICommunication.MessageCode.CAMERA_DOWN)

    @staticmethod
    def move_camera_left():
        return PICommunication.__format_message(PICommunication.MessageCode.CAMERA_LEFT)

    @staticmethod
    def move_camera_right():
        return PICommunication.__format_message(PICommunication.MessageCode.CAMERA_RIGHT)

    @staticmethod
    def toggle_depth_map():
        return PICommunication.__format_message(PICommunication.MessageCode.TOGGLE_DEPTH_MAP)

    @staticmethod
    def toggle_object_detection():
        return PICommunication.__format_message(PICommunication.MessageCode.TOGGLE_OBJECT_DETECTION)

    @staticmethod
    def toggle_distance():
        return PICommunication.__format_message(PICommunication.MessageCode.TOGGLE_DISTANCE)

    @staticmethod
    def reset_camera_position():
        return PICommunication.__format_message(PICommunication.MessageCode.RESET_CAMERA_POSITION)

    @staticmethod
    def error(error_message: str):
        return PICommunication.__format_message(PICommunication.MessageCode.ERROR, error_message.encode())

    @staticmethod
    def disconnect(exit_code: str):
        return PICommunication.__format_message(PICommunication.MessageCode.DISCONNECT, exit_code.encode())

    @staticmethod
    def __format_message(code: MessageCode, content: bytes = b""):
        code_value = code.value
        return code_value.encode() + content

    @staticmethod
    def parse_message(message: bytes):
        message = message.decode()
        code = message[:PICommunication.msg_code_size]
        content = message[PICommunication.msg_code_size:]
        return PICommunication.MessageCode(code), content
