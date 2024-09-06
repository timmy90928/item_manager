from flask import Flask,render_template,request,url_for,redirect,make_response,session,abort
from utils.db import database
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user # https://ithelp.ithome.com.tw/articles/10328420

db=database('./writable/item_manager.db')
app = Flask("Key Manager")

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/show/<table_name>")
def show(table_name):
    return render_template('show.html',name=table_name,datas=db.get_col(table_name,'*'),heads=db.get_head(table_name))

@app.route("/admin")
def admin():
    return render_template('/admin/main_page.html')

@app.route("/itemlist")
def itemlist():
    return render_template('/admin/item_list.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0",port="429")