# Sistema Cozinha OCR

> **Nota Pessoal:** Este projeto foi iniciado por mim (Rebeca Andrade) sem nenhuma experiência prévia em programação. A Maria Clara, que já tinha experiência, me incentivou a aprender na prática, jogando o desafio para mim e dizendo "se vire" como método de aprendizado. Todo o desenvolvimento foi um grande exercício de pesquisa, tentativa e erro, e evolução real de quem estava começando do zero.

Sistema de Gestão de Estoque e Usuários para Cozinha, automatizando o processamento de planilhas a partir de imagens.
________________________________________
Histórico do Projeto
Este sistema nasceu a partir do Wayne Security (Denner Lima e Maria Clara), originalmente focado em segurança.
•	NordHaus: primeira versão adaptada por Maria Clara e Rebeca Andrade, explorando a base existente e fazendo ajustes iniciais.
•	Cozinha OCR: segunda versão, com melhorias funcionais, integração de OCR para leitura de notas/imagens, upload de fotos, scripts auxiliares, ajustes estéticos e branding próprio.
Resumo: Maria Clara e Rebeca Andrade trabalharam juntas em todas as fases desta evolução, e este projeto é fruto dessa colaboração contínua.
________________________________________
Funcionalidades
•	Upload de imagens de planilhas
•	Processamento automático via OCR

# Sistema Cozinha OCR

![GitHub repo size](https://img.shields.io/github/repo-size/seu-usuario/sistema-cozinha)
![GitHub last commit](https://img.shields.io/github/last-commit/seu-usuario/sistema-cozinha)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

Sistema web para gestão de estoque e usuários em cozinhas, automatizando o processamento de planilhas a partir de imagens via OCR.

---

## :sparkles: Funcionalidades
- Upload de imagens de planilhas
- Processamento automático via OCR
- Organização dos dados extraídos
- Gestão de estoque centralizada
- Interface web com autenticação de usuários

---

## :computer: Tecnologias Utilizadas
- **Backend:** Python 3, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Frontend:** HTML, CSS, Bootstrap
- **Processamento de Imagens:** OpenCV, pytesseract (OCR)
- **Banco de Dados:** SQLite
- **Outras Ferramentas:** Git, Pip

---

## :rocket: Como Rodar Localmente

### Pré-requisitos
- Python 3.10+
- Tesseract OCR instalado ([download](https://github.com/tesseract-ocr/tesseract))

### Passos
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/sistema-cozinha.git
cd sistema-cozinha

# Crie e ative o ambiente virtual
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
# Renomeie .env.example para .env e ajuste as chaves conforme necessário

# Crie o banco de dados
python create_db.py

# Rode o sistema
python app.py

# Acesse em http://localhost:5000
```

---

## :file_folder: Estrutura do Projeto
```text
sistema-cozinha/
├── app.py
├── config.py
├── create_db.py
├── requirements.txt
├── .env
├── instance/
│   └── wayne_security.db
├── extensions.py
├── models.py
├── forms.py
├── ocr_processor.py
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   └── dashboard.py
├── static/
│   ├── css/
│   ├── img/
│   └── uploads/
├── temp_uploads/
├── templates/
│   ├── base.html
│   ├── login.html
│   └── ...
├── utils/
└── tests/
```

---

## :bulb: Aprendizados e Evolução
- Estruturação de projetos Flask do zero
- Conceitos de ORM, autenticação, blueprints e formulários web
- Integração de bibliotecas externas (OCR, OpenCV)
- Melhoria de habilidades de pesquisa, leitura de documentação e adaptação de código
- Evolução do “copiar e colar” para criar soluções próprias

---

## :handshake: Contribuição
Sugestões, críticas e pull requests são bem-vindos! Este projeto é fruto da colaboração entre Maria Clara e Rebeca Andrade e está aberto para quem quiser aprender ou contribuir.

---


## :mailbox: Contato
- [GitHub: rbkandraden](https://github.com/rbkandraden)
- [LinkedIn: rbkandraden](https://www.linkedin.com/in/rebecca-andrade-988026365/)
- [GitHub: mariaclara-d](https://github.com/mariaclara-d)
- [LinkedIn: mariaclara-d](https://www.linkedin.com/in/maria-clara-dev/)
- [GitHub: dennerlima-dev](https://github.com/dennerlima-dev)

---

Projeto em constante evolução. Obrigado por visitar!
