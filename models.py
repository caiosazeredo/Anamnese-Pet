# models.py - Modelos de Dados Completos
"""
Modelos do Sistema PetAnamnese - SENAC RJ
Estrutura completa do banco de dados
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

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
    uf = db.Column(db.String(2), default='RJ')
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
    uf = db.Column(db.String(2), default='RJ')
    cep = db.Column(db.String(10))
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
    foto = db.Column(db.String(255))  # Path para foto do pet
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tutor = db.relationship('Tutor', backref='pets')

class Anamnese(db.Model):
    __tablename__ = 'anamneses'
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pets.id'), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutores.id'), nullable=False)
    
    # Dados médicos baseados no template
    alergia = db.Column(db.Boolean, default=False)
    curso_atendimento = db.Column(db.Enum('Banho e Tosa', 'Técnicas Avançadas de Tosa', 'Adestramento', 'Dog Walker'), nullable=False)
    cirurgia_recente = db.Column(db.Boolean, default=False)
    pode_cortar_unha = db.Column(db.Boolean, default=True)
    pode_perfume = db.Column(db.Boolean, default=True)
    sofre_convulsao = db.Column(db.Boolean, default=False)
    problema_cardiorespiatorio = db.Column(db.Boolean, default=False)
    pulga_carrapato = db.Column(db.Boolean, default=False)
    problema_articular = db.Column(db.Boolean, default=False)
    pode_limpar_ouvido = db.Column(db.Boolean, default=True)
    vacinado_multipla_antirrabica = db.Column(db.Boolean, default=False)
    
    # Observações
    observacoes_alergia = db.Column(db.Text)
    observacoes_cirurgia = db.Column(db.Text)
    observacoes_gerais = db.Column(db.Text)
    
    # Data e horário do check-in planejado
    data_checkin_planejado = db.Column(db.Date)
    hora_checkin_planejado = db.Column(db.Time)
    
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
    
    # Assinaturas - Tutor + até 3 alunos
    assinatura_tutor = db.Column(db.Text)  # Base64
    assinatura_aluno1 = db.Column(db.Text)  # Base64
    assinatura_aluno2 = db.Column(db.Text)  # Base64
    assinatura_aluno3 = db.Column(db.Text)  # Base64
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    pet = db.relationship('Pet', backref='atendimentos')
    tutor = db.relationship('Tutor', backref='atendimentos')
    anamnese = db.relationship('Anamnese', backref='atendimentos')
    turma = db.relationship('Turma', backref='atendimentos')
    aula = db.relationship('Aula', backref='atendimentos')

class AtendimentoAluno(db.Model):
    """Tabela para registrar quais alunos atenderam um pet"""
    __tablename__ = 'atendimento_aluno'
    id = db.Column(db.Integer, primary_key=True)
    atendimento_id = db.Column(db.Integer, db.ForeignKey('atendimentos.id'), nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    funcao = db.Column(db.Enum('Principal', 'Auxiliar'), default='Auxiliar')
    assinatura = db.Column(db.Text)  # Base64 da assinatura
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    atendimento = db.relationship('Atendimento', backref='alunos_atendimento')
    aluno = db.relationship('Aluno', backref='atendimentos_realizados')

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

    def set_password(self, password):
        """Define senha criptografada"""
        self.senha = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica senha"""
        return check_password_hash(self.senha, password)

# Função para inicializar dados padrão
def init_default_data():
    """Inicializa dados padrão do sistema"""
    
    # Cursos padrão baseados no template
    cursos_default = [
        {
            'nome': 'Banho e Tosa',
            'codigo_sga': 'BT001',
            'carga_horaria': 60,
            'tipo_curso': 'Aperfeiçoamento',
            'eixo_tecnologico': 'Ambiente e Saúde',
            'segmento': 'Pet Care'
        },
        {
            'nome': 'Técnicas Avançadas de Tosa',
            'codigo_sga': 'TAT001', 
            'carga_horaria': 80,
            'tipo_curso': 'Aperfeiçoamento',
            'eixo_tecnologico': 'Ambiente e Saúde',
            'segmento': 'Pet Care'
        },
        {
            'nome': 'Adestramento',
            'codigo_sga': 'ADT001',
            'carga_horaria': 40,
            'tipo_curso': 'Socioprofissional',
            'eixo_tecnologico': 'Ambiente e Saúde',
            'segmento': 'Pet Care'
        },
        {
            'nome': 'Dog Walker',
            'codigo_sga': 'DW001',
            'carga_horaria': 30,
            'tipo_curso': 'Socioprofissional', 
            'eixo_tecnologico': 'Ambiente e Saúde',
            'segmento': 'Pet Care'
        }
    ]
    
    for curso_data in cursos_default:
        if not Curso.query.filter_by(codigo_sga=curso_data['codigo_sga']).first():
            curso = Curso(**curso_data)
            db.session.add(curso)
    
    # Procedimentos padrão
    procedimentos_default = [
        {'nome': 'Banho', 'descricao': 'Banho completo com produtos adequados'},
        {'nome': 'Tosa', 'descricao': 'Corte de pelo conforme padrão da raça'},
        {'nome': 'Corte de unha', 'descricao': 'Corte e limagem das unhas'},
        {'nome': 'Limpeza de ouvido', 'descricao': 'Higienização dos ouvidos'},
        {'nome': 'Escovação', 'descricao': 'Escovação e desembaraço'},
        {'nome': 'Perfume', 'descricao': 'Aplicação de perfume pet'},
        {'nome': 'Secagem', 'descricao': 'Secagem completa com equipamentos'},
        {'nome': 'Tosa higiênica', 'descricao': 'Corte em áreas específicas'},
    ]
    
    for proc_data in procedimentos_default:
        if not Procedimento.query.filter_by(nome=proc_data['nome']).first():
            procedimento = Procedimento(**proc_data)
            db.session.add(procedimento)
    
    try:
        db.session.commit()
        print('✅ Dados padrão inicializados com sucesso!')
    except Exception as e:
        db.session.rollback()
        print(f'❌ Erro ao inicializar dados padrão: {e}')