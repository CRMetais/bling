from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app, supports_credentials=True)

def mapear_para_bling(nf):
    f = nf["fornecedor"]
    e = f["endereco"]

    tipo = "0" if nf.get("tipoNota") == "ENTRADA" else "1"

    contato = {
        "nome":            f["nome"],
        "tipoPessoa":      f["tipoPessoa"],
        "numeroDocumento": f["documento"],
        "contribuinte":    1 if (f["tipoPessoa"] == "J" and f.get("ie", "")) else 2,
        "ie":              f.get("ie", ""),
        "rg":              "",
        "telefone":        f.get("telefone", ""),
        "email":           "",
        "endereco": {
            "endereco":    e["logradouro"],
            "numero":      e["numero"],
            "complemento": e.get("complemento", ""),
            "bairro":      e["bairro"],
            "municipio":   e["cidade"],
            "cep":         e["cep"],
            "uf":          e["estado"],
            "pais":        ""
        }
    }

    itens = []
    for item in nf["itens"]:
        itens.append({
            "codigo":      str(item["idProduto"]),
            "descricao":   item["descricao"],
            "unidade":     item["unidade"],
            "quantidade":  str(item["quantidade"]),
            "valor":       str(item["valorUnitario"])
        })

    payload_bling = {
        "tipo":         tipo,
        "situacao":     6,
        "dataOperacao": nf["dataEmissao"],
        "contato":      contato,
        "itens":        itens
    }

    return payload_bling


@app.route("/gerar-nf", methods=["POST"])
def receber_nf():
    try:
        nf = request.get_json()
        print("NF recebida do Java:")
        print(nf)
        payload_bling = mapear_para_bling(nf)
        print("\nPayload montado para o Bling:")
        print(json.dumps(payload_bling, indent=2, ensure_ascii=False))
        return jsonify({
            "status": "ok",
            "mensagem": "NF mapeada com sucesso",
            "payload_bling": payload_bling
        })
    except Exception as e:
        print("ERRO:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000)


# import requests
# import json
# import os
# from datetime import datetime, timedelta
# from base64 import b64encode
# from flask import Flask, jsonify, request, redirect
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app, supports_credentials=True)

# # Configurações do Bling
# CLIENT_ID     = "3a241b817839f9d8a9f9813636e0d82f61750766"
# CLIENT_SECRET = "37d5e3369038caebf32589567b5832623f9a3e408bdb643b1fdf99017ddb"
# REDIRECT_URI  = "http://127.0.0.1:5000/callback"
# TOKEN_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bling_token.json")

# # Token
# def salvar_token(token_data):
#     token_data["salvo_em"] = datetime.now().isoformat()
#     with open(TOKEN_FILE, "w") as f:
#         json.dump(token_data, f)
#     print("Token salvo em", TOKEN_FILE)

# def carregar_token():
#     if not os.path.exists(TOKEN_FILE):
#         return None
#     with open(TOKEN_FILE, "r") as f:
#         return json.load(f)

# def token_expirado(token_data):
#     salvo_em   = datetime.fromisoformat(token_data.get("salvo_em", "2000-01-01"))
#     expires_in = token_data.get("expires_in", 21600)
#     return datetime.now() >= salvo_em + timedelta(seconds=expires_in - 300)

# def get_access_token():
#     token_data = carregar_token()
#     if not token_data:
#         return None
#     if token_expirado(token_data):
#         print("Token expirado, renovando...")
#         token_data = renovar_token(token_data.get("refresh_token"))
#         if not token_data:
#             return None
#     return token_data.get("access_token")

# def renovar_token(refresh_token):
#     credentials = b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
#     response = requests.post(
#         "https://bling.com.br/Api/v3/oauth/token",
#         json={"grant_type": "refresh_token", "refresh_token": refresh_token},
#         headers={"Authorization": f"Basic {credentials}", "Content-Type": "application/json"}
#     )
#     print("Renovação token:", response.status_code, response.text)
#     if response.status_code == 200:
#         token_data = response.json()
#         salvar_token(token_data)
#         return token_data
#     return None

