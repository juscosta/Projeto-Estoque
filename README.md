# Sistema de Controle de Estoque

Um sistema completo de controle de estoque desenvolvido em Python/Flask, com interface web responsiva e funcionalidades avançadas de gerenciamento.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue.svg)

## Características Principais

- ✅ **Sistema de Autenticação** - Login/logout com controle de sessão
- ✅ **Controle de Acesso** - Usuários administrativos e comuns
- ✅ **Gestão de Produtos** - CRUD completo com validações
- ✅ **Movimentação de Estoque** - Entrada e saída com histórico
- ✅ **Alertas de Estoque** - N    otificações automáticas de estoque baixo
- ✅ **Dashboard Interativo** - Visão geral com estatísticas
- ✅ **Interface Responsiva** - Funciona em desktop e mobile
- ✅ **Validações** - Frontend e backend com feedback em tempo real

## Tecnologias Utilizadas

### Backend
- **Python 3.8+** - Linguagem de programação
- **Flask 2.3** - Framework web
- **Flask-SQLAlchemy** - ORM para banco de dados
- **Flask-Login** - Gerenciamento de sessões
- **Flask-WTF** - Formulários e validação
- **SQLite** - Banco de dados

### Frontend
- **HTML5/CSS3** - Estrutura e estilização
- **Bootstrap 5.3** - Framework CSS responsivo
- **JavaScript/jQuery** - Interatividade
- **Bootstrap Icons** - Ícones
- **DataTables** - Tabelas interativas

## Instalação e Execução

### 1️⃣ Pré-requisitos
```bash
# Verificar se Python 3.8+ está instalado
python --version
```

### 2️⃣ Instalação Rápida (Windows)
```bash
# 1. Navegar até o diretório
cd controle_estoque

# 2. Criar ambiente virtual
python -m venv venv

# 3. Ativar ambiente virtual
venv\Scripts\activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Executar o sistema
python app.py
```

### 3️⃣ Instalação Rápida (macOS/Linux)
```bash
# 1. Navegar até o diretório
cd controle_estoque

# 2. Criar ambiente virtual
python3 -m venv venv

# 3. Ativar ambiente virtual
source venv/bin/activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Executar o sistema
python app.py
```

### 4️⃣ Acessar o Sistema
- **URL:** http://localhost:5000
- **Admin:** admin@estoque.com / admin123
- **Usuário:** usuario@estoque.com / user123

## Estrutura do Projeto

```
controle_estoque/
│
├── 📄 app.py                 # Aplicação principal
├── 📄 config.py              # Configurações
├── 📄 forms.py               # Formulários WTF
├── 📄 requirements.txt       # Dependências
├── 📄 README.md              # Documentação
│
├── 📁 models/
│   └── 📄 database.py        # Modelos do banco
│
├── 📁 templates/             # Templates HTML
│   ├── 📄 base.html          # Template base
│   ├── 📄 dashboard.html     # Dashboard
│   └── 📁 auth/              # Autenticação
│
└── 📁 static/                # Arquivos estáticos
    ├── 📁 css/
    │   └── 📄 style.css      # Estilos customizados
    ├── 📁 js/
    │   └── 📄 main.js        # Scripts JavaScript
    └── 📁 images/            # Imagens
```

## Funcionalidades Detalhadas

### Sistema de Usuários
- **Tipos**: Administrador e Usuário Comum
- **Permissões**: Controle granular de acesso
- **Sessões**: Login/logout seguro
- **Cadastro**: Apenas admins podem criar usuários

### Gestão de Produtos
- **CRUD Completo**: Criar, ler, atualizar, deletar
- **Códigos Únicos**: Validação de código duplicado
- **Categorização**: Organização por categorias
- **Preços**: Controle de valores (opcional)
- **Validações**: Frontend e backend

### Controle de Estoque
- **Entradas**: Compras, devoluções, ajustes positivos
- **Saídas**: Vendas, uso interno, perdas
- **Histórico**: Registro completo de movimentações
- **Validações**: Verificação de estoque disponível
- **Rastreabilidade**: Quem fez, quando e por quê

