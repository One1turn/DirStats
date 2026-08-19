#!/usr/bin/env python3
"""
📊 DirStats — 项目目录统计工具
扫描文件夹，输出文件类型分布、大文件排行、代码行数统计
"""

import os
import sys
import json
import argparse
from datetime import datetime
from collections import Counter

# 代码文件扩展名
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".cc", ".cxx",
    ".h", ".hpp", ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala",
    ".m", ".mm", ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat",
    ".lua", ".r", ".dart", ".elm", ".ex", ".exs", ".erl", ".clj", ".cljs",
    ".lisp", ".hs", ".ml", ".fs", ".fsx", ".vim", ".el", ".sql",
    ".html", ".css", ".scss", ".sass", ".less", ".styl",
    ".vue", ".svelte", ".astro",
    ".yml", ".yaml", ".toml", ".ini", ".cfg", ".conf",
    ".xml", ".svg", ".graphql", ".gql",
    ".dockerfile", ".makefile", ".cmake",
}

DEFAULT_EXCLUDE = {".git", "node_modules", "__pycache__", ".venv", "venv",
                   "dist", "build", ".next", ".nuxt", "target", "*.egg-info"}

def humanSize(num):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num) < 1024.0:
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} PB"

def bar(pct, width=40):
    filled = int(pct * width / 100)
    return "█" * filled + "░" * (width - filled)

def scanDir(root, excludes, codeOnly):
    exclude_set = set(excludes)
    ext_counter = Counter()
    size_by_ext = Counter()
    large_files = []  # (size, path)
    code_lines = Counter()
    total_files = 0
    total_dirs = 0
    total_size = 0
    
    for dirpath, dirnames, filenames in os.walk(root):
        # 过滤排除目录
        dirnames[:] = [d for d in dirnames if d not in exclude_set]
        
        total_dirs += len(dirnames)
        
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                fsize = os.path.getsize(fpath)
            except OSError:
                continue
            
            total_files += 1
            total_size += fsize
            
            ext = os.path.splitext(fname)[1].lower()
            if not ext:
                ext = "(no ext)"
            
            ext_counter[ext] += 1
            size_by_ext[ext] += fsize
            
            large_files.append((fsize, os.path.relpath(fpath, root)))
            
            if codeOnly and ext not in CODE_EXTENSIONS:
                continue
            if ext in CODE_EXTENSIONS:
                try:
                    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                        line_count = sum(1 for _ in f)
                    code_lines[ext] += line_count
                except Exception:
                    pass
    
    large_files.sort(key=lambda x: -x[0])
    
    return {
        "root": root,
        "total_files": total_files,
        "total_dirs": total_dirs,
        "total_size": total_size,
        "ext_counts": ext_counter,
        "size_by_ext": size_by_ext,
        "large_files": large_files,
        "code_lines": code_lines,
    }


def printReport(stats, top):
    root = stats["root"]
    print(f"\n📊 DirStats — 目录统计报告")
    print(f"📂 扫描路径: {os.path.abspath(root)}")
    print(f"🕐 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sep = "═" * 51
    
    print(f"\n{sep}")
    print("  📁 总览")
    print(sep)
    print(f"  文件总数: {stats['total_files']:,}")
    print(f"  文件夹总数: {stats['total_dirs']:,}")
    print(f"  总大小: {humanSize(stats['total_size'])}")
    
    # 文件类型分布
    ext_counts = stats["ext_counts"]
    if ext_counts:
        print(f"\n📉 文件类型分布 (Top 10):")
        top_exts = ext_counts.most_common(10)
        max_count = top_exts[0][1] if top_exts else 1
        for ext, count in top_exts:
            pct = count / stats["total_files"] * 100 if stats["total_files"] else 0
            bar_pct = count / max_count * 100
            bar_str = bar(bar_pct, 15)
            print(f"  {ext:8s} {bar_str} {count:>5} files ({pct:.1f}%)")
    
    # 大文件排行
    large_files = stats["large_files"][:top]
    if large_files:
        print(f"\n🏆 大文件排行 (Top {min(top, len(large_files))}):")
        for i, (size, path) in enumerate(large_files, 1):
            print(f"  {i:2d}. {humanSize(size):>8s}  {path}")
    
    # 代码行数
    code_lines = stats["code_lines"]
    if code_lines:
        print(f"\n📝 代码行数统计:")
        total_lines = sum(code_lines.values())
        for ext, lines in code_lines.most_common():
            print(f"  {ext:8s} {lines:>10,} lines")
        print(f"  {'Total':8s} {total_lines:>10,} lines")
    
    print(sep + "\n")


def main():
    parser = argparse.ArgumentParser(description="📊 DirStats — 项目目录统计工具")
    parser.add_argument("path", type=str, help="要扫描的目录路径")
    parser.add_argument("--exclude", type=str, default="",
                        help="排除的目录名，逗号分隔")
    parser.add_argument("--code-only", action="store_true",
                        help="只统计代码文件")
    parser.add_argument("--json", action="store_true",
                        help="输出 JSON 格式")
    parser.add_argument("--top", type=int, default=10,
                        help="大文件排行数量 (默认 10)")
    args = parser.parse_args()
    
    root = args.path
    if not os.path.isdir(root):
        print(f"❌ 目录不存在: {root}")
        sys.exit(1)
    
    excludes = set()
    if args.exclude:
        excludes = set(e.strip() for e in args.exclude.split(","))
    excludes.update(DEFAULT_EXCLUDE)
    
    stats = scanDir(root, excludes, args.code_only)
    
    if args.json:
        output = {
            "path": os.path.abspath(root),
            "total_files": stats["total_files"],
            "total_dirs": stats["total_dirs"],
            "total_size": stats["total_size"],
            "ext_distribution": dict(stats["ext_counts"].most_common(20)),
            "large_files": [{"size": s, "path": p} for s, p in stats["large_files"][:args.top]],
            "code_lines": dict(stats["code_lines"]),
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        printReport(stats, args.top)


if __name__ == "__main__":
    main()
