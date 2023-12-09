import io
import base64
import zlib
import json
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

class DecryptService:

    def __init__(self,
                public_key_location: str=None,
                private_key_location: str=None) -> None:
        
        self.padding_function = padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                algorithm=hashes.SHA256(),
                                label=None)
        if public_key_location:
            self.public_key = self.__load_public_key__(public_key_location)
        if private_key_location:
            self.private_key_location = private_key_location
        self.B64_PREFIX = "b64:"

    def __load_public_key__(self,public_key_location) -> bytes:
        with open(public_key_location, "rb") as key_file:
            loaded_public_key = serialization.load_pem_public_key(key_file.read())
        return loaded_public_key

    def __load_private_key__(self) -> bytes:
        with open(self.private_key_location, "rb") as key_file:
            loaded_private_key = serialization.load_pem_private_key(key_file.read(),
                                                            password=None)
        return loaded_private_key

    def encrypt(self, values_to_encrypt: dict[str,bytes]) -> tuple:
        temp_dict = values_to_encrypt.copy()
        encryptor, encrypted_key = self.__prepare_encryptor__()
        for key, value in temp_dict.items():
            temp_dict[key] = encryptor.encrypt(zlib.compress(value))
            if not key=="image":
                try:
                    json.dumps(temp_dict[key])
                except Exception as err:
                    temp_dict[key] = self.B64_PREFIX+base64.b64encode(temp_dict[key]).decode()
        return temp_dict, base64.b64encode(encrypted_key).decode()

    def decrypt(self, encrypted_key, values_to_decrypt: dict[str,bytes]) -> dict[str, bytes]:
        temp_dict = values_to_decrypt.copy()
        loaded_private_key = self.__load_private_key__()
        encrypted_key=base64.b64decode(encrypted_key.encode())
        decrypted_key = loaded_private_key.decrypt(encrypted_key,self.padding_function)
        del loaded_private_key
        decryptor = Fernet(decrypted_key)
        del decrypted_key
        for key, value in temp_dict.items():
            if type(value) is str and value.startswith(self.B64_PREFIX):
                value=base64.b64decode(temp_dict[key][len(self.B64_PREFIX):].encode())
            try:
                temp_dict[key] = zlib.decompress(decryptor.decrypt(value))
            except InvalidToken:
                temp_dict[key] = decryptor.decrypt(zlib.decompress(value)) # For legacy support
        return temp_dict

    def __prepare_encryptor__(self):
        symmetric_key = Fernet.generate_key()
        encryptor = Fernet(symmetric_key)
        encrypted_key = self.public_key.encrypt(symmetric_key,self.padding_function)
        del symmetric_key
        return encryptor, encrypted_key