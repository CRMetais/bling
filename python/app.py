import requests
import webbrowser
from flask import Flask, jsonify

app = Flask(__name__)

URL_JAVA = "http://localhost:8080/nota-fiscal/1"

@app.route("/gerar-nf", methods=["GET"])
def gerar_nf():
    nf = requests.get(URL_JAVA).json()

    print("NF recebida do Java:")
    print(nf)

    return jsonify(nf)

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000/gerar-nf")
    app.run(port=5000)
