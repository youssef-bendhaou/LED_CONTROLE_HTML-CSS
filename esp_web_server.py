import machine
import socket
import network
import time
from machine import Pin

# Connexion Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("DESKTOP", "00000000")

led = Pin(4, Pin.OUT)

# Attente de la connexion Wi-Fi et diagnostic
wait_time = 10
while wait_time > 0:
    if wlan.isconnected():
        print('Connected:', wlan.ifconfig())
        break
    wait_time -= 1
    print('Waiting for connection...')
    time.sleep(1)

# Vérification de la connexion
if wlan.isconnected():
    print('Connected with IP:', wlan.ifconfig()[0])
    ip = wlan.ifconfig()[0]
else:
    raise RuntimeError('Wi-Fi connection failed')

# Génération de la page web
def generate_webpage():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 Web Server</title>
        <style>
            #title { color: blue; font-family: serif; background-color: lightblue; }
            h4 { color: black; background-color: lightgrey; }
            img { width: 300px; height: 300px; }
            #ON, #OFF {
                font-size: 30px;
                border: solid 3px;
                border-radius: 10px;
                padding: 10px;
                margin: 10px;
                cursor: pointer;
                transition-duration: 0.5s;
            }
            #ON { color: blue; background-color: white; }
            #ON:hover { color: white; background-color: blue; border-color: red; }
            #OFF { color: red; background-color: white; }
            #OFF:hover { color: white; background-color: red; border-color: blue; }
        </style>
    </head>
    <body>
        <center>
            <h1 id="title">CONTROLE</h1>
            <h4>Control a LED</h4>
            <img src="https://www.celectronix.com/18386-large_default/led-5mm-rouge.jpg" alt="LED icon">
            <form action="/up" method="get">
                <input id="ON" type="submit" value="ON">
            </form>
            <form action="/down" method="get">
                <input id="OFF" type="submit" value="OFF">
            </form>
        </center>
    </body>
    </html>
    """
    return html

# Gestion des requêtes clients
def handle_client(connection):
    while True:
        client, addr = connection.accept()
        print('Client connected from', addr)
        request = client.recv(1024).decode()
        print('Request:', request)
        
        # Extraction du chemin de la requête
        request_path = request.split(' ')[1]
        print('Request Path:', request_path)
        
        # Contrôle de la LED
        if request_path.startswith('/up'):
            led.on()
            print('LED ON')
        elif request_path.startswith('/down'):
            led.off()
            print('LED OFF')
        
        # Réponse HTTP
        response = generate_webpage()
        client.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + response)
        time.sleep(0.1)
        client.close()

# Lancement du serveur
def start_server(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(5)
    print('Server is listening on', ip)
    return connection

# Exécution principale
try:
    if ip:
        server_connection = start_server(ip)
        handle_client(server_connection)
except KeyboardInterrupt:
    machine.reset()
