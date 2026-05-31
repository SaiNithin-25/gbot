"""
gbot/gbot_server.py
Runs inside UE Python. Accepts commands from standalone app via TCP socket.
Start with: exec(open("D:/Collage/gbot/gbot_server.py").read())
"""
import sys, os, asyncio, json, threading, socket
import queue as _queue
_command_queue = _queue.Queue()
_result_store = {}
sys.path.insert(0, os.path.dirname(__file__))

import gbot_runner

import time as _time
_world_cache = {"actors": [], "last_update": 0}

def _update_world_cache(dt):
    try:
        import unreal
        actors = unreal.EditorLevelLibrary.get_all_level_actors()
        cache = []
        for a in actors:
            label = a.get_actor_label()
            loc = a.get_actor_location()
            cls = a.get_class().get_name()
            cache.append({
                "label": label,
                "class": cls,
                "location": [round(loc.x), round(loc.y), round(loc.z)]
            })
        _world_cache["actors"] = cache
        _world_cache["last_update"] = _time.time()
    except Exception:
        pass

def _process_command_queue(dt):
    """Process one command per tick on the main thread."""
    try:
        item = _command_queue.get_nowait()
        cmd_id = item["id"]
        command = item["command"]
        event = item["event"]
        try:
            import asyncio
            result = asyncio.run(gbot_runner.run_command(command))
            _result_store[cmd_id] = {"status": "ok", "report": result}
        except Exception as e:
            _result_store[cmd_id] = {"status": "error", "message": str(e)}
        finally:
            event.set()
    except _queue.Empty:
        pass

_tick_handle = None

HOST = "localhost"
PORT = 8765
_server_thread = None
_running = False


def handle_client(conn):
    """Handle one client connection - receive command, execute, return result."""
    try:
        data = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
            if data.endswith(b"\n"):
                break

        payload = json.loads(data.decode("utf-8").strip())
        command = payload.get("command", "").strip()
        print(f"[Gbot Server] Received: {command}")

        if command == "ping":
            result = {"status": "ok", "message": "Gbot server ready"}
        elif command == "grill_the_world":
            result = asyncio.run(handle_grill())
        else:
            result = asyncio.run(handle_command(command))

        response = json.dumps(result) + "\n"
        conn.sendall(response.encode("utf-8"))
    except Exception as e:
        error = json.dumps({"status": "error", "message": str(e)}) + "\n"
        conn.sendall(error.encode("utf-8"))
    finally:
        conn.close()


async def handle_command(command: str) -> dict:
    """Queue command for main thread execution, wait for result."""
    import threading, uuid
    cmd_id = str(uuid.uuid4())
    event = threading.Event()
    _command_queue.put({
        "id": cmd_id,
        "command": command,
        "event": event
    })
    # Wait for main thread to process it (max 120s for AI + spawn)
    event.wait(timeout=120.0)
    return _result_store.pop(cmd_id, {
        "status": "error", "message": "Command timed out."
    })


async def handle_grill() -> dict:
    try:
        actor_info = _world_cache.get("actors", [])
        if not actor_info:
            return {"status": "error", "message": "World cache empty — wait 2 seconds and try again."}

        gbot_actors = [a for a in actor_info if a["label"].startswith("Gbot_")]
        total = len(actor_info)
        gbot_count = len(gbot_actors)

        type_counts = {}
        for a in gbot_actors:
            parts = a["label"].split("_")
            t = parts[1].lower() if len(parts) > 1 else "unknown"
            type_counts[t] = type_counts.get(t, 0) + 1

        from ai.orchestrator import AIOrchestrator
        ai = AIOrchestrator()
        context = {
            "total_actors": total,
            "gbot_structures": gbot_count,
            "structure_types": type_counts,
            "sample_locations": [a["location"] for a in gbot_actors[:5]]
        }
        prompt = (
            f"You are Gbot, an AI worldbuilding assistant.\n"
            f"Analyze this Unreal Engine world and give a short, clear, "
            f"friendly summary in 3-4 sentences.\n"
            f"World data: {json.dumps(context)}\n"
            f"Talk about what has been built, the layout, and what kind of "
            f"world this feels like. Be descriptive and interesting.\n"
            f"Respond with plain text only, no JSON, no markdown."
        )
        raw = await ai._call_ollama(prompt)
        summary = raw.strip() if raw.strip() else (
            f"This world contains {gbot_count} Gbot structures across "
            f"{total} total actors. Breakdown: {type_counts}."
        )
        return {
            "status": "ok",
            "type": "grill_result",
            "total_actors": total,
            "gbot_structures": gbot_count,
            "structure_types": type_counts,
            "summary": summary
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def server_loop():
    """Main server loop - runs in background thread."""
    global _running
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        s.settimeout(1.0)
        print(f"[Gbot Server] Listening on {HOST}:{PORT}")
        while _running:
            try:
                conn, addr = s.accept()
                t = threading.Thread(target=handle_client, args=(conn,), daemon=True)
                t.start()
            except socket.timeout:
                continue
            except Exception as e:
                if _running:
                    print(f"[Gbot Server] Error: {e}")
                break
    print("[Gbot Server] Stopped.")


def start_server():
    global _server_thread, _running, _tick_handle
    if _running:
        print("[Gbot Server] Already running.")
        return

    # Pre-initialize gbot_runner on main thread before server starts
    import asyncio
    asyncio.run(gbot_runner._init())
    print("[Gbot Server] Gbot runner initialized.")

    # Register world cache tick
    import unreal
    _tick_handle = unreal.register_slate_post_tick_callback(_update_world_cache)
    unreal.register_slate_post_tick_callback(_process_command_queue)
    print("[Gbot Server] World cache tick registered.")

    _running = True
    _server_thread = threading.Thread(target=server_loop, daemon=True)
    _server_thread.start()
    print(f"[Gbot Server] Started on port {PORT}")


def stop_server():
    global _running
    _running = False
    print("[Gbot Server] Stopping...")


# Auto-start when exec'd in UE
start_server()
