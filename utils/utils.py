from datetime import timedelta,datetime
from shutil import copy2

def read_card() -> str:
    """
    """
    print("請刷卡...")
    card_data = input()  # Wait for user to swipe card from card reader.
    return card_data
    print(f"讀取到的卡資料：{card_data}")

def msgw(title:str="Title", text:str="contant", style:int=0, time:int=0) -> int:
    """
    ctypes.windll.user32.MessageBoxTimeoutW()

    Styles
    ------
    ```
    0 : OK
    1 : OK | Cancel
    2 : Abort | Retry | Ignore
    3 : Yes | No | Cancel
    4 : Yes | No
    5 : Retry | No 
    6 : Cancel | Try Again | Continue
    ```

    Example
    -------
    ```
    msg=msgw('title','contant',0,1000)  # time (ms)
    print(msg)
    ```
    """
    import ctypes
    # MessageBoxTimeoutW(父窗口句柄,消息內容,標題,按鈕,語言ID,等待時間)
    return ctypes.windll.user32.MessageBoxTimeoutW(0, text, title, style,0,time)

def now_time() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def copy():
    copy2()
