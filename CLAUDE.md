# Acessar Servidores — Gerenciador RDP

## Sobre o Projeto

Aplicação desktop Python/Tkinter para gerenciar conexões de Área de Trabalho Remota (RDP) no Windows. Permite cadastrar, editar, excluir e conectar rapidamente a servidores via `mstsc.exe`. Protegida por senha mestre.

## Estrutura

```
main.py          → Ponto de entrada (python main.py)
login.py         → Tela de autenticação (senha mestre)
app.py           → Interface gráfica (Tkinter, tema escuro, widgets customizados)
storage.py       → CRUD de conexões em JSON (connections.json)
crypto.py        → Criptografia de senhas (Fernet + PBKDF2HMAC, 1.2M iterações)
rdp.py           → Lança conexão RDP via cmdkey + mstsc.exe
create_icon.py   → Script para gerar icon.ico
icon.ico         → Ícone do app (monitor com símbolo de conexão)
```

## Arquitetura

- **Autenticação**: Senha mestre do usuário → PBKDF2HMAC (1.2M iterações) → chave Fernet. Sem senha correta, dados são inacessíveis
- **GUI**: Tkinter puro com widgets customizados (`FlatEntry`, `FlatButton`, `ConnectionCard`)
- **Armazenamento**: JSON simples em `%APPDATA%/AcessarServidores/connections.json`
- **Criptografia**: Senhas criptografadas com Fernet/AES-256. Chave derivada da senha mestre via PBKDF2HMAC + salt
- **RDP**: Usa `cmdkey` para salvar credencial temporária no Windows Credential Manager e `mstsc` com arquivo `.rdp` temporário
- **Dados persistentes**: Salvos em `%APPDATA%/AcessarServidores/` (funciona com .exe standalone)

## Fluxo de Autenticação

1. Primeiro acesso → cria senha mestre (salva token de verificação em `.verify`)
2. Acessos seguintes → valida senha contra o token de verificação
3. Senha correta → inicializa Fernet e abre o app principal
4. A chave é 100% derivada da senha do usuário (sem arquivo de chave)

## Dependências

- Python 3.13+
- `cryptography` (Fernet, PBKDF2HMAC)
- Tkinter (incluso no Python)
- Windows (mstsc.exe, cmdkey)
- PyInstaller (para gerar .exe)

## Build (.exe)

```bash
pyinstaller --onefile --windowed --name "Acessar Servidores" --icon=icon.ico --add-data "icon.ico;." main.py --noconfirm
```
Resultado: `dist/Acessar Servidores.exe` (~16 MB, standalone)

## Arquivos Sensíveis (não commitar)

- `.salt` — salt para derivação PBKDF2
- `.verify` — token de verificação da senha mestre
- `connections.json` — dados das conexões (senhas criptografadas)

Obs: Em produção (.exe), esses ficam em `%APPDATA%/AcessarServidores/`

## Atalhos de Teclado

- `Ctrl+S` — Salvar conexão
- `Ctrl+N` — Nova conexão (limpa formulário)
- `Enter` — Conectar
- `Esc` — Limpar formulário
- `↑` / `↓` — Navegar entre conexões
- `Enter` (na tela de login) — Autenticar
- Duplo clique no card — Conectar

## Convenções

- Tema escuro com paleta Indigo (#6366f1 accent)
- Fontes: Segoe UI (UI) + Cascadia Code (dados técnicos)
- Português brasileiro na interface
- DPI awareness habilitado via `ctypes.windll.shcore.SetProcessDpiAwareness`
- Title bar escura via DwmSetWindowAttribute (Windows 10/11)
- Janelas abrem centralizadas (withdraw → posicionar → deiconify)
- Campos de senha com toggle "Exibir/Ocultar"
- Focus automático no campo de senha ao abrir login
