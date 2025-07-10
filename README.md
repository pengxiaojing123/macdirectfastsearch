# Mac文件快速检索工具


mac下搜索文件一直让我头疼，又慢又不好用，写了个工具解决。 大概原理是扫描硬件建立一次缓存数据库（通常建立一次就够用比较久），以后查找在数据库中找，找到后给出文件所在目录。一个高效的Mac文件搜索工具，支持文件缓存和模糊匹配查找。

## 功能特性

- 🚀 **快速检索**: 使用SQLite数据库缓存文件信息，搜索速度极快
- 🔍 **模糊匹配**: 支持通配符搜索（`*` 和 `?`）
- 📊 **详细信息**: 显示文件路径、大小、修改时间
- 🛡️ **权限安全**: 自动跳过无权限访问的文件
- 💾 **本地存储**: 所有数据存储在本地SQLite数据库中

## 安装和运行

本工具使用Python 3标准库开发，无需额外依赖。

```bash
# 克隆或下载项目
cd macdirector

# 直接运行
python3 main.py --help
```

## 使用方法

### 1. 刷新文件缓存

首次使用需要先建立文件索引：

```bash
# 刷新默认路径（用户目录、应用程序目录）
python3 main.py refresh

# 刷新指定路径
python3 main.py refresh --paths /Users/username/Documents /Applications

# 刷新整个系统（需要较长时间）
python3 main.py refresh --paths /
```

### 2. 搜索文件

支持多种搜索模式：

```bash
# 精确文件名搜索
python3 main.py search test.mp4

# 部分文件名搜索
python3 main.py search mp4

# 模糊匹配搜索（使用通配符）
python3 main.py search "*st.mp4"
python3 main.py search "test.*"
python3 main.py search "*.pdf"

# 限制搜索结果数量
python3 main.py search "*.jpg" --limit 20
```



## 搜索语法

### 通配符支持

- `*` : 匹配任意字符序列
- `?` : 匹配单个字符

### 搜索示例

| 搜索模式 | 匹配示例 |
|---------|---------|
| `test.mp4` | 精确匹配 test.mp4 |
| `*test*` | 包含 "test" 的所有文件 |
| `*.mp4` | 所有 mp4 文件 |
| `test.*` | 以 "test" 开头的所有文件 |
| `*st.mp4` | 以 "st.mp4" 结尾的文件 |
| `?.txt` | 单字符名称的 txt 文件 |

## 性能说明

- **首次索引**: 根据文件数量，可能需要几分钟到十几分钟
- **搜索速度**: 通常在毫秒级完成
- **存储空间**: 每100万文件约占用100-200MB磁盘空间
- **内存使用**: 运行时内存占用较小

## 文件存储

- 数据库文件: `file_index.db` （在当前目录）
- 包含信息: 文件名、完整路径、文件大小、修改时间、索引时间

## 注意事项

1. **权限**: 某些系统目录可能需要管理员权限
2. **性能**: 首次索引大量文件时建议在空闲时进行
3. **更新**: 文件系统变化后需要重新运行 refresh 命令
4. **存储**: 确保有足够的磁盘空间存储数据库文件

## 常见用法示例

```bash
# 查找所有图片文件
python3 main.py search "*.jpg"
python3 main.py search "*.png"

# 查找配置文件
python3 main.py search "*.config"
python3 main.py search "*.plist"

# 查找特定应用
python3 main.py search "*.app"

# 查找文档
python3 main.py search "*.pdf"
python3 main.py search "*.docx"

# 查找项目文件
python3 main.py search "package.json"
python3 main.py search "*.py"
```

## 故障排除

如果遇到问题：

1. 检查Python版本（需要Python 3.6+）
2. 确保有足够的磁盘空间
3. 检查文件权限
4. 尝试删除 `file_index.db` 重新索引

## 许可证

本项目采用 MIT 许可证。 