# def obter_token(code):
#     credentials = b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
#     response = requests.post(
#         "https://bling.com.br/Api/v3/oauth/token",
#         json={"grant_type": "authorization_code", "redirect_uri": REDIRECT_URI, "code": code},
#         headers={"Authorization": f"Basic {credentials}", "Content-Type": "application/json"}
#     )
#     print("Resposta token:", response.status_code, response.text)
#     if response.status_code == 200:
#         return response.json()
#     return None

# # Mapeamento dos campos pro bling
# def mapear_para_bling(nf):
#     f = nf["fornecedor"]
#     e = f["endereco"]

#     tipo        = "0" if nf.get("tipoNota") == "ENTRADA" else "1"
#     is_pj       = f.get("tipoPessoa", "F") == "J"
#     ie          = f.get("ie", "")
#     contribuinte = 1 if (is_pj and ie) else 2
#     consumidor_final = 0 if (is_pj and ie) else 1

#     return {
#         "tipo":            tipo,
#         "consumidorFinal": consumidor_final,
#         "dataOperacao":    nf["dataEmissao"],
#         "naturezaOperacao": tipo,
#         "contato": {
#             "nome":            f["nome"],
#             "tipoPessoa":      f.get("tipoPessoa", "F"),
#             "numeroDocumento": f["documento"],
#             "contribuinte":    contribuinte,
#             "ie":              ie,
#             "rg":              "",
#             "telefone":        f.get("telefone", ""),
#             "email":           f.get("email", ""),
#             "endereco": {
#                 "endereco":    e["logradouro"],
#                 "numero":      e["numero"],
#                 "complemento": e.get("complemento", ""),
#                 "bairro":      e["bairro"],
#                 "municipio":   e["cidade"],
#                 "cep":         e["cep"],
#                 "uf":          e["estado"],
#                 "pais":        ""
#             }
#         },
#         "itens": [
#             {
#                 "codigo":     str(item["idProduto"]),
#                 "descricao":  item["descricao"],
#                 "unidade":    item.get("unidade", "KG"),
#                 "quantidade": str(item["quantidade"]),
#                 "valor":      str(item["valorUnitario"])
#             }
#             for item in nf["itens"]
#         ]
#     }

# # Enviar pro bling
# def enviar_para_bling(nf, token):
#     try:
#         payload = mapear_para_bling(nf)
#         print("\nJSON enviado pro Bling:\n", json.dumps(payload, indent=2, ensure_ascii=False))

#         response = requests.post(
#             "https://api.bling.com.br/Api/v3/nfe",
#             json=payload,
#             headers={
#                 "Authorization": f"Bearer {token}",
#                 "Content-Type":  "application/json"
#             }
#         )
#         print("Resposta Bling:", response.status_code, response.text)
#         return {
#             "status":   response.status_code,
#             "resposta": response.json() if response.content else {}
#         }
#     except Exception as e:
#         return {"erro": str(e)}

# # Rotas
# @app.route("/autorizar")
# def autorizar():
#     url = (
#         f"https://www.bling.com.br/Api/v3/oauth/authorize"
#         f"?response_type=code&client_id={CLIENT_ID}&state=randomstate123"
#     )
#     return redirect(url)

# @app.route("/callback")
# def callback():
#     code = request.args.get("code")
#     if not code:
#         return jsonify({"erro": "Código não recebido"}), 400
#     token_data = obter_token(code)
#     if token_data:
#         salvar_token(token_data)
#         return "<h2>✅ Autorizado com sucesso! Pode fechar esta aba.</h2>"
#     return jsonify({"erro": "Falha ao obter token"}), 500

# @app.route("/gerar-nf", methods=["POST"])
# def receber_nf():
#     try:
#         nf = request.get_json()
#         print("NF recebida do Java:\n", nf)

#         token = get_access_token()
#         if not token:
#             return jsonify({
#                 "status":   "erro",
#                 "mensagem": "Token não configurado. Acesse http://localhost:5000/autorizar primeiro."
#             }), 401

#         resultado = enviar_para_bling(nf, token)
#         return jsonify(resultado)

#     except Exception as e:
#         print("ERRO:", e)
#         return jsonify({"status": "erro", "mensagem": str(e)}), 500

# if __name__ == "__main__":
#     app.run(port=5000, debug=True)