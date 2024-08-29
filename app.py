from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import os
import pandas as pd
import cv2  # Import OpenCV

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CSV_PATH = 'colors.csv'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_color_name(R, G, B):
    index = ["color", "color_name", "hex", "R", "G", "B"]
    csv = pd.read_csv(CSV_PATH, names=index, header=None)
    minimum = 10000
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if d <= minimum:
            minimum = d
            cname = csv.loc[i, "color_name"]
    return cname

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Here you should add code to store user details securely (e.g., hashing passwords and storing in a database)
        session['username'] = username  # Simulating a successful sign-up
        return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Here you should add code to verify user credentials
        session['username'] = username  # Simulating a successful login
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return redirect(request.url)
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    img = cv2.imread(filepath)
    height, width, _ = img.shape
    center_x, center_y = width // 2, height // 2
    b, g, r = img[center_y, center_x]
    
    color_name = get_color_name(r, g, b)
    return render_template('result.html', image_file=filename, color_name=color_name, r=int(r), g=int(g), b=int(b))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/get_color', methods=['POST'])
def get_color():
    data = request.json
    img_path = os.path.join(UPLOAD_FOLDER, data['image'])
    x, y = int(data['x']), int(data['y'])
    
    img = cv2.imread(img_path)  # Ensure OpenCV is used to read the image
    if img is None:
        return jsonify({'error': 'Image not found or cannot be read'}), 404
    
    b, g, r = img[y, x]
    color_name = get_color_name(r, g, b)
    
    return jsonify({
        'color_name': color_name,
        'R': int(r),
        'G': int(g),
        'B': int(b)
    })
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
