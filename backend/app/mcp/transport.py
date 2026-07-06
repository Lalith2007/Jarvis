import subprocess
import threading

from app.mcp.models import MCPConnectionStatus


class MCPTransport:
    """
    Base transport. The default implementation is an inert stub (used by
    lightweight registration paths and legacy tests). Real transports override
    connect/disconnect/send.
    """

    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.status = MCPConnectionStatus.DISCONNECTED

    def connect(self) -> bool:
        self.status = MCPConnectionStatus.CONNECTED
        return True

    def disconnect(self) -> None:
        self.status = MCPConnectionStatus.DISCONNECTED

    def send(self, data: str) -> str:
        if self.status != MCPConnectionStatus.CONNECTED:
            raise ConnectionError("Not connected")
        return '{"result": "success"}'


class StdioMCPTransport(MCPTransport):
    """
    Real local MCP transport: spawns an MCP server subprocess and speaks
    line-delimited JSON-RPC over its stdin/stdout. Thread-safe request writes.
    """

    def __init__(self, command: str, args: list[str] | None = None, env: dict | None = None):
        super().__init__(endpoint=command)
        self.command = command
        self.args = args or []
        self.env = env
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()

    def connect(self) -> bool:
        try:
            self._proc = subprocess.Popen(
                [self.command, *self.args],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
                env=self.env,
            )
            self.status = MCPConnectionStatus.CONNECTED
            return True
        except Exception:
            self.status = MCPConnectionStatus.ERROR
            return False

    def disconnect(self) -> None:
        if self._proc:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=5)
            except Exception:
                self._proc.kill()
            self._proc = None
        self.status = MCPConnectionStatus.DISCONNECTED

    def send(self, data: str) -> str:
        if self.status != MCPConnectionStatus.CONNECTED or not self._proc:
            raise ConnectionError("Not connected")
        with self._lock:
            assert self._proc.stdin and self._proc.stdout
            self._proc.stdin.write(data.rstrip("\n") + "\n")
            self._proc.stdin.flush()
            line = self._proc.stdout.readline()
        if not line:
            raise ConnectionError("MCP server closed the connection")
        return line
