# 📊 DirStats — 项目目录统计工具

> 扫描任意文件夹，输出文件类型分布、大文件排行、代码行数统计。纯 Python 标准库，零依赖。

## 安装

```bash
git clone https://github.com/One1turn/DirStats.git
cd DirStats
```

## 使用

```bash
# 扫描当前目录
python dirstats.py .

# 扫描指定目录
python dirstats.py /path/to/project

# 输出 JSON 格式
python dirstats.py /path/to/project --json

# 排除 node_modules 和 .git
python dirstats.py /path/to/project --exclude node_modules,.git,dist,build

# 只统计代码文件
python dirstats.py /path/to/project --code-only

# 限制大文件排行数量
python dirstats.py /path/to/project --top 20
```

## 输出示例

```
📊 DirStats — 目录统计报告
📂 扫描路径: /home/user/my-project
🕐 扫描时间: 2026-08-19 12:00:00

═══════════════════════════════════════════════
  📁 总览
═══════════════════════════════════════════════
  文件总数: 1,247
  文件夹总数: 83
  总大小: 45.6 MB

📉 文件类型分布 (Top 10):
  .js     ███████████████ 423 files (33.9%)
  .py     ████████        287 files (23.0%)
  .css    ████            156 files (12.5%)
  .json   ██              89 files (7.1%)
  .md     ██              67 files (5.4%)
  ...

🏆 大文件排行 (Top 10):
  1. 3.2 MB  dist/bundle.min.js
  2. 1.8 MB  data/large_dataset.json
  ...

📝 代码行数统计:
  .js    45,231 lines
  .py    12,087 lines
  Total  57,318 lines
═══════════════════════════════════════════════
```

MIT License
