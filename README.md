# Acessar Servidores

Gerenciador de conexões de Área de Trabalho Remota (RDP) para Windows, com interface moderna e senhas protegidas por criptografia AES-256.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## Funcionalidades

- **CRUD completo** de conexões RDP (host, porta, usuário, senha, descrição)
- **Conexão automática** — abre a Área de Trabalho Remota com um clique
- **Senha mestre** — protege o acesso ao app e deriva a chave de criptografia
- **Criptografia AES-256** — senhas armazenadas com Fernet + PBKDF2HMAC (1.2M iterações)
- **Busca em tempo real** — filtra conexões por descrição, host ou usuário
- **Navegação por teclado** — setas, Enter, Ctrl+S, Ctrl+N, Esc
- **Interface escura** — tema Indigo com widgets customizados
- **Executável standalone** — distribua apenas o `.exe`, sem dependências

## Como usar

### Executável (.exe)

Baixe o `Acessar Servidores.exe` da [página de Releases](../../releases) e execute. Não precisa instalar nada.

### A partir do código-fonte

```bash
# Clone o repositório
git clone https://github.com/kayanaguiar/Conexao_Acesso_Remoto.git
cd Conexao_Acesso_Remoto

# Instale a dependência
pip install cryptography

# Execute
python main.py
```

## Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| `↑` / `↓` | Navegar entre conexões |
| `Enter` | Conectar |
| `Ctrl+S` | Salvar conexão |
| `Ctrl+N` | Nova conexão |
| `Esc` | Limpar formulário |

## Segurança

- A senha mestre **nunca é armazenada** — apenas um token de verificação criptografado
- A chave de criptografia é **derivada da senha** via PBKDF2HMAC com salt aleatório e 1.200.000 iterações
- Sem a senha correta, os dados são **inacessíveis**
- Dados salvos em `%APPDATA%\AcessarServidores\` (isolados por usuário do Windows)

## Build

Para gerar o executável:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Acessar Servidores" --icon=icon.ico --add-data "icon.ico;." main.py --noconfirm
```

O resultado fica em `dist/Acessar Servidores.exe` (~16 MB).

## Estrutura do Projeto

```
main.py          → Ponto de entrada
login.py         → Tela de autenticação (senha mestre)
app.py           → Interface gráfica (Tkinter, tema escuro)
storage.py       → CRUD de conexões em JSON
crypto.py        → Criptografia (Fernet + PBKDF2HMAC)
rdp.py           → Conexão RDP via cmdkey + mstsc.exe
create_icon.py   → Gerador do ícone
icon.ico         → Ícone do app
```

## Requisitos

- Windows 10/11
- Python 3.13+ (para rodar do código-fonte)
- `cryptography` (única dependência externa)
