from Crypto.Cipher import AES
import base64
from Crypto import Random


class AESCipher(object):

    def __init__(self, key):
        """
        Initialize an AESCipher object
        :param key:
        """
        self.bs = AES.block_size
        self.key = key

    def encrypt(self, raw):
        """
        Encrypt message of bytes type in AES encryption.
        :param raw:
        :return: Message encrypted in aes. type: bytes.
        """
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        """
        Decrypt message of bytes type in AES encryption.
        :param enc:
        :return: Message decrypted with aes. type: bytes.
        """
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        """
        Pad message to the size of self.bs
        :param s:
        :return: padded message
        """
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs).encode()

    @staticmethod
    def _unpad(s):
        """
        Unpad message to get original message
        :param s:
        :return: unpadded message
        """
        padding_size = int(s[-1])
        return s[: len(s) - padding_size]
