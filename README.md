# Enterprise Integration Hub

Uma fundação de portfólio profissional para demonstrar integração de sistemas corporativos de saúde. O projeto conectará sistemas hospitalares legados baseados em SOAP/XML a aplicações modernas orientadas a REST/JSON, preservando uma camada de integração explícita e auditável.

> Estado atual: fundação arquitetural e documental. Nenhum endpoint REST ou SOAP, banco de dados funcional ou dependência de aplicação foi implementado nesta etapa.

## Problema de negócio

Organizações de saúde frequentemente precisam trocar informações entre sistemas legados e produtos mais recentes. Os sistemas podem usar contratos, formatos de dados e protocolos distintos, o que aumenta o custo de manutenção e o risco de inconsistências.

O Enterprise Integration Hub propõe uma camada intermediária que recebe e expõe SOAP/XML e REST/JSON, transforma dados para um modelo interno e, futuramente, coordena a persistência em PostgreSQL. A proposta permite modernizar integrações sem exigir a substituição imediata dos sistemas legados.

## Cenário empresarial

Um sistema hospitalar legado envia uma solicitação SOAP/XML. O Hub a valida contra os contratos definidos, converte o conteúdo para um objeto interno e encaminha a operação à interface REST. No sentido inverso, consumidores REST recebem JSON enquanto o Hub adapta a resposta ao contrato SOAP/XML esperado pelo legado.

## Objetivo

Demonstrar, de forma progressiva e reproduzível, boas práticas de integração corporativa: contratos bem definidos, separação de responsabilidades, autenticação, rastreabilidade, tratamento consistente de erros e testes automatizados.

## Arquitetura

```text
Legacy Hospital System
        |
     SOAP/XML
        v
SOAP Web Service
        |
        v
Integration Layer <----> REST API <----> PostgreSQL
        |
  XML <-> modelo interno <-> JSON
```

O detalhamento dos componentes e fluxos está em [docs/architecture.md](docs/architecture.md).

## Tecnologias planejadas

- Python
- FastAPI, para a futura API REST e documentação OpenAPI
- Biblioteca SOAP compatível com WSDL e XSD (a ser selecionada na fase de implementação)
- PostgreSQL
- Docker e Docker Compose
- Pytest
- JWT para autenticação de consumidores REST, conforme os requisitos da fase de segurança
- Postman para coleções e cenários de integração

Nenhuma dependência é declarada nesta fase; elas serão introduzidas apenas quando houver uma necessidade funcional concreta.

## Fluxo de integração

1. Um consumidor legado chama a interface SOAP usando XML.
2. A interface SOAP valida e delega a solicitação à camada de integração.
3. A camada transforma XML em um modelo interno independente de transporte.
4. A interface REST usa o modelo interno e, em fases futuras, coordena o acesso ao PostgreSQL.
5. As respostas percorrem o caminho inverso, convertendo o modelo interno em JSON ou XML conforme o consumidor.

## Estrutura inicial

```text
.
├── docs/
│   ├── architecture/
│   ├── examples/
│   ├── screenshots/
│   └── architecture.md
├── .env.example
├── .gitignore
├── CONTRIBUTING.md
└── README.md
```

## Roadmap

- [x] Fundação do repositório e documentação arquitetural
- [ ] Definir contratos de integração (OpenAPI, WSDL e XSD)
- [ ] Criar a estrutura de aplicação Python e as interfaces REST e SOAP
- [ ] Implementar modelo interno, transformações XML/JSON e tratamento de erros
- [ ] Adicionar persistência PostgreSQL e migrações
- [ ] Implementar JWT, logs estruturados e Correlation ID
- [ ] Criar testes automatizados e coleções Postman
- [ ] Containerizar a aplicação e documentar a execução local

## Próximos passos

Após a revisão desta fundação, a próxima fase deve começar pelos contratos e pela estrutura de aplicação, mantendo REST, SOAP e persistência desacoplados da lógica de transformação.

