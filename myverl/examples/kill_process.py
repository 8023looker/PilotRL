import subprocess
import sys

def free_gpu(ip):
    """检查指定 IP 的机器上的 GPU 是否空闲"""
    try:
        # 运行 nvidia-smi 并捕获输出
        result = subprocess.run(
            ["ssh", ip, "nvidia-smi"],
            text=True,
            capture_output=True,
            timeout=10
        )
        if result.returncode != 0:
            return False, "ssh failed"  # SSH 命令失败
        elif "No running processes found" in result.stdout:
            return True, None  # GPU 空闲
        else:
            result = subprocess.run(["ssh",ip,"ps -ef | egrep \"train_ppo|train_rm\" | grep -v grep | awk '{print $2}'  | xargs kill -9"])
            return False, result  # GPU 正在被使用
    except subprocess.TimeoutExpired:
        return False, "timeout"  # 连接超时
def read_ips(file_path):
    """从文件中读取IP列表"""
    with open(file_path, 'r') as file:
        return [line.strip() if 'slot' not in line else line.strip().split()[0] for line in file if line.strip()]

if __name__ == "__main__":
    if len(sys.argv) == 2:
        iplist = read_ips(sys.argv[1])
    else:
        iplist = read_ips('hostfile.txt')
    for ip in iplist:
        print(ip,":",free_gpu(ip))
