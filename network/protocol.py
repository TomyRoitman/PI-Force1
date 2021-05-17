from enum import Enum


class PICommunication:
    msg_code_size = 4
    msg_size_header_size = 8
    msg_header_size = msg_code_size + msg_size_header_size

    class MessageCode(Enum):
        CHOOSE_CAMERA = "CCAM"  # = Choose camera to stream
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
    def turn_right(duration: float):
        return PICommunication.__format_message(PICommunication.MessageCode.TURN_RIGHT, str(duration).encode())

    @staticmethod
    def turn_left(duration: float):
        return PICommunication.__format_message(PICommunication.MessageCode.TURN_LEFT, str(duration).encode())

    @staticmethod
    def choose_camera(camera: str):
        return PICommunication.__format_message(PICommunication.MessageCode.CHOOSE_CAMERA, camera.encode())

    @staticmethod
    def error(error_message: str):
        return PICommunication.__format_message(PICommunication.MessageCode.ERROR, error_message.encode())

    @staticmethod
    def disconnect(exit_code: str):
        return PICommunication.__format_message(PICommunication.MessageCode.DISCONNECT, exit_code.encode())

    @staticmethod
    def __format_message(code: MessageCode, content: bytes):
        code_value = code.value
        return code_value.encode() + content

    @staticmethod
    def parse_message(message: bytes):
        message = message.decode()
        code = message[:PICommunication.msg_code_size]
        content = message[PICommunication.msg_code_size:]
        return PICommunication.MessageCode(code), content
