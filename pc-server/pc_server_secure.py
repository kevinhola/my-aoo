# Guarda este archivo como: pc-server/pc_server_secure.py
import ctypes
import win32com.client
import socket
import ssl
import psutil
import ctypes
import secrets
import hashlib
from threading import Thread

# Genera un token secreto al iniciar el servidor
SECRET_TOKEN = secrets.token_hex(16)
print(f"Token secreto generado: {SECRET_TOKEN}")

def get_battery_info():
    battery = psutil.sensors_battery()
    if battery:
        return f"Batería: {battery.percent}%, {'Cargando' if battery.power_plugged else 'Desconectado'}"
    return "Información de batería no disponible"

def get_running_processes():
    processes = []
    for proc in psutil.process_iter(['name']):
        processes.append(proc.info['name'])
    return ", ".join(processes[:5])

def lock_pc():
    ctypes.windll.user32.LockWorkStation()
    return "PC bloqueada"

def set_lock_screen_message(message):
    print(f"Mensaje de bloqueo establecido: {message}")
    return "Mensaje de bloqueo establecido"

def unlock_pc():
    # Esta función simula presionar Ctrl+Alt+Del y luego Enter
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys("^%{DELETE}")
    shell.SendKeys("{ENTER}")
    return "Comando de desbloqueo enviado"

def handle_client(conn):
    try:
        # Primero, verificamos la autenticación
        auth_token = conn.recv(1024).decode('utf-8').strip()
        if not secrets.compare_digest(hashlib.sha256(auth_token.encode()).hexdigest(), 
                                      hashlib.sha256(SECRET_TOKEN.encode()).hexdigest()):
            conn.send("Autenticación fallida".encode('utf-8'))
            return

        conn.send("Autenticado".encode('utf-8'))

        while True:
            data = conn.recv(1024).decode('utf-8').strip()
            if not data:
                break

            if data == "STATUS":
                response = f"{get_battery_info()}\nProcesos: {get_running_processes()}"
            elif data == "LOCK":
                response = lock_pc()
            elif data == "UNLOCK":
                response = unlock_pc()
            elif data.startswith("SETMSG:"):
                message = data.split(":", 1)[1]
                # Validación de entrada
                if len(message) > 100:  # Limitar longitud del mensaje
                    response = "Mensaje demasiado largo"
                else:
                    response = set_lock_screen_message(message)
            else:
                response = "Comando no reconocido"

            conn.send(response.encode('utf-8'))

    except Exception as e:
        print(f"Error en la conexión: {e}")
    finally:
        conn.close()

def main():
    host = '0.0.0.0'
    port = 12345

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Servidor seguro escuchando en {host}:{port}")

        with context.wrap_socket(server_socket, server_side=True) as secure_socket:
            while True:
                conn, addr = secure_socket.accept()
                print(f"Conexión segura establecida desde {addr}")
                client_thread = Thread(target=handle_client, args=(conn,))
                client_thread.start()

if __name__ == "__main__":
    main()