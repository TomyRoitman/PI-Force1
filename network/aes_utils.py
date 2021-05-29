from Crypto.Cipher import AES
import base64
from Crypto import Random


class AESCipher(object):

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = key
        print("AES Key: ", key)

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        print(enc)
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        print(chr(self.bs - len(s) % self.bs).encode())
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs).encode()

    @staticmethod
    def _unpad(s):
        padding_size = int(s[-1])
        return s[: len(s) - padding_size]
