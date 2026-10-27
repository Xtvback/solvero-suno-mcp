# Solvero Suno MCP

Servidor MCP experimental, desenvolvido em Python para utilização local através de **stdio**.

## Funcionalidades v0.1
- Preparar briefs musicais para Suno\n- Guardar e consultar um catálogo local de músicas

**Limitações:** Não existe autenticação nem ligação ativa à conta Suno. Não gera, descarrega, envia ou publica músicas nas plataformas. O servidor stdio não pode ser ligado diretamente como servidor remoto ao ChatGPT; para isso será preciso alojamento HTTPS e autenticação adequada.

## Executar localmente

```bash
python -m venv .venv
pip install -r requirements.txt
python server.py
```

Configurar o cliente MCP para executar `python` com o argumento `server.py` na pasta deste repositório. A variável opcional `SOLVERO_DATA_DIR` define onde os ficheiros locais são guardados. Não colocar chaves ou dados privados no GitHub.

## Estado
Versão inicial de desenvolvimento. Antes de qualquer operação real, verificar as regras e documentação oficiais do serviço.
