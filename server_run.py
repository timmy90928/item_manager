from flask import Flask,render_template,request,url_for,redirect,make_response,session,abort,send_from_directory
from utils.db import database
from utils.utils import now_time
from os import getcwd,path,makedirs,listdir
# from utils.web import set_cookie,get_cookie
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user # https://ithelp.ithome.com.tw/articles/10328420


app = Flask("Key Manager")
app.secret_key = 'ailab120'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Set the maximum upload file size to 16MB.
app.config['UPLOAD_FOLDER'] = path.join(getcwd(), 'writable') # Define the address of the upload folder.

db=database('./writable/item_manager.db')
clients = set()

@app.before_request
def track_connection() -> None:
    """Tracks all the current clients (by IP) and stores them in the set clients."""
    ip = request.remote_addr
    clients.add(ip)

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
            return redirect(url_for('upload'))  # 上傳後重定向刷新頁面

    # 列出上傳資料夾中的所有文件
    files = listdir(app.config['UPLOAD_FOLDER'])
    return render_template('upload.html', files=files)

@app.route("/download/<filename>")
def download(filename: str):
    """Handles a download request by sending the file from the configured upload folder."""
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/clients")
def client():
    return f"目前有 {len(clients)} 個連線: {str('、'.join(clients))}"

@app.route("/show/<table_name>")
def show(table_name):
    return render_template('show.html',name=table_name,datas=db.get_col(table_name,'*'),heads=db.get_head(table_name))

@app.route("/admin")
def admin():
    return render_template('/admin/main_page.html')

@app.route("/itemlist")
def itemlist():
    return render_template('/admin/item_list.html')

@app.route("/database/<method>")
def process_database(method):
    assert request.method == 'POST', 'Only POST requests are accepted'
    if request.method == 'POST':
        print(request.form)
        return redirect(url_for('admin'))
    return render_template('admin/database.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0",port="429")