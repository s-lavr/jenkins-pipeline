from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "<h1> New message to test correct deploying of new chart </h1>"

@app.route('/test')
def test():
    return "<h1>Changed line to this</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
