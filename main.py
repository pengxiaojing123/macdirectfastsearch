#!/usr/bin/env python3
"""
Mac文件快速检索工具
支持文件缓存刷新和模糊查找功能
"""

import os
import sqlite3
import argparse
import fnmatch
import sys
from pathlib import Path
import time
from datetime import datetime

class FileIndexer:
    def __init__(self, db_path="file_index.db"):
        """初始化文件索引器"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化SQLite数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建文件索引表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL UNIQUE,
                filesize INTEGER,
                last_modified REAL,
                indexed_time REAL
            )
        ''')
        
        # 创建索引以提高查询性能
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_filename ON files(filename)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_filepath ON files(filepath)')
        
        conn.commit()
        conn.close()
    
    def refresh_cache(self, root_paths=None):
        """刷新文件缓存"""
        if root_paths is None:
            # 默认扫描用户目录和常用目录
            root_paths = [
                os.path.expanduser("~"),  # 用户主目录
                "/Applications",          # 应用程序目录
                "/System/Applications",   # 系统应用程序
            ]
        
        print("开始刷新文件缓存...")
        start_time = time.time()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 清空现有数据
        cursor.execute('DELETE FROM files')
        
        total_files = 0
        current_time = time.time()
        
        for root_path in root_paths:
            if not os.path.exists(root_path):
                print(f"路径不存在，跳过: {root_path}")
                continue
                
            print(f"正在扫描: {root_path}")
            
            for root, dirs, files in os.walk(root_path):
                # 跳过一些系统目录和隐藏目录以提高性能
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                          d not in ['node_modules', '__pycache__', '.git', '.svn']]
                
                for file in files:
                    try:
                        filepath = os.path.join(root, file)
                        
                        # 检查文件访问权限
                        if not os.access(filepath, os.R_OK):
                            continue
                        
                        # 获取文件信息
                        stat_info = os.stat(filepath)
                        filesize = stat_info.st_size
                        last_modified = stat_info.st_mtime
                        
                        # 插入数据库
                        cursor.execute('''
                            INSERT OR REPLACE INTO files 
                            (filename, filepath, filesize, last_modified, indexed_time) 
                            VALUES (?, ?, ?, ?, ?)
                        ''', (file, filepath, filesize, last_modified, current_time))
                        
                        total_files += 1
                        
                        if total_files % 1000 == 0:
                            print(f"已索引 {total_files} 个文件...")
                            conn.commit()  # 定期提交以避免内存问题
                            
                    except (OSError, PermissionError) as e:
                        # 跳过无权限访问的文件
                        continue
                    except Exception as e:
                        print(f"处理文件时发生错误 {filepath}: {e}")
                        continue
        
        conn.commit()
        conn.close()
        
        end_time = time.time()
        print(f"缓存刷新完成！")
        print(f"总共索引了 {total_files} 个文件")
        print(f"耗时: {end_time - start_time:.2f} 秒")
    
    def search_files(self, pattern, limit=50):
        """搜索文件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查数据库是否有数据
        cursor.execute('SELECT COUNT(*) FROM files')
        total_files = cursor.fetchone()[0]
        
        if total_files == 0:
            print("数据库为空，请先运行 refresh 命令刷新缓存")
            conn.close()
            return []
        
        print(f"在 {total_files} 个文件中搜索...")
        
        results = []
        
        if '*' in pattern or '?' in pattern:
            # 模糊匹配
            print(f"使用模糊匹配搜索: {pattern}")
            cursor.execute('SELECT filename, filepath, filesize, last_modified FROM files')
            all_files = cursor.fetchall()
            
            # 收集所有匹配的文件
            matched_files = []
            for filename, filepath, filesize, last_modified in all_files:
                if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                    matched_files.append((filename, filepath, filesize, last_modified))
            
            # 按文件大小从大到小排序
            matched_files.sort(key=lambda x: x[2], reverse=True)
            
            # 限制结果数量
            results = matched_files[:limit]
        else:
            # 精确匹配或包含匹配
            print(f"使用精确匹配搜索: {pattern}")
            cursor.execute('''
                SELECT filename, filepath, filesize, last_modified 
                FROM files 
                WHERE filename LIKE ? 
                ORDER BY filename
                LIMIT ?
            ''', (f'%{pattern}%', limit))
            results = cursor.fetchall()
        
        conn.close()
        return results
    
    def format_file_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def display_results(self, results):
        """显示搜索结果"""
        if not results:
            print("没有找到匹配的文件")
            return
        
        print(f"\n找到 {len(results)} 个文件:")
        print("-" * 80)
        
        for i, (filename, filepath, filesize, last_modified) in enumerate(results, 1):
            size_str = self.format_file_size(filesize)
            modified_time = datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"{i:3d}. {filename}")
            print(f"     路径: {filepath}")
            print(f"     大小: {size_str}")
            print(f"     修改时间: {modified_time}")
            print()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Mac文件快速检索工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 刷新缓存命令
    refresh_parser = subparsers.add_parser('refresh', help='刷新文件缓存')
    refresh_parser.add_argument('--paths', nargs='+', help='指定要扫描的路径')
    
    # 搜索文件命令
    search_parser = subparsers.add_parser('search', help='搜索文件')
    search_parser.add_argument('pattern', help='搜索模式 (支持通配符 * 和 ?)')
    search_parser.add_argument('--limit', type=int, default=50, help='限制结果数量 (默认: 50)')
    
    # 状态命令
    status_parser = subparsers.add_parser('status', help='显示数据库状态')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    indexer = FileIndexer()
    
    if args.command == 'refresh':
        indexer.refresh_cache(args.paths)
    
    elif args.command == 'search':
        results = indexer.search_files(args.pattern, args.limit)
        indexer.display_results(results)
    
    elif args.command == 'status':
        conn = sqlite3.connect(indexer.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM files')
        total_files = cursor.fetchone()[0]
        
        if total_files > 0:
            cursor.execute('SELECT MAX(indexed_time) FROM files')
            last_indexed = cursor.fetchone()[0]
            last_indexed_str = datetime.fromtimestamp(last_indexed).strftime('%Y-%m-%d %H:%M:%S')
            print(f"数据库状态:")
            print(f"  总文件数: {total_files}")
            print(f"  最后更新: {last_indexed_str}")
        else:
            print("数据库为空，请先运行 refresh 命令")
        
        conn.close()

if __name__ == '__main__':
    main()
