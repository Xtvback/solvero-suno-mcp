# Solvero Suno MCP

Servidor MCP experimental em Python, disponível localmente por **stdio** e remotamente por **Streamable HTTP**.

## Funcionalidades v0.1
- Preparar briefs musicais para Suno
- Guardar e consultar um catálogo local de músicas

**Limitações:** Não existe ligação ativa à conta Suno. O projeto não gera, descarrega, envia ou publica músicas na plataforma.

## Executar localmente

```bash
python -m venv .venv
pip install -r requirements.txt
python server.py
```

Configurar o cliente MCP para executar `python` com o argumento `server.py` na pasta deste repositório. A variável opcional `SOLVERO_DATA_DIR` define onde os ficheiros locais são guardados. Não colocar chaves ou dados privados no GitHub.

## Servidor remoto

O endpoint público é `https://solvero-suno-mcp.onrender.com/mcp`. Todas as chamadas MCP exigem um access token Auth0 RS256 para a audience desse endpoint e com o scope `mcp:tools`. Apenas `/health` e os metadados OAuth são públicos.

O deployment usa o plano gratuito do Render. O servidor pode adormecer por inatividade e os ficheiros locais não são armazenamento durável.

Consultar `docs/OAUTH.md`, `docs/REMOTE.md` e `docs/OAUTH_ROLLOUT.md` para detalhes e estado da integração com ChatGPT.

## Estado
OAuth e transporte remoto estão implementados e publicados. O registo do conector no ChatGPT e o primeiro login interativo continuam pendentes. Antes de qualquer operação real no Suno, verificar as regras e documentação oficiais do serviço.
