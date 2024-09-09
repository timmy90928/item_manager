from flask import Flask,render_template,request,url_for,redirect,make_response,session,abort,send_from_directory
from utils.db import database
from utils.utils import now_time,convert_size,datetime,copy_file,sha,timedelta
from os import getcwd,path,makedirs,listdir,stat,remove
from time import time
from platform import system,node
from utils.web import process_db, check_file, LoginManager, User, login_user, logout_user, login_required
    
# from utils.web import set_cookie,get_cookie
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user # https://ithelp.ithome.com.tw/articles/10328420


app = Flask("Key Manager")
app.secret_key = '92644cb198bc1416d96563067f306ba738bc11750e0f163017e8ddfb8f2d71a6' # ailab120
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Set the maximum upload file size to 16MB.
app.config['UPLOAD_FOLDER'] = path.join(getcwd(), 'writable') # Define the address of the upload folder.
app.config['SERVER_RUN_TIME'] = now_time()
app.config['ITEM_MANAGER_VERSION'] = '1.0.0 beta'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=1)

db=database('./writable/item_manager.db')
pdb = process_db(db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

clients = {}

@app.before_request
def track_connection() -> None:
    """Tracks all the current clients (by IP) and stores them in the set clients."""
    ip = request.remote_addr
    clients[ip] = time()

@app.teardown_request
def remove_client(exc=None):
    """Removes the client from the set clients when the request is finished."""
    for ip, timestamp in list(clients.items()):
        if time() - timestamp > 300:  # 5 minutes
            del clients[ip]

@app.context_processor
def inject_global_vars():
    return {
        'site_header_title': '國立中正大學 通訊工程學系',
    }
@app.route('/alert/<message>', methods=['GET'])
def alert(message: str) -> None:
    """Prints an alert message to the terminal."""
    return render_template('alert.html', message=message)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    Handles an upload request by saving the file to the configured upload folder.
    """
    if request.method == 'POST':
        try: file = check_file(request)
        except AssertionError as e: return str(e), 500
        if file.filename == 'item_manager.db':
            copy_file(f'./writable/item_manager_{now_time().replace("-","_").replace(" ","_").replace(":","_")}.db')
        file.save(path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return redirect(url_for('upload'))

    data = []
    files = listdir(app.config['UPLOAD_FOLDER'])

    def time_convert(timestamp ):return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    for file in files:
        file_info = stat(path.join(app.config['UPLOAD_FOLDER'], file))
        data.append([file,convert_size(file_info.st_size),time_convert(file_info.st_atime),time_convert(file_info.st_mtime),time_convert(file_info.st_ctime)]) # 檔案名稱、檔案大小、上次存取時間、上次修改時間、建立時間
    return render_template('admin/upload.html', files=data)

@app.route("/download/<filename>")
def download(filename: str):
    """Handles a download request by sending the file from the configured upload folder."""
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

@app.route("/delete_file/<filename>")
def delete_file(filename: str):
    """Handles a delete request by removing the specified file from the upload folder."""
    file_path = path.join(app.config["UPLOAD_FOLDER"], filename)
    if filename == 'item_manager.db':
        return redirect(url_for('alert',message='無法刪除預設檔案'))
    if path.isfile(file_path):
        try:
            remove(file_path)
            return redirect(url_for('upload'))
        except Exception as e:
            return str(e), 500
    else:
        return "File not found", 404
    
@app.route("/")
def index():
    table_name = 'item'
    item = db.get_col(table_name, '*')
    return render_template('/admin/item_list.html', items=item,title='物品管理系統')

@login_manager.user_loader
def load_user(user_id):return User(user_id)
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        verify = db.get_row('account', ['name',username],'password,permissions')[0]

        if  sha(password) == verify[0] and verify[1] == 'admin':
            user = User(username)
            login_user(user)
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('alert',message='帳號密碼錯誤'))
    return render_template('login.html')
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route("/server_info")
@login_required
def server_info():
    data = {
        '伺服器名稱': node(),
        '伺服器系統': system(), 
        '伺服器版本': app.config['ITEM_MANAGER_VERSION'],
        '伺服器啟動時間': app.config['SERVER_RUN_TIME'],
        '目前連線數':len(clients),
        '目前連線IP': str('、'.join(clients)),
    }
    return render_template('admin/server_info.html',data=data)

@app.route("/show/<table_name>")
@login_required
def show(table_name):
    return render_template('show.html',name=table_name,datas=db.get_col(table_name,'*'),heads=db.get_head(table_name))

@app.route("/admin")
@login_required
def admin():
    return render_template('/admin/main_page.html')

@app.route("/item/<page>")
@login_required
def item(page):
    match page:
        case 'add':
            return render_template('/admin/add_item.html')
        case 'manager':
            table_name = 'item'
            item = db.get_col(table_name, '*')
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
            return render_template('/admin/item_list.html', items=formatted_items,title='物品清單')
        case 'condition':
            table_name = 'item_record'
            item_condition = db.get_col(table_name, '*')
            # 確保數據格式對應表格標題
            formatted_items = []
            for item in item_condition:
                formatted_items.append([
                    item[0],  # ID
                    item[1],  # 學生證卡號
                    item[2],  # 財產編號
                    item[3],  # 借出狀況
                    item[4],  # 歸還狀況
                    item[5],  # 備註
                ])
            return render_template('/admin/item_condition.html', items=item_condition)
        case _:
            pass

@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    return render_template('/admin/search_history.html')

@app.route("/search_results", methods=['POST'])
@login_required
def search_results():
    borrow  = f"%{request.form.get('borrowDate')}%" if request.form.get('borrowDate') else "%"
    _return = f"%{request.form.get('returnDate')}%" if request.form.get('returnDate') else "%"
    person  = f"%{request.form.get('studentId')}%" if request.form.get('studentId') else "%"
    item    = f"%{request.form.get('propertyNumber')}%" if request.form.get('propertyNumber') else "%"
    note    = f"%{request.form.get('note')}%" if request.form.get('note') else "%"
    
    search = {
        'borrow': borrow,
        'return': _return,
        'person': person,
        'item': item,
        'note': note
    }
    datas = db.get_col('item_record', '*', search)
    return render_template('/admin/search_results.html', datas=datas)

@app.route("/sheet/<item_id>/<method>",methods=['GET'])
def sheet(item_id,method):
    assert 'return' in method or 'borrow' in method, 'Invalid method'
    item = db.get_row('item', ['id',item_id], 'item,number,borrow,sheet')[0]
    new_id = int(db.get_row('sqlite_sequence', ['name','item_record'], 'seq')[0][0]) + 1
    record = db.get_row('item_record', ['id',item[3]], 'borrow,note')[0] if method == 'return' else ['','']

    datas = {
        'item_id': item_id,
        'item_name': item[0],
        'item_number': item[1],
        'borrow_date': now_time() if method == 'borrow' else record[0],
        'return_date': now_time() if method == 'return' else '',
        'new_id': new_id if method == 'borrow' else 'return',
    }
    return render_template('/sheet.html',datas=datas)

@app.route("/process_database/<method>",methods=['POST','GET'])
def process_database(method):
    match method:
        case 'delete_item':
            assert request.method == 'POST', 'Only POST requests are accepted'
            return pdb.delete_item(request.args.get('item_id'))
        case 'additem': 
            assert request.method == 'POST', 'Only POST requests are accepted'
            item_name = request.form['itemName'].strip()
            item_number = request.form['itemNumber']
            note = request.form.get('note', '')
            return pdb.additem(item_name, item_number, note)
        case 'borrow_and_return':
            assert request.method == 'POST', 'Only POST requests are accepted'
            if request.form.get('new_id') == 'return':
                sheet_id = db.get_row('item',['id',request.form.get('item_id')],'sheet')[0][0]
                person = db.get_row('item_record',['id',sheet_id],'person')[0][0]

                if person != request.form.get('person'):
                    return redirect(url_for('alert', message="借出人與歸還人不符"))
                
                try:
                    verifier_name= db.get_row('verifier',['ID',request.form.get('verifier')],'name')[0][0]
                except IndexError:
                    return redirect(url_for('alert', message="驗證人員錯誤"))

                db.revise('item_record',['id',sheet_id],['return',now_time()])
                db.revise('item_record',['id',sheet_id],['r_verifier',verifier_name])
                db.revise('item',['id',request.form.get('item_id')],['borrow',''])
                return redirect('/')
            else:
                try:
                    verifier_name= db.get_row('verifier',['ID',request.form.get('verifier')],'name')[0][0]
                except IndexError:
                    return redirect(url_for('alert', message="驗證人員錯誤"))
                
                db.add('item_record', 'person,item,borrow,b_verifier,note', f"'{request.form.get('person')}','{request.form.get('item_id')}','{now_time()}','{verifier_name}','{request.form.get('note')}'")
                db.revise('item',['id',request.form.get('item_id')],['borrow','已借出'])
                db.revise('item',['id',request.form.get('item_id')],['sheet',request.form.get('new_id')])
                return redirect('/')
        case _:
            pass
  
if __name__ == "__main__":
    app.run(host="0.0.0.0",port="429")