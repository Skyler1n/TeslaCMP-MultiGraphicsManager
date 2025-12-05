import subprocess
import sys
import os


def check_nuitka_installed():
    """检查Nuitka是否已安装"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "nuitka", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_nuitka():
    """安装Nuitka及其依赖"""
    print("正在安装Nuitka...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "nuitka", "ordered-set", "zstandard"],
            check=True
        )
        print("Nuitka安装成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"安装Nuitka失败：{e}")
        return False


def create_output_dir():
    """创建输出目录"""
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录 {output_dir} 成功")
    else:
        print(f"输出目录 {output_dir} 已存在")
    return output_dir


def build_with_nuitka(output_dir):
    """使用Nuitka打包程序"""
    print("开始使用Nuitka打包程序...")
    try:
        # 构建Nuitka命令
        nuitka_cmd = [
            sys.executable,
            "-m", "nuitka",
            "--standalone",
            "--onefile",
            "--windows-console-mode=disable",
            "--enable-plugin=tk-inter",
            f"--include-data-file={os.path.abspath('ic_launcher.ico')}=ic_launcher.ico",
            f"--output-dir={output_dir}",
            f"--windows-icon-from-ico={os.path.abspath('ic_launcher.ico')}",
            "GraphicsMgr.py"
        ]
        
        # 执行命令
        subprocess.run(nuitka_cmd, check=True)
        
        print("打包成功！可执行文件位于output目录中。")
        return True
    except subprocess.CalledProcessError as e:
        print(f"打包失败：{e}")
        return False


if __name__ == "__main__":
    # 检查Nuitka是否已安装
    if not check_nuitka_installed():
        if not install_nuitka():
            print("请手动安装Nuitka后再运行此脚本。")
            sys.exit(1)
    
    # 创建输出目录
    output_dir = create_output_dir()
    
    # 使用Nuitka打包
    if build_with_nuitka(output_dir):
        print("打包完成！")
    else:
        print("打包过程中出现错误。")
        sys.exit(1)
    
    # 等待用户按任意键继续
    input("按任意键退出...")