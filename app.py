from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import hmac
import os
import threading
from Crypto.Random import get_random_bytes

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

if not os.path.exists('static'):
    os.makedirs('static')


def load_key(filename):
    with open(filename, 'rb') as key_file:
        return key_file.read()

folder_path = 'keys'

# Load AES keys and HMAC key from the keys folder
aes_key1 = load_key(os.path.join(folder_path, 'aes1.key'))
aes_key2 = load_key(os.path.join(folder_path, 'aes2.key'))
hmac_key = load_key(os.path.join(folder_path, 'hmac.key'))


def encrypt_with_aes(data, key):
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return cipher.nonce + tag + ciphertext  


def hmac_sign(data):
    return hmac.new(hmac_key, data, SHA256).digest()


def delete_file_later(file_path, delay=5):
    def delete_file():
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
    
    timer = threading.Timer(delay, delete_file)
    timer.start()


@app.route('/')
def index():
    return redirect(url_for('encryption'))


@app.route('/encryption', methods=['GET', 'POST'])
def encryption():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            with open(file_path, 'rb') as f:
                image_data = f.read()

            # Encrypt with the first AES key as Developer bhanu said :)
            first_encryption = encrypt_with_aes(image_data, aes_key1)
            print("1st time encryption completed as Developer bhanu said :)")

            # Encrypt the first encrypted data with the second AES key as  Developer banu said :)
            second_encryption = encrypt_with_aes(first_encryption, aes_key2)
            print("2st time encryption completed as Developer bhanu said :)")

            # Generate HMAC of the double-encrypted data as Developer bhanu said :)
            hmac_signature = hmac_sign(second_encryption)

            final_output = hmac_signature + second_encryption  
            print("3rd time encryption completed as Developer bhanu said :)")

            output_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.enc')
            with open(output_file_path, 'wb') as f:
                f.write(final_output)

            os.remove(file_path)

            delete_file_later(output_file_path)

            return jsonify({'file_url': url_for('static', filename='output.enc')})

    return render_template('encryption.html')


@app.route('/decryption', methods=['GET', 'POST'])
def decryption():
    if request.method == 'POST':
        file = request.files['encrypted_file']
        if file:
            filename = secure_filename(file.filename)
            encrypted_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(encrypted_file_path)

            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()

            hmac_signature = encrypted_data[:32]  
            data_to_verify = encrypted_data[32:]  

            if hmac.compare_digest(hmac_signature, hmac_sign(data_to_verify)):
                nonce = data_to_verify[:16]
                tag = data_to_verify[16:32]
                second_encrypted_data = data_to_verify[32:]

                cipher = AES.new(aes_key2, AES.MODE_GCM, nonce=nonce)
                first_encrypted_data = cipher.decrypt_and_verify(second_encrypted_data, tag)

                nonce = first_encrypted_data[:16]
                tag = first_encrypted_data[16:32]
                image_data = first_encrypted_data[32:]

                cipher = AES.new(aes_key1, AES.MODE_GCM, nonce=nonce)
                decrypted_data = cipher.decrypt_and_verify(image_data, tag)

                decrypted_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'decrypted_image.png')
                with open(decrypted_file_path, 'wb') as f:
                    f.write(decrypted_data)

                os.remove(encrypted_file_path)

                delete_file_later(decrypted_file_path)

                return jsonify({'file_url': url_for('static', filename='decrypted_image.png')})
            else:
                return "HMAC verification failed. Decryption not performed."

    return render_template('decryption.html')


if __name__ == '__main__':
    app.run(debug=True)
