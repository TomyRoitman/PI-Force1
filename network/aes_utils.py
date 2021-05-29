from Crypto.Cipher import AES
import base64
from Crypto import Random


class AESCipher(object):

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = key
        print("AES Key: ", key)

    def encrypt(self, raw):
        print(raw)
        raw = self._pad(raw)
        print("Padded: ", raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        print(enc)
        enc = base64.b64decode(enc)
        print("b64 Decoded: ", enc)
        iv = enc[:AES.block_size]
        print(len(enc), len(iv))
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        print(cipher.decrypt(enc[AES.block_size:]))
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        print(chr(self.bs - len(s) % self.bs).encode())
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs).encode()

    @staticmethod
    def _unpad(s):
        print(s[len(s) - 1:])
        return s[:-ord(s[len(s) - 1:].decode())]
