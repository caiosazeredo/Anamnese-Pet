# utils/reports.py
"""
Utilitários para geração de relatórios do Sistema PetAnamnese
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

import io
import base64
from datetime import datetime, date
from collections import defaultdict, Counter
from sqlalchemy import func, distinct
from models import db, Atendimento, Pet, Tutor, Curso, Turma, Aluno, AtendimentoAluno

def criar_cabecalho_pdf():
    """Cria estilo padrão para cabeçalho dos relatórios"""
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para título
    titulo_style = ParagraphStyle(
        'TituloCustom',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1f4e79')
    )
    
    # Estilo para subtítulo
    subtitulo_style = ParagraphStyle(
        'SubtituloCustom',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2f5f8f')
    )
    
    # Estilo para informações gerais
    info_style = ParagraphStyle(
        'InfoCustom',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=10,
        alignment=TA_RIGHT,
        textColor=colors.grey
    )
    
    return {
        'titulo': titulo_style,
        'subtitulo': subtitulo_style,
        'info': info_style,
        'normal': styles['Normal']
    }

def gerar_cabecalho_senac(doc_title, filters=None):
    """Gera cabeçalho padrão SENAC para relatórios"""
    styles = criar_cabecalho_pdf()
    story = []
    
    # Logo SENAC (simulado - substituir pelo logo real)
    # logo = Image('static/images/logo-senac.png', width=2*inch, height=0.8*inch)
    # story.append(logo)
    
    # Título do sistema
    story.append(Paragraph("SENAC RJ - Sistema PetAnamnese", styles['titulo']))
    story.append(Paragraph(doc_title, styles['subtitulo']))
    
    # Informações de geração
    data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M')
    story.append(Paragraph(f"Gerado em: {data_geracao}", styles['info']))
    
    # Filtros aplicados
    if filters:
        filtros_text = "Filtros aplicados: " + ", ".join([f"{k}: {v}" for k, v in filters.items() if v])
        story.append(Paragraph(filtros_text, styles['info']))
    
    story.append(Spacer(1, 20))
    
    return story

def criar_tabela_pdf(headers, data, col_widths=None):
    """Cria tabela formatada para PDF"""
    if not data:
        return Paragraph("Nenhum dado encontrado", getSampleStyleSheet()['Normal'])
    
    # Preparar dados da tabela
    table_data = [headers] + data
    
    # Definir larguras das colunas
    if col_widths is None:
        col_widths = [1.5*inch] * len(headers)
    
    # Criar tabela
    table = Table(table_data, colWidths=col_widths)
    
    # Estilo da tabela
    table_style = TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        
        # Dados
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        
        # Linhas alternadas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        
        # Bordas
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    table.setStyle(table_style)
    return table

def relatorio_pets_por_turma(turma_id=None, data_inicio=None, data_fim=None, curso_id=None):
    """Gera relatório de pets atendidos por turma"""
    
    # Query base
    query = db.session.query(
        Turma.codigo.label('turma'),
        Curso.nome.label('curso'),
        func.count(distinct(Atendimento.pet_id)).label('pets_unicos'),
        func.count(Atendimento.id).label('total_atendimentos'),
        func.date(Atendimento.data_checkin).label('data_aula')
    ).join(Curso).join(Atendimento)
    
    # Aplicar filtros
    if turma_id:
        query = query.filter(Turma.id == turma_id)
    if curso_id:
        query = query.filter(Curso.id == curso_id)
    if data_inicio:
        query = query.filter(Atendimento.data_checkin >= data_inicio)
    if data_fim:
        query = query.filter(Atendimento.data_checkin <= data_fim)
    
    # Agrupar por turma e data
    resultados = query.group_by(
        Turma.codigo, Curso.nome, func.date(Atendimento.data_checkin)
    ).order_by(Turma.codigo, func.date(Atendimento.data_checkin)).all()
    
    return resultados

def relatorio_alunos_atendimentos(aluno_id=None, data_inicio=None, data_fim=None):
    """Gera relatório de pets atendidos por aluno"""
    
    query = db.session.query(
        Aluno.nome.label('aluno_nome'),
        Pet.nome.label('pet_nome'),
        Pet.especie.label('pet_especie'),
        Pet.raca.label('pet_raca'),
        Tutor.nome.label('tutor_nome'),
        Curso.nome.label('curso_nome'),
        Turma.codigo.label('turma_codigo'),
        Atendimento.data_checkin.label('data_atendimento'),
        AtendimentoAluno.funcao.label('funcao_aluno')
    ).join(AtendimentoAluno).join(Atendimento).join(Pet).join(Tutor).join(Turma).join(Curso)
    
    # Filtros
    if aluno_id:
        query = query.filter(Aluno.id == aluno_id)
    if data_inicio:
        query = query.filter(Atendimento.data_checkin >= data_inicio)
    if data_fim:
        query = query.filter(Atendimento.data_checkin <= data_fim)
    
    resultados = query.order_by(Atendimento.data_checkin.desc()).all()
    
    return resultados

def relatorio_especies_por_curso(curso_id=None, data_inicio=None, data_fim=None):
    """Gera estatísticas de espécies por curso"""
    
    query = db.session.query(
        Curso.nome.label('curso_nome'),
        Pet.especie.label('especie'),
        func.count(distinct(Pet.id)).label('pets_unicos'),
        func.count(Atendimento.id).label('total_atendimentos')
    ).join(Turma).join(Atendimento).join(Pet)
    
    # Filtros
    if curso_id:
        query = query.filter(Curso.id == curso_id)
    if data_inicio:
        query = query.filter(Atendimento.data_checkin >= data_inicio)
    if data_fim:
        query = query.filter(Atendimento.data_checkin <= data_fim)
    
    resultados = query.group_by(Curso.nome, Pet.especie).all()
    
    # Processar dados para visualização
    dados_por_curso = defaultdict(lambda: {'Canino': 0, 'Felino': 0, 'Outros': 0})
    
    for resultado in resultados:
        dados_por_curso[resultado.curso_nome][resultado.especie] = resultado.total_atendimentos
    
    return dados_por_curso

def relatorio_racas_por_curso(curso_id=None, especie=None, data_inicio=None, data_fim=None):
    """Gera estatísticas de raças por curso"""
    
    query = db.session.query(
        Curso.nome.label('curso_nome'),
        Pet.raca.label('raca'),
        Pet.especie.label('especie'),
        func.count(distinct(Pet.id)).label('pets_unicos'),
        func.count(Atendimento.id).label('total_atendimentos')
    ).join(Turma).join(Atendimento).join(Pet)
    
    # Filtros
    if curso_id:
        query = query.filter(Curso.id == curso_id)
    if especie:
        query = query.filter(Pet.especie == especie)
    if data_inicio:
        query = query.filter(Atendimento.data_checkin >= data_inicio)
    if data_fim:
        query = query.filter(Atendimento.data_checkin <= data_fim)
    
    resultados = query.group_by(Curso.nome, Pet.raca, Pet.especie).order_by(
        func.count(Atendimento.id).desc()
    ).all()
    
    return resultados

def relatorio_portes_por_curso(curso_id=None, especie=None, data_inicio=None, data_fim=None):
    """Gera estatísticas de portes por curso"""
    
    query = db.session.query(
        Curso.nome.label('curso_nome'),
        Pet.porte.label('porte'),
        Pet.especie.label('especie'),
        func.count(distinct(Pet.id)).label('pets_unicos'),
        func.count(Atendimento.id).label('total_atendimentos')
    ).join(Turma).join(Atendimento).join(Pet)
    
    # Filtros
    if curso_id:
        query = query.filter(Curso.id == curso_id)
    if especie:
        query = query.filter(Pet.especie == especie)
    if data_inicio:
        query = query.filter(Atendimento.data_checkin >= data_inicio)
    if data_fim:
        query = query.filter(Atendimento.data_checkin <= data_fim)
    
    resultados = query.group_by(Curso.nome, Pet.porte, Pet.especie).all()
    
    return resultados

def gerar_historico_pet_pdf(pet_id, data_inicio=None, data_fim=None):
    """Gera PDF do histórico completo de um pet"""
    
    # Buscar dados do pet
    pet = Pet.query.get(pet_id)
    if not pet:
        return None
    
    # Buscar atendimentos
    query = Atendimento.query.filter_by(pet_id=pet_id)
    if data_inicio:
        query = query.filter(Atendimento.data_checkin >= data_inicio)
    if data_fim:
        query = query.filter(Atendimento.data_checkin <= data_fim)
    
    atendimentos = query.order_by(Atendimento.data_checkin.desc()).all()
    
    # Criar PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Cabeçalho
    filters = {
        'Pet': pet.nome,
        'Tutor': pet.tutor.nome,
        'Período': f"{data_inicio or 'Início'} a {data_fim or 'Hoje'}"
    }
    story.extend(gerar_cabecalho_senac(f"Histórico de Atendimentos - {pet.nome}", filters))
    
    # Informações do pet
    styles = criar_cabecalho_pdf()
    story.append(Paragraph("Informações do Pet", styles['subtitulo']))
    
    info_pet = [
        ['Nome', pet.nome],
        ['Espécie', pet.especie],
        ['Raça', pet.raca or 'SRD'],
        ['Porte', pet.porte or 'Não informado'],
        ['Idade', f"{pet.idade} anos" if pet.idade else 'Não informado'],
        ['Tutor', pet.tutor.nome],
        ['Telefone', pet.tutor.telefone],
    ]
    
    tabela_pet = criar_tabela_pdf(['Campo', 'Valor'], info_pet, [2*inch, 4*inch])
    story.append(tabela_pet)
    story.append(Spacer(1, 20))
    
    # Histórico de atendimentos
    story.append(Paragraph("Histórico de Atendimentos", styles['subtitulo']))
    
    if atendimentos:
        headers = ['Data', 'Curso', 'Turma', 'Status', 'Observações']
        dados_atendimentos = []
        
        for atendimento in atendimentos:
            dados_atendimentos.append([
                atendimento.data_checkin.strftime('%d/%m/%Y'),
                atendimento.turma.curso.nome,
                atendimento.turma.codigo,
                atendimento.status_atendimento,
                (atendimento.observacoes_dia[:50] + '...') if atendimento.observacoes_dia and len(atendimento.observacoes_dia) > 50 else (atendimento.observacoes_dia or '-')
            ])
        
        tabela_atendimentos = criar_tabela_pdf(headers, dados_atendimentos)
        story.append(tabela_atendimentos)
    else:
        story.append(Paragraph("Nenhum atendimento encontrado no período", styles['normal']))
    
    # Gerar PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def gerar_relatorio_pdf(tipo_relatorio, dados, filtros=None):
    """Função genérica para gerar PDFs de relatórios"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Títulos por tipo de relatório
    titulos = {
        'pets_turma': 'Pets por Turma',
        'alunos_atendimentos': 'Alunos por Atendimento',
        'especies_curso': 'Espécies por Curso',
        'racas_curso': 'Raças por Curso',
        'portes_curso': 'Portes por Curso'
    }
    
    titulo = titulos.get(tipo_relatorio, 'Relatório do Sistema')
    
    # Cabeçalho
    story.extend(gerar_cabecalho_senac(titulo, filtros))
    
    # Processar dados baseado no tipo
    if tipo_relatorio == 'pets_turma':
        headers = ['Turma', 'Curso', 'Data da Aula', 'Pets Únicos', 'Total Atendimentos']
        dados_tabela = []
        
        for item in dados:
            dados_tabela.append([
                item.turma,
                item.curso,
                item.data_aula.strftime('%d/%m/%Y') if item.data_aula else '-',
                str(item.pets_unicos),
                str(item.total_atendimentos)
            ])
    
    elif tipo_relatorio == 'alunos_atendimentos':
        headers = ['Aluno', 'Pet', 'Tutor', 'Curso', 'Data', 'Função']
        dados_tabela = []
        
        for item in dados:
            dados_tabela.append([
                item.aluno_nome,
                f"{item.pet_nome} ({item.pet_especie})",
                item.tutor_nome,
                item.curso_nome,
                item.data_atendimento.strftime('%d/%m/%Y'),
                item.funcao_aluno
            ])
    
    # Adicionar tabela
    tabela = criar_tabela_pdf(headers, dados_tabela)
    story.append(tabela)
    
    # Resumo estatístico
    styles = criar_cabecalho_pdf()
    story.append(Spacer(1, 20))
    story.append(Paragraph("Resumo Estatístico", styles['subtitulo']))
    
    total_registros = len(dados)
    story.append(Paragraph(f"Total de registros: {total_registros}", styles['normal']))
    
    # Gerar PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def calcular_estatisticas_dashboard():
    """Calcula estatísticas para o dashboard de relatórios"""
    
    hoje = date.today()
    primeiro_dia_mes = hoje.replace(day=1)
    
    stats = {}
    
    # Atendimentos do mês
    stats['total_atendimentos_mes'] = Atendimento.query.filter(
        Atendimento.data_checkin >= primeiro_dia_mes
    ).count()
    
    # Pets diferentes atendidos
    stats['pets_diferentes'] = db.session.query(distinct(Atendimento.pet_id)).count()
    
    # Cursos ativos
    stats['cursos_ativos'] = Curso.query.filter_by(ativo=True).count()
    
    # Alunos que participaram de atendimentos
    stats['alunos_participantes'] = db.session.query(distinct(AtendimentoAluno.aluno_id)).count()
    
    return stats

def exportar_dados_excel(dados, nome_arquivo, sheets=None):
    """Exporta dados para Excel (funcionalidade futura)"""
    # Implementar com pandas/openpyxl quando necessário
    pass

def gerar_grafico_pizza(dados, titulo="Gráfico"):
    """Gera gráfico de pizza para relatórios"""
    # Implementar com matplotlib/plotly quando necessário
    pass

def gerar_grafico_barras(dados, titulo="Gráfico"):
    """Gera gráfico de barras para relatórios"""
    # Implementar com matplotlib/plotly quando necessário
    pass