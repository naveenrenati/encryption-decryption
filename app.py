from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
import os
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

if not os.path.exists('static'):
    os.makedirs('static')


def load_cipher_key(filename='cipher.key'):
    """Load the cipher key from a file."""
    with open(filename, 'rb') as key_file:
        return key_file.read()

key = load_cipher_key()
cipher = Fernet(key)



def delete_file_later(file_path, delay=5):
    """Delete a file after a specified delay in seconds."""
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

            # Read the image file in binary mode
            with open(file_path, 'rb') as f:
                image_data = f.read()

            # Encrypt the image data
            encrypted_data = cipher.encrypt(image_data)
            encrypted_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encrypted.enc')

            # Save the encrypted data
            with open(encrypted_file_path, 'wb') as f:
                f.write(encrypted_data)

            # Delete the original uploaded file
            os.remove(file_path)

            # Schedule deletion of the encrypted file after download
            delete_file_later(encrypted_file_path)

            # Serve the encrypted file to the client
            return jsonify({'file_url': url_for('static', filename='encrypted.enc')})

    return render_template('encryption.html')

@app.route('/decryption', methods=['GET', 'POST'])
def decryption():
    if request.method == 'POST':
        file = request.files['encrypted_file']
        if file:
            filename = secure_filename(file.filename)
            encrypted_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(encrypted_file_path)

            # Read the encrypted file
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()

            # Decrypt the data
            try:
                decrypted_data = cipher.decrypt(encrypted_data)
                decrypted_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'decrypted.png')

                # Save the decrypted image
                with open(decrypted_file_path, 'wb') as f:
                    f.write(decrypted_data)

                # Delete the uploaded encrypted file
                os.remove(encrypted_file_path)

                # Schedule deletion of the decrypted file after download
                delete_file_later(decrypted_file_path)

                # Serve the decrypted file to the client
                return jsonify({'file_url': url_for('static', filename='decrypted.png')})
            except Exception as e:
                return f"Decryption failed: {str(e)}"

    return render_template('decryption.html')

if __name__ == '__main__':
    app.run(debug=True)
