import json

def recv_exact(sock, n_bytes):
    buffer = bytearray()
    while len(buffer) < n_bytes:
        chunk = sock.recv(n_bytes - len(buffer))

        if not chunk:
            raise ConnectionError("Socket closed prematurely")

        buffer.extend(chunk)
    return bytes(buffer)

def receive_message(sock):
    header = recv_exact(sock, 4)

    length = int.from_bytes(header, "big")
    payload_bytes = recv_exact(sock, length)

    return json.loads(payload_bytes.decode("utf-8"))

def send_message(sock, data):
    payload = json.dumps(data).encode("utf-8")
    length = len(payload).to_bytes(4, "big")

    sock.sendall(length)
    sock.sendall(payload)