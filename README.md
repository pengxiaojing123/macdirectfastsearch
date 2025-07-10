# macdirectfastsearch
mac下搜索文件一直让我头疼，又慢又不好用，写了个工具解决。 大概原理是扫描硬件建立一次缓存数据库（通常建立一次就够用比较久），以后查找在数据库中找，找到后给出文件所在目录。

# 1. 刷新文件缓存 
python3 main.py refresh

# 2. 搜索文件
python3 main.py search "test.mp4"      # 精确搜索
python3 main.py search "*st.mp4"       # 模糊匹配
python3 main.py search "*.mp4"         # 查找所有mp4文件
