from flask import Flask, render_template, request, send_file, redirect, session, url_for
import subprocess
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = '124qz53'  # Replace with a strong secret key

# Get the absolute path of the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script's location
os.chdir(script_dir)
@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response
# Valid login credentials (replace with your actual login details)
VALID_CREDENTIALS = {
    'anurag': '7@Anurag',
    'username2': 'password2'
}

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html')
    else:
        return render_template('login.html')
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password:
        session['username'] = username
        return redirect('/')
    else:
        return render_template('login.html', error_message='Invalid login credentials')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')
@app.route('/upload', methods=['POST'])
def upload():
    if 'username' in session:
        file1 = request.files['file1']
        file2 = request.files['file2']
        file3 = request.files['file3']

        file1.save('Plan.xlsx')
        file2.save('Prduction.xlsx')
        file3.save('stock.xlsx')

        # Run your manipulation script (man.py) using subprocess
        subprocess.run(['python', 'man.py'])

        return render_template('index.html', message='Files uploaded and processed successfully!')
    else:
        return redirect('/')

@app.route('/download/<filename>')
def download(filename):
    if 'username' in session:
        return send_file(filename, as_attachment=True)
    else:
        return redirect('/')

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=80)
    app.run()

