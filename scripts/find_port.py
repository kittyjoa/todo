"""Find an available TCP port starting from the given port."""
import socket
import sys


def find_port(start: int = 8080) -> int:
    """Return the first available port from start up to start+3."""
    for port in range(start, start + 4):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("127.0.0.1", port))
            s.close()
            return port
        except OSError:
            pass
    raise RuntimeError("No available port in range")


if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(find_port(start))
