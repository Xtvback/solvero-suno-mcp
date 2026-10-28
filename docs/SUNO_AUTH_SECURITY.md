# Autenticação Suno — avaliação de segurança (28 outubro 2026)

## Decisão
Não automatizar a reutilização de cookies Suno no GitHub Actions enquanto não houver autorização explícita do serviço para esse tipo de acesso. Os Termos Suno (3 setembro 2026) restringem robots, scraping e obtenção de cópias por canais diferentes do download disponibilizado pelo Suno.

## Segurança
O GitHub Actions suporta secrets encriptados, mas o ficheiro Playwright storageState pode conter cookies de sessão que permitiriam acesso à conta. **Nunca** incluir esse estado em commits, artefactos, logs ou outputs. O repositório é público.

## Teste implementado
`tests/test_auth_boundary.py`: usa dados fictícios localmente, verifica que um ficheiro efémero pode ser eliminado e impede acidentalmente a presença de duas variáveis de sessão Suno. Não acede ao Suno, não guarda credenciais nem faz downloads.

## Etapa por resolver
A integração sem qualquer operação manual exige um canal de exportação autorizado e acessível por automação; os atuais conectores não expõem um ficheiro descarregado pelo navegador Suno. Se a plataforma disponibilizar oficialmente um endpoint de downloads compatível com este uso ou um fluxo autorizado, pode acrescentar-se um conector seguro e testes completos.

Referências:
- https://suno.com/terms/
- https://playwright.dev/docs/auth
- https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions
