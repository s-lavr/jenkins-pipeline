from flask import Flask, render_template
import os
app = Flask(__name__)

@app.route('/')
def hello():
    image_tag = os.environ.get('FLASKVERSION')
    host = os.environ.get('HOSTNAME')
    return render_template('index.html', image_tag=image_tag, host=host)

@app.route('/test')
def test():
    return "<h1>Changed line to this</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
