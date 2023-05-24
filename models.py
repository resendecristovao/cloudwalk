from CWmonitorCR import database


class Registros1(database.Model):
    __tablename__ = 'registros1'

    id = database.Column(database.Integer, primary_key=True)
    time = database.Column(database.String, nullable=False)
    status = database.Column(database.String, nullable=False)
    count = database.Column(database.String, nullable=False)
    acao = database.Column(database.String, nullable=True)
