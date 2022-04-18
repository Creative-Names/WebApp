from cryptography.fernet import Fernet
import sys

with open('assets/password.txt', 'r') as f:
    ENC_KEY = f.read()[-44:]
    # ENC_KEY = 'OW_2k1EhxOLEm4Es3O8vheRbzFQyW8blqITOFtRv49s='

try:
    fernet = Fernet(ENC_KEY)
except ValueError as e:
    print(e)
    print("WRONG KEY")
    sys.exit()


def encrypt_file(filename):
    if filename == 'assets/password.txt':
        
        with open(filename, 'rb') as file:
            original = file.read()
            
        encrypted = fernet.encrypt(original)
        
        with open(filename, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
        with open(filename, 'a') as f:
            f.write(ENC_KEY)
            
    else:
        with open(filename, 'rb') as file:
            original = file.read()

        encrypted = fernet.encrypt(original)
        
        with open(filename, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)

def decrypt_file(filename):
    if filename == 'assets/password.txt':
        
        with open(filename, 'r') as enc_file:
            encrypted = enc_file.read()[:-44]
            
        with open(filename, 'w') as enc_file:
            enc_file.write(encrypted)
            
        with open(filename, 'rb') as enc_file:
            encrypted = enc_file.read()
            
        decrypted = fernet.decrypt(encrypted)

        with open(filename, 'wb') as encrypted_file:
            encrypted_file.write(decrypted)
    else:
        with open(filename, 'rb') as enc_file:
            encrypted = enc_file.read()
                
        decrypted = fernet.decrypt(encrypted)

        with open(filename, 'wb') as encrypted_file:
            encrypted_file.write(decrypted)


