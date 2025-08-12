# 🚀 Nexus Panel | Your Personal Device Control Center

![License](https://img.shields.io/badge/license-MIT-lightgrey.svg) ![Status](https://img.shields.io/badge/status-Educational-orange)

Nexus Panel is a powerful, self-hosted web application that provides a "GOD Mode" dashboard for controlling and managing your Android devices directly from your PC's web browser. Built with Python and Flask, it leverages the power of `adb` and `scrcpy` to give you a comprehensive suite of tools in one clean, modern interface.



### ⚠️ Disclaimer & Important Warnings

**This is a powerful tool intended for educational purposes and personal use on your own devices.**

*   **Use at Your Own Risk:** Some actions, like uninstalling apps, rebooting, or executing shell commands, can have unintended consequences if used improperly. The creator of this tool is not responsible for any damage or data loss that may occur to your device.
*   **Security:** This application is designed to be run on a **secure, private local network (like your home Wi-Fi)**. Do **NOT** expose this server to the public internet. The API Key provides a basic layer of security, but it is not sufficient for a hostile environment.
*   **Root Not Required:** All features in this panel are designed to work on a standard, non-rooted Android device.

---

### ✨ What is This? (The "What")

This is a local web server that you run on your computer. Once it's running, you can access a feature-rich dashboard from any device on your Wi-Fi network (your PC, your phone, a tablet) to perform advanced actions on any connected Android phone. It acts as a beautiful and user-friendly remote control for the powerful but command-line-based Android Debug Bridge (`adb`).

### ✅ Why Use Nexus Panel? (The "Why")

*   **🌐 Unified Dashboard:** All your essential power-user tools in one place. No more memorizing terminal commands.
*   **📡 True Wireless Freedom:** Connect and control your phone entirely over Wi-Fi, with no USB cables required (even for the initial setup on Android 11+).
*   **🤖 Automation-Focused:** Discover devices on your network automatically with Nmap, making connections seamless.
*   **⚡️ GOD-Mode Features:** Go beyond simple mirroring with a direct shell executor, process manager, app uninstaller, and more.
*   **🔒 Secure & Private:** Everything runs on your local network. No data ever leaves your home. The API key ensures only you can access the panel.
*   **🖥️ Cross-Platform:** Works on Windows, macOS, and Linux.

---

### 🚧 Project Status

This project is currently under active development and should be considered a **work in progress**. While the core features are functional, you may encounter bugs. Future updates will focus on improving stability, adding more features, and refining the user interface.

---

### 🛠️ Core Features

*   **GOD Mode Suite**
    *   **Direct Shell Executor:** Run any `adb shell` command and see the raw output.
    *   **Process Manager:** View all running processes and force-stop misbehaving apps.
*   **Device Management**
    *   **Screen Mirroring:** High-speed, low-latency screen mirroring with `scrcpy`.
    *   **Screen Recording:** Record your phone's screen and save it directly to your PC as an `.mp4`.
    *   **App Manager:** List all user-installed apps and uninstall them with one click.
    *   **Device Info Panel:** View detailed information like device model, Android version, CPU, RAM, and battery status.
*   **Automation & Discovery**
    *   **Network Scanner:** Uses Nmap to automatically find all devices on your Wi-Fi.
*   **Security & Health**
    *   **Security Auditor:** Checks for common security risks like "Unknown Sources" and "USB Debugging" being enabled.
    *   **Cache Cleaner:** Frees up space by clearing the cache for all installed applications.
    *   **Connection Monitor:** See a live list of your phone's active network connections.
*   **File Management**
    *   **Push & Pull Files:** Transfer files between your PC and phone.
    *   **Install APKs:** Easily install `.apk` files from your PC onto your phone.
*   **Advanced Actions**
    *   Control hardware buttons (Power, Volume), system settings (Dark Mode, Timeout), and more.

---

### ⚙️ Prerequisites

Before you begin, you **must** have the following software installed on your computer and available in your system's PATH.

1.  **🐍 Python 3.7+**: [Download Python](https://www.python.org/downloads/)
2.  **📲 ADB & scrcpy**: The easiest way is to download the latest `scrcpy` release, which includes `adb`.
    *   [Download scrcpy Releases](https://github.com/Genymobile/scrcpy/releases)
    *   Unzip the folder and add its location to your system's PATH.
3.  **🗺️ Nmap**: Required for the Network Discovery feature.
    *   [Download Nmap](https://nmap.org/download.html)
    *   **On Windows**, ensure you keep the default option to install **Npcap**.

---

### 🚀 Getting Started

#### 1. Setup the Project

```bash
# 1. Download or clone this repository
git clone [your-repo-link]
cd nexus-panel

# 2. Create the required folders
mkdir uploads pulled_files recordings

# 3. Install the required Python libraries
pip install Flask python-nmap werkzeug
```

#### 2. Configure the API Key 🔑

For your security, you must set a private API key.

1.  Open the `app.py` file.
2.  Find the line: `API_SECRET_KEY = "pogiako"`
3.  Change `"pogiako"` to a long, secret password that only you know.

#### 3. Run the Server

```bash
python app.py
```
The terminal will print your API Key and the URLs to access the panel. Keep this terminal window open.

---

### 📱 Connecting Your Phone (No USB Cable Needed!)

This method uses Android 11's built-in "Wireless Debugging" feature.

#### **Part I: One-Time Pairing**

You only need to do this the very first time you connect a phone to your PC.

1.  **On Your Phone:**
    *   Connect to your Wi-Fi network.
    *   Enable **Developer Options**. (Go to `Settings > About phone` and tap `Build number` 7 times).
    *   Go to `Settings > System > Developer options`.
    *   Turn on the **Wireless debugging** toggle.
    *   Tap on the **`Pair device with pairing code`** option.
    *   Your phone will show a pop-up with a **pairing code** and an **IP Address & Port** (e.g., `192.168.1.15:41239`).

2.  **On Your PC:**
    *   Open a **new** Terminal or Command Prompt window (do not close the server window).
    *   Run the `adb pair` command using the IP:Port from your phone's screen:
        ```bash
        adb pair 192.168.1.15:41239
        ```
    *   The terminal will ask for the pairing code. Enter the 6-digit code from your phone and press Enter.
    *   You should see a "Successfully paired" message. You can now close this terminal window.

#### **Part II: Daily Connection Workflow**

This is what you'll do every time you want to use the app.

1.  **On Your Phone:**
    *   Go to `Settings > Developer options`.
    *   **Turn ON the "Wireless debugging" toggle**.
    *   Tap on the "Wireless debugging" text to see your phone's **main IP Address & Port** for connections (e.g., `192.168.1.15:37895`). This is different from the pairing port.

2.  **On the Nexus Panel Web App:**
    *   Open the dashboard in your browser.
    *   Enter the **API Key** you configured in `app.py`.
    *   You can now either:
        *   **Automated Way:** Go to the "Network" tab and click "Scan Network". Find your phone in the list, click "Select", and enter the port from Step 1.
        *   **Manual Way:** Type the full IP Address & Port from Step 1 directly into the "Target Device" box.
    *   Click **"Connect to Target"**.

Once connected, all the feature buttons will become active. You are now in control! 🎉

---

### 📜 License

This project is licensed under the MIT License.

**MIT License**

Copyright (c) 2024 [Your Name/Project Contributors]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
