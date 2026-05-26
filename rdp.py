import subprocess


def connect(host: str, port: str, username: str, password: str):
    """Abre uma conexão RDP usando cmdkey + mstsc direto (sem arquivo .rdp).

    Chamar mstsc com /v: em vez de passar um arquivo .rdp evita o aviso
    "Cuidado: conexão remota desconhecida / Distribuidor: Fornecedor desconhecido",
    que o Windows dispara para arquivos .rdp não assinados.
    """
    server = f"{host}:{port}" if port and port != "3389" else host

    subprocess.run(
        ["cmdkey", f"/generic:TERMSRV/{server}", f"/user:{username}", f"/pass:{password}"],
        creationflags=subprocess.CREATE_NO_WINDOW,
        check=True,
    )

    subprocess.Popen(["mstsc", f"/v:{server}"])
