#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海龟交易系统安装脚本
自动安装所需的依赖包
"""

import subprocess
import sys
import os

def install_package(package):
    """安装单个包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """主安装函数"""
    print("🚀 海龟交易系统安装程序")
    print("=" * 50)
    
    # 需要安装的包
    packages = [
        "binance-futures-connector==4.1.0",
        "requests==2.31.0", 
        "python-dotenv==1.0.0",
        "pandas==2.0.3",
        "numpy==1.24.3"
    ]
    
    print("📦 开始安装依赖包...")
    print()
    
    success_count = 0
    for package in packages:
        print(f"正在安装 {package}...")
        if install_package(package):
            print(f"✅ {package} 安装成功")
            success_count += 1
        else:
            print(f"❌ {package} 安装失败")
        print()
    
    print(f"📊 安装结果: {success_count}/{len(packages)} 个包安装成功")
    
    if success_count == len(packages):
        print("🎉 所有依赖包安装完成!")
        print()
        print("📝 下一步:")
        print("1. 复制 email_config_example.txt 为 .env")
        print("2. 配置您的钉钉机器人设置")
        print("3. 运行 python test_turtle_system.py 测试系统")
        print("4. 运行 python turtle_trading_system.py 启动监控")
    else:
        print("⚠️ 部分包安装失败，请手动安装")
        print("运行: pip install -r requirements.txt")

if __name__ == "__main__":
    main() 