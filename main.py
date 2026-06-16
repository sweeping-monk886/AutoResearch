"""
AutoResearch — 基于多智能体协作的深度研究助手
主入口：启动 Streamlit 应用

用法:
    streamlit run main.py
"""
import subprocess
import sys


def main():
    print("=" * 50)
    print("  AutoResearch — 多智能体深度研究助手")
    print("=" * 50)
    print()
    print("正在启动 Web 界面...")
    print("浏览器将自动打开，若未打开请访问 http://localhost:8501")
    print()
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py",
                    "--server.port", "8501",
                    "--server.headless", "false",
                    "--theme.base", "dark"])


if __name__ == "__main__":
    main()
