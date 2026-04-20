import os
import sys
import time
import subprocess
import threading
import socket
import webbrowser
from pathlib import Path


def get_available_port(start_port=5000):
    """获取可用端口"""
    port = start_port
    while port < start_port + 100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                port += 1
    raise RuntimeError("无法找到可用端口")


def print_banner():
    """打印启动横幅"""
    print("=" * 60)
    print("🚀 商品价格查询系统 - 一键启动")
    print("=" * 60)
    print()


def start_backend(port):
    """启动后端服务（同时提供前端静态文件）"""
    print(f"🔧 正在启动服务（端口: {port}）...")
    os.environ['FLASK_DEBUG'] = 'False'
    
    backend_process = subprocess.Popen(
        [sys.executable, '-m', 'backend.app'],
        cwd=str(Path(__file__).parent),
        env={**os.environ, 'FLASK_RUN_PORT': str(port)}
    )
    
    # 等待服务启动
    time.sleep(2)
    return backend_process


def open_browser(url):
    """延迟打开浏览器"""
    time.sleep(3)
    print(f"🌐 正在打开浏览器: {url}")
    webbrowser.open(url)


def main():
    """主函数"""
    print_banner()
    
    # 获取可用端口
    try:
        port = get_available_port(5000)
    except RuntimeError as e:
        print(f"❌ 错误: {e}")
        return
    
    print(f"📡 服务端口: {port}")
    print()
    
    # 启动后端（同时提供前端）
    try:
        backend_process = start_backend(port)
        print("✅ 服务启动成功")
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        return
    
    # 显示访问地址
    print()
    print("=" * 60)
    print("🎉 服务启动完成！")
    print("=" * 60)
    print()
    print(f"📱 访问地址: http://127.0.0.1:{port}")
    print()
    print("💡 提示: 按 Ctrl+C 停止服务")
    print()
    
    # 在后台打开浏览器
    browser_thread = threading.Thread(
        target=open_browser,
        args=(f"http://127.0.0.1:{port}",),
        daemon=True
    )
    browser_thread.start()
    
    # 等待进程结束
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        backend_process.terminate()
        backend_process.wait()
        print("✅ 服务已停止")


if __name__ == '__main__':
    main()
