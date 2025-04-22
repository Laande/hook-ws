# WebSocket Interceptor

This project is a WebSocket interceptor tool built using Python and customtkinter. It allows you to connect to a WebSocket server, send and receive messages, and manage message visibility preferences.

## Features

- Connect to WebSocket servers
- Send and receive messages
- Toggle visibility of different message types
- Save preferences for future sessions

## Usage

1. Install the required Python packages by running:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure `mitmproxy` is installed and available in your system's PATH
3. Use FoxyProxy or a similar tool to configure your browser to route WebSocket traffic through the proxy. Restrict the proxy settings to only intercept the desired WebSocket connections
4. Run the application:
   ```bash
   python main.py
   ```
4. Click "Connect" to start intercepting WebSocket traffic

## Configuring FoxyProxy

To configure FoxyProxy for WebSocket interception:

1. Install FoxyProxy in your browser
2. Open FoxyProxy settings and add a new proxy configuration
3. Set the proxy type to "HTTP"
4. Enter `127.0.0.1` as the proxy IP and port to `8080`
6. Save the configuration and enable it for the desired URLs or patterns (e.g., `*.example.com`)