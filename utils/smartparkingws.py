import json
import requests
from datetime import datetime


URL = "https://smartparkingws.herokuapp.com/"
# URL = "http://127.0.0.1:8080/"
ESTACIONAMENTO_PATH = "api/estacionamento/"
AUTH = ('leonardoblack.net@gmail.com', '24021684Leo@')

DATE_FORMAT = "%d/%m/%Y"
TIME_FORMAT = "%H:%M:%S"
SHORT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def pegar_data_hora_atual():
    """
    Retorna a data e hora atual
    :return data, hora, data_hora
    :rtype list
    """
    atual = datetime.now()
    data = atual.date().strftime(DATE_FORMAT)
    hora = atual.time().strftime(TIME_FORMAT)
    data_hora = atual.strftime(SHORT_DATETIME_FORMAT)
    return data, hora, data_hora


def get_auth_token():
    url_path = "api-token-auth/"
    data = {
        "username": "leonardoblack.net@gmail.com",
        "password": "24021684Leo@"
    }
    response = requests.post(f"{URL}{url_path}", data=data)
    return json.loads(response.text)['token']


def listar_veiculos():
    response = requests.get(f"{URL}{ESTACIONAMENTO_PATH}", auth=AUTH)
    return response.text


def ver_veiculo_estacionado(placa):
    response = requests.get(f"{URL}{ESTACIONAMENTO_PATH}{placa}", auth=AUTH)
    if response.status_code == 200:
        response = json.loads(response.text)
        return response
    else:
        return False


def cadastrar_veiculo_estacionado(vaga, placa, entrada):
    data = {
        "vaga": vaga,
        "placa": placa,
        "entrada": entrada
    }
    response = requests.post(f"{URL}{ESTACIONAMENTO_PATH}", data=data, auth=AUTH)
    response_text = response.text
    response_status = response.status_code
    return response_text, response_status


def alterar_veiculo_estacionado(placa, saida, entrada=None):
    veiculo_estacionado = ver_veiculo_estacionado(placa)
    if veiculo_estacionado and isinstance(veiculo_estacionado, dict):
        if veiculo_estacionado['status'] == 'ok':
            veiculo_id = veiculo_estacionado['veiculo_estacionado']['id']
            data = {
                "id": veiculo_id,
                "placa": placa,
                "saida": saida,
            }
            if entrada:
                data["entrada"] = entrada
            response = requests.patch(f"{URL}{ESTACIONAMENTO_PATH}{placa}/", data=data, auth=AUTH)
            response_text = response.text
            response_status = response.status_code
            return response_text, response_status
        else:
            return veiculo_estacionado
    else:
        response = {
            "mensagem": "erro",
            "status": "erro"
        }
        return response


vaga = "TN3"
placa = "AAA-0000"
entrada = pegar_data_hora_atual()[2]
saida = pegar_data_hora_atual()[2]
# print(cadastrar_veiculo_estacionado(vaga=vaga, placa="AAA-0200", entrada=entrada))
