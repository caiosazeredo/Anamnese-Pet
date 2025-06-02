# app.py - Sistema PetAnamnese Completo em Um Arquivo
"""
Sistema PetAnamnese - SENAC RJ
Todas as funcionalidades em um único arquivo para facilitar implementação
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import os
from functools import wraps
import json
from sqlalchemy import or_, func, distinct
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da aplicação
app = Flask(__name__)

# Configurações usando variáveis de ambiente
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///petanamnese.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {
        'ssl_disabled': False,
        'ssl_check_hostname': False,
        'ssl_verify_cert': False
    }
}

# Inicialização da extensão
db = SQLAlchemy(app)

# =====================================================
# MODELOS DO BANCO DE DADOS
# =====================================================

class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    codigo_sga = db.Column(db.String(20), unique=True)
    carga_horaria = db.Column(db.Integer, nullable=False)
    tipo_curso = db.Column(db.Enum('Aperfeiçoamento', 'Socioprofissional'), nullable=False)
    eixo_tecnologico = db.Column(db.String(100))
    segmento = db.Column(db.String(100))
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Instrutor(db.Model):
    __tablename__ = 'instrutores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    especialidade = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Turma(db.Model):
    __tablename__ = 'turmas'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    instrutor_id = db.Column(db.Integer, db.ForeignKey('instrutores.id'), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    horario_inicio = db.Column(db.Time)
    horario_fim = db.Column(db.Time)
    local = db.Column(db.String(255))
    max_alunos = db.Column(db.Integer, default=30)
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    curso = db.relationship('Curso', backref='turmas')
    instrutor = db.relationship('Instrutor', backref='turmas')

class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    rg = db.Column(db.String(20))
    data_nascimento = db.Column(db.Date)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    endereco = db.Column(db.Text)
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    cep = db.Column(db.String(10))
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AlunoTurma(db.Model):
    __tablename__ = 'aluno_turma'
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)
    data_matricula = db.Column(db.Date, default=date.today)
    situacao = db.Column(db.Enum('Matriculado', 'Aprovado', 'Reprovado', 'Desistente'), default='Matriculado')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    aluno = db.relationship('Aluno', backref='matriculas')
    turma = db.relationship('Turma', backref='matriculas')

class Tutor(db.Model):
    __tablename__ = 'tutores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    rg = db.Column(db.String(20))
    endereco = db.Column(db.Text, nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    uf = db.Column(db.String(2))
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255))
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Pet(db.Model):
    __tablename__ = 'pets'
    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutores.id'), nullable=False)
    nome = db.Column(db.String(255), nullable=False)
    idade = db.Column(db.Integer)
    raca = db.Column(db.String(100))
    cor = db.Column(db.String(100))
    especie = db.Column(db.Enum('Canino', 'Felino', 'Outros'), nullable=False)
    porte = db.Column(db.Enum('Pequeno', 'Médio', 'Grande', 'Gigante'))
    pelagem = db.Column(db.Enum('Curta', 'Longa', 'Crespa', 'Lisa', 'Ondulada', 'Dupla'), default='Curta')
    temperamento = db.Column(db.Enum('Manso', 'Agressivo', 'Agitado', 'Tímido'), default='Manso')
    peso = db.Column(db.Numeric(5, 2))
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tutor = db.relationship('Tutor', backref='pets')

class Anamnese(db.Model):
    __tablename__ = 'anamneses'
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutores.id'), nullable=False)
    
    # Dados médicos
    alergia = db.Column(db.Boolean, default=False)
    pode_perfume = db.Column(db.Boolean, default=True)
    pode_limpar_ouvido = db.Column(db.Boolean, default=True)
    pode_cortar_unha = db.Column(db.Boolean, default=True)
    problema_cardiorespiatorio = db.Column(db.Boolean, default=False)
    pulga_carrapato = db.Column(db.Boolean, default=False)
    sofre_convulsao = db.Column(db.Boolean, default=False)
    problema_articular = db.Column(db.Boolean, default=False)
    cirurgia_recente = db.Column(db.Boolean, default=False)
    vacinado_multipla_antirrabica = db.Column(db.Boolean, default=False)
    
    # Observações
    observacoes_alergia = db.Column(db.Text)
    observacoes_cirurgia = db.Column(db.Text)
    observacoes_gerais = db.Column(db.Text)
    
    # Controle
    termo_assinado = db.Column(db.Boolean, default=False)
    assinatura_tutor = db.Column(db.Text)  # Base64
    data_assinatura = db.Column(db.DateTime)
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    pet = db.relationship('Pet', backref='anamneses')
    tutor = db.relationship('Tutor', backref='anamneses')

class Procedimento(db.Model):
    __tablename__ = 'procedimentos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text)
    curso_relacionado = db.Column(db.Integer, db.ForeignKey('cursos.id'))
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    curso = db.relationship('Curso', backref='procedimentos')

class Aula(db.Model):
    __tablename__ = 'aulas'
    id = db.Column(db.Integer, primary_key=True)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)
    data_aula = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time)
    hora_fim = db.Column(db.Time)
    tema = db.Column(db.String(255))
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    turma = db.relationship('Turma', backref='aulas')

class Atendimento(db.Model):
    __tablename__ = 'atendimentos'
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutores.id'), nullable=False)
    anamnese_id = db.Column(db.Integer, db.ForeignKey('anamneses.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)
    aula_id = db.Column(db.Integer, db.ForeignKey('aulas.id'))
    
    # Check-in
    data_checkin = db.Column(db.DateTime, default=datetime.utcnow)
    hora_checkin = db.Column(db.Time)
    status_atendimento = db.Column(db.Enum('Aguardando', 'Em Atendimento', 'Finalizado', 'Cancelado'), default='Aguardando')
    
    # Check-out
    data_checkout = db.Column(db.DateTime)
    hora_checkout = db.Column(db.Time)
    intercorrencia = db.Column(db.Boolean, default=False)
    observacoes_intercorrencia = db.Column(db.Text)
    observacoes_dia = db.Column(db.Text)
    
    # Assinaturas
    assinatura_tutor = db.Column(db.Text)  # Base64
    assinatura_aluno1 = db.Column(db.Text)  # Base64
    assinatura_aluno2 = db.Column(db.Text)  # Base64
    assinatura_aluno3 = db.Column(db.Text)  # Base64
    nome_aluno1 = db.Column(db.String(255))
    nome_aluno2 = db.Column(db.String(255))
    nome_aluno3 = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    pet = db.relationship('Pet', backref='atendimentos')
    tutor = db.relationship('Tutor', backref='atendimentos')
    anamnese = db.relationship('Anamnese', backref='atendimentos')
    turma = db.relationship('Turma', backref='atendimentos')
    aula = db.relationship('Aula', backref='atendimentos')

class AtendimentoProcedimento(db.Model):
    __tablename__ = 'atendimento_procedimento'
    id = db.Column(db.Integer, primary_key=True)
    atendimento_id = db.Column(db.Integer, db.ForeignKey('atendimentos.id'), nullable=False)
    procedimento_id = db.Column(db.Integer, db.ForeignKey('procedimentos.id'), nullable=False)
    realizado = db.Column(db.Boolean, default=False)
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    atendimento = db.relationship('Atendimento', backref='procedimentos_atendimento')
    procedimento = db.relationship('Procedimento', backref='atendimentos_procedimento')

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    tipo_usuario = db.Column(db.Enum('Administrador', 'Secretaria', 'Instrutor'), nullable=False)
    instrutor_id = db.Column(db.Integer, db.ForeignKey('instrutores.id'))
    ativo = db.Column(db.Boolean, default=True)
    ultimo_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    instrutor = db.relationship('Instrutor', backref='usuario')

# =====================================================
# DECORADOR PARA LOGIN
# =====================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# =====================================================
# ROTAS PRINCIPAIS
# =====================================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        user = Usuario.query.filter_by(email=email, ativo=True).first()
        
        if user and check_password_hash(user.senha, senha):
            session['user_id'] = user.id
            session['user_nome'] = user.nome
            session['user_tipo'] = user.tipo_usuario
            
            user.ultimo_login = datetime.utcnow()
            db.session.commit()
            
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha inválidos')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Estatísticas básicas
    total_pets = Pet.query.filter_by(ativo=True).count()
    total_tutores = Tutor.query.filter_by(ativo=True).count()
    atendimentos_hoje = Atendimento.query.filter(
        Atendimento.data_checkin >= datetime.now().date()
    ).count()
    turmas_ativas = Turma.query.filter_by(ativa=True).count()
    
    stats = {
        'total_pets': total_pets,
        'total_tutores': total_tutores,
        'atendimentos_hoje': atendimentos_hoje,
        'turmas_ativas': turmas_ativas
    }
    
    return render_template('dashboard.html', stats=stats)

# =====================================================
# ROTAS DE TUTORES
# =====================================================

@app.route('/tutores')
@login_required
def list_tutores():
    search = request.args.get('search', '')
    raca = request.args.get('raca', '')
    porte = request.args.get('porte', '')
    
    query = db.session.query(Tutor).filter(Tutor.ativo == True)
    
    if search:
        query = query.filter(
            or_(
                Tutor.nome.contains(search),
                Tutor.cpf.contains(search)
            )
        )
    
    if raca or porte:
        query = query.join(Pet)
        if raca:
            query = query.filter(Pet.raca.contains(raca))
        if porte:
            query = query.filter(Pet.porte == porte)
    
    tutores = query.distinct().all()
    
    # Buscar raças e portes únicos para os filtros
    racas = db.session.query(Pet.raca).filter(Pet.raca.isnot(None)).distinct().all()
    portes = db.session.query(Pet.porte).filter(Pet.porte.isnot(None)).distinct().all()
    
    return render_template('tutores/gerenciar.html', 
                         tutores=tutores, 
                         racas=[r[0] for r in racas],
                         portes=[p[0] for p in portes],
                         search=search,
                         raca_filter=raca,
                         porte_filter=porte)

@app.route('/tutores/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar_tutor():
    if request.method == 'POST':
        data = request.get_json()
        
        # Verificar se CPF já existe
        if Tutor.query.filter_by(cpf=data['cpf']).first():
            return jsonify({'success': False, 'message': 'CPF já cadastrado'})
        
        try:
            tutor = Tutor(
                nome=data['nome'],
                cpf=data['cpf'],
                endereco=data['endereco'],
                bairro=data['bairro'],
                cidade=data['cidade'],
                telefone=data['telefone'],
                rg=data.get('rg'),
                email=data.get('email'),
                uf=data.get('uf', 'RJ')
            )
            
            db.session.add(tutor)
            db.session.commit()
            
            return jsonify({'success': True, 'tutor_id': tutor.id})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    return render_template('tutores/form.html')

@app.route('/tutores/buscar')
@login_required
def buscar_tutores():
    termo = request.args.get('q', '')
    
    if len(termo) < 3:
        return jsonify([])
    
    tutores = Tutor.query.filter(
        Tutor.ativo == True,
        or_(
            Tutor.nome.contains(termo),
            Tutor.cpf.contains(termo)
        )
    ).limit(10).all()
    
    result = []
    for tutor in tutores:
        result.append({
            'id': tutor.id,
            'nome': tutor.nome,
            'cpf': tutor.cpf,
            'telefone': tutor.telefone,
            'cidade': tutor.cidade,
            'pets_count': len(tutor.pets)
        })
    
    return jsonify(result)

# =====================================================
# ROTAS DE PETS
# =====================================================

@app.route('/pets/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar_pet():
    if request.method == 'POST':
        data = request.get_json()
        
        try:
            pet = Pet(
                tutor_id=data['tutor_id'],
                nome=data['nome'],
                idade=data.get('idade'),
                raca=data.get('raca'),
                cor=data.get('cor'),
                especie=data['especie'],
                porte=data.get('porte'),
                pelagem=data.get('pelagem', 'Curta'),
                temperamento=data.get('temperamento', 'Manso'),
                peso=data.get('peso'),
                observacoes=data.get('observacoes')
            )
            
            db.session.add(pet)
            db.session.commit()
            
            return jsonify({'success': True, 'pet_id': pet.id})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    tutores = Tutor.query.filter_by(ativo=True).all()
    return render_template('pets/form.html', tutores=tutores)

@app.route('/pets/gerenciar')
@login_required
def gerenciar_pets():
    search = request.args.get('search', '')
    especie = request.args.get('especie', '')
    porte = request.args.get('porte', '')
    raca = request.args.get('raca', '')
    
    query = Pet.query.filter(Pet.ativo == True)
    
    if search:
        query = query.join(Tutor).filter(
            or_(
                Pet.nome.contains(search),
                Tutor.nome.contains(search)
            )
        )
    
    if especie:
        query = query.filter(Pet.especie == especie)
    
    if porte:
        query = query.filter(Pet.porte == porte)
    
    if raca:
        query = query.filter(Pet.raca.contains(raca))
    
    pets = query.all()
    
    return render_template('pets/gerenciar.html', pets=pets)

# =====================================================
# ROTAS DE ANAMNESE
# =====================================================

@app.route('/anamnese/nova/<int:pet_id>')
@login_required
def nova_anamnese(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    tutor_id = request.args.get('tutor_id')
    
    if tutor_id:
        tutor = Tutor.query.get_or_404(tutor_id)
    else:
        tutor = pet.tutor
    
    return render_template('anamnese/form.html', pet=pet, tutor=tutor)

@app.route('/anamnese/salvar', methods=['POST'])
@login_required
def salvar_anamnese():
    data = request.get_json()
    
    try:
        # Desativar anamneses anteriores do pet
        anamneses_antigas = Anamnese.query.filter_by(pet_id=data['pet_id'], ativa=True).all()
        for anamnese_antiga in anamneses_antigas:
            anamnese_antiga.ativa = False
        
        # Criar nova anamnese
        anamnese = Anamnese(
            pet_id=data['pet_id'],
            tutor_id=data['tutor_id'],
            alergia=data.get('alergia', False),
            pode_perfume=data.get('pode_perfume', True),
            pode_limpar_ouvido=data.get('pode_limpar_ouvido', True),
            pode_cortar_unha=data.get('pode_cortar_unha', True),
            problema_cardiorespiatorio=data.get('problema_cardiorespiatorio', False),
            pulga_carrapato=data.get('pulga_carrapato', False),
            sofre_convulsao=data.get('sofre_convulsao', False),
            problema_articular=data.get('problema_articular', False),
            cirurgia_recente=data.get('cirurgia_recente', False),
            vacinado_multipla_antirrabica=data.get('vacinado_multipla_antirrabica', False),
            observacoes_alergia=data.get('observacoes_alergia'),
            observacoes_cirurgia=data.get('observacoes_cirurgia'),
            observacoes_gerais=data.get('observacoes_gerais'),
            termo_assinado=data.get('termo_assinado', False),
            assinatura_tutor=data.get('assinatura_tutor'),
            data_assinatura=datetime.utcnow() if data.get('assinatura_tutor') else None
        )
        
        db.session.add(anamnese)
        db.session.commit()
        
        return jsonify({'success': True, 'anamnese_id': anamnese.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/termo-ciencia')
@login_required
def termo_ciencia():
    return render_template('termo/ciencia.html')

@app.route('/assinatura-tutor')
@login_required
def assinatura_tutor():
    return render_template('assinatura/tutor.html')

# =====================================================
# ROTAS DE ATENDIMENTOS
# =====================================================

@app.route('/checkin', methods=['GET', 'POST'])
@login_required
def novo_checkin():
    if request.method == 'POST':
        data = request.get_json()
        
        # Verificar se existe anamnese ativa para o pet
        anamnese = Anamnese.query.filter_by(
            pet_id=data['pet_id'], 
            ativa=True
        ).first()
        
        if not anamnese:
            return jsonify({'success': False, 'message': 'Pet sem anamnese ativa'})
        
        try:
            # Criar ou buscar aula do dia
            aula = Aula.query.filter_by(
                turma_id=data['turma_id'],
                data_aula=datetime.strptime(data['aula_data'], '%Y-%m-%d').date()
            ).first()
            
            if not aula:
                aula = Aula(
                    turma_id=data['turma_id'],
                    data_aula=datetime.strptime(data['aula_data'], '%Y-%m-%d').date(),
                    hora_inicio=datetime.strptime(data['hora_checkin'], '%H:%M').time()
                )
                db.session.add(aula)
                db.session.flush()
            
            atendimento = Atendimento(
                pet_id=data['pet_id'],
                tutor_id=data['tutor_id'],
                anamnese_id=anamnese.id,
                turma_id=data['turma_id'],
                aula_id=aula.id,
                data_checkin=datetime.utcnow(),
                hora_checkin=datetime.strptime(data['hora_checkin'], '%H:%M').time(),
                status_atendimento='Aguardando'
            )
            
            db.session.add(atendimento)
            db.session.commit()
            
            return jsonify({'success': True, 'atendimento_id': atendimento.id})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    pets = Pet.query.filter_by(ativo=True).all()
    turmas = Turma.query.filter_by(ativa=True).all()
    
    return render_template('atendimentos/checkin.html', pets=pets, turmas=turmas)

@app.route('/checkout/<int:atendimento_id>', methods=['GET', 'POST'])
@login_required
def checkout(atendimento_id):
    atendimento = Atendimento.query.get_or_404(atendimento_id)
    
    if request.method == 'POST':
        data = request.get_json()
        
        try:
            atendimento.data_checkout = datetime.utcnow()
            atendimento.hora_checkout = datetime.now().time()
            atendimento.status_atendimento = 'Finalizado'
            atendimento.intercorrencia = data.get('intercorrencia', False)
            atendimento.observacoes_intercorrencia = data.get('observacoes_intercorrencia')
            atendimento.observacoes_dia = data.get('observacoes_dia')
            
            # Assinaturas
            atendimento.assinatura_tutor = data.get('assinatura_tutor')
            atendimento.assinatura_aluno1 = data.get('assinatura_aluno1')
            atendimento.assinatura_aluno2 = data.get('assinatura_aluno2')
            atendimento.assinatura_aluno3 = data.get('assinatura_aluno3')
            atendimento.nome_aluno1 = data.get('nome_aluno1')
            atendimento.nome_aluno2 = data.get('nome_aluno2')
            atendimento.nome_aluno3 = data.get('nome_aluno3')
            
            # Procedimentos realizados
            procedimentos = data.get('procedimentos', [])
            for proc in procedimentos:
                atend_proc = AtendimentoProcedimento(
                    atendimento_id=atendimento.id,
                    procedimento_id=proc['id'],
                    realizado=proc['realizado']
                )
                db.session.add(atend_proc)
            
            db.session.commit()
            
            return jsonify({'success': True})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    procedimentos = Procedimento.query.filter_by(ativo=True).all()
    alunos_turma = db.session.query(Aluno).join(AlunoTurma).filter(
        AlunoTurma.turma_id == atendimento.turma_id
    ).all()
    
    return render_template('atendimentos/checkout.html', 
                         atendimento=atendimento, 
                         procedimentos=procedimentos,
                         alunos_turma=alunos_turma)

@app.route('/consultar-atendimentos')
@login_required
def consultar_atendimentos():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    status = request.args.get('status')
    busca = request.args.get('busca')
    
    query = Atendimento.query.join(Pet).join(Tutor).join(Turma).join(Curso)
    
    if data_inicio:
        query = query.filter(Atendimento.data_checkin >= data_inicio)
    
    if data_fim:
        query = query.filter(Atendimento.data_checkin <= data_fim)
    
    if status:
        query = query.filter(Atendimento.status_atendimento == status)
    
    if busca:
        query = query.filter(
            or_(
                Pet.nome.contains(busca),
                Tutor.nome.contains(busca)
            )
        )
    
    atendimentos = query.order_by(Atendimento.data_checkin.desc()).all()
    
    return render_template('atendimentos/consultar.html', atendimentos=atendimentos)

# =====================================================
# ROTAS DE RELATÓRIOS
# =====================================================

@app.route('/relatorios')
@login_required
def relatorios():
    return render_template('relatorios/index.html')

@app.route('/relatorios/pets-por-turma')
@login_required
def relatorio_pets_turma():
    turma_id = request.args.get('turma_id')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    query = db.session.query(Atendimento).join(Pet).join(Turma).join(Curso)
    
    if turma_id:
        query = query.filter(Atendimento.turma_id == turma_id)
    
    if data_inicio:
        query = query.filter(Atendimento.data_checkin >= data_inicio)
    
    if data_fim:
        query = query.filter(Atendimento.data_checkin <= data_fim)
    
    atendimentos = query.order_by(Atendimento.data_checkin.desc()).all()
    turmas = Turma.query.filter_by(ativa=True).all()
    
    return render_template('relatorios/pets_turma.html', 
                         atendimentos=atendimentos, 
                         turmas=turmas)

# =====================================================
# ROTAS DE GERENCIAMENTO
# =====================================================

@app.route('/gerenciar-turmas')
@login_required
def gerenciar_turmas():
    search = request.args.get('search', '')
    
    query = Turma.query.join(Curso).filter(Turma.ativa == True)
    
    if search:
        query = query.filter(
            or_(
                Turma.codigo.contains(search),
                Curso.nome.contains(search)
            )
        )
    
    turmas = query.order_by(Turma.data_inicio.desc()).all()
    
    return render_template('turmas/gerenciar.html', turmas=turmas)

@app.route('/gerenciar-tutores')
@login_required
def gerenciar_tutores():
    return redirect(url_for('list_tutores'))

@app.route('/gerenciar-pets')
@login_required
def gerenciar_pets_redirect():
    return redirect(url_for('gerenciar_pets'))

# =====================================================
# ROTAS DE API
# =====================================================

@app.route('/api/pets/<int:tutor_id>')
@login_required
def api_pets_tutor(tutor_id):
    pets = Pet.query.filter_by(tutor_id=tutor_id, ativo=True).all()
    return jsonify([{
        'id': p.id,
        'nome': p.nome,
        'raca': p.raca,
        'especie': p.especie,
        'porte': p.porte
    } for p in pets])

@app.route('/api/anamnese/verificar/<int:pet_id>')
@login_required
def verificar_anamnese(pet_id):
    anamnese = Anamnese.query.filter_by(pet_id=pet_id, ativa=True).first()
    
    return jsonify({
        'tem_anamnese': anamnese is not None,
        'anamnese_id': anamnese.id if anamnese else None,
        'data_criacao': anamnese.created_at.isoformat() if anamnese else None
    })

# =====================================================
# INICIALIZAÇÃO
# =====================================================

def init_db():
    """Inicializa o banco de dados com dados básicos"""
    with app.app_context():
        db.create_all()
        
        # Criar usuário admin padrão se não existir
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@senac.br')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        if not Usuario.query.filter_by(email=admin_email).first():
            admin = Usuario(
                nome='Administrador Sistema',
                email=admin_email,
                senha=generate_password_hash(admin_password),
                tipo_usuario='Administrador'
            )
            db.session.add(admin)
            
            try:
                db.session.commit()
                print(f'✅ Usuário administrador criado: {admin_email} / {admin_password}')
            except Exception as e:
                db.session.rollback()
                print(f'❌ Erro ao criar usuário admin: {e}')

if __name__ == '__main__':
    # Inicializar banco na primeira execução
    init_db()
    
    print('🚀 Sistema PetAnamnese iniciando...')
    print('📊 Acesse: http://localhost:5000')
    print('🔐 Login: admin@senac.br / admin123')
    
    # Configurações de execução baseadas em variáveis de ambiente
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    app.run(debug=debug_mode, host=host, port=port)