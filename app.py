import os
import subprocess
import socket
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from urllib.parse import quote
import re
import datetime

try:
    import nmap
except ImportError:
    nmap = None

app = Flask(__name__)

# --- CONFIGURATION ---
API_SECRET_KEY = "pogiako" 
UPLOAD_FOLDER = 'uploads'
PULLED_FILES_FOLDER = 'pulled_files'
RECORDINGS_FOLDER = 'recordings'
# NEW: Define the D: drive as the base for all backups
BACKUP_BASE_DRIVE = 'D:\\'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PULLED_FILES_FOLDER'] = PULLED_FILES_FOLDER
app.config['RECORDINGS_FOLDER'] = RECORDINGS_FOLDER
# --- END CONFIGURATION ---

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PULLED_FILES_FOLDER, exist_ok=True)
os.makedirs(RECORDINGS_FOLDER, exist_ok=True)
# NEW: Ensure the base backup directory exists on the D: drive
os.makedirs(os.path.join(BACKUP_BASE_DRIVE, 'NexusPanel_Backups'), exist_ok=True)
os.makedirs(os.path.join(BACKUP_BASE_DRIVE, 'NexusPanel_Photos'), exist_ok=True)

active_process = None

# --- Helper Functions (Unchanged) ---
def is_authorized(req):
    return req.headers.get("X-Api-Key") == API_SECRET_KEY

def run_command(command, timeout=30):
    try:
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.run(
            command, capture_output=True, text=True, timeout=timeout, check=False, startupinfo=startupinfo, encoding='utf-8', errors='ignore'
        )
        output = (process.stdout or "") + (process.stderr or "")
        return process.returncode == 0, output.strip()
    except Exception as e: return False, f"An unexpected error occurred: {e}"

def get_connected_device():
    success, output = run_command(["adb", "devices"])
    if not success: return None
    lines = output.strip().split('\n')[1:]
    for line in lines:
        if '\tdevice' in line: return line.split('\t')[0]
    return None

# --- Main App Routes ---
@app.route('/')
def index(): return render_template('index.html')

# --- NEW Backup & Media Routes ---
@app.route('/backup_device', methods=['POST'])
def backup_device():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    device_id = get_connected_device()
    if not device_id: return jsonify({"status": "error", "message": "No device connected."}), 400

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_folder = os.path.join(BACKUP_BASE_DRIVE, 'NexusPanel_Backups')
    filename = f"full_backup_{timestamp}.ab"
    pc_path = os.path.join(backup_folder, filename)

    # The 'adb backup' command. -all includes all apps. -f specifies the output file.
    # This command can be very slow, so we set a very long timeout.
    # Note: This command does not produce much stdout, success is determined by the return code.
    command = ["adb", "-s", device_id, "backup", "-all", "-f", pc_path]
    success, output = run_command(command, timeout=3600) # 1 hour timeout

    if success:
        return jsonify({"status": "success", "message": f"Backup process finished. File saved to {pc_path}"})
    else:
        # Check if the file was created but is empty, which can happen if the user cancels on the phone
        if os.path.exists(pc_path) and os.path.getsize(pc_path) == 0:
            os.remove(pc_path)
            return jsonify({"status": "error", "message": "Backup was cancelled or failed on the device."})
        return jsonify({"status": "error", "message": f"Backup failed: {output}"})

@app.route('/download_photos', methods=['POST'])
def download_photos():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    device_id = get_connected_device()
    if not device_id: return jsonify({"status": "error", "message": "No device connected."}), 400

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    pc_folder_path = os.path.join(BACKUP_BASE_DRIVE, 'NexusPanel_Photos', f"Photos_{timestamp}")
    os.makedirs(pc_folder_path, exist_ok=True)

    phone_camera_path = "/sdcard/DCIM/Camera/"
    
    # This command can also be slow, so a long timeout is good.
    command = ["adb", "-s", device_id, "pull", phone_camera_path, pc_folder_path]
    success, output = run_command(command, timeout=1800) # 30 minute timeout

    if success:
        # Count the number of files pulled for a better message
        files_pulled = len(os.listdir(pc_folder_path))
        return jsonify({"status": "success", "message": f"Successfully pulled {files_pulled} items to {pc_folder_path}"})
    return jsonify({"status": "error", "message": f"Failed to download photos: {output}"})


