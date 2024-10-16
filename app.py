from flask import Flask, render_template, request, jsonify
import requests
import base64
import json

app = Flask(__name__)

# Credenciais
ID = 'sorrisosaude2'
TOKEN = '311e1db5-ae3a-4998-9eb4-71e7a8bd7f1b'

# Combina e codifica as credenciais em base64
credentials = f"{ID}:{TOKEN}"
encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

# URLs da API
url_criar_paciente = 'https://api.clinicorp.com/rest/v1/patient/create'
url_agendar = "https://api.clinicorp.com/rest/v1/appointment/create_appointment_by_api/"

# Função para criar o paciente
def criar_paciente(nome, telefone):
    payload = {
        "subscriber_id": ID,
        "Name": nome,
        "BirthDate": "YYYY-MM-DD",
        "Sex": "I",
        "Email": "paciente@email.com",
        "MobilePhone": telefone,
        "DocumentId": 0,
        "OtherDocumentId": 0,
        "Notes": "AVALIAÇÃO CREDITO ODONTO",
        "IgnoreSameName": 'X',
        "IgnoreSameDoc": 'X'
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {encoded_credentials}'
    }

    response = requests.post(url_criar_paciente, json=payload, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        generated_id = response_data.get('id')  # Capturando o 'id'
        return generated_id
    else:
        print(f"Erro na criação do paciente: {response.status_code}")
        print(f"Detalhes: {response.text}")
        return None

# Rota inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para agendamento
@app.route('/agendar', methods=['POST'])
def agendar():
    try:
        # Recebendo os dados do formulário enviado via JavaScript (fetch)
        data = request.get_json()
        
        if data is None:
            return jsonify({"message": "Nenhum dado enviado!"}), 400

        nome = data.get('nome')
        telefone = data.get('telefone')
        from_time = data.get('fromTime')
        to_time = data.get('toTime')

        # Remover a data dos campos fromTime e toTime, mantendo apenas os horários
        from_time_horario = from_time.split(' ')[1] if ' ' in from_time else from_time
        to_time_horario = to_time.split(' ')[1] if ' ' in to_time else to_time

        # Verificando se todos os dados obrigatórios estão presentes
        if not nome or not telefone or not from_time or not to_time:
            return jsonify({"message": "Faltam dados obrigatórios!"}), 400

        # Criação do paciente
        paciente_id = criar_paciente(nome, telefone)
        if paciente_id is None:
            return jsonify({"message": "Erro ao criar o paciente!"}), 500

        # Cabeçalho com a autenticação em Basic Auth
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {encoded_credentials}'
        }

        # Dados do agendamento (payload)
        payload = {
            "PatientName": nome,
            "MobilePhone": telefone,
            "Email": "email.exemplo@exemplo.com",  # Este pode ser alterado conforme necessário
            "fromTime": from_time_horario,
            "toTime": to_time_horario,
            "date": from_time.split(' ')[0],  # Extrair a data do fromTime
            "Clinic_BusinessId": 5159843053174784,
            "Dentist_PersonId": 5596642231451648,
            "Patient_PersonId": paciente_id  # Utilizar o ID gerado para o paciente
        }

        # Fazendo a requisição POST para agendar
        response = requests.post(url_agendar, json=payload, headers=headers)

        # Retornando o resultado da requisição
        if response.status_code == 200:
            return jsonify({"message": "Agendamento realizado com sucesso!"}), 200
        else:
            print(f"Erro ao agendar: {response.status_code} - {response.text}")
            return jsonify({"message": f"Erro ao realizar agendamento: {response.text}"}), response.status_code

    except Exception as e:
        print(f"Erro interno: {str(e)}")
        return jsonify({"message": f"Erro interno: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
