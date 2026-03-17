import os
import random
import asyncio
import subprocess
import threading

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

def execute_ssl_pinning_bypass(package_name: str) -> str:
    # currently frida can't load code from a codeshare file so we need to hardcode the script in the project
    # So in a way this below code mimics the behaviour of the below frida command
    # frida -U -f package_name -l bypass_security_controls.js
    try:
        script_path = settings.PROJECT_ROOT / "frida-scripts" / "ssl_pinning_bypass.js"
        check_cert_availability_and_push("cert-der.crt", "/data/local/tmp/cert-der.crt")
        device = frida.get_usb_device()

        pid = device.spawn([package_name])
        session = device.attach(pid)

        with open(script_path, "r", encoding="utf-8") as f:
            script_code = f.read()

        wrapper_script = f"""
        function wait_for_java() {{
            if (typeof Java !== 'undefined' && Java.available) {{
                // 1. Run the custom onResume verification hook
                try {{
                    Java.perform(function () {{
                        var Activity = Java.use("android.app.Activity");
                        Activity.onResume.implementation = function () {{
                            send("Class 'android.app.Activity' method 'onResume()' was executed!");
                            this.onResume(); 
                        }};
                        send("Activity hooks installed successfully.");
                    }});
                }} catch (e) {{
                    send("Failed to install Activity hook: " + e);
                }}

                // 2. Run the original SSL Pinning script logic you downloaded from Codeshare.
                // We inject it directly into this runtime block so we know Java is ready.
                {{setTimeout(function(){{
                    Java.perform(function (){{
                        console.log("");
                        console.log("[.] Cert Pinning Bypass/Re-Pinning");

                        var CertificateFactory = Java.use("java.security.cert.CertificateFactory");
                        var FileInputStream = Java.use("java.io.FileInputStream");
                        var BufferedInputStream = Java.use("java.io.BufferedInputStream");
                        var X509Certificate = Java.use("java.security.cert.X509Certificate");
                        var KeyStore = Java.use("java.security.KeyStore");
                        var TrustManagerFactory = Java.use("javax.net.ssl.TrustManagerFactory");
                        var SSLContext = Java.use("javax.net.ssl.SSLContext");

                        // Load CAs from an InputStream
                        console.log("[+] Loading our CA...")
                        var cf = CertificateFactory.getInstance("X.509");
                        
                        try {{
                            var fileInputStream = FileInputStream.$new("/data/local/tmp/cert-der.crt");
                        }}
                        catch(err) {{
                            console.log("[o] " + err);
                        }}
                        
                        var bufferedInputStream = BufferedInputStream.$new(fileInputStream);
                        var ca = cf.generateCertificate(bufferedInputStream);
                        bufferedInputStream.close();

                        var certInfo = Java.cast(ca, X509Certificate);
                        console.log("[o] Our CA Info: " + certInfo.getSubjectDN());

                        // Create a KeyStore containing our trusted CAs
                        console.log("[+] Creating a KeyStore for our CA...");
                        var keyStoreType = KeyStore.getDefaultType();
                        var keyStore = KeyStore.getInstance(keyStoreType);
                        keyStore.load(null, null);
                        keyStore.setCertificateEntry("ca", ca);
                        
                        // Create a TrustManager that trusts the CAs in our KeyStore
                        console.log("[+] Creating a TrustManager that trusts the CA in our KeyStore...");
                        var tmfAlgorithm = TrustManagerFactory.getDefaultAlgorithm();
                        var tmf = TrustManagerFactory.getInstance(tmfAlgorithm);
                        tmf.init(keyStore);
                        console.log("[+] Our TrustManager is ready...");

                        console.log("[+] Hijacking SSLContext methods now...")
                        console.log("[-] Waiting for the app to invoke SSLContext.init()...")

                        SSLContext.init.overload("[Ljavax.net.ssl.KeyManager;", "[Ljavax.net.ssl.TrustManager;", "java.security.SecureRandom").implementation = function(a,b,c) {{
                            console.log("[o] App invoked javax.net.ssl.SSLContext.init...");
                            SSLContext.init.overload("[Ljavax.net.ssl.KeyManager;", "[Ljavax.net.ssl.TrustManager;", "java.security.SecureRandom").call(this, a, tmf.getTrustManagers(), c);
                            console.log("[+] SSLContext initialized with our custom TrustManager!");
                        }}
                    }});
                }},0);}}

            }} else {{
                setTimeout(wait_for_java, 250); // Poll again in 250ms
            }}
        }}
        wait_for_java();
        """

        js_ready_event = threading.Event()
        bypass_logs = []

        def on_message(message, data):
            if message['type'] == 'send':
                payload = message['payload']
                print(f"[*] Frida Log: {payload}")
                bypass_logs.append(payload)
                
                if "Our TrustManager is ready" in payload or "Bypass/Re-Pinning" in payload:
                    js_ready_event.set()
                    
            elif message['type'] == 'error':
                print(f"[!] Frida Error: {message['stack']}")
        
        script = session.create_script(wrapper_script)
        script.on("message", on_message)
        script.load()

        device.resume(pid)

        print("[*] Waiting for SSL Pinning script to initialize...")
        js_ready_event.wait(timeout=10.0)

        return True
    
    except Exception as e:
        raise RuntimeError(f"Error executing SSL pinning bypass: {e}")

async def mimic_human_behavior_delays():

    base_delay = random.uniform(1.3, 4.6)
    stutter = random.choice([0, random.uniform(0.5, 1.5)])

    total_delay = base_delay + stutter    
    await asyncio.sleep(total_delay)
