from app import create_app, db
from models import User  # Certifique-se de importar os modelos que você deseja criar no banco

# Criação da aplicação
app = create_app()

# Criação do banco de dados
with app.app_context():
    db.create_all()  # Cria todas as tabelas definidas nos modelos
    print("Banco de dados criado com sucesso!")