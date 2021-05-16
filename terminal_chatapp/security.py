import json

from cryptography.fernet import Fernet


class Security:
    '''
    Cryptography for Terminal Chat Application.
    '''

    def __init__(self, key):
        self.fernet = Fernet(key)
    

    def encrypt(self, message, digest_count=3):
        '''
        Encrypts the `message` based on `digestion_count`.
        '''
        # Make the message to be an instance of bytes if 
        # its just str.
        if not isinstance(message, bytes):
            message = message.encode()
        for index, _ in enumerate(range(digest_count)):
            if index == 0:
                encrypted_message = self.fernet.encrypt(message)
                continue
            encrypted_message = self.fernet.encrypt(encrypted_message)
        return encrypted_message
    

    def decrypt(self, encrypted_message, digest_count=3):
        '''
        Decrypts the `encrypted_message` based on `digestion_count`.
        '''
        # Make the encrypted_message to be an instance of bytes if 
        # its just str.
        if not isinstance(encrypted_message, bytes):
            encrypted_message = encrypted_message.encode()
        for index, _ in enumerate(range(digest_count)):
            if index == 0:
                decrypted_message = self.fernet.decrypt(encrypted_message)
                continue
            decrypted_message = self.fernet.decrypt(decrypted_message)
        return decrypted_message
    
    
    def encrypt_event(self, type, digest_count=3, **kwargs):
        '''
        Returns an encrypted event.
        '''
        event = json.dumps({'type': type, **kwargs})
        encrypted_event = self.encrypt(event, digest_count)
        return encrypted_event
    

    def decrypt_event(self, encrypted_event, digest_count=3, **kwargs):
        '''
        Returns an decrypted event.
        '''
        return json.loads(self.decrypt_event(encrypted_event, digest_count))


    @classmethod
    def generate_key(cls):
        '''
        Generates key using `Fernet.generate_key()`. So that, you don't
        need to import `Fernet` from cryptography.
        '''
        return Fernet.generate_key()