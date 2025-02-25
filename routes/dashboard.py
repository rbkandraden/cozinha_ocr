from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
from werkzeug.utils import secure_filename
from flask_login import login_required
from extensions import db
from models import Item
from ocr_processor import OCRProcessor

dashboard_bp = Blueprint('dashboard', __name__)

# Configurações
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rotas principais
@dashboard_bp.route('/')
@login_required
def dashboard():
    stats = {
        'total_itens': Item.query.count(),
        'itens_abaixo_minimo': Item.query.filter(Item.quantidade_atual < Item.quantidade_minima).count(),
        'itens_para_repor': Item.query.filter(Item.quantidade_atual <= Item.quantidade_minima * 1.1).count()
    }
    return render_template('dashboard.html', **stats)

@dashboard_bp.route('/estoque')
@login_required
def estoque():
    return render_template('estoque.html', 
        itens=Item.query.order_by(Item.nome).all()
    )

# CRUD de Itens
@dashboard_bp.route('/adicionar_item', methods=['GET', 'POST'])
@login_required
def adicionar_item():
    if request.method == 'POST':
        try:
            novo_item = Item(
                nome=request.form['nome'],
                quantidade_minima=float(request.form['quantidade_minima']),
                quantidade_atual=float(request.form['quantidade_atual']),
                unidade=request.form['unidade']
            )
            db.session.add(novo_item)
            db.session.commit()
            flash('Item adicionado com sucesso!', 'success')
            return redirect(url_for('dashboard.estoque'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar item: {str(e)}', 'danger')
    return render_template('adicionar_item.html')

@dashboard_bp.route('/editar_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def editar_item(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == 'POST':
        try:
            item.nome = request.form['nome']
            item.quantidade_minima = float(request.form['quantidade_minima'])
            item.quantidade_atual = float(request.form['quantidade_atual'])
            item.unidade = request.form['unidade']
            db.session.commit()
            flash('Item atualizado com sucesso!', 'success')
            return redirect(url_for('dashboard.estoque'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar item: {str(e)}', 'danger')
    return render_template('editar_item.html', item=item)

@dashboard_bp.route('/remover_item/<int:item_id>', methods=['POST'])
@login_required
def remover_item(item_id):
    try:
        item = Item.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        flash('Item removido com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover item: {str(e)}', 'danger')
    return redirect(url_for('dashboard.estoque'))

# Upload e OCR
@dashboard_bp.route('/upload_tabela', methods=['POST'])
@login_required
def upload_tabela():
    if 'file' not in request.files:
        flash('Nenhum arquivo enviado', 'danger')
        return redirect(url_for('dashboard.estoque'))

    file = request.files['file']
    if not file or file.filename == '':
        flash('Arquivo inválido', 'danger')
        return redirect(url_for('dashboard.estoque'))

    if not allowed_file(file.filename):
        flash('Formato de arquivo não permitido', 'danger')
        return redirect(url_for('dashboard.estoque'))

    try:
        # Configurar pasta temporária
        upload_folder = os.path.join(current_app.root_path, 'temp_uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Salvar arquivo temporário
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Processar OCR
        ocr = OCRProcessor(TESSERACT_PATH)
        df = ocr.process_inventory_table(filepath)

        # Atualizar banco de dados
        with db.session.begin():
            for _, row in df.iterrows():
                item = Item.query.filter_by(nome=row['nome']).first()
                
                if item:
                    # Atualizar item existente
                    item.quantidade_minima = row['quantidade_minima']
                    item.quantidade_atual = row['quantidade_atual']
                    item.unidade = row['unidade']
                else:
                    # Criar novo item
                    db.session.add(Item(
                        nome=row['nome'],
                        quantidade_minima=row['quantidade_minima'],
                        quantidade_atual=row['quantidade_atual'],
                        unidade=row['unidade']
                    ))
        
        db.session.commit()
        os.remove(filepath)
        flash(f'{len(df)} itens processados ({(len(df) - Item.query.count())} novos)', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Erro no processamento: {str(e)}', 'danger')
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)

    return redirect(url_for('dashboard.estoque'))

@dashboard_bp.route('/atualizar_estoque/<int:item_id>', methods=['POST'])
@login_required
def atualizar_estoque(item_id):
    item = Item.query.get_or_404(item_id)
    try:
        nova_quantidade = float(request.form.get('quantidade_atual', 0))
        if nova_quantidade < 0:
            raise ValueError("Quantidade negativa")
            
        item.quantidade_atual = nova_quantidade
        db.session.commit()
        flash('Estoque atualizado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro na atualização: {str(e)}', 'danger')
    return redirect(url_for('dashboard.estoque'))