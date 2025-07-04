# This file is part of URL Status Checker.
#
# Copyright (C) 2024 Gabor VARGA
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import os
import json
from collections import OrderedDict
from flask import request, render_template, send_from_directory, jsonify, current_app as app

DATA_FILE = os.path.join(app.root_path, 'data', 'url_registry.json')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/data/<path:filename>')
def data_files(filename):
    return send_from_directory('data', filename)


@app.route('/add_url', methods=['POST'])
def add_url():
    data = request.get_json()
    if not data or 'url' not in data or 'name' not in data:
        return jsonify({"error": "Name and URL are required"}), 400

    new_website = OrderedDict(
        [('id', None), ('name', data['name']), ('url', data['url']), ('statuscd', data['statuscd']), ('statusmsg', data['statusmsg']), ('firstcheck', data['firstcheck']), ('lastcheck', data['lastcheck']), ('lastchange', data['lastchange']), ('totaldowntime', data['totaldowntime'])])

    try:
        with open(DATA_FILE, 'r+') as file:
            urls = json.load(file)
            new_website['id'] = max([url['id'] for url in urls] + [0]) + 1
            urls.append(new_website)
            file.seek(0)
            json.dump(urls, file, indent=4)
            file.truncate()
        return jsonify({"message": "URL added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/edit_url', methods=['PUT'])
def edit_url():
    data = request.get_json()
    if not data or 'id' not in data or 'url' not in data or 'name' not in data:
        return jsonify({"error": "ID, Name, and URL are required"}), 400

    try:
        with open(DATA_FILE, 'r+') as file:
            urls = json.load(file)
            for url in urls:
                if url['id'] == data['id']:
                    url['name'] = data['name']
                    url['url'] = data['url']
                    break
            else:
                return jsonify({"error": "URL not found"}), 404

            file.seek(0)
            json.dump(urls, file, indent=4)
            file.truncate()

        return jsonify({"message": "URL updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/delete_url', methods=['DELETE'])
def delete_url():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"error": "ID is required"}), 400

    delete_id = data['id']
    try:
        with open(DATA_FILE, 'r+') as file:
            urls = json.load(file)
            urls = [url for url in urls if url['id'] != delete_id]
            file.seek(0)
            json.dump(urls, file, indent=4)
            file.truncate()
        return jsonify({"message": "URL deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def validate_data(data):
    for entry in data:
        if not all(key in entry for key in ['id', 'name', 'url', 'statuscd', 'statusmsg', 'firstcheck', 'lastcheck', 'lastchange', 'totaldowntime']):
            return False
        if not isinstance(entry['id'], int) or not isinstance(entry['name'], str) or not isinstance(entry['url'], str) or not isinstance(entry['statuscd'], str) or not isinstance(entry['statusmsg'], str) or not isinstance(entry['firstcheck'], str) or not isinstance(entry['lastcheck'], str) or not isinstance(entry['lastchange'], str) or not isinstance(entry['totaldowntime'], str):
            return False
    return True


@app.route('/import_url_registry', methods=['POST'])
def import_url_registry():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    # Check the file type
    if not file.filename.endswith('.json'):
        return jsonify({"error": "Only JSON files can be uploaded"}), 400

    if file.mimetype != 'application/json':
        return jsonify({"error": "Invalid file type"}), 400

    try:
        imported_data = json.load(file)

        # Validate the data
        if not validate_data(imported_data):
            return jsonify({"error": "Invalid data structure"}), 400

        # Overwrite the file on the server
        with open(DATA_FILE, 'w') as f:
            json.dump(imported_data, f, indent=4)

        return jsonify({"message": "Import successful!"}), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON file"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/reset_url', methods=['PUT'])
def reset_url():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"error": "ID is required"}), 400

    reset_id = data['id']
    try:
        with open(DATA_FILE, 'r+') as file:
            urls = json.load(file)
            for url in urls:
                if url['id'] == reset_id:
                    url['statuscd'] = "N/A"
                    url['statusmsg'] = "N/A"
                    url['firstcheck'] = "N/A"
                    url['lastcheck'] = "N/A"
                    url['lastchange'] = "N/A"
                    url['totaldowntime'] = "N/A"
                    break
            else:
                return jsonify({"error": "URL not found"}), 404

            file.seek(0)
            json.dump(urls, file, indent=4)
            file.truncate()

        return jsonify({"message": "Status reset successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
