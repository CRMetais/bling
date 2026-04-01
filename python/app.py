from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app, supports_credentials=True)

URL_JAVA = "http://localhost:8080/nota-fiscal/1"

@app.route("/receber-nf", methods=["POST"])
def receber_nf():
    try:
        nf = request.get_json()

        print("NF recebida:")
        print(nf)

        return jsonify({
            "status": "ok",
            "mensagem": "NF recebida com sucesso"
        })

    except Exception as e:
        print("ERRO:", e)
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500

if __name__ == "__main__":
    app.run(port=5000)
