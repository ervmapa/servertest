import logging
from flask import Flask, jsonify
from flask import request
import threading
import time
import os
import signal
import multiprocessing

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initial status and timestamp
alive_status = True
ready_status = True
last_ready_change_time = time.time()

# Flag to indicate whether to simulate high CPU load
high_cpu_flag = False

# Routes for Kubernetes probes
@app.route('/alive', methods=['GET'])
def healthz():
    global alive_status
    return ('', 200 if alive_status else 500)

@app.route('/ready', methods=['GET'])
def ready():
    global ready_status
    return ('', 200 if ready_status else 500)

# Control endpoint
@app.route('/control', methods=['POST'])
def control():
    global alive_status, ready_status, last_ready_change_time, high_cpu_flag
    data = request.get_json()

    if 'set_alive' in data:
        logging.info(f"Setting alive status to {data['set_alive']}")
        alive_status = data['set_alive']
    if 'set_ready' in data:
        logging.info(f"Setting ready status to {data['set_ready']}")
        ready_status = data['set_ready']
        last_ready_change_time = time.time()  # Update the timestamp
    if 'shutdown' in data and data['shutdown']:
        logging.info("Shutting down the server...")
        graceful_shutdown()
    if 'set_high_cpu' in data and data['set_high_cpu']:
        logging.info("Setting high CPU load...")
        set_high_cpu()

    # Get the pod's IP address
    pod_ip = get_pod_ip()

    return jsonify({'alive': alive_status, 'ready': ready_status, 'pod_ip': pod_ip})

def reset_ready_status():
    global ready_status, last_ready_change_time
    while True:
        time.sleep(1)
        current_time = time.time()
        if not ready_status and current_time - last_ready_change_time >= 60:
            logging.info("Resetting ready status to True")
            ready_status = True

def run_app(host, port):
    # Start the thread for resetting ready status
    threading.Thread(target=reset_ready_status).start()
    # Run the Flask app on the specified host and port
    app.run(host=host, port=port)

def graceful_shutdown():
    logging.info("Initiating graceful shutdown...")
    os.kill(os.getpid(), signal.SIGINT)

def get_pod_ip():
    # Get the remote address from the request object
    remote_address = request.remote_addr
    # If running in Kubernetes, the remote address should be the pod's IP
    return remote_address

def set_high_cpu():
    global high_cpu_flag
    high_cpu_flag = True
    # Start a separate process to simulate high CPU load
    multiprocessing.Process(target=consume_cpu).start()

def consume_cpu():
    logging.info("Simulating high CPU load...")
    while high_cpu_flag:
        # This loop simulates CPU-intensive work
        pass

if __name__ == '__main__':
    # Run the app on ports 5000, 5001, and 5002 in separate threads
    threading.Thread(target=run_app, args=('0.0.0.0', 5000)).start()
    threading.Thread(target=run_app, args=('0.0.0.0', 5001)).start()
    threading.Thread(target=run_app, args=('0.0.0.0', 5002)).start()

