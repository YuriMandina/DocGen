DocGen - Sistema de Gestão e Automação de Contratos
O DocGen é uma aplicação completa (Full-Stack) projetada para a gestão de Recursos Humanos e geração automatizada de contratos de trabalho. O sistema permite cadastrar a estrutura organizacional, gerenciar colaboradores e automatizar o preenchimento de documentos Word (.docx) com base em modelos predefinidos.

Visão Geral e Tecnologias
A arquitetura do DocGen é dividida entre uma API robusta e uma interface de usuário reativa (Single Page Application).

Backend (API):

Framework: FastAPI com servidor Uvicorn.

Banco de Dados: PostgreSQL, gerenciado via SQLAlchemy e psycopg2.

Processamento de Documentos: Biblioteca python-docx operando 100% em memória RAM (io.BytesIO), garantindo que nenhum arquivo temporário seja salvo no disco do servidor.

Validação de Dados: Pydantic para garantir a integridade dos dados de entrada e saída.

Frontend (Interface):

Framework: Vue.js 3 utilizando a Composition API (<script setup>).

Roteamento: Vue Router para navegação fluida entre telas.

Comunicação HTTP: Axios configurado para consumir a API local na porta 8000.

Instalação e Configuração
1. Configurando o Backend
Certifique-se de ter o Python instalado.

Instale as dependências listadas no projeto:

Bash
pip install -r requirements.txt
Crie um arquivo .env na raiz do backend e defina a variável DATABASE_URL com as credenciais do seu banco de dados PostgreSQL. O sistema impede a inicialização caso esta variável não seja encontrada.

Inicie o servidor:

Bash
uvicorn main:app --reload
Nota: O banco de dados e as tabelas serão criados automaticamente na primeira execução.

2. Configurando o Frontend
Navegue até a pasta do frontend e instale as dependências do Node.js (assumindo o uso de um gerenciador como NPM ou Yarn).

O Axios já está pré-configurado para apontar para http://127.0.0.1:8000.

Inicie o servidor de desenvolvimento do Vue.

Manual do Usuário
A navegação do DocGen ocorre através de um cabeçalho fixo com menus de acesso rápido.

Cargos (/cargos): Permite cadastrar, editar e excluir os cargos da organização. O sistema bloqueia a exclusão de um cargo caso existam funcionários vinculados a ele.

Funcionários (/funcionarios): Módulo para gerenciar a equipe. Possui busca em tempo real e aplica automaticamente uma máscara visual inteligente na Carteira Profissional (00123456/00123-UF) durante a digitação.

Modelos (/modelos): Tela para upload de arquivos .docx. Os contratos podem ser classificados como UNIVERSAL (visíveis para todos) ou ESPECIFICO (restritos a um cargo selecionado). Os arquivos binários são salvos de forma segura diretamente no banco de dados.

Gerar Contrato (/gerar): O motor de geração cruza os dados do funcionário com os modelos disponíveis. O usuário pode selecionar múltiplos documentos simultaneamente, e o sistema processa um download em lote (batch), inserindo uma pausa de 300ms entre as requisições para evitar bloqueios do navegador.

Regras de Negócio e Validações
O DocGen implementa proteções estritas para garantir a consistência dos dados:

Tags Obrigatórias em Documentos: Para que o sistema aceite o upload de um modelo Word, o documento deve conter as seguintes tags exatas: [NOME DO COLABORADOR], [NÚMERO DA CARTEIRA] e [DIA, MÊS E ANO]. Caso falte alguma, a API recusa o arquivo imediatamente e informa o usuário.

Unicidade de Identificação: A Carteira Profissional é validada por Expressão Regular (Regex) no backend (^\d{8}\/\d{5}-[A-Z]{2}$) e o banco de dados garante que duas pessoas não possam ter o mesmo número.

Data Dinâmica: Ao gerar um contrato, o usuário pode escolher uma "Data Personalizada". Se deixada em branco, o sistema assume automaticamente a "Data de Admissão" do colaborador. O mês é traduzido automaticamente para o formato por extenso em português (ex: "Janeiro").

Referência da API REST
A API foi documentada utilizando padrões semânticos e retorna status HTTP adequados (ex: 201 Created, 400 Bad Request, 404 Not Found).

Cargos:

POST /roles/ | GET /roles/ | PUT /roles/{role_id} | DELETE /roles/{role_id}

Funcionários:

POST /employees/ | GET /employees/ | PUT /employees/{employee_id} | DELETE /employees/{employee_id}

Contratos:

GET /contracts/ | DELETE /contracts/{contract_id}

POST /contracts/upload/ (Recebe multipart/form-data com o arquivo)

POST /contracts/generate/ (Substitui as tags e retorna o arquivo .docx preenchido como um fluxo contínuo)