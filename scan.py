import os
import json
import csv
from datetime import datetime


SCAN_DIRECTORY = "C:\\"  # Change this if needed


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

def scan_directory(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for name in dirs + files:
            file_path = os.path.join(root, name)
            if os.path.commonpath([directory, file_path]) == os.path.abspath(directory):
                file_list.append(get_file_info(file_path))
    return file_list

def save_as_json(data, filename="scan_report.json"):
    try:
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"JSON report saved as {filename}")
    except Exception as e:
        print(f"Failed to save JSON report: {e}")

def save_as_csv(data, filename="scan_report.csv"):
    try:
        keys = data[0].keys() if data else ["File Name", "Path", "Size (KB)", "Created On", "Modified On", "Type"]
        with open(filename, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        print(f"CSV report saved as {filename}")
    except Exception as e:
        print(f"Failed to save CSV report: {e}")

if __name__ == "__main__":
    if not os.path.exists(SCAN_DIRECTORY):
        print(f"The directory {SCAN_DIRECTORY} does not exist.")
    else:
        print(f"Scanning {SCAN_DIRECTORY} ...")
        scanned_data = scan_directory(SCAN_DIRECTORY)
        save_as_json(scanned_data)
        save_as_csv(scanned_data)
        print("Scan completed! Check the reports for details.")
