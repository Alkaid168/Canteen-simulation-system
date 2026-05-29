"""
食堂管理系统 - 一键启动器
双击此文件或在终端中运行: python 启动服务.py
"""
import subprocess
import sys
import os
import time
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 需要使用的端口
PORTS = [5000, 5173, 5174, 5175, 5176]

services = [
    {
        "name": "后端API",
        "cwd": os.path.join(BASE_DIR, "backend"),
        "exe": sys.executable,
        "args": ["app.py"],
    },
    {
        "name": "学生端",
        "cwd": os.path.join(BASE_DIR, "student-app"),
        "exe": "npx",
        "args": ["vite", "--port", "5173", "--host"],
    },
    {
        "name": "后厨端",
        "cwd": os.path.join(BASE_DIR, "kitchen-app"),
        "exe": "npx",
        "args": ["vite", "--port", "5174", "--host"],
    },
    {
        "name": "保洁端",
        "cwd": os.path.join(BASE_DIR, "cleaner-app"),
        "exe": "npx",
        "args": ["vite", "--port", "5175", "--host"],
    },
    {
        "name": "管理员端",
        "cwd": os.path.join(BASE_DIR, "admin-app"),
        "exe": "npx",
        "args": ["vite", "--port", "5176", "--host"],
    },
]


def kill_port(port):
    """杀掉占用指定端口的进程"""
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
    print("       食堂管理系统 - 一键启动")
    print("=" * 55)
    print()

    # 环境检查
    try:
        subprocess.run([sys.executable, "--version"], capture_output=True, timeout=5)
    except Exception:
        print("[错误] 未检测到 Python！")
        input("按回车键退出...")
        sys.exit(1)

    try:
        subprocess.run(["node", "--version"], capture_output=True, timeout=5)
    except Exception:
        print("[错误] 未检测到 Node.js！")
        input("按回车键退出...")
        sys.exit(1)

    print("[OK] Python + Node.js 环境检查通过")

    # 清理旧端口
    print("[清理] 正在释放端口...")
    for port in PORTS:
        kill_port(port)
    time.sleep(1)
    print("[OK] 端口清理完成")
    print()

    # 检查目录
    for svc in services:
        if not os.path.isdir(svc["cwd"]):
            print(f"[错误] 目录不存在: {svc['cwd']}")
            input("按回车键退出...")
            sys.exit(1)

    # 启动服务
    for i, svc in enumerate(services):
        name = svc["name"]
        cwd = svc["cwd"]
        exe = svc["exe"]
        args = svc["args"]
        port = PORTS[i]

        print(f"[启动] {name} (端口 {port}) ... ", end="", flush=True)
        try:
            # 构建命令: cmd /k "cd /d "目录" && 命令 参数..."
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
            print(f"失败: {e}")

    print()
    print("=" * 55)
    print("  所有服务已启动！")
    print()
    print("  后端API:    http://localhost:5000")
    print("  学生端:     http://localhost:5173")
    print("  后厨端:     http://localhost:5174")
    print("  保洁端:     http://localhost:5175")
    print("  管理员端:   http://localhost:5176")
    print()
    print("  正在打开浏览器...")
    print("=" * 55)

    # 等前端启动好
    time.sleep(3)
    frontend_ports = [5173, 5174, 5175, 5176]
    for port in frontend_ports:
        webbrowser.open(f"http://localhost:{port}")
        time.sleep(0.5)

    print()
    print("浏览器已打开全部 4 个页面。")
    print()
    print("提示：关闭黑色窗口 = 停止对应服务")
    input("按回车键退出本窗口（不会关闭服务）...")


if __name__ == "__main__":
    main()
