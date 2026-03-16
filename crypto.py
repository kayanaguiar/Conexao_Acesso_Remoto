import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Dados persistentes ficam em %APPDATA%/AcessarServidores
_DATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "AcessarServidores")
os.makedirs(_DATA_DIR, exist_ok=True)

_SALT_FILE = os.path.join(_DATA_DIR, ".salt")
_VERIFY_FILE = os.path.join(_DATA_DIR, ".verify")

_VERIFY_PHRASE = b"ACESSAR_SERVIDORES_OK"

_fernet: Fernet | None = None


def _load_or_create_salt() -> bytes:
    if os.path.exists(_SALT_FILE):
        with open(_SALT_FILE, "rb") as f:
            return f.read()
    salt = os.urandom(16)
    with open(_SALT_FILE, "wb") as f:
        f.write(salt)
    return salt


def _derive_key(password: str) -> bytes:
    salt = _load_or_create_salt()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1_200_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def is_first_run() -> bool:
    """Retorna True se ainda não existe uma senha mestre cadastrada."""
    return not os.path.exists(_VERIFY_FILE)


def create_master_password(password: str):
    """Cria a senha mestre pela primeira vez."""
    global _fernet
    key = _derive_key(password)
    f = Fernet(key)
    # Salva um token de verificação para validar a senha futuramente
    with open(_VERIFY_FILE, "wb") as file:
        file.write(f.encrypt(_VERIFY_PHRASE))
    _fernet = f


def authenticate(password: str) -> bool:
    """Valida a senha mestre. Retorna True se correta."""
    global _fernet
    if not os.path.exists(_VERIFY_FILE):
        return False
    key = _derive_key(password)
    f = Fernet(key)
    try:
        with open(_VERIFY_FILE, "rb") as file:
            token = file.read()
        result = f.decrypt(token)
        if result == _VERIFY_PHRASE:
            _fernet = f
            return True
    except InvalidToken:
        pass
    return False


def encrypt(text: str) -> str:
    if _fernet is None:
        raise RuntimeError("Autenticação necessária antes de criptografar.")
    return _fernet.encrypt(text.encode()).decode()


def decrypt(token: str) -> str:
    if _fernet is None:
        raise RuntimeError("Autenticação necessária antes de descriptografar.")
    return _fernet.decrypt(token.encode()).decode()
