from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello world"

@app.route("/meet")
def meet():
    return "Nice to meet you"

if __name__ == '__main__':
    app.run(host='192.168.0.4', port=5488)
