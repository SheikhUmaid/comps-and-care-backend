import requests
import os
import random
import string
from datetime import datetime

# Step 1: Create random file (~300 KB)
def create_random_file(filename, size_kb=302):
    with open(filename, "w") as f:
        for _ in range(size_kb * 10):
            f.write(''.join(random.choices(string.ascii_letters + string.digits, k=100)) + '\n')

# Create dummy files
create_random_file("vehicle_registration_doc.txt")
create_random_file("driver_license.txt")
create_random_file("vehicle_insurance.txt")

# Endpoint
url = "http://82.25.104.152/auth_api/document-upload/"

# Track total upload size
total_bytes_sent = 0
log_file = "upload_log.txt"

# Clear or create log file
with open(log_file, "w") as log:
    log.write("Upload Log Started at: " + str(datetime.now()) + "\n\n")

try:
    while True:
        random_plate = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        data = {
            "license_plate_number": random_plate,
            "user_id": "12"
        }

        file_paths = {
            "vehicle_registration_doc": "vehicle_registration_doc.txt",
            "driver_license": "driver_license.txt",
            "vehicle_insurance": "vehicle_insurance.txt"
        }

        files = {k: open(v, "rb") for k, v in file_paths.items()}
        current_upload_size = sum(os.path.getsize(p) for p in file_paths.values())
        total_bytes_sent += current_upload_size

        print(f"Generated Plate: {random_plate}")
        print(f"Current Upload: {current_upload_size / 1024:.2f} KB")
        print(f"Total Data Sent: {total_bytes_sent / 1024:.2f} KB")

        response = requests.post(url, data=data, files=files)

        # Save log
        with open(log_file, "a") as log:
            log.write(f"Time: {datetime.now()}\n")
            log.write(f"Plate: {random_plate}\n")
            log.write(f"Upload Size: {current_upload_size / 1024:.2f} KB\n")
            log.write(f"Total Sent: {total_bytes_sent / 1024:.2f} KB\n")
            log.write(f"Status Code: {response.status_code}\n")
            try:
                log.write(f"Response: {response.json()}\n")
            except:
                log.write(f"Response Text: {response.text}\n")
            log.write("-" * 50 + "\n")

        for f in files.values():
            f.close()

except KeyboardInterrupt:
    print("Stopped. Cleaning up...")

# Final cleanup
os.remove("vehicle_registration_doc.txt")
os.remove("driver_license.txt")
os.remove("vehicle_insurance.txt")
