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
    table_name = 'item'
    item = db.get_col(table_name, '*', ['id', '%'])
    # 確保數據格式對應表格標題
    formatted_items = []
    for item in item:
        formatted_items.append([
            item[0],  # ID
            item[1],  # 物品名稱
            item[2],  # 財產編號
            item[3],  # 借出狀況
            item[4]   # 備註
        ])
    return render_template('/admin/item_list.html', items=formatted_items)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port="429")