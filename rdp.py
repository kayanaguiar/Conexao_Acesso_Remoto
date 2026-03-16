import subprocess
import tempfile
import os


def connect(host: str, port: str, username: str, password: str):
    """Abre uma conexão RDP usando cmdkey + mstsc."""
    server = f"{host}:{port}" if port and port != "3389" else host

    # Salva credencial temporária no Windows Credential Manager
    subprocess.run(
        ["cmdkey", f"/generic:TERMSRV/{server}", f"/user:{username}", f"/pass:{password}"],
        creationflags=subprocess.CREATE_NO_WINDOW,
        check=True,
    )

    # Cria arquivo .rdp temporário
    rdp_content = (
        f"full address:s:{server}\n"
        f"username:s:{username}\n"
        "prompt for credentials:i:0\n"
        "authentication level:i:2\n"
    )

    rdp_path = os.path.join(tempfile.gettempdir(), "acessar_servidor.rdp")
    with open(rdp_path, "w") as f:
        f.write(rdp_content)

    subprocess.Popen(["mstsc", rdp_path])
