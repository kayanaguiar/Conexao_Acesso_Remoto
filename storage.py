import json
import os
import uuid
from crypto import encrypt, decrypt

_DATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "AcessarServidores")
os.makedirs(_DATA_DIR, exist_ok=True)

DATA_FILE = os.path.join(_DATA_DIR, "connections.json")


def _load_raw() -> list[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_raw(data: list[dict]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def list_connections() -> list[dict]:
    connections = _load_raw()
    for conn in connections:
        conn["password"] = decrypt(conn["password"])
    return connections


def get_connection(conn_id: str) -> dict | None:
    for conn in _load_raw():
        if conn["id"] == conn_id:
            conn["password"] = decrypt(conn["password"])
            return conn
    return None


def add_connection(host: str, port: str, username: str, password: str, description: str) -> dict:
    connections = _load_raw()
    conn = {
        "id": uuid.uuid4().hex,
        "host": host,
        "port": port,
        "username": username,
        "password": encrypt(password),
        "description": description,
    }
    connections.append(conn)
    _save_raw(connections)
    conn["password"] = password
    return conn


def update_connection(conn_id: str, host: str, port: str, username: str, password: str, description: str) -> bool:
    connections = _load_raw()
    for conn in connections:
        if conn["id"] == conn_id:
            conn["host"] = host
            conn["port"] = port
            conn["username"] = username
            conn["password"] = encrypt(password)
            conn["description"] = description
            _save_raw(connections)
            return True
    return False


def delete_connection(conn_id: str) -> bool:
    connections = _load_raw()
    new_connections = [c for c in connections if c["id"] != conn_id]
    if len(new_connections) == len(connections):
        return False
    _save_raw(new_connections)
    return True
