from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect, generate_csrf
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from config import config
from models.database import db, Usuario, Produto, MovimentacaoEstoque, Categoria
from forms import LoginForm, RegisterForm, ProdutoForm, MovimentacaoForm
import os
from datetime import datetime
from functools import wraps

def create_app(config_name='default'):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializa extensões
    db.init_app(app)
    
    # Configuração do CSRF Protection
    csrf = CSRFProtect(app)
    
    # Configuração do Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Decorator para verificar se usuário é admin
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_admin():
                flash('Acesso negado. Apenas administradores podem acessar esta funcionalidade.', 'error')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    
    # Função helper para arquivos permitidos
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    
    # ==================== ROTAS PRINCIPAIS ====================
    
    @app.route('/')
    def index():
        """Página inicial - redireciona para dashboard se logado"""
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Dashboard principal do sistema"""
        # Estatísticas gerais
        total_produtos = Produto.query.filter_by(ativo=True).count()
        produtos_estoque_baixo = Produto.query.filter(
            Produto.quantidade <= Produto.estoque_minimo,
            Produto.ativo == True
        ).count()
        
        # Movimentações recentes
        movimentacoes_recentes = MovimentacaoEstoque.query\
            .join(Produto)\
            .order_by(MovimentacaoEstoque.data_movimentacao.desc())\
            .limit(5).all()
        
        # Produtos com estoque baixo
        produtos_alerta = Produto.query.filter(
            Produto.quantidade <= Produto.estoque_minimo,
            Produto.ativo == True
        ).limit(5).all()
        
        return render_template('dashboard.html',
                             total_produtos=total_produtos,
                             produtos_estoque_baixo=produtos_estoque_baixo,
                             movimentacoes_recentes=movimentacoes_recentes,
                             produtos_alerta=produtos_alerta)
    
    # ==================== ROTAS DE AUTENTICAÇÃO ====================
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Página de login"""
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = Usuario.query.filter_by(email=form.email.data, ativo=True).first()
            
            if user and user.verificar_senha(form.senha.data):
                login_user(user, remember=form.lembrar.data)
                flash(f'Bem-vindo, {user.nome}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
            else:
                flash('Email ou senha inválidos.', 'error')
        
        return render_template('auth/login.html', form=form)
    
    @app.route('/register', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def register():
        """Cadastro de novos usuários (apenas para admin)"""
        form = RegisterForm()
        if form.validate_on_submit():
            # Verifica se email já existe
            if Usuario.query.filter_by(email=form.email.data).first():
                flash('Este email já está cadastrado no sistema.', 'error')
                return render_template('auth/register.html', form=form)
            
            # Cria novo usuário
            usuario = Usuario(
                nome=form.nome.data,
                email=form.email.data,
                senha=form.senha.data,
                tipo_usuario=form.tipo_usuario.data
            )
            
            try:
                db.session.add(usuario)
                db.session.commit()
                flash(f'Usuário {usuario.nome} cadastrado com sucesso!', 'success')
                return redirect(url_for('main.usuarios'))
            except Exception as e:
                db.session.rollback()
                flash('Erro ao cadastrar usuário. Tente novamente.', 'error')
        
        return render_template('auth/register.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        """Logout do usuário"""
        logout_user()
        flash('Você foi desconectado do sistema.', 'info')
        return redirect(url_for('auth.login'))
    
    # ==================== ROTAS DE PRODUTOS ====================
    
    @app.route('/produtos')
    @login_required
    def produtos():
        """Listagem de produtos"""
        page = request.args.get('page', 1, type=int)
        busca = request.args.get('busca', '', type=str)
        categoria = request.args.get('categoria', '', type=str)
        
        query = Produto.query.filter_by(ativo=True)
        
        # Filtros de busca
        if busca:
            query = query.filter(
                (Produto.nome.contains(busca)) |
                (Produto.codigo.contains(busca)) |
                (Produto.descricao.contains(busca))
            )
        
        if categoria:
            query = query.filter_by(categoria=categoria)
        
        produtos = query.order_by(Produto.nome).paginate(
            page=page, per_page=10, error_out=False
        )
        
        # Buscar categorias para o filtro
        categorias = db.session.query(Produto.categoria)\
            .filter(Produto.categoria.isnot(None))\
            .filter(Produto.categoria != '')\
            .distinct().all()
        
        return render_template('produtos/lista.html',
                             produtos=produtos,
                             categorias=[c[0] for c in categorias],
                             busca=busca,
                             categoria_selecionada=categoria)
    
    @app.route('/produto/novo', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def produto_novo():
        """Cadastro de novo produto"""
        form = ProdutoForm()
        if form.validate_on_submit():
            # Verifica se código já existe
            if Produto.query.filter_by(codigo=form.codigo.data).first():
                flash('Este código de produto já existe.', 'error')
                return render_template('produtos/form.html', form=form, titulo='Novo Produto')
            
            produto = Produto(
                codigo=form.codigo.data,
                nome=form.nome.data,
                descricao=form.descricao.data,
                estoque_minimo=form.estoque_minimo.data,
                preco=form.preco.data,
                categoria=form.categoria.data
            )
            
            try:
                db.session.add(produto)
                db.session.commit()
                flash(f'Produto {produto.nome} cadastrado com sucesso!', 'success')
                return redirect(url_for('main.produtos'))
            except Exception as e:
                db.session.rollback()
                flash('Erro ao cadastrar produto. Tente novamente.', 'error')
        
        return render_template('produtos/form.html', form=form, titulo='Novo Produto')
    
    @app.route('/produto/<int:id>/editar', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def produto_editar(id):
        """Edição de produto existente"""
        produto = Produto.query.get_or_404(id)
        form = ProdutoForm(obj=produto)
        
        # Define o código original e o ID para validação
        form.original_codigo = produto.codigo
        form.produto_id = produto.id
        
        if form.validate_on_submit():
            # Verifica se código já existe em outro produto
            produto_existente = Produto.query.filter_by(codigo=form.codigo.data).first()
            if produto_existente and produto_existente.id != id:
                flash('Este código de produto já existe.', 'error')
                return render_template('produtos/form.html', form=form, titulo='Editar Produto')
            
            form.populate_obj(produto)
            
            try:
                db.session.commit()
                flash(f'Produto {produto.nome} atualizado com sucesso!', 'success')
                return redirect(url_for('main.produtos'))
            except Exception as e:
                db.session.rollback()
                flash('Erro ao atualizar produto. Tente novamente.', 'error')
        
        return render_template('produtos/form.html', form=form, titulo='Editar Produto')
    
    @app.route('/produto/<int:id>/excluir', methods=['POST'])
    @login_required
    @admin_required
    def produto_excluir(id):
        """Exclusão lógica de produto"""
        produto = Produto.query.get_or_404(id)
        produto.ativo = False
        
        try:
            db.session.commit()
            flash(f'Produto {produto.nome} excluído com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao excluir produto. Tente novamente.', 'error')
        
        return redirect(url_for('main.produtos'))
    
    # ==================== ROTAS DE MOVIMENTAÇÃO ====================
    
    @app.route('/movimentacoes')
    @login_required
    def movimentacoes():
        """Listagem de movimentações"""
        page = request.args.get('page', 1, type=int)
        tipo = request.args.get('tipo', '', type=str)
        produto_id = request.args.get('produto', '', type=int)
        
        query = MovimentacaoEstoque.query.join(Produto)
        
        if tipo:
            query = query.filter(MovimentacaoEstoque.tipo == tipo)
        
        if produto_id:
            query = query.filter(MovimentacaoEstoque.produto_id == produto_id)
        
        movimentacoes = query.order_by(MovimentacaoEstoque.data_movimentacao.desc())\
            .paginate(page=page, per_page=15, error_out=False)
        
        # Produtos para filtro
        produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
        
        return render_template('movimentacoes/lista.html',
                             movimentacoes=movimentacoes,
                             produtos=produtos,
                             tipo_selecionado=tipo,
                             produto_selecionado=produto_id)
    
    @app.route('/movimentacao/nova', methods=['GET', 'POST'])
    @login_required
    def movimentacao_nova():
        """Nova movimentação de estoque"""
        form = MovimentacaoForm()
        
        # Popular produtos ativos
        form.produto_id.choices = [(p.id, f'{p.codigo} - {p.nome}') 
                                   for p in Produto.query.filter_by(ativo=True).order_by(Produto.nome)]
        
        if form.validate_on_submit():
            produto = Produto.query.get(form.produto_id.data)
            
            # Validação para saída
            if form.tipo.data == 'saida' and produto.quantidade < form.quantidade.data:
                flash(f'Quantidade insuficiente em estoque. Disponível: {produto.quantidade}', 'error')
                return render_template('movimentacoes/form.html', form=form, titulo='Nova Movimentação')
            
            # Cria movimentação
            movimentacao = MovimentacaoEstoque(
                produto_id=form.produto_id.data,
                usuario_id=current_user.id,
                tipo=form.tipo.data,
                quantidade=form.quantidade.data,
                observacao=form.observacao.data
            )
            
            # Atualiza estoque do produto
            if form.tipo.data == 'entrada':
                produto.adicionar_estoque(form.quantidade.data)
            else:
                produto.remover_estoque(form.quantidade.data)
            
            try:
                db.session.add(movimentacao)
                db.session.commit()
                flash(f'Movimentação de {form.tipo.data} registrada com sucesso!', 'success')
                return redirect(url_for('main.movimentacoes'))
            except Exception as e:
                db.session.rollback()
                flash('Erro ao registrar movimentação. Tente novamente.', 'error')
        
        return render_template('movimentacoes/form.html', form=form, titulo='Nova Movimentação')
    
    # ==================== ROTAS DE RELATÓRIOS E ALERTAS ====================
    
    @app.route('/alertas')
    @login_required
    @admin_required
    def alertas():
        """Página de alertas de estoque baixo"""
        produtos_estoque_baixo = Produto.query.filter(
            Produto.quantidade <= Produto.estoque_minimo,
            Produto.ativo == True
        ).order_by(Produto.nome).all()
        
        return render_template('alertas.html', produtos=produtos_estoque_baixo)
    
    @app.route('/api/alertas')
    @login_required
    def api_alertas():
        """API para alertas de estoque baixo"""
        produtos_estoque_baixo = Produto.query.filter(
            Produto.quantidade <= Produto.estoque_minimo,
            Produto.ativo == True
        ).all()
        
        alertas = []
        for produto in produtos_estoque_baixo:
            alertas.append({
                'id': produto.id,
                'codigo': produto.codigo,
                'nome': produto.nome,
                'quantidade': produto.quantidade,
                'estoque_minimo': produto.estoque_minimo
            })
        
        return jsonify({
            'total': len(alertas),
            'produtos': alertas
        })
    
    @app.route('/api/produto/<int:id>')
    @login_required
    def api_produto(id):
        """API para obter informações de um produto"""
        produto = Produto.query.get_or_404(id)
        return jsonify({
            'id': produto.id,
            'codigo': produto.codigo,
            'nome': produto.nome,
            'descricao': produto.descricao,
            'quantidade': produto.quantidade,
            'estoque_minimo': produto.estoque_minimo,
            'preco': produto.preco,
            'status': produto.status,
            'ativo': produto.ativo
        })
    
    @app.route('/usuarios')
    @login_required
    @admin_required
    def usuarios():
        """Listagem de usuários (apenas admin)"""
        usuarios = Usuario.query.filter_by(ativo=True).order_by(Usuario.nome).all()
        return render_template('usuarios.html', usuarios=usuarios)
    
    # ==================== FILTROS DE TEMPLATE ====================
    
    @app.template_filter('datetime')
    def datetime_filter(value, format='%d/%m/%Y %H:%M'):
        """Filtro para formatação de data/hora"""
        if value is None:
            return ''
        return value.strftime(format)
    
    @app.template_filter('currency')
    def currency_filter(value):
        """Filtro para formatação de moeda"""
        if value is None:
            return 'R$ 0,00'
        return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    # ==================== CONTEXT PROCESSORS ====================
    
    @app.context_processor
    def inject_alertas():
        """Injeta alertas globais nos templates"""
        if current_user.is_authenticated and current_user.is_admin():
            count_alertas = Produto.query.filter(
                Produto.quantidade <= Produto.estoque_minimo,
                Produto.ativo == True
            ).count()
            return dict(alertas_count=count_alertas)
        return dict(alertas_count=0)
    
    @app.context_processor
    def inject_csrf_token():
        """Injeta csrf_token em todos os templates"""
        return dict(csrf_token=generate_csrf)
    
    # ==================== MANIPULADORES DE ERRO ====================
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    @app.route('/favicon.ico')
    def favicon():
        return '', 204  # No Content
    
    # Registrar todas as rotas no namespace principal
    app.add_url_rule('/', 'main.index', index)
    app.add_url_rule('/dashboard', 'main.dashboard', dashboard, methods=['GET'])
    app.add_url_rule('/login', 'auth.login', login, methods=['GET', 'POST'])
    app.add_url_rule('/register', 'auth.register', register, methods=['GET', 'POST'])
    app.add_url_rule('/logout', 'auth.logout', logout)
    app.add_url_rule('/produtos', 'main.produtos', produtos)
    app.add_url_rule('/produto/novo', 'main.produto_novo', produto_novo, methods=['GET', 'POST'])
    app.add_url_rule('/produto/<int:id>/editar', 'main.produto_editar', produto_editar, methods=['GET', 'POST'])
    app.add_url_rule('/produto/<int:id>/excluir', 'main.produto_excluir', produto_excluir, methods=['POST'])
    app.add_url_rule('/movimentacoes', 'main.movimentacoes', movimentacoes)
    app.add_url_rule('/movimentacao/nova', 'main.movimentacao_nova', movimentacao_nova, methods=['GET', 'POST'])
    app.add_url_rule('/alertas', 'main.alertas', alertas)
    app.add_url_rule('/api/alertas', 'api.alertas', api_alertas)
    app.add_url_rule('/api/produto/<int:id>', 'api.produto', api_produto)
    app.add_url_rule('/usuarios', 'main.usuarios', usuarios)
    
    return app

def init_db():
    """Inicializa o banco de dados com dados de exemplo"""
    db.create_all()
    
    # Criar usuário admin padrão se não existir
    admin = Usuario.query.filter_by(email='admin@estoque.com').first()
    if not admin:
        admin = Usuario(
            nome='Administrador',
            email='admin@estoque.com',
            senha='admin123',
            tipo_usuario='admin'
        )
        db.session.add(admin)
    
    # Criar usuário comum de exemplo
    user_comum = Usuario.query.filter_by(email='usuario@estoque.com').first()
    if not user_comum:
        user_comum = Usuario(
            nome='Usuário Comum',
            email='usuario@estoque.com',
            senha='user123',
            tipo_usuario='comum'
        )
        db.session.add(user_comum)
    
    # Criar categorias de exemplo
    categorias = ['Eletrônicos', 'Escritório', 'Limpeza', 'Informática', 'Móveis']
    for cat_nome in categorias:
        categoria_existente = Categoria.query.filter_by(nome=cat_nome).first()
        if not categoria_existente:
            categoria = Categoria(nome=cat_nome)
            db.session.add(categoria)
    
    # Criar produtos de exemplo
    produtos_exemplo = [
        ('PROD001', 'Notebook Dell', 'Notebook Dell Inspiron 15', 5, 2500.00, 'Informática'),
        ('PROD002', 'Mouse Logitech', 'Mouse óptico Logitech MX Master', 50, 120.00, 'Informática'),
        ('PROD003', 'Papel A4', 'Papel A4 75g pacote 500 folhas', 100, 25.00, 'Escritório'),
        ('PROD004', 'Detergente', 'Detergente líquido 500ml', 30, 3.50, 'Limpeza'),
        ('PROD005', 'Cadeira Executiva', 'Cadeira executiva com rodízios', 8, 450.00, 'Móveis'),
        ('PROD006', 'Smartphone Samsung', 'Samsung Galaxy A54', 15, 1200.00, 'Eletrônicos'),
        ('PROD007', 'Impressora HP', 'Impressora HP LaserJet Pro', 3, 800.00, 'Informática'),
        ('PROD008', 'Caneta BIC', 'Caneta esferográfica BIC azul', 200, 1.50, 'Escritório'),
    ]
    
    for codigo, nome, desc, estoque_min, preco, cat in produtos_exemplo:
        produto_existente = Produto.query.filter_by(codigo=codigo).first()
        if not produto_existente:
            produto = Produto(
                codigo=codigo,
                nome=nome,
                descricao=desc,
                estoque_minimo=estoque_min,
                preco=preco,
                categoria=cat
            )
            # Adicionar estoque inicial
            produto.quantidade = estoque_min * 2
            db.session.add(produto)
    
    try:
        db.session.commit()
        print("Banco de dados inicializado com dados de exemplo.")
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao inicializar banco: {e}")

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        init_db()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
