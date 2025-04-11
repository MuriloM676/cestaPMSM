# Sistema de Gerenciamento de Beneficiários - CestaPMSM

## Descrição
O **CestaPMSM** é um sistema web desenvolvido para gerenciar beneficiários de cestas básicas em uma prefeitura. Ele permite o cadastro de beneficiários, a marcação de cestas como retiradas, a filtragem de beneficiários por nome, telefone ou status da cesta, e a visualização do histórico de retiradas. O sistema possui um controle de acesso com dois tipos de usuários: administradores (que podem cadastrar beneficiários) e usuários comuns (que podem apenas visualizar e marcar cestas como retiradas).

O projeto foi desenvolvido usando **Flask** (um framework web em Python) e **SQLite** como banco de dados (com opção de migração para MySQL). Ele pode ser executado localmente ou implantado em um servidor usando Docker.

---

## Funcionalidades
- **Autenticação de Usuários**:
  - Login e logout com controle de acesso baseado em papéis (admin e user).
- **Gerenciamento de Beneficiários**:
  - Cadastro de beneficiários (nome, telefone, endereço) - restrito a administradores.
  - Filtros por nome, telefone e status da cesta (retirada ou não retirada).
  - Paginação para exibir beneficiários em lotes de 10 por página.
- **Marcação de Cestas**:
  - Marcar cestas como retiradas, com registro automático no histórico.
- **Histórico de Retiradas**:
  - Visualização do histórico de retiradas com data, nome do beneficiário e ID.

---

## Tecnologias Utilizadas
- **Backend**: Flask (Python)
- **Banco de Dados**: SQLite (com opção de migração para MySQL)
- **Frontend**: HTML, CSS (estilização básica)
- **Controle de Acesso**: Sessões do Flask
- **Implantação**: Docker (opcional)

---

## Pré-requisitos
Antes de executar o projeto, certifique-se de ter os seguintes itens instalados:
- **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
- **pip** (gerenciador de pacotes do Python)
- **Git** (opcional, para clonar o repositório): [Download Git](https://git-scm.com/downloads)
- **Docker** (opcional, para rodar com contêineres): [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **MySQL** (se optar por usar MySQL em vez de SQLite): [Download MySQL](https://dev.mysql.com/downloads/mysql/)

---

## Instalação e Configuração

### 1. Clonar o Repositório (se aplicável)
Se o projeto estiver em um repositório Git, clone-o:
```bash
git clone https://github.com/seu-usuario/cestaPMSM.git
cd cestaPMSM