# --- Security & Health Routes ---
@app.route('/clear_caches', methods=['POST'])
def clear_caches():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    device_id = get_connected_device()
    if not device_id: return jsonify({"status": "error", "message": "No device connected."}), 400
    success, output = run_command(["adb", "-s", device_id, "shell", "pm", "trim-caches", "999999999M"], timeout=120)
    if success: return jsonify({"status": "success", "message": "Successfully cleared application caches."})
    return jsonify({"status": "error", "message": f"Failed to clear caches: {output}"})

@app.route('/security_audit', methods=['POST'])
def security_audit():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    device_id = get_connected_device()
    if not device_id: return jsonify({"status": "error", "message": "No device connected."}), 400
    audit_results = []
    _, output_unknown = run_command(["adb", "-s", device_id, "shell", "settings", "get", "secure", "install_non_market_apps"])
    if output_unknown == '1':
        audit_results.append({"level": "warning", "check": "Unknown Sources", "details": "ENABLED. This allows app installation from outside the Play Store, which is a security risk."})
    else:
        audit_results.append({"level": "good", "check": "Unknown Sources", "details": "DISABLED. Apps can only be installed from the Play Store."})
    _, output_adb = run_command(["adb", "-s", device_id, "shell", "settings", "get", "global", "adb_enabled"])
    if output_adb == '1':
        audit_results.append({"level": "warning", "check": "USB Debugging", "details": "ENABLED. This is a security risk if your device is lost or stolen."})
    else:
        audit_results.append({"level": "good", "check": "USB Debugging", "details": "DISABLED. Good for daily use."})
    return jsonify({"status": "success", "results": audit_results})

@app.route('/get_connections', methods=['POST'])
def get_connections():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    device_id = get_connected_device()
    if not device_id: return jsonify({"status": "error", "message": "No device connected."}), 400
    success, output = run_command(["adb", "-s", device_id, "shell", "netstat", "-tnp"])
    if success: return jsonify({"status": "success", "connections": output})
    return jsonify({"status": "error", "message": f"Could not get connections: {output}"})

# --- GOD Mode Routes ---
@app.route('/process_manager', methods=['POST'])
def process_manager():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    device_id = get_connected_device()
    if not device_id: return jsonify({"error": "No device connected."}), 400
    data = request.json
    action = data.get('action')
    package_name = data.get('package_name')
    if action == 'list':
        success, output = run_command(["adb", "-s", device_id, "shell", "ps", "-A"])
        if success: return jsonify({"status": "success", "processes": output})
        return jsonify({"status": "error", "message": "Could not list processes."})
    elif action == 'kill':
        if not package_name: return jsonify({"error": "Package name required."}), 400
        success, output = run_command(["adb", "-s", device_id, "shell", "am", "force-stop", package_name])
        message = f"Attempted to force-stop {package_name}." if success else f"Failed to force-stop: {output}"
        return jsonify({"status": "success" if success else "error", "message": message})
    return jsonify({"error": "Invalid process action."}), 400

@app.route('/execute_shell', methods=['POST'])
def execute_shell():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    device_id = get_connected_device()
    if not device_id: return jsonify({"error": "No device connected."}), 400
    command_to_run = request.json.get('command')
    if not command_to_run: return jsonify({"error": "No command provided."}), 400
    full_command = ["adb", "-s", device_id, "shell"] + command_to_run.split()
    success, output = run_command(full_command, timeout=60)
    return jsonify({"status": "success", "output": output or "(No output)"})

