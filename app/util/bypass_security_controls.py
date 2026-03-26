import os
import random
import asyncio
import subprocess
import threading
import shlex
import time

import frida

from app.config.settings import settings

def check_cert_availability_and_push(local_cert_path, remote_cert_path):
    # the ssl pinning bypass script needs the certificate to be present on the device, 
    # so we need to check if it's already there before trying to execute the bypass
    try:
        check_command = ["adb", "shell", "ls", remote_cert_path]
        result = subprocess.run(check_command, capture_output=True, text=True)
        if result.returncode != 0 or "No such file" in result.stdout or "No such file" in result.stderr:
            print(f"Certificate not found on the device. Pushing {local_cert_path} to {remote_cert_path}")
            push_command = ["adb", "push", local_cert_path, remote_cert_path]
            subprocess.run(push_command, check=True)
        else:
            print(f"Certificate already exists on the device.")
    except subprocess.CalledProcessError as e:
        print(f"Error checking or pushing certificate: {e}")

def _log_subprocess_output(proc: subprocess.Popen):
    """Continuously reads stdout from a process in a background thread."""
    try:
        if proc.stdout:
            for line in iter(proc.stdout.readline, ''):
                if line:
                    print(line.rstrip())
                if proc.poll() is not None:
                    break
    except Exception as e:
        print(f"Error reading process output: {e}")

def execute_ssl_pinning_bypass(package_name: str) -> str:
    # currently frida can't load code from a codeshare file so we need to hardcode the script in the project
    # So in a way this below code mimics the behaviour of the below frida command
    # frida -U -f package_name -l bypass_security_controls.js
    # updated code below. mimicing the frida cmd command as it works successfully instead of using frida library
    try:
        script_path = settings.PROJECT_ROOT / "frida-scripts" / "ssl_pinning_bypass.js"
        check_cert_availability_and_push("cert-der.crt", "/data/local/tmp/cert-der.crt")
        cmd = ["frida", "-U", "-f", package_name, "-l", str(script_path)]
        print(f"[*] Running: {' '.join(cmd)}")
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1  # Line buffered
        )
        
        thread = threading.Thread(target=_log_subprocess_output, args=(proc,), daemon=True)
        thread.start()
        
        time.sleep(3)
        
        if proc.poll() is not None:
            raise RuntimeError("Frida process exited immediately. Check the script or package name.")
            
        return "SSL Pinning bypass successfully started."
    
    except Exception as e:
        raise RuntimeError(f"Error executing SSL pinning bypass: {e}")

async def mimic_human_behavior_delays():

    base_delay = random.uniform(1.3, 4.6)
    stutter = random.choice([0, random.uniform(0.5, 1.5)])

    total_delay = base_delay + stutter    
    await asyncio.sleep(total_delay)
