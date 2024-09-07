from flask import Flask,render_template,request,url_for,redirect,make_response,session,abort,send_from_directory
from flask import jsonify, request
from utils.db import database
from utils.utils import now_time,convert_size,datetime
from os import getcwd,path,makedirs,listdir,stat,remove
from time import time
from platform import system,node
    
# from utils.web import set_cookie,get_cookie
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user # https://ithelp.ithome.com.tw/articles/10328420


app = Flask("Key Manager")
app.secret_key = 'ailab120'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Set the maximum upload file size to 16MB.
app.config['UPLOAD_FOLDER'] = path.join(getcwd(), 'writable') # Define the address of the upload folder.
app.config['SERVER_RUN_TIME'] = now_time()

db=database('./writable/item_manager.db')
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
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            file.save(path.join(app.config['UPLOAD_FOLDER'], file.filename))
            return redirect(url_for('upload'))

    data = []
    files = listdir(app.config['UPLOAD_FOLDER'])

    def time_convert(timestamp ):return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    for file in files:
        file_info = stat(path.join(app.config['UPLOAD_FOLDER'], file))
        data.append([file,convert_size(file_info.st_size),time_convert(file_info.st_atime),time_convert(file_info.st_mtime),time_convert(file_info.st_ctime)]) # 檔案名稱、檔案大小、上次存取時間、上次修改時間、建立時間
    return render_template('upload.html', files=data)

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
            # remove(file_path)
            return redirect(url_for('upload'))
        except Exception as e:
            return str(e), 500
    else:
        return "File not found", 404
    
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/server_info")
def server_info():
    data = {
        '伺服器名稱': node(),
        '伺服器系統': system(), 
        '伺服器啟動時間': app.config['SERVER_RUN_TIME'],
        '目前連線數':len(clients),
        '目前連線IP': str('、'.join(clients)),
    }
    return render_template('server_info.html',data=data)
    return f"目前有 {len(clients)} 個連線: {str('、'.join(clients))} (Server Start Time: {app.config['SERVER_RUN_TIME']})"

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

@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    try:
        result = db.delete('item', ['id', str(item_id)])
        
        if result:
            return jsonify({"success": True, "message": "Item deleted successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Deletion cancelled or item not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
@app.route("/add_item")
def add_item():
    return render_template('/admin/add_item.html')
    
@app.route('/additem', methods=['POST'])
def additem():
    try:
        item_name = request.form['itemName'].strip()
        item_number = request.form['itemNumber']
        note = request.form.get('note', '')
        
        if not item_name:
            return jsonify({"success": False, "message": "物品名稱不能為空"}), 400
        
        # 建立 col_name 和 value 字符串
        col_name = 'item, number, borrow, note'
        value = f"{repr(item_name)}, {repr(item_number)}, NULL, {repr(note)}"
        
        db.add('item', col_name, value)
        
        return jsonify({"success": True, "message": "物品新增成功"}), 200
    except Exception as e:
        print(f"新增物品時發生錯誤: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500
    
@app.route("/database/<method>")
def process_database(method):
    assert request.method == 'POST', 'Only POST requests are accepted'
    if request.method == 'POST':
        print(request.form)
        return redirect(url_for('admin'))
    return render_template('admin/database.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0",port="429")