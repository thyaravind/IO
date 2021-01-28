from flask import Flask


app = Flask(__name__)

@app.route("/")
def hello():
    return "Hi from the Flask App"

if (__name__ == '__main__'):
    app.run()