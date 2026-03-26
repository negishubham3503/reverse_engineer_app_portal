import subprocess
import shlex

PACKAGE = "com.fixeads.olxportugal"
SCRIPT = "frida-scripts/ssl_pinning_bypass.js"

def run_frida_cli_spawn(package: str, script: str):
    #cmd = f'frida --codeshare pcipolloni/universal-android-ssl-pinning-bypass-with-frida -U -f {package}'
    cmd = f'frida -U -f {package} -l {script}'
    print(f"[*] Running: {cmd}")
    proc = subprocess.Popen(
        shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    try:
        for line in proc.stdout:
            print(line.rstrip())
    except KeyboardInterrupt:
        print("\n[*] Stopping frida CLI...")
        proc.terminate()
        proc.wait(timeout=5)

if __name__ == "__main__":
    run_frida_cli_spawn(PACKAGE, SCRIPT)