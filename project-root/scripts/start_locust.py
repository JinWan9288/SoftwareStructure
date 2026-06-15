import subprocess
import sys

if __name__ == "__main__":
    print("正在启动 Locust 压测控制台...")
    # 使用当前 PyCharm 激活的正确 Python 环境去强制运行 locust
    subprocess.run([sys.executable, "-m", "locust", "-f", "locustfile.py"])