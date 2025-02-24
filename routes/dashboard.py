from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from flask_login import login_required
from extensions import db, allowed_file
from models import Item

dashboard_bp = Blueprint('dashboard', __name__)

# Rota para o dashboard
@dashboard_bp.route('/')
@login_required
def dashboard():
    total_itens = Item.query.count()
    itens_abaixo_minimo = Item.query.filter(Item.quantidade_atual < Item.quantidade_minima).count()
    itens_para_repor = Item.query.filter(Item.quantidade_atual <= Item.quantidade_minima * 1.1).count()

    return render_template(
        'dashboard.html',
        total_itens=total_itens,
        itens_abaixo_minimo=itens_abaixo_minimo,
        itens_para_repor=itens_para_repor
    )

# Rota para listar o estoque
@dashboard_bp.route('/estoque')
@login_required
def estoque():
    itens = Item.query.all()
    return render_template('estoque.html', itens=itens)

# Rota para adicionar item
@dashboard_bp.route('/adicionar_item', methods=['GET', 'POST'])
@login_required
def adicionar_item():
    if request.method == 'POST':
        nome = request.form.get('nome')
        quantidade_minima = float(request.form.get('quantidade_minima'))
        quantidade_atual = float(request.form.get('quantidade_atual'))
        unidade = request.form.get('unidade')

        novo_item = Item(nome=nome, quantidade_minima=quantidade_minima, quantidade_atual=quantidade_atual, unidade=unidade)
        db.session.add(novo_item)
        db.session.commit()

        flash('Item adicionado com sucesso!', 'success')
        return redirect(url_for('dashboard.estoque'))

    return render_template('adicionar_item.html')

# Rota para editar item
@dashboard_bp.route('/editar_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def editar_item(item_id):
    item = Item.query.get_or_404(item_id)

    if request.method == 'POST':
        item.nome = request.form.get('nome')
        item.quantidade_minima = float(request.form.get('quantidade_minima'))
        item.quantidade_atual = float(request.form.get('quantidade_atual'))
        item.unidade = request.form.get('unidade')

        db.session.commit()
        flash('Item atualizado com sucesso!', 'success')
        return redirect(url_for('dashboard.estoque'))

    return render_template('editar_item.html', item=item)

# Rota para remover item
@dashboard_bp.route('/remover_item/<int:item_id>', methods=['POST'])
@login_required
def remover_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()

    flash('Item removido com sucesso!', 'success')
    return redirect(url_for('dashboard.estoque'))

# Rota para atualizar estoque
@dashboard_bp.route('/atualizar_estoque/<int:item_id>', methods=['POST'])
@login_required
def atualizar_estoque(item_id):
    item = Item.query.get_or_404(item_id)
    nova_quantidade = request.form.get('quantidade_atual', type=float)

    if nova_quantidade is None or nova_quantidade < 0:
        flash('Quantidade inválida.', 'danger')
        return redirect(url_for('dashboard.estoque'))

    item.quantidade_atual = nova_quantidade
    db.session.commit()
    flash('Estoque atualizado com sucesso!', 'success')
    return redirect(url_for('dashboard.estoque'))

# Rota para upload de foto
@dashboard_bp.route('/upload_foto', methods=['POST'])
def upload_foto():
    if 'file' not in request.files:
        flash('Nenhum arquivo enviado', 'error')
        return redirect(url_for('dashboard.estoque'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('dashboard.estoque'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        flash('Foto enviada com sucesso!', 'success')
    else:
        flash('Formato de arquivo não permitido. Use PNG, JPG, JPEG ou GIF.', 'error')
    
    return redirect(url_for('dashboard.estoque'))

# Rota para upload de tabela com OCR
@dashboard_bp.route('/upload_tabela', methods=['POST'])
def upload_tabela():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nome de arquivo inválido"}), 400
    
    upload_folder = os.path.join(current_app.root_path, 'static/uploads')
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, file.filename)
    file.save(filepath)
    
    ocr = OCRProcessor(tesseract_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    df = ocr.process_image(filepath)
    
    return jsonify({"dados": df.to_dict(orient='records')})