# --- Other Routes (Info, Actions, etc.) ---
@app.route('/get_device_info', methods=['POST'])
def get_device_info():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    device_id = get_connected_device()
    if not device_id: return jsonify({"status": "error", "message": "No device connected."}), 400
    props = ["ro.product.model", "ro.build.version.release", "ro.serialno"]
    info = {}
    for prop in props:
        _, output = run_command(["adb", "-s", device_id, "shell", "getprop", prop])
        info[prop] = output
    _, battery_output = run_command(["adb", "-s", device_id, "shell", "dumpsys", "battery"])
    level_match = re.search(r'level: (\d+)', battery_output)
    status_match = re.search(r'status: (\d+)', battery_output)
    battery_status_codes = {"1": "Unknown", "2": "Charging", "3": "Discharging", "4": "Not charging", "5": "Full"}
    info['battery_level'] = level_match.group(1) if level_match else "N/A"
    info['battery_status'] = battery_status_codes.get(status_match.group(1), "N/A") if status_match else "N/A"
    _, cpu_output = run_command(["adb", "-s", device_id, "shell", "cat", "/proc/cpuinfo"])
    cpu_model_match = re.search(r'Hardware\s+:\s+(.*)', cpu_output)
    info['cpu'] = cpu_model_match.group(1).strip() if cpu_model_match else "N/A"
    _, mem_output = run_command(["adb", "-s", device_id, "shell", "cat", "/proc/meminfo"])
    mem_total_match = re.search(r'MemTotal:\s+(\d+)\s+kB', mem_output)
    info['ram'] = f"{int(mem_total_match.group(1)) // 1024} MB" if mem_total_match else "N/A"
    return jsonify({
        "status": "success", "model": info.get("ro.product.model"), "android_version": info.get("ro.build.version.release"),
        "serial": info.get("ro.serialno"), "battery_level": info.get("battery_level"), "battery_status": info.get("battery_status"),
        "ip_address": device_id, "cpu": info.get("cpu"), "ram": info.get("ram")
    })

@app.route('/device_action', methods=['POST'])
def device_action():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    device_id = get_connected_device()
    if not device_id: return jsonify({"status": "error", "message": "No device connected."}), 400
    
    data = request.json
    action = data.get('action')
    value = data.get('value')
    cmd = ["adb", "-s", device_id]
    message = f"Action '{action}' executed."

    key_events = {"volume_up": "24", "volume_down": "25", "mute": "164", "power": "26"}

    if action == 'reboot':
        cmd.append('reboot')
    elif action == 'screenshot':
        screenshot_name = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        phone_path = f"/sdcard/{screenshot_name}"
        pc_path = os.path.join(app.config['PULLED_FILES_FOLDER'], screenshot_name)
        run_command(cmd + ["shell", "screencap", phone_path])
        run_command(cmd + ["pull", phone_path, pc_path])
        run_command(cmd + ["shell", "rm", phone_path])
        message = f"Screenshot saved to 'pulled_files'."
        return jsonify({"status": "success", "message": message})
    elif action == 'open_url':
        target_url = value if value else "https://www.google.com"
        if not target_url.startswith(('http://', 'https://')): target_url = 'https://' + target_url
        cmd.extend(['shell', 'am', 'start', '-a', 'android.intent.action.VIEW', '-d', target_url])
    elif action in key_events:
        cmd.extend(['shell', 'input', 'keyevent', key_events[action]])
    elif action == 'set_dark_mode':
        cmd.extend(["shell", "settings", "put", "secure", "ui_night_mode", str(value)])
    elif action == 'set_timeout':
        cmd.extend(["shell", "settings", "put", "system", "screen_off_timeout", str(value)])
    elif action == 'toggle_wifi':
        cmd.extend(["shell", "svc", "wifi", "toggle"])
        message = "Toggled Wi-Fi. You will be disconnected."
    elif action == 'launch_droidcam':
        cmd.extend(['shell', 'am', 'start', '-n', 'com.dev47apps.obsdroidcam/.MainActivity'])
        message = "Launched DroidCam OBS on phone. Now start the PC client."
    else: 
        return jsonify({"status": "error", "message": "Invalid action received."}), 400

    success, output = run_command(cmd)
    if success: 
        return jsonify({"status": "success", "message": message, "output": output})
    return jsonify({"status": "error", "message": f"Action failed: {output}"}), 500

