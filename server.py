# JARVIS HELMET server.
#  - http://localhost:8000 on the PC, and on the Quest over the USB cable (adb reverse; the Quest browser treats localhost as secure, so WebXR works)
#  - https://<pc-ip>:8443 for wireless (self-signed cert: the Quest browser shows a warning once -> Advanced -> Proceed)
# When the Quest is plugged in it keeps adb reverse up, and opens the helmet page in the Quest browser once per launch.
import http.server, os, socket, ssl, subprocess, threading, time

ROOT = os.path.dirname(os.path.abspath(__file__))
ADB = r"C:\Users\mikem\Downloads\Vrgames\platform-tools\adb.exe"
HTTP_PORT, HTTPS_PORT = 8000, 8443
CERT, KEY = os.path.join(ROOT, "cert", "cert.pem"), os.path.join(ROOT, "cert", "key.pem")
NOWIN = 0x08000000  # CREATE_NO_WINDOW


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *a):
        with open(os.path.join(ROOT, 'helmet.log'), 'a') as f:
            f.write(time.strftime('%H:%M:%S ') + self.client_address[0] + ' ' + (fmt % a) + '\n')


def serve(port, tls):
    srv = http.server.ThreadingHTTPServer(("0.0.0.0", port), Handler)
    if tls:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(CERT, KEY)
        srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
    srv.serve_forever()


def adb(*args):
    try:
        return subprocess.run([ADB, *args], capture_output=True, text=True, timeout=15, creationflags=NOWIN).stdout
    except Exception:
        return ""


WIFI_FILE = os.path.join(ROOT, "quest_wifi.txt")


def rookie_busy():
    # adb tcpip restarts the headset's adbd, which would kill a Rookie install mid-copy
    out = subprocess.run(["tasklist"], capture_output=True, text=True, creationflags=NOWIN).stdout.lower()
    return "androidsideloader" in out


def headset_watch():
    # Wi-Fi ADB: on a USB connection, switch the headset's adb to tcp:5555 and remember its IP, so adb reverse
    # (and helmet updates) keep working over Wi-Fi after the cable comes out. Lasts until the headset reboots.
    opened = set()
    while True:
        out = adb("devices")
        devs = [l.split("\t")[0] for l in out.splitlines()[1:] if l.endswith("\tdevice")]
        wifi = open(WIFI_FILE).read().strip() if os.path.exists(WIFI_FILE) else ""
        if wifi and wifi not in devs:
            adb("connect", wifi)
        for d in devs:
            if ":" not in d and not rookie_busy():
                ipout = adb("-s", d, "shell", "ip", "-f", "inet", "addr", "show", "wlan0")
                ip = next((w.split("/")[0] for l in ipout.splitlines() for w in l.split()[1:2] if "inet " in l), "")
                if ip and f"{ip}:5555" not in devs:
                    adb("-s", d, "tcpip", "5555")
                    time.sleep(3)
                    adb("connect", f"{ip}:5555")
                    with open(WIFI_FILE, "w") as f:
                        f.write(f"{ip}:5555")
                    print("wifi adb", ip)
            adb("-s", d, "reverse", f"tcp:{HTTP_PORT}", f"tcp:{HTTP_PORT}")
            # once per headset (USB and Wi-Fi entries are the same headset), and only when it's awake:
            # an intent sent to a sleeping headset never loads the page
            sn = adb("-s", d, "shell", "getprop", "ro.serialno").strip() or d
            if sn not in opened and "mWakefulness=Awake" in adb("-s", d, "shell", "dumpsys", "power"):
                opened.add(sn)
                adb("-s", d, "shell", "am", "start", "-a", "android.intent.action.VIEW",
                    "-d", f"http://localhost:{HTTP_PORT}/", "com.oculus.browser")
                print("headset", d, "-> helmet opened")
        time.sleep(4)


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("192.168.1.1", 1))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    threading.Thread(target=serve, args=(HTTP_PORT, False), daemon=True).start()
    if os.path.exists(CERT):
        threading.Thread(target=serve, args=(HTTPS_PORT, True), daemon=True).start()
    if os.path.exists(ADB):
        threading.Thread(target=headset_watch, daemon=True).start()
    print(f"JARVIS HELMET  cable: http://localhost:{HTTP_PORT}   wireless: https://{lan_ip()}:{HTTPS_PORT}")
    while True:
        time.sleep(3600)
