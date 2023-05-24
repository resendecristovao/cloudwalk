from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import sqlalchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = '27474225c680f8414d45600e3f7fraq9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projeto.db'
database = SQLAlchemy(app)

from CWmonitorCR.models import Registros1
engine = sqlalchemy.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
inspector = sqlalchemy.inspect(engine)

if not os.path.exists("projeto.db"):
    with app.app_context():
        database.drop_all()
        database.create_all()
        print("BD criado.")
        print(inspector.get_table_names())
        # Criar a tabela 'registros'
        try:
            database.session.execute('''
            CREATE TABLE registros1 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT NOT NULL,
                status TEXT NOT NULL,
                count TEXT NOT NULL,
                acao TEXT
            )
            ''')
            database.session.commit()
            print("Tabelas 'registros' criada.")
        except Exception as e:
            print("Erro ao criar tabelas 'registros':", str(e))
else:
    print("BD existente.")


from CWmonitorCR import routes
