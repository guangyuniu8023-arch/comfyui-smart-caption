"""
ComfyUI Smart Caption - 自动安装脚本
"""
import subprocess
import sys
import os

def install():
    """自动安装依赖"""
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    
    print("=" * 60)
    print("Installing ComfyUI Smart Caption dependencies...")
    print("=" * 60)
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", req_path
        ])
        print("\n" + "=" * 60)
        print("✅ Installation complete!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install()

