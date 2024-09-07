from flask import jsonify, request
from utils.db import database

def return_page(success:str, message:str, state:int):
    return jsonify({"success": success, "message": message}), state

class process_db:
    def __init__(self, db:database):
        self.db = db
    def delete_item(self,item_id):
        try:
            result = self.db.delete('item', ['id', str(item_id)])
            
            if result:
                return return_page(True, '物品刪除成功', 200) #jsonify({"success": True, "message": "Item deleted successfully"}), 200
            else:
                return return_page(False, '物品刪除失敗', 404) #jsonify({"success": False, "message": "Deletion cancelled or item not found"}), 404
        except Exception as e:
            return return_page(False, str(e), 500) # jsonify({"success": False, "message": str(e)}), 500
        
    def additem(self, item_name, item_number, note):
        try:
            if not item_name:
                return return_page(False, '物品名稱不能為空', 400) # jsonify({"success": False, "message": "物品名稱不能為空"}), 400
            
            # 建立 col_name 和 value 字符串
            col_name = 'item, number, borrow, note'
            value = f"{repr(item_name)}, {repr(item_number)}, NULL, {repr(note)}"
            
            self.db.add('item', col_name, value)
            
            return return_page(True, '物品新增成功', 200) # jsonify({"success": True, "message": "物品新增成功"}), 200
        except Exception as e:
            print(f"新增物品時發生錯誤: {str(e)}")
            return return_page(False, str(e), 500) # jsonify({"success": False, "message": str(e)}), 500