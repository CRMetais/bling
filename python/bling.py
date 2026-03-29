import requests
from flask import Flask, jsonify

app = Flask(__name__)

URL_JAVA = "http://localhost:8080/nota-fiscal/1"
TOKEN_BLING = "SEU_TOKEN_AQUI"


def enviar_para_bling(nf_java):
    try:
        bling_json = {
            "numero": 1,
            "dataEmissao": nf_java["dataEmissao"],
            "tipo": 1 if nf_java["tipoNota"] == "SAÍDA" else 0,

            "cliente": {
                "nome": nf_java["fornecedor"]["nome"],
                "tipoPessoa": "J" if len(nf_java["fornecedor"]["documento"]) > 11 else "F",
                "numeroDocumento": nf_java["fornecedor"]["documento"],
                "endereco": {
                    "logradouro": nf_java["fornecedor"]["endereco"]["logradouro"],
                    "numero": nf_java["fornecedor"]["endereco"]["numero"],
                    "bairro": nf_java["fornecedor"]["endereco"]["bairro"],
                    "cidade": nf_java["fornecedor"]["endereco"]["cidade"],
                    "uf": nf_java["fornecedor"]["endereco"]["estado"],
                    "cep": nf_java["fornecedor"]["endereco"]["cep"]
                }
            },

            "itens": [
                {
                    "descricao": item["descricao"],
                    "quantidade": item["quantidade"],
                    "valor": item["valorUnitario"]
                }
                for item in nf_java["itens"]
            ]
        }

        url = "https://api.bling.com.br/Api/v3/nfe"

        headers = {
            "Authorization": f"Bearer {TOKEN_BLING}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=bling_json, headers=headers)

        return {
            "status": response.status_code,
            "resposta": response.text
        }

    except Exception as e:
        return {"erro": str(e)}


@app.route("/gerar-nf", methods=["GET"])
def gerar_nf():
    nf = requests.get(URL_JAVA).json()

    resultado = enviar_para_bling(nf)

    return jsonify(resultado)


if __name__ == "__main__":
    app.run(port=5001)