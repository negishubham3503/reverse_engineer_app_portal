import frida
import sys
import time

TARGET = "com.fixeads.olxportugal"   # package prefix
SCRIPT_PATH = "frida-scripts/ssl_pinning_bypass.js"

def on_message(message, data):
    if message["type"] == "send":
        print(f"[*] {message['payload']}")
    elif message["type"] == "error":
        print(f"[!] Error: {message.get('stack', message)}")
    else:
        print(message)

def find_process(device, target_prefix):
    procs = device.enumerate_processes()
    # exact match first
    for p in procs:
        if p.name == target_prefix:
            return p
    # prefix/contains fallback
    for p in procs:
        if p.name.startswith(target_prefix) or target_prefix in p.name:
            return p
    return None

def main():
    device = frida.get_usb_device(timeout=10)

    print(f"[*] Waiting for running process (match): {TARGET}")
    proc = None
    for _ in range(30):
        proc = find_process(device, TARGET)
        if proc:
            break
        time.sleep(1)

    if not proc:
        print("[!] Process not found.")
        print("[i] Run: frida-ps -Uai | grep -i olx")
        return

    print(f"[*] Attaching to: {proc.name} (pid={proc.pid})")
    session = device.attach(proc.pid)

    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        js = f.read()

    script = session.create_script(js)
    script.on("message", on_message)
    script.load()

    print("[*] Script loaded. Press Ctrl+C to exit.")
    try:
        sys.stdin.read()
    except KeyboardInterrupt:
        pass
    finally:
        session.detach()

if __name__ == "__main__":
    main()