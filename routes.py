from flask import render_template, redirect, url_for, flash, request
from CWmonitorCR import app, database
from CWmonitorCR.models import Registros1
import json
import pandas as pd
from collections import defaultdict
from sqlalchemy.inspection import inspect
import plotly.graph_objects as go
import plotly
from twilio.rest import Client
import credenciais

df1 = pd.DataFrame(columns=["Time", "Status", "Count", "Acao"])

# Envio de SMS
def enviar_sms(mensagem):
    account_sid = credenciais.account_sid
    token = credenciais.token

    client = Client(account_sid, token)

    remetente = credenciais.remetente
    destino = '+5561981028080'

    message = client.messages.create(
        to=destino,
        from_=remetente,
        body=mensagem)
    print(message.sid)

# SQL para DF
def pegar_df():
    with app.app_context():
        resultado = Registros1.query.all()
        if resultado:
            df1 = pd.DataFrame(query_to_dict(resultado))
            df1['count'] = df1['count'].astype('int')
            df1_pivot = df1.pivot_table(index='time', columns='status', values='count', aggfunc='sum').reset_index()
    return df1, df1_pivot

@app.route('/callback', methods=['POST', 'GET'])
def cb():
    return gm(request.args.get('data'))


@app.route('/')
def home():
    return render_template('chartsajax.html', graphJSON=gm(data=''))


def query_to_dict(rset):
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)
    return result


def gm(data):
    with app.app_context():
        resultado = Registros1.query.all()
        if resultado:
            df1 = pd.DataFrame(query_to_dict(resultado))
            df1['count'] = df1['count'].astype('int')
            print(df1.describe())
            print(df1.info())

            # Reorganizar os dados usando pivot_table
            df1_pivot = df1.pivot_table(index='time', columns='status', values='count', aggfunc='sum').reset_index()

            # Criar o gráfico interativo usando a biblioteca Plotly
            fig1 = go.Figure()

            # Adicionar as linhas de cada status no gráfico
            for column in df1['status'].unique():
                fig1.add_trace(go.Scatter(x=df1_pivot['time'], y=df1_pivot[f'{column}'], name=f'{column}'))

            # Configurar o título e os rótulos dos eixos
            fig1.update_layout(title='Número de Transações por Status', title_x=0.5,
                               xaxis_title='Hora',
                               yaxis_title='Número de Transações')

            # Exibir o gráfico interativo
            graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
            return graphJSON

@app.route('/endpoint1', methods=['POST'])
def endpoint1():
    if request.method == 'POST':
        try:
            ls_denied = ls_reversed = ls_failed = 1000
            dados = json.loads(request.data)
            print(dados)
            df1, df1_pivot = pegar_df()
        except:
            print("BD Vazio")

        try:
            mean_denied = df1_pivot['denied'].mean()
            std_denied = df1_pivot['denied'].std()
            ls_denied = mean_denied + 3 * std_denied
        except:
            print("Erro Denied")
        try:
            mean_reversed = df1_pivot['reversed'].mean()
            std_reversed = df1_pivot['reversed'].std()
            ls_reversed = mean_reversed + 3 * std_reversed
        except:
            print("Erro Reversed")
        try:
            mean_failed = df1_pivot['failed'].mean()
            std_failed = df1_pivot['failed'].std()
            ls_failed = mean_failed + 3 * std_failed
        except:
            print("Erro Failed")

        if dados['status'] == 'denied' and int(dados['f0_']) > ls_denied:
            enviar_sms('Alerta! Número de transações DENIED anormal.')
            acao = 'Número de transações DENIED anormal'
        if dados['status'] == 'reversed' and int(dados['f0_']) > ls_reversed:
            enviar_sms('Alerta! Número de transações REVERSED anormal.')
            acao = 'Número de transações REVERSED anormal'
        if dados['status'] == 'failed' and int(dados['f0_']) > ls_failed:
            enviar_sms('Alerta! Número de transações FAILED anormal.')
            acao = 'Número de transações FAILED anormal'
        else:
            acao = ''

        #with app.app_context():
        registro = Registros1(time=dados['time'], status=dados['status'], count=dados['f0_'], acao=acao)
        database.session.add(registro)
        database.session.commit()
        return '200' + acao
    else:
        return '404'

