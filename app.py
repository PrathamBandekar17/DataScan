import os
import json
import csv
import platform
import subprocess
import psutil
from datetime import datetime, timedelta
from flask import Flask, jsonify, request

app = Flask(__name__)

# Directory to scan
SCAN_DIRECTORY = "C:\\"  # Change if needed

# Get file details
def get_file_info(file_path):
    try:
        file_stats = os.stat(file_path)
        return {
            "File Name": os.path.basename(file_path),
            "Path": file_path,
            "Size (KB)": round(file_stats.st_size / 1024, 2),
            "Created On": datetime.fromtimestamp(file_stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "Modified On": datetime.fromtimestamp(file_stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "Type": "Folder" if os.path.isdir(file_path) else "File"
        }
    except Exception as e:
        return {"File Name": file_path, "Error": str(e)}

# Scan directories recursively
def scan_directory(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for name in dirs + files:
            file_path = os.path.join(root, name)
            file_list.append(get_file_info(file_path))
    return file_list

# Store scanned data in memory
scanned_data = scan_directory(SCAN_DIRECTORY)

@app.route('/scan', methods=['GET'])
def scan():
    return jsonify(scanned_data)

@app.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('term', '').strip()
    if not search_term:
        return jsonify({"error": "Search term is required"}), 400

    filtered_results = [entry for entry in scanned_data if search_term.lower() in entry["File Name"].lower()]
    return jsonify(filtered_results) if filtered_results else jsonify({"message": "No matching files or folders found."}), 404

if __name__ == "__main__":
    app.run(debug=True)