### Sistema de Alertas
- **Estoque Baixo**: Produtos abaixo do mínimo
- **Produtos Zerados**: Lista de itens sem estoque
- **Notificações**: Badges e contadores visuais
- **Dashboard**: Resumo no painel principal

## Como Usar

### 1. Primeiro Acesso
1. Acesse `http://localhost:5000`
2. Faça login com um dos usuários padrão
3. Explore o dashboard inicial

### 2. Cadastrando Produtos (Apenas Admin)
1. Vá para **Produtos** → **Novo Produto**
2. Preencha os dados obrigatórios:
   - Código único
   - Nome do produto
   - Estoque mínimo
3. Salve o produto

### 3. Movimentando Estoque
1. Acesse **Movimentações** → **Nova Movimentação**
2. Selecione o produto
3. Escolha o tipo (Entrada/Saída)
4. Informe a quantidade
5. Adicione observações (opcional)
6. Registre a movimentação

### 4. Monitorando Alertas
- Produtos com estoque baixo aparecerão no dashboard
- Administradores podem ver alertas detalhados
- Use o botão de alertas na barra de navegação

## Personalização

### Cores e Tema
Edite o arquivo `static/css/style.css`:
```css
:root {
    --primary-color: #0d6efd;    /* Azul principal */
    --success-color: #198754;    /* Verde sucesso */
    --danger-color: #dc3545;     /* Vermelho perigo */
    --warning-color: #ffc107;    /* Amarelo aviso */
}
```

### Logotipo
Substitua o ícone na navbar editando `templates/base.html`:
```html
<a class="navbar-brand" href="{{ url_for('main.dashboard') }}">
    <img src="{{ url_for('static', filename='images/logo.png') }}" height="30">
    Sua Empresa
</a>
```

## Segurança

### Medidas Implementadas
- ✅ Validação CSRF nos formulários
- ✅ Controle de sessões seguro
- ✅ Validação de entrada de dados
- ✅ Controle de acesso por perfil

### Recomendações para Produção
- [ ] Implementar HTTPS
- [ ] Usar banco de dados robusto (PostgreSQL)
- [ ] Configurar logs de auditoria
- [ ] Implementar rate limiting
- [ ] Backup automático dos dados

## Solução de Problemas

### ❌ Erro: "Python não encontrado"
```bash
# Windows
winget install Python.Python.3.11

# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt update && sudo apt install python3.11 python3.11-venv
```

### ❌ Erro: "Porta 5000 em uso"
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
sudo lsof -ti:5000 | xargs kill -9
```

### ❌ Erro: "Dependências não instaladas"
```bash
# Atualizar pip e tentar novamente
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Requisitos Atendidos

✅ **Linguagem Python** - Desenvolvimento completo em Python/Flask  
✅ **Interface de Usuário** - Web interface responsiva com Bootstrap  
✅ **Validações** - Campos obrigatórios e tipos de dados  
✅ **Usabilidade** - Sistema fácil de navegar e usar  
✅ **Biblioteca de Interface** - Flask para backend, Bootstrap para frontend  
✅ **Validação de Usuário** - Login e senha com controle de sessão  
✅ **Conexão com BD** - SQLite com SQLAlchemy  
✅ **Sessão de Usuário** - Gerenciamento completo de sessões  
✅ **Perfis de Usuário** - Admin e Comum com permissões diferentes  
✅ **Cadastro Restrito** - Apenas admin cadastra usuários  
✅ **Sistema de Alertas** - Produtos com estoque baixo em destaque  

## Dados de Demonstração

O sistema vem com dados pré-carregados:
- 2 usuários (admin e comum)
- 9 produtos de exemplo
- Categorias pré-definidas
- Movimentações de exemplo

## Licença

Este projeto foi desenvolvido para fins educacionais.

---

<div align="center">
  
  **Sistema de Controle de Estoque**
  
  
  **Versão 1.0.0**
  
</div>
