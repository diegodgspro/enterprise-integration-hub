# Arquitetura — Enterprise Integration Hub

## Visão geral

O Enterprise Integration Hub será uma plataforma de integração para interoperabilidade entre sistemas hospitalares legados que utilizam SOAP/XML e consumidores modernos que utilizam REST/JSON. A arquitetura separa os adaptadores de transporte, a lógica de integração e a persistência, para que uma mudança de protocolo não se propague pela aplicação inteira.

Nesta etapa, esta é uma arquitetura-alvo: não há serviços, banco de dados, contratos executáveis ou dependências instaladas.

## Componentes

| Componente | Responsabilidade futura |
| --- | --- |
| Sistema hospitalar legado | Consumir e produzir mensagens SOAP/XML. |
| Serviço SOAP | Expor operações descritas por WSDL, validar XML com XSD e adaptar o transporte SOAP. |
| Camada de integração | Normalizar entradas para um modelo interno, coordenar regras de orquestração e transformar saídas. |
| API REST | Expor recursos JSON, aplicar autenticação/autorização e publicar OpenAPI. |
| Persistência | Armazenar dados operacionais no PostgreSQL através de uma camada de acesso dedicada. |
| Observabilidade | Correlacionar requisições, registrar eventos estruturados e produzir sinais operacionais. |

## Fluxo SOAP

1. O sistema legado envia uma requisição SOAP contendo XML.
2. O adaptador SOAP valida a mensagem e o contrato aplicável (WSDL/XSD).
3. O adaptador converte os dados para o modelo interno canônico.
4. A camada de integração executa a orquestração necessária e usa as portas internas adequadas.
5. O resultado é convertido em resposta SOAP/XML ou em uma SOAP Fault padronizada.

## Fluxo REST

1. Um consumidor envia uma requisição HTTP para a API REST com corpo JSON.
2. A API valida autenticação, autorização e o contrato OpenAPI.
3. O adaptador REST converte o JSON para o mesmo modelo interno usado pelo fluxo SOAP.
4. A camada de integração orquestra a operação e consulta ou persiste dados quando necessário.
5. A API serializa a resposta em JSON e devolve um código HTTP coerente com o resultado.

## Transformação de dados

XML e JSON são formatos de fronteira, não o modelo central do domínio. Adaptadores específicos transformarão cada formato em objetos internos tipados. Isso reduz o acoplamento entre SOAP, REST e armazenamento, além de concentrar regras de mapeamento e validação em locais testáveis.

Os contratos WSDL, XSD e OpenAPI deverão ser tratados como artefatos versionados. Mudanças incompatíveis exigirão uma nova versão de contrato e um período explícito de convivência.

## Persistência

O PostgreSQL será a fonte de persistência relacional futura. A lógica de negócio acessará dados por interfaces internas; adaptadores SOAP e REST não devem executar SQL nem depender de detalhes de tabelas. Migrações e modelo físico serão definidos somente quando os primeiros casos de uso forem aprovados.

## Autenticação

Para a futura API REST, JWT será o mecanismo planejado de autenticação. A validação do token ficará na borda HTTP, e a camada de integração receberá apenas o contexto de identidade necessário. A segurança do endpoint SOAP será definida junto dos requisitos de parceiros, podendo incluir TLS mútuo, credenciais de serviço ou WS-Security.

## Observabilidade

Cada solicitação deverá receber ou propagar um Correlation ID. Logs estruturados deverão registrar esse identificador, o adaptador de entrada, a operação, o resultado e informações de erro seguras para diagnóstico. Métricas e tracing distribuído podem ser incorporados posteriormente, sem expor dados sensíveis de pacientes nos sinais operacionais.

## Tratamento de erros

Erros internos serão classificados em validação, autenticação/autorização, conflito de negócio, indisponibilidade de dependência e falha inesperada. A tradução para o transporte ocorrerá apenas na borda:

- REST: status HTTP e corpo JSON consistente, sem detalhes internos.
- SOAP: SOAP Fault com código e mensagem compatíveis com o contrato.

Os detalhes técnicos deverão permanecer nos logs correlacionados, evitando vazamento de dados sensíveis.

## Decisões arquiteturais

| Decisão | Justificativa |
| --- | --- |
| Modelo interno independente de transporte | Evita acoplamento entre XML, JSON, endpoints e banco. |
| Adaptadores nas bordas | Isola detalhes de SOAP, REST e PostgreSQL da orquestração. |
| Contratos versionados | Protege integrações externas contra mudanças acidentais. |
| Dependências adiadas | Mantém a fundação simples até que os contratos e casos de uso definam necessidades reais. |
| Correlation ID desde o desenho | Facilita suporte e investigação de fluxos distribuídos. |

## Possíveis evoluções

- Versionamento e publicação formal de OpenAPI, WSDL e XSD.
- Filas ou eventos assíncronos para operações de longa duração.
- Idempotência, retentativas e circuit breakers para dependências externas.
- Controle de acesso baseado em papéis e rotação de chaves JWT.
- Métricas, tracing e alertas operacionais.
- Mascaramento de dados e trilhas de auditoria adequadas ao contexto de saúde.
- Estratégia de testes de contrato, integração e ponta a ponta.

