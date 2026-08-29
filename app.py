from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash
import socket

APP_USER = "KEVINARREOLA" #Ejemplo diana
APP_PW_HASH = "scrypt:32768:8:1$ygUSSYXE57LDvDww$b72a588cd4b8eadde7e5a200f0ce0eb52fb8dd27c99db51edaf156a06e0444ff2b598ef3cae5b4bab769d211ccf198d395c0c92d9b6c24df095c2e9950e868a1"      # Ejemplo: "scrypt:32768:8:1$...$..."
SECRET_KEY = "contrasenax" # Pon una clave larga y aleatoria 


TCP_HOST = "127.0.0.1"
TCP_PORT = 5001

app = Flask(__name__)
app.secret_key = SECRET_KEY

def is_logged_in():
    return session.get("logged_in") is True

def send_cmd(cmd: str) -> str:
    with socket.create_connection((TCP_HOST, TCP_PORT), timeout=3) as s:
        s.sendall((cmd + "\n").encode("utf-8"))
        return s.recv(1024).decode("utf-8", errors="ignore").strip()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username", "").strip()
        pw = request.form.get("password", "")
        if user == APP_USER and check_password_hash(APP_PW_HASH, pw):
            session["logged_in"] = True
            return redirect(url_for("index"))
        return render_template("login.html", error="Usuario o contraseña incorrectos")
    return render_template("login.html", error=None)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if not is_logged_in():
        return redirect(url_for("login"))
    return render_template("index.html")

@app.post("/set_led")
def set_led():
    if not is_logged_in():
        return jsonify({"ok": False, "error": "No autorizado"}), 401

    data = request.get_json(silent=True) or {}
    state = str(data.get("state", "")).strip()
    led = str(data.get("led", "")).strip()

    if led not in ("1", "2"):
        return jsonify({"ok": False, "error": "Usa led=1 o led=2"}), 400

    if state in ("1", "on", "ON", "true", "TRUE"):
        cmd = f"LED{led}_ON"
    elif state in ("0", "off", "OFF", "false", "FALSE"):
        cmd = f"LED{led}_OFF"
    else:
        return jsonify({"ok": False, "error": "Usa state=1 o state=0"}), 400

    resp = send_cmd(cmd)
    return jsonify({"ok": resp.startswith("OK"), "cmd": cmd, "resp": resp})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


#FDFSFSF
#git add .
#git commit -m "cambio X"
#git push
