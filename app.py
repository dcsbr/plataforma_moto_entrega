from flask import Flask, render_template, request, Response, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Configuração do Banco de Dados
def get_db():
    conn = sqlite3.connect('motofrete.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS entregas
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 cliente TEXT NOT NULL,
                 telefone TEXT NOT NULL,
                 endereco TEXT NOT NULL,
                 tipo_encomenda TEXT NOT NULL,
                 data_entrega TEXT NOT NULL,
                 forma_pagamento TEXT NOT NULL,
                 observacoes TEXT,
                 peso REAL NOT NULL,
                 altura REAL NOT NULL,
                 largura REAL NOT NULL,
                 profundidade REAL NOT NULL,
                 distancia REAL NOT NULL,
                 frete REAL NOT NULL)''')
    return conn

# Rotas Principais
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    try:
        dados = request.form
        distancia = float(dados['distancia'])
        peso = float(dados['peso'])
        volume = float(dados['altura']) * float(dados['largura']) * float(dados['profundidade'])
        frete = (distancia * 2.50) + (peso * 0.50) + (volume * 0.10)
        
        conn = get_db()
        conn.execute('''INSERT INTO entregas VALUES
                     (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (dados['cliente'], dados['telefone'], dados['endereco'],
                      dados['tipo_encomenda'], dados['data_entrega'],
                      dados['forma_pagamento'], dados.get('observacoes', ''),
                      peso, float(dados['altura']), float(dados['largura']), 
                      float(dados['profundidade']), distancia, frete))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'frete': f"R${frete:.2f}",
            'message': "Cálculo realizado com sucesso!"
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Erro: {str(e)}"
        }), 400

@app.route('/entregas')
def listar_entregas():
    if request.args.get('senha') != '123':
        return render_template('acesso_negado.html')
    
    conn = get_db()
    entregas = conn.execute('SELECT * FROM entregas ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('entregas.html', entregas=entregas)

@app.route('/editar/<int:id>')
def editar_entrega(id):
    conn = get_db()
    entrega = conn.execute('SELECT * FROM entregas WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('editar.html', entrega=entrega)

@app.route('/atualizar/<int:id>', methods=['POST'])
def atualizar_entrega(id):
    try:
        dados = request.form
        conn = get_db()
        conn.execute('''UPDATE entregas SET
                     cliente=?, telefone=?, endereco=?,
                     tipo_encomenda=?, data_entrega=?,
                     forma_pagamento=?, observacoes=?,
                     peso=?, altura=?, largura=?,
                     profundidade=?, distancia=?
                     WHERE id=?''',
                     (dados['cliente'], dados['telefone'], dados['endereco'],
                      dados['tipo_encomenda'], dados['data_entrega'],
                      dados['forma_pagamento'], dados.get('observacoes', ''),
                      dados['peso'], dados['altura'], dados['largura'],
                      dados['profundidade'], dados['distancia'], id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/exportar')
def exportar_csv():
    conn = get_db()
    entregas = conn.execute('SELECT * FROM entregas').fetchall()
    conn.close()
    
    csv = "ID,Cliente,Telefone,Endereço,Tipo,Data,Pagamento,Observações,Peso,Altura,Largura,Profundidade,Distância,Frete\n"
    for entrega in entregas:
        csv += f"{entrega[0]},{entrega[1]},{entrega[2]},{entrega[3]},{entrega[4]},{entrega[5]},{entrega[6]},{entrega[7]},{entrega[8]},{entrega[9]},{entrega[10]},{entrega[11]},{entrega[12]},{entrega[13]}\n"
    
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment;filename=entregas.csv"}
    )

if __name__ == '__main__':
    app.run(debug=True)