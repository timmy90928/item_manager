from flask import Flask,render_template,request,url_for
from utils.db import database

db=database('./writable/item_manager.db')
app = Flask("Key Manager")

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/show/<table_name>")
def show(table_name):
    return render_template('show.html',name=table_name,datas=db.get_col(table_name,'*',['id','%']),heads=db.get_head(table_name))

if __name__ == "__main__":
    app.run(host="0.0.0.0",port="120")