@app.route('/launch_pc_client', methods=['POST'])
def launch_pc_client():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401

    # --- THIS IS YOUR CORRECT, FINAL PATH ---
    pc_client_path = "C:\\Program Files\\DroidCam\\Client\\bin\\64bit\\droidcam.exe"
    # --- END CONFIGURATION ---

    device_ip = request.json.get('ip')
    if not device_ip:
        return jsonify({"error": "Device IP not provided."}), 400

    if not os.path.exists(pc_client_path):
        return jsonify({"error": f"DroidCam client not found at path: {pc_client_path}. Please check the path in app.py."}), 500

    try:
        # --- THE FIX IS HERE ---
        # 1. Get the directory where the .exe is located
        pc_client_dir = os.path.dirname(pc_client_path)
        
        command = [pc_client_path, "-connect", device_ip, "4747"]
        
        # 2. Launch the process and tell it to use its own directory as the working directory
        subprocess.Popen(command, cwd=pc_client_dir)
        # --- END OF FIX ---
        
        return jsonify({"status": "success", "message": "Attempting to launch and connect DroidCam PC client."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to launch DroidCam client: {e}"}), 500
    
@app.route('/scan_network', methods=['POST'])
def scan_network():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    if nmap is None: return jsonify({"error": "'python-nmap' is not installed."}), 500
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        network_prefix = ".".join(local_ip.split('.')[:-1]) + ".0/24"
    except Exception: return jsonify({"error": "Could not determine local network."}), 500
    try:
        nm = nmap.PortScanner()
        nm.scan(hosts=network_prefix, arguments='-sn')
        hosts = []
        for host_ip in nm.all_hosts():
            mac_address = nm[host_ip].get('addresses', {}).get('mac', 'N/A')
            vendor = nm[host_ip]['vendor'].get(mac_address, 'Unknown') if mac_address != 'N/A' else 'N/A'
            hosts.append({"ip": host_ip, "vendor": vendor})
        return jsonify({"status": "success", "hosts": hosts})
    except nmap.nmap.PortScannerError: return jsonify({"error": "Nmap not found."}), 500
    except Exception as e: return jsonify({"error": f"Scan error: {e}"}), 500

@app.route('/connect', methods=['POST'])
def connect_device():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    ip_port = request.json.get('ip_port')
    run_command(["adb", "disconnect", ip_port]) 
    success, message = run_command(["adb", "connect", ip_port])
    if success and ("connected" in message or "already" in message):
        return jsonify({"status": "success", "message": f"Connected to {ip_port}!"})
    return jsonify({"status": "error", "message": message}), 500

@app.route('/start_mirror', methods=['POST'])
def start_mirror():
    global active_process
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    if active_process and active_process.poll() is None: return jsonify({"status": "error", "message": "Another process is active."}), 400
    device_id = get_connected_device()
    if not device_id: return jsonify({"status": "error", "message": "No device connected."}), 400
    command = ["scrcpy", "--serial", device_id, "--no-audio", "--video-bit-rate", "8M", "--max-size", "1280", "--window-title", f"Mirroring {device_id}"]
    try:
        active_process = subprocess.Popen(command)
        return jsonify({"status": "success", "message": "Mirroring started!"})
    except Exception as e: return jsonify({"status": "error", "message": f"An error occurred: {e}"}), 500

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global active_process
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    if active_process and active_process.poll() is None: return jsonify({"status": "error", "message": "Another process is active."}), 400
    device_id = get_connected_device()
    if not device_id: return jsonify({"status": "error", "message": "No device connected."}), 400
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"recording_{timestamp}.mp4"
    pc_path = os.path.join(app.config['RECORDINGS_FOLDER'], filename)
    command = ["scrcpy", "--serial", device_id, "--no-audio", "--record", pc_path, "--window-title", f"RECORDING - {device_id}"]
    try:
        active_process = subprocess.Popen(command)
        return jsonify({"status": "success", "message": f"Recording started! Saving to {pc_path}"})
    except Exception as e: return jsonify({"status": "error", "message": f"An error occurred: {e}"})

@app.route('/stop_mirror', methods=['POST'])
def stop_mirror():
    
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    global active_process
    if active_process:
        active_process.terminate()
        active_process = None
    return jsonify({"status": "success", "message": "Mirror/Record process stopped."})

@app.route('/list_apps', methods=['POST'])
def list_apps():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    device_id = get_connected_device()
    if not device_id: return jsonify({"status": "error", "message": "No device connected."}), 400
    success, output = run_command(["adb", "-s", device_id, "shell", "pm", "list", "packages", "-3"])
    if success:
        apps = [line.replace('package:', '').strip() for line in output.split('\n') if line]
        return jsonify({"status": "success", "apps": sorted(apps)})
    return jsonify({"status": "error", "message": "Could not list apps."})

@app.route('/uninstall_app', methods=['POST'])
def uninstall_app():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    device_id = get_connected_device()
    if not device_id: return jsonify({"status": "error", "message": "No device connected."}), 400
    package_name = request.json.get('package_name')
    if not package_name: return jsonify({"status": "error", "message": "No package name provided."}), 400
    success, output = run_command(["adb", "-s", device_id, "uninstall", package_name])
    if success and "Success" in output:
        return jsonify({"status": "success", "message": f"Successfully uninstalled {package_name}."})
    return jsonify({"status": "error", "message": f"Failed to uninstall: {output}"})
    
@app.route('/pull_file', methods=['POST'])
def pull_file():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    device_id = get_connected_device()
    if not device_id: return jsonify({"status": "error", "message": "No device connected."}), 400
    phone_path = request.json.get('path')
    if not phone_path: return jsonify({"error": "No file path provided."}), 400
    filename = os.path.basename(phone_path)
    pc_path = os.path.join(app.config['PULLED_FILES_FOLDER'], secure_filename(filename))
    success, output = run_command(["adb", "-s", device_id, "pull", phone_path, pc_path], timeout=120)
    if success: return jsonify({"status": "success", "message": f"Pulled {filename}."})
    return jsonify({"status": "error", "message": f"Failed to pull file: {output}"})

@app.route('/push_file', methods=['POST'])
def push_file():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    device_id = get_connected_device()
    if not device_id: return jsonify({"status": "error", "message": "No device connected."}), 400
    if 'file' not in request.files: return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400
    filename = secure_filename(file.filename)
    pc_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(pc_path)
    phone_path = f"/sdcard/Download/{filename}"
    success, output = run_command(["adb", "-s", device_id, "push", pc_path, phone_path], timeout=120)
    if success: return jsonify({"status": "success", "message": f"Pushed {filename}."})
    return jsonify({"status": "error", "message": f"Failed to push file: {output}"}), 500

@app.route('/install_apk', methods=['POST'])
def install_apk():
    if not is_authorized(request): return jsonify({"error": "Unauthorized"}), 401
    device_id = get_connected_device()
    if not device_id: return jsonify({"status": "error", "message": "No device connected."}), 400
    if 'file' not in request.files: return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400
    filename = secure_filename(file.filename)
    pc_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(pc_path)
    success, output = run_command(["adb", "-s", device_id, "install", "-r", pc_path], timeout=120)
    if success and ("Success" in output or "success" in output.lower()):
        return jsonify({"status": "success", "message": f"Successfully installed {filename}."})
    return jsonify({"status": "error", "message": f"Failed to install APK: {output}"}), 500

if __name__ == '__main__':
    if API_SECRET_KEY == "pogiako" or API_SECRET_KEY == "YourSuperSecretKey123!@#":
        print("\n!!! SECURITY WARNING: Please change the default API_SECRET_KEY in app.py !!!\n")
    print("--- Device Control Center ---")
    print("Accessible on your local network.")
    print(f"Your API Secret Key is: {API_SECRET_KEY}")
    print("Find your PC's IP and go to: http://<YOUR_PC_IP_ADDRESS>:5000")
    print("-----------------------------")
    app.run(host='0.0.0.0', port=5000)