from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, FloatField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError
from models.database import Usuario, Produto

class LoginForm(FlaskForm):
    """Formulário de login"""
    email = StringField('Email', validators=[
        DataRequired(message='Email é obrigatório'),
        Email(message='Email inválido')
    ], render_kw={'placeholder': 'seu@email.com'})
    
    senha = PasswordField('Senha', validators=[
        DataRequired(message='Senha é obrigatória')
    ], render_kw={'placeholder': 'Sua senha'})
    
    lembrar = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar')

class RegisterForm(FlaskForm):
    """Formulário de registro de usuário"""
    nome = StringField('Nome Completo', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(min=2, max=100, message='Nome deve ter entre 2 e 100 caracteres')
    ], render_kw={'placeholder': 'Nome completo do usuário'})
    
    email = StringField('Email', validators=[
        DataRequired(message='Email é obrigatório'),
        Email(message='Email inválido'),
        Length(max=120, message='Email deve ter no máximo 120 caracteres')
    ], render_kw={'placeholder': 'email@exemplo.com'})
    
    senha = PasswordField('Senha', validators=[
        DataRequired(message='Senha é obrigatória'),
        Length(min=6, message='Senha deve ter pelo menos 6 caracteres')
    ], render_kw={'placeholder': 'Mínimo 6 caracteres'})
    
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(message='Confirmação de senha é obrigatória'),
        EqualTo('senha', message='Senhas devem ser iguais')
    ], render_kw={'placeholder': 'Digite a senha novamente'})
    
    tipo_usuario = SelectField('Tipo de Usuário', 
                              choices=[('comum', 'Usuário Comum'), ('admin', 'Administrador')],
                              default='comum')
    
    submit = SubmitField('Cadastrar Usuário')
    
    def validate_email(self, field):
        """Validação customizada para email único"""
        if Usuario.query.filter_by(email=field.data).first():
            raise ValidationError('Este email já está cadastrado no sistema.')

class ProdutoForm(FlaskForm):
    """Formulário para cadastro/edição de produtos"""
    codigo = StringField('Código do Produto', validators=[
        DataRequired(message='Código é obrigatório'),
        Length(min=1, max=50, message='Código deve ter entre 1 e 50 caracteres')
    ], render_kw={'placeholder': 'Ex: PROD001'})
    
    nome = StringField('Nome do Produto', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(min=2, max=100, message='Nome deve ter entre 2 e 100 caracteres')
    ], render_kw={'placeholder': 'Nome descritivo do produto'})
    
    descricao = TextAreaField('Descrição', 
                             render_kw={'placeholder': 'Descrição detalhada do produto', 'rows': 4})
    
    estoque_minimo = IntegerField('Estoque Mínimo', validators=[
        DataRequired(message='Estoque mínimo é obrigatório'),
        NumberRange(min=0, message='Estoque mínimo deve ser maior ou igual a zero')
    ], default=10, render_kw={'placeholder': '10'})
    
    preco = FloatField('Preço', validators=[
        NumberRange(min=0, message='Preço deve ser maior ou igual a zero')
    ], default=0.0, render_kw={'placeholder': '0.00', 'step': '0.01'})
    
    categoria = StringField('Categoria', validators=[
        Length(max=50, message='Categoria deve ter no máximo 50 caracteres')
    ], render_kw={'placeholder': 'Ex: Eletrônicos, Escritório, etc.'})
    
    submit = SubmitField('Salvar Produto')
    
    def __init__(self, *args, **kwargs):
        super(ProdutoForm, self).__init__(*args, **kwargs)
        self.original_codigo = None
        self.produto_id = None
    
    def validate_codigo(self, field):
        """Validação customizada para código único"""
        # Se estamos editando e o código não mudou, não validar
        if self.original_codigo and self.original_codigo == field.data:
            return
        
        # Verificar se existe outro produto com esse código
        produto = Produto.query.filter_by(codigo=field.data).first()
        if produto:
            # Se estamos editando e é o mesmo produto, permitir
            if self.produto_id and produto.id == self.produto_id:
                return
            raise ValidationError('Este código já está em uso por outro produto.')

class MovimentacaoForm(FlaskForm):
    """Formulário para movimentação de estoque"""
    produto_id = SelectField('Produto', validators=[
        DataRequired(message='Produto é obrigatório')
    ], coerce=int, choices=[])
    
    tipo = SelectField('Tipo de Movimentação', validators=[
        DataRequired(message='Tipo de movimentação é obrigatório')
    ], choices=[('entrada', 'Entrada'), ('saida', 'Saída')])
    
    quantidade = IntegerField('Quantidade', validators=[
        DataRequired(message='Quantidade é obrigatória'),
        NumberRange(min=1, message='Quantidade deve ser maior que zero')
    ], render_kw={'placeholder': '1', 'min': '1'})
    
    observacao = TextAreaField('Observação', 
                              render_kw={'placeholder': 'Observações sobre a movimentação (opcional)', 'rows': 3})
    
    submit = SubmitField('Registrar Movimentação')