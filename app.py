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
SCAN_DIRECTORY = "C:\\Users\prath\OneDrive\Documents"  # Change if needed

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

# Save results in JSON
def save_as_json(data, filename="combined_report.json"):
    try:
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"JSON report saved as {filename}")
    except Exception as e:
        print(f"Failed to save JSON report: {e}")

# Save results in CSV
def save_as_csv(data, filename="combined_report.csv"):
    try:
        keys = data[0].keys() if data else ["File Name", "Path", "Size (KB)", "Created On", "Modified On", "Type"]
        with open(filename, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        print(f"CSV report saved as {filename}")
    except Exception as e:
        print(f"Failed to save CSV report: {e}")

# Filter function to search for a file
def filter_results(data, search_term):
    return [entry for entry in data if search_term.lower() in entry["File Name"].lower()]

@app.route('/scan', methods=['GET'])
def scan():
    print(f"Scanning {SCAN_DIRECTORY} ...")
    scanned_data = scan_directory(SCAN_DIRECTORY)
    save_as_json(scanned_data, "file_scan_report.json")
    save_as_csv(scanned_data, "file_scan_report.csv")
    return jsonify(scanned_data)

@app.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('term', '').strip()
    if not search_term:
        return jsonify({"error": "Search term is required"}), 400

    scanned_data = scan_directory(SCAN_DIRECTORY)
    filtered_results = filter_results(scanned_data, search_term)
    if filtered_results:
        save_as_json(filtered_results, "filtered_results.json")
        save_as_csv(filtered_results, "filtered_results.csv")
        return jsonify(filtered_results)
    else:
        return jsonify({"message": "No matching files or folders found."}), 404

if __name__ == "__main__":
    app.run(debug=True)