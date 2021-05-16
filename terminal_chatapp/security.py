from cryptography.fernet import Fernet, InvalidToken


class Security:
    '''
    Cryptography for Terminal Chat Application.
    '''

    def __init__(self, key, digest_count):
        self.fernet = Fernet(key)
        self.digest_count = digest_count
    

    def encrypt(self, message):
        '''
        Encrypts the `message` based on `self.digest_count`.

        `message` can be an instance of bytes, str, or int.
        '''

        # Make the message to be an instance of bytes if 
        # its just str or int.
        if not isinstance(message, bytes):
            if isinstance(message, int):
                message = str(message)
            message = message.encode()

        for index, _ in enumerate(range(self.digest_count)):
            if index == 0:
                encrypted_message = self.fernet.encrypt(message)
                continue
            encrypted_message = self.fernet.encrypt(encrypted_message)
        return encrypted_message
    

    def decrypt(self, encrypted_message):
        '''
        Decrypts the `encrypted_message` based on `self.digest_count`.

        `encrypted_message` can be an instance of bytes or str.
        '''

        # Make the `encrypted_message` to be an instance of bytes if 
        # its just str.
        if not isinstance(encrypted_message, bytes):
            encrypted_message = encrypted_message.encode()

        try:
            for index, _ in enumerate(range(self.digest_count)):
                if index == 0:
                    decrypted_message = self.fernet.decrypt(encrypted_message)
                    continue
                decrypted_message = self.fernet.decrypt(decrypted_message)
            return decrypted_message
        except InvalidToken:
            # Return None if `encrypted_message` can't be encrypted.
            # This is to avoid using the try...except... statement
            # when using this.
            return None