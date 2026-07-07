import subprocess
import threading

import json
import logging
from typing import Callable

from app.mcp.models import MCPConnectionStatus


logger = logging.getLogger(__name__)

class MCPTransport:
    """
    Base transport. The default implementation is an inert stub (used by
    lightweight registration paths and legacy tests). Real transports override
    connect/disconnect/send.
    """

    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.status = MCPConnectionStatus.DISCONNECTED
        self.on_notification: Callable[[dict], None] | None = None

    def connect(self) -> bool:
        self.status = MCPConnectionStatus.READY
        return True

    def disconnect(self) -> None:
        self.status = MCPConnectionStatus.DISCONNECTED

    def send(self, data: str, message_id: str | None = None, wait_for_response: bool = True, timeout: float = 10.0) -> str:
        if self.status in (MCPConnectionStatus.DISCONNECTED, MCPConnectionStatus.FAILED, MCPConnectionStatus.UNAVAILABLE):
            raise ConnectionError("Not connected")
        return '{"result": "success"}'


class StdioMCPTransport(MCPTransport):
    """
    Real local MCP transport: spawns an MCP server subprocess and speaks
    line-delimited JSON-RPC over its stdin/stdout. Thread-safe request writes
    and background reader thread to handle async notifications and interweaved logs.
    """

    def __init__(self, command: str, args: list[str] | None = None, env: dict | None = None, cwd: str | None = None):
        super().__init__(endpoint=command)
        self.command = command
        self.args = args or []
        self.env = env
        self.cwd = cwd
        self._proc: subprocess.Popen | None = None
        self._write_lock = threading.Lock()
        
        self._pending_requests: dict[str, threading.Event] = {}
        self._responses: dict[str, str] = {}
        self._reader_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def connect(self) -> bool:
        try:
            # Merge configured env over the current environment so PATH/HOME are
            # preserved (a partial env dict would otherwise replace everything).
            import os as _os

            proc_env = {**_os.environ, **(self.env or {})} if self.env else None
            self._proc = subprocess.Popen(
                [self.command, *self.args],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
                env=proc_env,
                cwd=self.cwd,
            )
            self.status = MCPConnectionStatus.CONNECTING
            self._stop_event.clear()
            self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self._reader_thread.start()
            return True
        except Exception as e:
            logger.error("Failed to start MCP subprocess %s: %s", self.command, e)
            self.status = MCPConnectionStatus.FAILED
            return False

    def _read_loop(self) -> None:
        while not self._stop_event.is_set() and self._proc and self._proc.stdout:
            try:
                line = self._proc.stdout.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    payload = json.loads(line)
                    if "id" in payload:
                        msg_id = str(payload["id"])
                        if msg_id in self._pending_requests:
                            self._responses[msg_id] = line
                            self._pending_requests[msg_id].set()
                    elif "method" in payload and self.on_notification:
                        self.on_notification(payload)
                except json.JSONDecodeError:
                    # Ignore non-JSON lines (e.g. standard console output)
                    pass
            except Exception as e:
                logger.debug("MCP transport read error: %s", e)
                break
                
        self.status = MCPConnectionStatus.DISCONNECTED
        for event in self._pending_requests.values():
            event.set()

    def disconnect(self) -> None:
        self._stop_event.set()
        if self._proc:
            try:
                if self._proc.stdin:
                    self._proc.stdin.close()
                self._proc.terminate()
                self._proc.wait(timeout=2)
            except Exception:
                self._proc.kill()
            self._proc = None
        self.status = MCPConnectionStatus.DISCONNECTED

    def send(self, data: str, message_id: str | None = None, wait_for_response: bool = True, timeout: float = 10.0) -> str:
        if self.status in (MCPConnectionStatus.DISCONNECTED, MCPConnectionStatus.FAILED, MCPConnectionStatus.UNAVAILABLE):
            raise ConnectionError("Not connected")
            
        if not self._proc or not self._proc.stdin:
            raise ConnectionError("Process not running")

        event = None
        if wait_for_response and message_id is not None:
            event = threading.Event()
            self._pending_requests[message_id] = event

        with self._write_lock:
            try:
                self._proc.stdin.write(data.rstrip("\n") + "\n")
                self._proc.stdin.flush()
            except Exception as e:
                if event:
                    self._pending_requests.pop(message_id, None)
                raise ConnectionError(f"Failed to write to MCP subprocess: {e}")

        if not wait_for_response or message_id is None or event is None:
            return ""

        success = event.wait(timeout=timeout)
        self._pending_requests.pop(message_id, None)
        
        if not success:
            raise TimeoutError(f"Timeout waiting for response to {message_id}")
            
        resp = self._responses.pop(message_id, None)
        if not resp:
            raise ConnectionError("Connection closed before receiving response")
            
        return resp
