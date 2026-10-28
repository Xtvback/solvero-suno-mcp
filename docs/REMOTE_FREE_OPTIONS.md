# Investigação: fluxo remoto sem custo adicional (28-10-2026)

## Restrições
- Interação apenas por ChatGPT (sem instalação local).
- Não contratar serviços, comprar downloads ou gastar créditos em testes.
- Não expor cookies, MP3s, capas privadas nem tokens num repositório público.
- Não usar endpoints não oficiais, contornar quotas ou proteções do Suno.
- Verificar ficheiro na Drive antes de iniciar download.

## Evidência atual
- Suno: descarregar novamente **a mesma música** não consome outro download. Também se aplica a outros formatos dessa música; uma música nunca descarregada consome quota. Fonte: https://help.suno.com/en/articles/13926209
- GitHub Actions: executores standard gratuitos em repositórios públicos, mas os workflows e logs podem expor dados; não enviar música privada para artefactos públicos. Fonte: https://docs.github.com/en/actions/concepts/billing-and-usage
- Cloudflare Browser Run: plano Free anuncia 10 minutos de browser/dia e até 3 browsers simultâneos. Fonte: https://developers.cloudflare.com/browser-run/pricing/
- Cloudflare Workers Free tem limites de CPU muito curtos (10 ms/request); processar/transcodificar áudio numa request não é adequado. Fonte: https://developers.cloudflare.com/workers/platform/limits/

## Opções ordenadas
1. **Usar conectores de ChatGPT (browser + Google Drive)**. O Google Drive já dispõe de upload_file para objetos de ficheiro. Bloqueio: o browser usado no Suno ainda não expõe um ficheiro transferível para este conector. Precisa de capacidade nativa de exportar o download ou de sessão no mesmo computador.
2. **Cloudflare Browser Run + Worker com segurança OAuth**. Arquitetura possível: uma ação autorizada começa uma sessão browser, clica no download oficial, captura bytes de resposta/ficheiro, incorpora ID3 num processo adequado e entrega objeto ao Google Drive API. Validar **primeiro** se cookies/sessões e o download são suportados sem exfiltrar cookies nem superar os 10 minutos diários. Não ativar billing.
3. **GitHub Actions**. Pode testar funções *sem autenticação*: organização de nomes, tags ID3 em MP3 fictício, fluxo de upload de teste. Não guardar cookies do Suno no repo público. Não é substituto adequado da sessão privada Suno sem desenho seguro de secrets.
4. **TinyFish**. Permite editar a biblioteca, mas automações podem ser cobradas e o download não apareceu como recurso exportável; não usar enquanto custo zero não estiver verificado.
5. **MCP Python no Render Free**. Pode coordenar metadados e pedidos ao Drive, mas o processo deve receber MP3 por canal autorizado; não inventar ligação Suno.

## Próximo teste livre de downloads
- Criar e validar testes unitários usando dados fictícios (sem Suno), mais um teste de upload de um ficheiro sintético por conector oficial Google Drive, apenas quando autorizado a criar o ficheiro.
- Ensaiar o transporte a partir do browser com um ficheiro de teste público, não com áudio Suno e sem credenciais; não iniciar serviço cobrado.
- Quando o transporte for comprovado, testar UMA canção já desbloqueada, confirmar quotas e destino, e guardar capa/ID3.
- Separar 'metadados preparados', 'música publicada', 'download obtido', 'Drive confirmado' como estados distintos.

## Segurança
Cloudflare Browser Run e GitHub Actions têm quotas, não garantias de gratuidade em qualquer plano/configuração. Bloquear faturação/limites e nunca iniciar pagamentos. É essencial não publicar downloads nem credenciais em URLs, commits, artefactos ou logs.
