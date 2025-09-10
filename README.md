Sistema de Controle de Estoque para Materiais de Construção Civil
Sistema web desenvolvido em Flask para gerenciamento de estoque de materiais de construção civil, com autenticação de usuários, controle de movimentações e relatórios.

📋 Funcionalidades
Gestão de Produtos: Cadastro, edição e exclusão de produtos
Controle de Estoque: Entradas, saídas e ajustes de quantidade
Sistema de Autenticação: Login com usuário e senha
Relatórios: Visualização de estoque atual e histórico de movimentações
Alertas: Notificações de produtos com estoque abaixo do mínimo
Categorização: Organização por categorias de materiais de construção
API REST: Endpoints para integração com outros sistemas

🚀 Tecnologias Utilizadas
Backend: Python 3.x, Flask, Flask-Login
Banco de Dados: SQLite (com opção para PostgreSQL)
Frontend: HTML5, CSS3, Bootstrap 5, JavaScript
Autenticação: Hash de senhas com Werkzeug

📦 Instalação e Configuração
Pré-requisitos
Python 3.8 ou superior
pip (gerenciador de pacotes Python)
Virtualenv (recomendado)
Importante: Altere a senha padrão após o primeiro login.

🗃️ Estrutura do Banco de Dados
Tabelas Principais
usuarios: Armazena dados de usuários do sistema
produtos: Cadastro de produtos/materiais de construção
movimentacoes: Histórico de entradas e saídas do estoque

📊 Funcionalidades Principais
Gestão de Produtos
Cadastro com código, descrição, categoria, quantidade, preço e fornecedor
Controle de estoque mínimo e dados de validade/lote
Edição e exclusão de produto
Movimentações de Estoque
Registro de entradas (compras, recebimentos)
Registro de saídas (vendas, consumo)
Histórico completo com data, usuário e observações
Relatórios e Consultas
Visualização do estoque atual com valores totais
Alertas de produtos com estoque abaixo do mínimo
Histórico de movimentações filtrado por data/produto
API REST
Endpoint: /api/produtos - Lista todos os produtos
Endpoint: /api/produtos/<id> - Detalhes de um produto específico

🔒 Segurança
Senhas armazenadas com hash bcrypt
Proteção contra CSRF
Autenticação requerida para todas as rotas
SQL injection prevention com parameterized queries

📞 Suporte
Para issues e dúvidas:
Verifique a documentação acima
Consulte os logs da aplicação
Abra uma issue no repositório do projeto

📄 Licença
Este projeto é para uso interno. Entre em contato com os desenvolvedores para informações sobre licenciamento.
Versão: 1.0.0
Última atualização: {{10/09/2025}}
Desenvolvido por: [Maria F Correia]

