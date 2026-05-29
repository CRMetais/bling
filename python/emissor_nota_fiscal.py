import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOKEN_BLING = "SEU_TOKEN_AQUI"


def transformar_para_bling(nf):
    fornecedor = nf["fornecedor"]

    return {
        "contato": {
            "nome": fornecedor["nome"],
            "tipoPessoa": "J" if len(fornecedor["documento"]) > 11 else "F",
            "numeroDocumento": fornecedor["documento"],
            "endereco": {
                "logradouro": fornecedor["endereco"]["logradouro"],
                "numero": fornecedor["endereco"]["numero"],
                "bairro": fornecedor["endereco"]["bairro"],
                "cidade": fornecedor["endereco"]["cidade"],
                "uf": fornecedor["endereco"]["estado"],
                "cep": fornecedor["endereco"]["cep"],
                "pais": "BR"
            }
        },

        "tipo": "E" if nf["tipoNota"] == "ENTRADA" else "S",

        "numeroDocumento": "1",

        "dataOperacao": nf["dataEmissao"],

        "itens": [
            {
                "codigo": str(item["idProduto"]),
                "descricao": item["descricao"],
                "quantidade": item["quantidade"],
                "valor": item["valorUnitario"],
                "unidade": "UN"
            }
            for item in nf["itens"]
        ],

        "valor": nf["valorTotal"]
    }


def enviar_para_bling(nf):
    try:
        bling_json = transformar_para_bling(nf)

        url = "https://api.bling.com.br/Api/v3/nfe"

        headers = {
            "Authorization": f"Bearer {TOKEN_BLING}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=bling_json, headers=headers)

        print("\n🚀 JSON enviado pro Bling:")
        print(bling_json)

        print("\n📨 Resposta do Bling:")
        print(response.status_code, response.text)

        return {
            "status": response.status_code,
            "resposta": response.text
        }

    except Exception as e:
        return {"erro": str(e)}


@app.route("/enviar-bling", methods=["POST"])
def gerar_nf():
    nf = request.json

    resultado = enviar_para_bling(nf)

    return jsonify(resultado)


if __name__ == "__main__":
    app.run(port=5001)