from cryptography.fernet import Fernet

def generate_cipher_key(filename='cipher.key'):
    """Generate a new key and save it into a file."""
    key = Fernet.generate_key()
    with open(filename, 'wb') as key_file:
        key_file.write(key)
    print(f"Key generated and saved to {filename}")

if __name__ == '__main__':
    generate_cipher_key()
