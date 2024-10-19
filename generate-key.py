import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def generate_aes_key():
    return get_random_bytes(16) 

def generate_hmac_key():

    return get_random_bytes(32)  

def save_key_to_file(key, filename):
    with open(filename, 'wb') as key_file:
        key_file.write(key)

def main():
    aes_key1 = generate_aes_key()
    aes_key2 = generate_aes_key()
    hmac_key = generate_hmac_key()

    folder_path = 'keys'

    os.makedirs(folder_path, exist_ok=True)

    save_key_to_file(aes_key1, os.path.join(folder_path, 'aes1.key'))
    save_key_to_file(aes_key2, os.path.join(folder_path, 'aes2.key'))
    save_key_to_file(hmac_key, os.path.join(folder_path, 'hmac.key'))

    print("Keys generated and saved to files:")
    print("AES1 Key: aes1.key")
    print("AES2 Key: aes2.key")
    print("HMAC Key: hmac.key")

if __name__ == '__main__':
    main()
