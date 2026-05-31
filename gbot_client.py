"""
gbot/gbot_client.py
Standalone client - communicates with gbot_server.py running inside UE.
No unreal imports. Pure Python.
"""
import socket, json, threading
from typing import Callable, Optional

HOST = "localhost"
PORT = 8765
TIMEOUT = 60  # seconds - AI calls can take time


def send_command(command: str) -> dict:
    """Send a command to UE server and return the result dict."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            s.connect((HOST, PORT))
            payload = json.dumps({"command": command}) + "\n"
            s.sendall(payload.encode("utf-8"))
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
                if data.endswith(b"\n"):
                    break
            return json.loads(data.decode("utf-8").strip())
    except ConnectionRefusedError:
        return {"status": "error", "message": "UE not connected. Start gbot_server in UE first."}
    except socket.timeout:
        return {"status": "error", "message": "Command timed out. UE may be busy."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def ping() -> bool:
    """Check if UE server is reachable."""
    result = send_command("ping")
    return result.get("status") == "ok"


def send_async(command: str, callback: Callable[[dict], None]):
    """Send command in background thread - callback called with result."""
    def run():
        result = send_command(command)
        callback(result)
    t = threading.Thread(target=run, daemon=True)
    t.start()
