from datetime import timedelta,datetime,timedelta
from shutil import copy2, rmtree, ignore_patterns, copytree
from os import environ,mkdir
from os.path import isfile, isdir, split as path_split,join
from base64 import b64encode,b64decode
from typing import Union
import math
from hashlib import sha3_256
def sha(text:str) -> str:
    return sha3_256(text.encode()).hexdigest()

def read_card_data() -> str:
    """
    Reads card data from the card reader.
    """
    input("請刷卡...")
    return input()

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

def copy(src:str, dst:str, ignore:list = [], return_format:str = '{mode}: {src} -> {dst}') -> str:
    """
    Copies a file from the `src` path to the `dst` path.

    :param src: The source file path. Must be a Path object.
    :param dst: The destination file path. Must be a Path object.

    >>> copy()
    Traceback (most recent call last):
    ...
    TypeError: copy() missing 2 required positional arguments: 'src' and 'dst'
    """
    if not src or not dst:
        raise ValueError("Both src and dst must be non-empty")
    try:
        if isdir(src):
            mode = 'dir'
            dst = join(dst,path_split(src)[-1])
            copytree(src, dst, ignore=ignore_patterns(*ignore), dirs_exist_ok=True)
        elif isfile(src):
            mode = 'file'
            copy2(src, dst)
        else:
            raise ValueError(f"{src} is neither a file nor a directory")
        _format = {'src': src, 'dst': dst, 'mode':mode}
        return return_format.format(**_format)
    except OSError as e:
        raise OSError(f"Error copying file from {src} to {dst}: {e}") from e

class base64:
    """
    Base64 encoding and decoding.

    ## Example

    ```
    value_str = 'abcde'
    value_list = ['ac','cd']
    b64_str = base64(value_str).encode()
    b64_list = base64(value_list).encode()

    print(b64_str)      # YWJjZGU=
    print(b64_list)     # YWMsY2Q=
    print(base64(b64_str).decode())     # abcde
    print(base64(b64_list).decode())    # ['ac', 'cd']
    ```
    """
    # __slots__ = ("data",)

    def __init__(self, data: Union[str,list]) -> None:
        self.data = str(','.join(data))  if isinstance(data, list) else str(data)

    def encode(self) -> str:
        """Encode the stored data to a base64 string."""
        return b64encode(self.data.encode()).decode("utf-8")
    def decode(self) -> Union[str, list[str]]:
        """
        Decode the stored base64 string to the original string.

        Returns a list of strings if the original data was a list, otherwise a single string.
        """
        decoded_string = b64decode(self.data).decode()
        return decoded_string.split(",") if "," in decoded_string else decoded_string
        
def get_data_path(dir_name:str, copy_dir_or_file:list, root_dir:str = None) -> Union[bool, str]:
    """
    Return the path to the directory for storing application data, or a tuple of a boolean and the path.
    
    >>> exists,program_data_path = get_data_path('Intel')

    :param dir_name: The name of the directory to create.
    :param copy_dir_or_file: A list of files/directories to copy into the created directory.
    :param replace: Whether to replace the directory if it already exists.
    :return: A tuple of a boolean and the path to the created directory.If the directory already existed, the boolean will be True.

    """
    program_data_path = join(environ.get('ProgramData', '/var/lib'), dir_name)
    no_exists = not isdir(program_data_path)
    if no_exists:
        mkdir(program_data_path)
        for dir_or_file in copy_dir_or_file:
            dir_or_file = join(root_dir, dir_or_file) if root_dir else dir_or_file
            c =  copy(dir_or_file, program_data_path)
            # print(c)
        return False,program_data_path
    else:
        return True,program_data_path
    
def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"