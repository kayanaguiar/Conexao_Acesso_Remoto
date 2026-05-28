import subprocess
import tempfile
import os


def _is_domain_user(username: str) -> bool:
    # Usuários de domínio vêm como DOMINIO\user ou user@dominio. Para esses,
    # o mstsc precisa de arquivo .rdp com username:s: para casar com a
    # credencial salva e fazer login automático.
    return "\\" in username or "@" in username


def connect(host: str, port: str, username: str, password: str):
    """Abre uma conexão RDP usando cmdkey + mstsc.

    Abordagem híbrida:
      - User de domínio (DOMINIO\\user ou user@dominio): cria arquivo .rdp
        com username:s:, o que dispara o aviso "Cuidado: conexão remota
        desconhecida" mas garante login automático.
      - User local: chama mstsc /v: direto sem arquivo .rdp, evitando o aviso.
    """
    server = f"{host}:{port}" if port and port != "3389" else host

    # Limpa qualquer credencial residual (Domain + LegacyGeneric) para o
    # servidor, evitando que o mstsc reuse user/senha de uma conexão anterior
    # quando o usuário troca o user cadastrado no app.
    subprocess.run(
        ["cmdkey", f"/delete:TERMSRV/{server}"],
        creationflags=subprocess.CREATE_NO_WINDOW,
        capture_output=True,
    )

    subprocess.run(
        ["cmdkey", f"/add:TERMSRV/{server}", f"/user:{username}", f"/pass:{password}"],
        creationflags=subprocess.CREATE_NO_WINDOW,
        check=True,
    )

    if _is_domain_user(username):
        rdp_content = (
            f"full address:s:{server}\n"
            f"username:s:{username}\n"
            "prompt for credentials:i:0\n"
            "authentication level:i:2\n"
            "enablecredsspsupport:i:1\n"
        )
        rdp_path = os.path.join(tempfile.gettempdir(), "acessar_servidor.rdp")
        with open(rdp_path, "w", encoding="utf-8") as f:
            f.write(rdp_content)
        subprocess.Popen(["mstsc", rdp_path])
    else:
        subprocess.Popen(["mstsc", f"/v:{server}"])
