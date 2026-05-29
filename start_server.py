"""
Canteen Management System - One-click Launcher
Run: python start_server.py
"""
import subprocess
import sys
import os
import time
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PORTS = [5000, 5173, 5174, 5175, 5176]

services = [
    {
        "name": "Backend API",
        "cwd": os.path.join(BASE_DIR, "backend"),
        "exe": sys.executable,
        "args": ["app.py"],
    },
    {
        "name": "Student App",
        "cwd": os.path.join(BASE_DIR, "student-app"),
        "exe": "npx",
        "args": ["vite", "--port", "5173", "--host"],
    },
    {
        "name": "Kitchen App",
        "cwd": os.path.join(BASE_DIR, "kitchen-app"),
        "exe": "npx",
        "args": ["vite", "--port", "5174", "--host"],
    },
    {
        "name": "Cleaner App",
        "cwd": os.path.join(BASE_DIR, "cleaner-app"),
        "exe": "npx",
        "args": ["vite", "--port", "5175", "--host"],
    },
    {
        "name": "Admin App",
        "cwd": os.path.join(BASE_DIR, "admin-app"),
        "exe": "npx",
        "args": ["vite", "--port", "5176", "--host"],
    },
]


def kill_port(port):
    try:
        result = subprocess.run(
            f'netstat -ano | findstr :{port} | findstr LISTENING',
            capture_output=True, text=True, shell=True, timeout=5
        )
        for line in result.stdout.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 5:
                pid = parts[-1]
                subprocess.run(f"taskkill /F /PID {pid}", capture_output=True, shell=True, timeout=5)
    except Exception:
        pass


def main():
    print("=" * 55)
    print("      Canteen Management System - Launcher")
    print("=" * 55)
    print()

    try:
        subprocess.run([sys.executable, "--version"], capture_output=True, timeout=5)
    except Exception:
        print("[ERROR] Python not found!")
        input("Press Enter to exit...")
        sys.exit(1)

    try:
        subprocess.run(["node", "--version"], capture_output=True, timeout=5)
    except Exception:
        print("[ERROR] Node.js not found!")
        input("Press Enter to exit...")
        sys.exit(1)

    print("[OK] Python + Node.js environment check passed")

    print("[Cleanup] Releasing ports...")
    for port in PORTS:
        kill_port(port)
    time.sleep(1)
    print("[OK] Ports cleaned")
    print()

    for svc in services:
        if not os.path.isdir(svc["cwd"]):
            print(f"[ERROR] Directory not found: {svc['cwd']}")
            input("Press Enter to exit...")
            sys.exit(1)

    for i, svc in enumerate(services):
        name = svc["name"]
        cwd = svc["cwd"]
        exe = svc["exe"]
        args = svc["args"]
        port = PORTS[i]

        print(f"[Start] {name} (Port {port}) ... ", end="", flush=True)
        try:
            arg_str = " ".join(args)
            cmd = f'cmd /k "cd /d "{cwd}" && {exe} {arg_str}"'

            subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                shell=True,
            )
            print("OK")
            time.sleep(2)
        except Exception as e:
            print(f"Failed: {e}")

    print()
    print("=" * 55)
    print("  All services started!")
    print()
    print("  Backend API:  http://localhost:5000")
    print("  Student:      http://localhost:5173")
    print("  Kitchen:      http://localhost:5174")
    print("  Cleaner:      http://localhost:5175")
    print("  Admin:        http://localhost:5176")
    print()
    print("  Opening browser...")
    print("=" * 55)

    time.sleep(3)
    frontend_ports = [5173, 5174, 5175, 5176]
    for port in frontend_ports:
        webbrowser.open(f"http://localhost:{port}")
        time.sleep(0.5)

    print()
    print("All 4 browser pages opened.")
    print()
    print("Tip: Close the black window to stop the service")
    input("Press Enter to exit this window (services continue running)...")


if __name__ == "__main__":
    main()
