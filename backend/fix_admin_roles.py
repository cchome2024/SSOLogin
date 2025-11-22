#!/usr/bin/env python3
"""
快速修复脚本：为已存在的 admin 用户添加角色和权限
运行方式: python fix_admin_roles.py
"""
from app.database import init_db

if __name__ == "__main__":
    print("正在修复 admin 用户角色...")
    init_db()
    print("✅ 完成！admin 用户角色已更新。")
    print("请重启服务以使更改生效。")

