﻿Environment:
- Python 3.6.0
所依赖的包
- Django
- beautifulsoup4
- lxml
- pymysql
- requests


1. 请将~/my_website/my_website/settings.py 中的DATABASES中的用户名与密码改为自己数据库的用户名与密码
2. 在MySQL中建立数据库'web', 并将default character set设为utf8, 否则会出现乱码
3. python ~/my_website/manage.py makemigrations
4. python ~/my_website/manage.py migrate
5. 创建管理员账户: python ~/my_website/manage.py createsuperuser
6. python ~/my_website/manage.py runserver 8000(默认端口, 可以自行转换), 如果出现静态文件如图片等无法加载的问题, 改
用如下命令python ~/my_website/manage.py runserver 8000 --insecure
7. 用管理员账户登陆 localhost:8000/admin并将该管理员的Profile里的Authority改为3
8. 进入 localhost:8000/index 即可
