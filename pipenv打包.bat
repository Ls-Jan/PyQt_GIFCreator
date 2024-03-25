
pipenv shell

pipenv install pyinstaller --dev
pipenv install pillow --dev
pipenv install opencv-python --dev
pipenv install numpy --dev
pipenv install PyQt5 --dev
pipenv install psutil --dev
pipenv install XJ-1.0-py3-none-any.whl --dev

pyinstaller -w -D --clean --add-data="./Icons;./Icons" -i="./Icons/Logo.png" Main.py
pause

: pyinstaller参数：https://blog.csdn.net/lipenghandsome/article/details/120137667
: --add-data指定额外资源文件：https://blog.csdn.net/dou3516/article/details/125533985
: --clean: 在构建之前清理PyInstaller缓存并删除临时文件
: -D: 创建包含可执行文件的单文件夹包，同时会有一大堆依赖的 dll 文件，这是默认选项
: -F: 只生成一个 .exe 文件，如果项目比较小的话可以用这个，但比较大的话就不推荐
: -w:不要console(取消类似于cmd的黑框框)
: -i:后面接图标地址（图标一定要是标准的ico格式）







