import os
import json
import zipfile
from flask import Flask, request, jsonify, send_file
from recorder2 import main


LOCK = False

app = Flask(__name__,
            static_folder='static')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/html2pdf', methods=['POST'])
def html2pdf():
    output_dir = 'output'
    zip_filename = 'output.zip'
    try:
        os.remove(zip_filename)
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                os.remove(os.path.join(root, file))
    except FileNotFoundError:
        pass

    global LOCK
    if LOCK:
        return jsonify({"status": "busy"}), 400
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        links = data['links']

        main(username, password, links)
        # Create a zip archive of the output directory

        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_dir))
        return send_file(zip_filename, as_attachment=True)
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    except KeyError:
        return jsonify({"status": "error", "message": "Missing required fields: username, password, links"}), 400
    except Exception:
        return jsonify({"status": "error", "message": "Grabbing pages failed"}), 400
    finally:
        LOCK = False



if __name__ == '__main__':
    app.run(debug=True)