#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试安装脚本 - 验证所有依赖是否正确安装
"""

import sys
import platform


def test_imports():
    """测试所有必要的导入"""
    print("🧪 测试导入...")
    
    # 测试列表
    imports_to_test = [
        ("binance.um_futures", "UMFutures"),
        ("binance.cm_futures", "CMFutures"),
        ("requests", "requests"),
        ("dotenv", "load_dotenv")
    ]
    
    success_count = 0
    for module, item in imports_to_test:
        try:
            if module == "binance.um_futures":
                from binance.um_futures import UMFutures
                print(f"✅ {module} 导入成功")
            elif module == "binance.cm_futures":
                from binance.cm_futures import CMFutures
                print(f"✅ {module} 导入成功")
            elif module == "requests":
                import requests
                print(f"✅ {module} 导入成功")
            elif module == "dotenv":
                from dotenv import load_dotenv
                print(f"✅ {module} 导入成功")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module} 导入失败: {e}")
    
    return success_count == len(imports_to_test)


def test_binance_api():
    """测试 Binance API 连接"""
    print("\n🌐 测试 Binance API 连接...")
    
    try:
        from binance.um_futures import UMFutures
        client = UMFutures()
        
        # 测试获取服务器时间
        server_time = client.time()
        print(f"✅ API 连接成功，服务器时间: {server_time['serverTime']}")
        
        # 测试获取价格
        price = client.ticker_price(symbol="BTCUSDT")
        print(f"✅ 价格查询成功，BTCUSDT: ${price['price']}")
        
        return True
    except Exception as e:
        print(f"❌ API 连接失败: {e}")
        return False


def main():
    """主函数"""
    print("🔍 数字货币合约价格查询 Demo - 安装测试")
    print("=" * 50)
    print(f"Python 版本: {sys.version}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print()
    
    # 1. 测试导入
    if not test_imports():
        print("\n❌ 部分依赖导入失败")
        print("请运行: python install_improved.py")
        return False
    
    print("\n✅ 所有依赖导入成功!")
    
    # 2. 测试 API 连接
    if not test_binance_api():
        print("\n❌ API 连接失败")
        print("请检查网络连接")
        return False
    
    print("\n🎉 所有测试通过!")
    print("您现在可以运行 demo 了:")
    print("  python basic_.py")
    print("  python simple_price_demo.py")
    print("  python futures_price_demo.py")
    
    return True


if __name__ == "__main__":
    main()