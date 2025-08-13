# 🚀 Nexus Panel | Your Personal Device Control Center

![License](https://img.shields.io/badge/license-MIT-lightgrey.svg) ![Status](https://img.shields.io/badge/status-Educational-orange)

Nexus Panel is a powerful, self-hosted web application that provides a "GOD Mode" dashboard for controlling and managing your Android devices directly from your PC's web browser. Built with Python and Flask, it leverages the power of `adb` and `scrcpy` to give you a comprehensive suite of tools in one clean, modern interface.

---

### ⚠️ Disclaimer & Important Warnings

**This is a powerful tool intended for educational purposes and personal use on your own devices. Use at your own risk.**

#### **Why a Feature Might Not Work on Your Phone**
The Android ecosystem is incredibly diverse. A command that works perfectly on one phone may fail on another. If a feature is not working for you, it is likely due to one of the following reasons:

*   **Manufacturer Customizations (OEM Skins):** Brands like **Samsung (One UI)**, **Xiaomi (MIUI)**, and **Transsion (XOS)** heavily modify the Android operating system. They may change, restrict, or disable certain `adb` functions. The behavior you observed with text input going to the **XOS Launcher** is a perfect example of this.
*   **Android Version & Security:** Newer versions of Android are more secure. Some commands that worked on Android 10 may be protected or require new permissions on Android 13+.
*   **Special Permissions:** As we discovered, changing system settings (like Dark Mode or Screen Timeout) often requires enabling an extra **`USB debugging (Security settings)`** toggle in Developer Options. Without it, the commands will silently fail.
*   **`adb` or `scrcpy` Version:** This tool is built on `adb` and `scrcpy`. If your versions are very old or very new, some commands may have different syntax (like the `--video-bit-rate` issue we fixed).

**The "Direct Shell" tab is your best friend for debugging!** If a button doesn't work, try running the underlying command in the shell to see the raw error message from your phone.

#### **Security Notice**
This application is designed to be run on a **secure, private local network (like your home Wi-Fi)**. Do **NOT** expose this server to the public internet.

---

### ✨ What is This?

This is a local web server that you run on your computer. Once it's running, you can access a feature-rich dashboard from any device on your Wi-Fi network to perform advanced actions on any connected Android phone. It acts as a beautiful remote control for the powerful but command-line-based Android Debug Bridge (`adb`).

### ✅ Why Use Nexus Panel?

*   **🌐 Unified Dashboard:** All your essential power-user tools in one place.
*   **📡 True Wireless Freedom:** Connect and control your phone entirely over Wi-Fi (no USB needed for setup on Android 11+).
*   **🤖 Automation-Focused:** Discover devices on your network automatically with Nmap.
*   **⚡️ GOD-Mode Features:** A direct shell executor, process manager, app uninstaller, and more.
*   **🎮 Gaming Ready:** Launch games in an optimized, low-latency mirror session with custom keyboard mapping.
*   **🔒 Secure & Private:** Everything runs on your local network. No data ever leaves your home.

---

### 🚧 Project Status

This project is a functional prototype and should be considered a **work in progress**. While many features are stable, you may encounter bugs or features that do not work on your specific device due to the reasons listed in the disclaimer.

---

### 🛠️ Core Features

*   **Backup & Media**
    *   One-click full device backup to your PC's D: drive.
    *   One-click download of all photos and videos from your camera folder to your PC's D: drive.
*   **GOD Mode Suite**
    *   **Direct Shell Executor:** Run any `adb shell` command and see the raw output.
    *   **Process Manager:** View all running processes and force-stop misbehaving apps.
*   **Security & Health**
    *   **Security Auditor:** Checks for common security risks.
    *   **Cache Cleaner:** Frees up space for all installed applications.
    *   **Connection Monitor:** See a live list of your phone's active network connections.
*   **Device Management**
    *   Screen Mirroring & Recording.
    *   App Manager (List & Uninstall).
    *   Detailed Device Info Panel (Model, Android Version, CPU, RAM, Battery).
*   **Automation & Discovery**
    *   Network Scanner (Nmap) to find devices on your Wi-Fi.
*   **File Management**
    *   Push & Pull any file by path.
    *   Install APKs.
*   **Advanced Actions**
    *   Control hardware buttons, system settings (Dark Mode, Timeout), and more.

---

### ⚙️ Prerequisites

Before you begin, you **must** have the following software installed on your computer and available in your system's PATH.

1.  **🐍 Python 3.7+**: [Download Python](https://www.python.org/downloads/)
2.  **📲 ADB & scrcpy**: [Download scrcpy Releases](https://github.com/Genymobile/scrcpy/releases) (includes `adb`). Unzip and add the folder to your system's PATH.
3.  **🗺️ Nmap**: [Download Nmap](https://nmap.org/download.html). On Windows, install **Npcap** when prompted.

---

### 🚀 Getting Started

#### 1. Setup the Project

```bash
# Clone or download the project files
# ...

# 2. Create the required folders
mkdir uploads pulled_files recordings

# 3. Install the required Python libraries
pip install Flask python-nmap werkzeug
```

#### 2. Configure the API Key 🔑

1.  Open `app.py`.
2.  Find `API_SECRET_KEY = "pogiako"` and change it to your own secret password.

#### 3. Run the Server

```bash
python app.py
```
The terminal will print your API Key and access URLs. Keep this window open.

---

### 📱 Connecting Your Phone (No USB Cable Needed!)

This method uses Android 11+'s built-in "Wireless Debugging" feature.

#### **Part I: One-Time Pairing**

1.  **On Your Phone:** `Settings > Developer options` -> Enable **Wireless debugging**. Tap **`Pair device with pairing code`**. Note the code and IP:Port.
2.  **On Your PC:** Open a **new** terminal and run `adb pair [IP:Port_from_phone]`. Enter the pairing code.

#### **Part II: Daily Connection Workflow**

1.  **On Your Phone:** `Settings > Developer options` -> **Turn ON "Wireless debugging"**. Note the main connection IP:Port displayed on this screen.
2.  **On the Nexus Panel Web App:** Enter your API Key and the phone's connection IP:Port. Click **"Connect to Target"**.

Once connected, all feature buttons will become active. You are now in control! 🎉

---

### 📜 License

This project is licensed under the MIT License.

Copyright (c) 2024 Amitred11.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
