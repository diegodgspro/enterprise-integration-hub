# Contribuindo

Obrigado por contribuir com o Enterprise Integration Hub. O projeto está em fase de fundação; priorize mudanças pequenas, bem documentadas e alinhadas à arquitetura.

## Princípios

- Não introduza endpoints REST, serviços SOAP, banco funcional ou dependências sem uma tarefa aprovada para a fase correspondente.
- Mantenha os adaptadores de transporte separados da camada de integração e da persistência.
- Não versione segredos, tokens, credenciais ou arquivos `.env`; use `.env.example` apenas como referência de nomes de variáveis.
- Ao adicionar contratos, versione e documente alterações incompatíveis em OpenAPI, WSDL ou XSD.

## Fluxo básico

1. Crie uma branch descritiva a partir da branch principal.
2. Mantenha o escopo da mudança focado e atualize a documentação relacionada.
3. Execute as validações disponíveis antes de abrir uma solicitação de mudança.
4. Descreva objetivo, impacto, validações executadas e decisões relevantes na revisão.

## Convenções iniciais

- Use inglês para nomes de arquivos, código, contratos e identificadores técnicos.
- Use Markdown para a documentação e mantenha exemplos sem dados reais de pacientes.
- Prefira logs estruturados e propague o Correlation ID quando a implementação for iniciada.
- Inclua testes automatizados junto de funcionalidades futuras, com atenção especial a transformação e contratos.

## Segurança e privacidade

Não utilize dados reais de pacientes em exemplos, testes, logs ou screenshots. Reporte vulnerabilidades de forma privada ao responsável pelo repositório, sem abrir uma issue pública com detalhes exploráveis.

