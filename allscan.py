import os
import json
import csv
import platform
import subprocess
import psutil
from datetime import datetime, timedelta


SCAN_DIRECTORY = "C:\\"  # Change if needed

# File details
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

#  scan directories
def scan_directory(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for name in dirs + files:
            file_path = os.path.join(root, name)
            file_list.append(get_file_info(file_path))
    return file_list

# save results in JSON
def save_as_json(data, filename="combined_report.json"):
    try:
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"JSON report saved as {filename}")
    except Exception as e:
        print(f"Failed to save JSON report: {e}")

#  save results in CSV
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

# last password change date (Windows)
def get_last_password_change_windows():
    try:
        command = 'powershell "(Get-LocalUser -Name $env:UserName).PasswordLastSet"'
        output = subprocess.check_output(command, shell=True).decode().strip()

        if not output:
            return "Password change date not found"

        # Adjust the format string 
        last_changed_date = datetime.strptime(output, "%d %B %Y %I:%M:%S %p")
        return last_changed_date
    except Exception as e:
        return str(e)

#  if password was changed in the last 6 months
def check_password_age():
    last_changed = get_last_password_change_windows()

    if isinstance(last_changed, str):  
        return last_changed

    six_months_ago = datetime.now() - timedelta(days=180)

    if last_changed > six_months_ago:
        return f"Password is updated (Last changed: {last_changed})"
    else:
        return f"Password NOT changed in the last 6 months! (Last changed: {last_changed})"

#  check if Windows Hello PIN is enabled
def is_pin_enabled():
    try:
        command = 'powershell "Get-LocalUser -Name $env:UserName | Select-Object PasswordRequired"'
        output = subprocess.check_output(command, shell=True).decode().strip()

        if "True" in output:
            return "Windows Hello PIN is enabled"
        else:
            return "Windows Hello PIN is not enabled"
    except Exception as e:
        return str(e)

#  get hard disk information
def get_disk_info():
    disk_info = []
    partitions = psutil.disk_partitions()

    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append({
                "Drive": partition.device,
                "Total Space (GB)": round(usage.total / (1024**3), 2),
                "Used Space (GB)": round(usage.used / (1024**3), 2),
                "Free Space (GB)": round(usage.free / (1024**3), 2),
                "File System": partition.fstype
            })
        except Exception as e:
            disk_info.append({"Drive": partition.device, "Error": str(e)})

    return disk_info

# get complete system information
def get_system_info():
    return {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Architecture": platform.architecture()[0],
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "RAM (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
        "Last Password Change Check": check_password_age(),
        "Windows Hello PIN Status": is_pin_enabled(),
        "Disk Information": get_disk_info()
    }

# flatten system information for CSV
def flatten_system_info(system_info):
    flattened_info = []
    for key, value in system_info.items():
        if isinstance(value, list):
            for item in value:
                flattened_info.append({**item, "Category": key})
        else:
            flattened_info.append({"Category": key, "Value": value})
    return flattened_info

# Main function
if __name__ == "__main__": 
    print(f"Scanning {SCAN_DIRECTORY} ...")
    scanned_data = scan_directory(SCAN_DIRECTORY)
    print("Gathering system information...")
    system_info = get_system_info()
    combined_data = {
        "File Scan": scanned_data,
        "System Information": system_info
    }
    save_as_json(combined_data, "combined_report.json")
    flattened_system_info = flatten_system_info(system_info)
    save_as_csv(scanned_data + flattened_system_info, "combined_report.csv")
    print("Scan completed! Check the reports for details.")
