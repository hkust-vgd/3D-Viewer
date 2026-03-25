# 3D Viewer Homepage

A Flask-based homepage that organizes and provides access to all 3D visualizations in this repository.

## Features

- 🌊 **Centralized Navigation**: View all available 3D reconstructions in one place
- 🔗 **External Links**: Access existing underwater and campus visualizations
- 📊 **Local Predictions**: Browse and launch visualization servers for 18 local .pkl files
- ⚡ **Dynamic Server Management**: Start and stop viser servers on demand
- 🎨 **Responsive UI**: Modern, clean interface that works on all devices
- 📱 **Status Tracking**: Real-time server status and port information

## Architecture

```
3D-Viewer/
├── app.py                  # Flask homepage server
├── viser.py                # Original viser visualization server
├── templates/
│   └── index.html         # Homepage HTML template
├── static/
│   └── css/
│       └── style.css      # Homepage styles
├── predictions/            # 18 .pkl prediction files
├── links.txt              # External visualization links
└── README.md              # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install flask
```

### 2. Start the Homepage Server

```bash
python app.py
```

The homepage will be available at: **http://localhost:5000**

### 3. Using the Homepage

1. **Browse External Links**: Click on any external visualization to open in a new tab
2. **Start Local Visualization**:
   - Find the desired prediction file in the "Local Predictions" section
   - Click "▶️ Start Server" button
   - Wait 2-3 seconds for the server to start
   - Click "🔍 Open Viewer" to open the viser visualization
3. **Manage Servers**:
   - Use individual "⏹️ Stop" buttons to stop specific servers
   - Use "⏹️ Stop All Servers" to stop all running servers

## Local Prediction Files

The following 18 prediction files are available:

- vggt_predictions_0.pkl through vggt_predictions_19.pkl (excluding 2, 3)

Each file represents a different 3D reconstruction that can be visualized using the viser framework.

## External Visualizations

### Hong Kong Underwater Pointclouds
- WWF Site #1
- Ghost Gear
- WWF 360
- WWF Site #2

### HKUST Campus View
- Campus Splat Viewer

## Technical Details

### Port Allocation

- **Homepage**: Port 5000
- **Viser Servers**: Ports 8080-8097 (one per prediction file)
  - vggt_predictions_0.pkl → Port 8080
  - vggt_predictions_1.pkl → Port 8081
  - ...
  - vggt_predictions_19.pkl → Port 8099

### Server Management

The `app.py` script:
- Serves the homepage at `/` with all available visualizations
- Provides REST API endpoints for server management:
  - `GET /api/status` - Get status of all servers
  - `GET /api/start/<index>` - Start server for prediction at index
  - `GET /api/stop/<port>` - Stop server on specific port
  - `GET /api/stop-all` - Stop all running servers

### How It Works

1. Homepage loads and displays all external links and local prediction files
2. When user clicks "Start Server" for a prediction:
   - Flask backend spawns a subprocess running `viser.py` with the selected file
   - Server runs on a unique port (8080 + index)
   - Status updates in real-time on the homepage
3. User clicks "Open Viewer" to access the viser visualization in a new tab
4. Servers can be stopped individually or all at once

## Customization

### Adding New External Links

Edit the `EXTERNAL_LINKS` dictionary in [app.py:18-31](app.py#L18-L31):

```python
EXTERNAL_LINKS = [
    {
        "title": "Your Category",
        "description": "Category description",
        "items": [
            {"name": "Link Name", "url": "https://your-url.com"},
        ]
    }
]
```

### Changing Base Port

Modify the `BASE_PORT` constant in [app.py:15](app.py#L15):

```python
BASE_PORT = 9000  # Instead of 8080
```

### Styling

Edit [static/css/style.css](static/css/style.css) to customize the homepage appearance.

## Troubleshooting

### Server Won't Start

- Check if the port is already in use
- Verify the .pkl file exists and is valid
- Check console output for error messages

### Homepage Not Loading

- Ensure Flask is installed: `pip install flask`
- Check if port 5000 is available
- Try accessing http://127.0.0.1:5000 instead

### Viser Visualization Not Appearing

- Wait a few seconds after clicking "Start Server"
- Check that the viser server process is running
- Verify the prediction file is valid

## Notes

- Each viser server runs independently in the background
- Stopping a server terminates its process and frees the port
- The homepage polls server status every 2 seconds for real-time updates
- All servers are automatically stopped when the homepage is terminated (Ctrl+C)

## License

This project builds on the original viser visualization code from Meta Platforms, Inc.
