import requests
from flask import Flask, jsonify

app = Flask(__name__)

URL_JAVA = "http://localhost:8080/nota-fiscal/1"

@app.route("/gerar-nf", methods=["GET"])
def gerar_nf():
    nf = requests.get(URL_JAVA).json()

    # Aqui você faria o envio pro Bling
    print("NF recebida do Java:")
    print(nf)

    return jsonify(nf)

if __name__ == "__main__":
    app.run(port=5000)
