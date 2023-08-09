from flask import Flask, render_template, request, send_file
import subprocess

import os

# Get the absolute path of the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script's location
os.chdir(script_dir)


app = Flask(__name__)
app.config['DEBUG'] = True
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file1 = request.files['file1']
    file2 = request.files['file2']
    file3 = request.files['file3']

    file1.save('Plan.xlsx')
    file2.save('Prduction.xlsx')
    file3.save('stock.xlsx')

    # Run your manipulation script (man.py) using subprocess
    subprocess.run(['python', 'man.py'])

    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    return send_file(f'./{filename}', as_attachment=True)

if __name__ == '__main__':
    app.run()
