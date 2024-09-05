from flask import Flask,render_template,request,url_for
from utils.db import database

db=database('./writable/item_manager.db')
app = Flask("Key Manager")

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0",port="120")