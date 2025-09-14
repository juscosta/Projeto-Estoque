from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    """Modelo para usuários do sistema"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    tipo_usuario = db.Column(db.String(20), default='comum', nullable=False)  # admin ou comum
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamento com movimentações
    movimentacoes = db.relationship('MovimentacaoEstoque', backref='usuario_responsavel', lazy=True)
    
    def __init__(self, nome, email, senha, tipo_usuario='comum'):
        self.nome = nome
        self.email = email
        self.senha = generate_password_hash(senha)
        self.tipo_usuario = tipo_usuario
    
    def verificar_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha, senha)
    
    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.tipo_usuario == 'admin'
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'

class Produto(db.Model):
    """Modelo para produtos/materiais do estoque"""
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    quantidade = db.Column(db.Integer, default=0, nullable=False)
    estoque_minimo = db.Column(db.Integer, default=10, nullable=False)
    preco = db.Column(db.Float, default=0.0)
    categoria = db.Column(db.String(50))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamento com movimentações
    movimentacoes = db.relationship('MovimentacaoEstoque', backref='produto', lazy=True)
    
    def __init__(self, codigo, nome, descricao='', estoque_minimo=10, preco=0.0, categoria=''):
        self.codigo = codigo
        self.nome = nome
        self.descricao = descricao
        self.estoque_minimo = estoque_minimo
        self.preco = preco
        self.categoria = categoria
    
    def estoque_baixo(self):
        """Verifica se o produto está com estoque baixo"""
        return self.quantidade <= self.estoque_minimo
    
    def adicionar_estoque(self, quantidade):
        """Adiciona quantidade ao estoque"""
        self.quantidade += quantidade
    
    def remover_estoque(self, quantidade):
        """Remove quantidade do estoque se disponível"""
        if self.quantidade >= quantidade:
            self.quantidade -= quantidade
            return True
        return False
    
    def __repr__(self):
        return f'<Produto {self.codigo} - {self.nome}>'

class MovimentacaoEstoque(db.Model):
    """Modelo para controle de movimentações de estoque"""
    __tablename__ = 'movimentacoes_estoque'
    
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # entrada ou saida
    quantidade = db.Column(db.Integer, nullable=False)
    data_movimentacao = db.Column(db.DateTime, default=datetime.utcnow)
    observacao = db.Column(db.Text)
    
    def __init__(self, produto_id, usuario_id, tipo, quantidade, observacao=''):
        self.produto_id = produto_id
        self.usuario_id = usuario_id
        self.tipo = tipo
        self.quantidade = quantidade
        self.observacao = observacao
    
    def __repr__(self):
        return f'<Movimentacao {self.tipo} - {self.quantidade} unidades>'

class Categoria(db.Model):
    """Modelo para categorias de produtos"""
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, nome, descricao=''):
        self.nome = nome
        self.descricao = descricao
    
    def __repr__(self):
        return f'<Categoria {self.nome}>'