# Autenticação com GitHub — Guia de Segurança

Nunca coloque tokens, senhas ou credenciais em texto aberto no chat, commits, issues ou arquivos do repositório. Mensagens ficam no histórico, podem ser logadas e qualquer sistema no caminho pode capturar.

## Opção 1: Variável de ambiente

A mais simples. No seu terminal:

```bash
# Adicione ao ~/.bashrc ou ~/.zshrc para persistir
export GITHUB_TOKEN="ghp_seu_token_aqui"
```

Use em scripts:
```bash
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user/repos
git remote set-url origin https://$GITHUB_TOKEN@github.com/Tretabolt/ice-core-data-lab.git
```

O token nunca aparece no chat nem no histórico de comandos (desde que não seja colado inline).

## Opção 2: GitHub CLI (`gh`) — Recomendado

Instalação:
```bash
# macOS
brew install gh

# Linux (Debian/Ubuntu)
sudo apt install gh

# Windows
winget install GitHub.cli
```

Autenticação:
```bash
gh auth login
```

Ele abre o navegador ou pede o token no terminal local. Depois disso, o `gh` já está autenticado. Use:

```bash
gh repo create ice-core-data-lab --public --source=. --push
gh repo view Tretabolt/ice-core-data-lab
gh api repos/Tretabolt/ice-core-data-lab/issues
```

Nunca precise digitar o token de novo.

## Opção 3: Arquivo `.netrc`

O Git lê automaticamente desse arquivo:

```bash
# Crie ou edite ~/.netrc
echo "machine github.com login Tretabolt password ghp_seu_token" >> ~/.netrc
chmod 600 ~/.netrc  # só você pode ler
```

Depois, `git push` e `git pull` funcionam sem pedir credenciais.

**Atenção:** em macOS, o arquivo se chama `~/.netrc` (mesmo nome). No Windows, use `%USERPROFILE%\.netrc`.

## Opção 4: Git Credential Store

O Git salva as credenciais após o primeiro uso:

```bash
git config --global credential.helper store
```

Na próxima vez que fizer `git push`, ele pede usuário e token uma vez e salva em `~/.git-credentials` (texto plano, proteja com `chmod 600`).

Para mais segurança, use o `cache` (armazena em memória por tempo limitado):
```bash
git config --global credential.helper 'cache --timeout=3600'
```

## Opção 5: Git Credential Manager (GCM)

A opção mais robusta. Armazena tokens de forma criptografada no keyring do sistema:

```bash
# Instalação (Linux)
git-credential-manager configure

# Ou via .gitconfig
[credential]
    helper = /usr/share/gcm-core/git-credential-manager
```

No macOS/Windows, o GCM integra com o Keychain/Credential Manager do sistema.

## Criando um Personal Access Token

1. Acesse https://github.com/settings/tokens
2. Clique em **Generate new token** → **Fine-grained token**
3. Defina nome, expiração e permissões (mínimo necessário)
4. Copie o token **uma única vez** — depois disso, GitHub não mostra de novo

### Permissões recomendadas para este projeto

| Escopo | Nível | Por quê |
|---|---|---|
| `repo` | read/write | Clonar, push, pull |
| `workflow` | read | Ler GitHub Actions |

## Regra de ouro

> O token pode existir na máquina. Não deve passar pelo chat.

Se o token for exposto por engano:

1. **Revogue imediatamente** em https://github.com/settings/tokens
2. Gere um novo token
3. Atualize onde estiver armazenado (`~/.netrc`, variável de ambiente, etc.)
