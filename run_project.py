import os
import sys
import subprocess  # nosec B404
import time
import signal

def run_services():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "apps", "backend")
    frontend_dir = os.path.join(base_dir, "apps", "frontend")
    teams_dir = os.path.join(base_dir, "apps", "teams-bot")

    processes = []
    
    print("==================================================")
    print("     Starting SecureCopilot 365 Services...      ")
    print("==================================================")

    # 1. Start backend
    print("\n[+] Starting FastAPI Backend (Port 8000)...")
    backend_proc = subprocess.Popen(  # nosec B603
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=backend_dir,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    processes.append(("Backend", backend_proc))
    
    # Wait briefly for DB check / tables creation
    time.sleep(2)

    # 2. Start frontend
    print("\n[+] Starting React Frontend Dashboard (Port 5173)...")
    frontend_proc = subprocess.Popen(  # nosec B602 B607
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    processes.append(("Frontend", frontend_proc))

    # 3. Start Teams Bot
    print("\n[+] Starting Teams Bot (Port 3978)...")
    teams_proc = subprocess.Popen(  # nosec B602 B607
        ["npm", "start"],
        cwd=teams_dir,
        shell=True,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    processes.append(("Teams Bot", teams_proc))

    print("\n[!] All services are running. Press Ctrl+C to terminate all services.")
    print("==================================================\n")

    def signal_handler(sig, frame):
        print("\n\n[!] Shutting down all services gracefully...")
        for name, proc in processes:
            print(f"[-] Terminating {name}...")
            try:
                if sys.platform == "win32":
                    subprocess.call(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # nosec B603 B607
                else:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except Exception:
                proc.terminate()
        print("[+] Done.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Keep script alive and check processes status
    while True:
        for name, proc in processes:
            if proc.poll() is not None:
                print(f"\n[!] Warning: {name} process has terminated unexpectedly with exit code {proc.poll()}")
                # Trigger shutdown
                signal_handler(None, None)
        time.sleep(1)

if __name__ == "__main__":
    try:
        run_services()
    except KeyboardInterrupt:
        pass
