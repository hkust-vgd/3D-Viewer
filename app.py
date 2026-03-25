#!/usr/bin/env python3.10
"""
3D Viewer Homepage - Flask-based web server that organizes all visualizations
All viser servers are launched at startup and run until the app terminates
"""
import os
import sys
import subprocess
import threading
import pickle
import time
import argparse
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from viser_server import viser_wrapper

# Setup logging directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Add parent directory to path to import viser_wrapper
sys.path.append(str(Path(__file__).parent))

# Parse command-line arguments
parser = argparse.ArgumentParser(description='3D Viewer Homepage')
parser.add_argument('--base_url', type=str, default=os.getenv('BASE_URL', 'localhost'),
                   help='Base URL for viser servers (default: localhost)')
args = parser.parse_args()

app = Flask(__name__)

# Configuration
BASE_PORT = 8080
BASE_URL = args.base_url  # Can be overridden via command-line argument or environment variable
VISER_SERVERS = {}  # Dictionary to track all running viser servers: {port: (process, prediction_name)}
PREDICTIONS_DIR = Path("predictions")

# Predefined external links
EXTERNAL_LINKS = [
    {
        "title": "Hong Kong Underwater Pointclouds",
        "description": "Underwater 3D reconstructions from WWF sites",
        "links": [
            {"name": "WWF Site #1", "url": "https://pcd-viewer.hkustvgd.com/?url=wwf_site_1"},
            {"name": "Ghost Gear", "url": "https://pcd-viewer.hkustvgd.com/?url=ghost_gear"},
            {"name": "WWF 360", "url": "https://pcd-viewer.hkustvgd.com/?url=wwf_360"},
            {"name": "WWF Site #2", "url": "https://pcd-viewer.hkustvgd.com/?url=wwf_site_2"},
        ]
    },
    {
        "title": "HKUST Campus View",
        "description": "Campus 3D reconstruction",
        "links": [
            {"name": "Campus Splat Viewer", "url": "https://splat-viewer.hkustvgd.com/"},
        ]
    }
]

def get_predictions_files():
    """Get list of all .pkl prediction files"""
    if not PREDICTIONS_DIR.exists():
        return []

    pkl_files = sorted(PREDICTIONS_DIR.glob("*.pkl"))
    files_info = []
    i = 0
    for pkl_file in pkl_files:
        # Extract number from filename (e.g., vggt_predictions_0.pkl -> 0)
        name = pkl_file.stem
        try:
            num = int(name.split('_')[-1])
        except:
            num = -1

        # Get file size
        size_mb = pkl_file.stat().st_size / (1024 * 1024)

        files_info.append({
            "name": f"Demo {i}",
            "path": str(pkl_file),
            "num": num,
            "size_mb": round(size_mb, 2)
        })

        i = i + 1

    # Sort by number
    files_info.sort(key=lambda x: x['num'])
    return files_info

def start_server(predictions_path, conf_threshold, use_point_map, background_mode, host, port):
    with open(predictions_path, 'rb') as f:
        predictions = pickle.load(f)

    print("Starting viser visualization...")

    viser_server = viser_wrapper(
        predictions,
        port=port,
        init_conf_threshold=conf_threshold,
        use_point_map=use_point_map,
        background_mode=background_mode,
        host=host
    )

def start_all_servers():
    """Launch all viser servers at startup"""
    predictions = get_predictions_files()

    if not predictions:
        print("No prediction files found in predictions/ directory")
        return

    print(f"Launching {len(predictions)} viser servers...")

    for index, pred_file in enumerate(predictions):
        port = BASE_PORT + index

        # Start viser server in background
        cmd = [
            sys.executable, "viser_server.py",
            "--predictions_path", pred_file['path'],
            "--port", str(port),
            "--background_mode",
            "--conf_threshold", "25.0"
        ]

        try:
            start_server(pred_file['path'], 25.0, True, True, BASE_URL, port)

            print(f"✓ Started server for {pred_file['name']} on port {port}")

            # Small delay between launches to avoid resource contention
            time.sleep(0.5)




        except Exception as e:
            print(f"✗ Failed to start server for {pred_file['name']} on port {port}: {e}")

    print(f"All {len(VISER_SERVERS)} servers started successfully")

def stop_all_servers():
    """Stop all running viser servers"""
    for port, (process, pred_name) in list(VISER_SERVERS.items()):
        try:
            print(f"Stopping server for {pred_name} on port {port}...")
            process.terminate()
            process.wait(timeout=5)
        except:
            pass
    VISER_SERVERS.clear()
    print("All servers stopped")

@app.route('/')
def index():
    """Main homepage"""
    predictions = get_predictions_files()
    return render_template('index.html',
                         predictions=predictions,
                         external_links=EXTERNAL_LINKS,
                         base_port=BASE_PORT,
                         base_url=BASE_URL,
                         viser_servers=VISER_SERVERS)

@app.route('/api/status')
def status():
    """Get status of all servers"""
    servers_info = {}
    for port, (process, pred_name) in VISER_SERVERS.items():
        servers_info[str(port)] = {
            "port": port,
            "prediction": pred_name,
            "pid": process.pid,
            "returncode": process.poll()
        }

    return jsonify({
        "servers": servers_info,
        "server_count": len(VISER_SERVERS),
        "predictions": get_predictions_files()
    })

@app.route('/api/stop-all')
def stop_all():
    """Stop all viser servers (for graceful shutdown)"""
    stop_all_servers()
    return jsonify({"status": "all_stopped"})

def run_server():
    """Run Flask server"""
    print("=" * 60)
    print("3D Viewer Homepage")
    print("=" * 60)
    print(f"Starting homepage on http://{BASE_URL}:5000")
    print(f"Base port for viser servers: {BASE_PORT}")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)

    # Launch all viser servers before starting Flask
    start_all_servers()

    # Print server URLs
    print("\n" + "=" * 60)
    print("Available Viser Servers:")
    print("=" * 60)
    for port in sorted(VISER_SERVERS.keys()):
        pred_name = VISER_SERVERS[port][1]
        print(f"  • {pred_name}: http://{BASE_URL}:{port}")
    print("=" * 60 + "\n")

    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Shutting down...")
        print("=" * 60)
        stop_all_servers()
        print("Shutdown complete")

if __name__ == '__main__':
    run_server()
