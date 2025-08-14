import subprocess
import sys
from concurrent import futures
from tqdm import tqdm

def thread_parallel(processor, dataset, threads=10, name=None, extra_paras=None):
    with futures.ThreadPoolExecutor(threads) as executor:
        if extra_paras is None:
            process_futures = [executor.submit(processor, data)for data in dataset]
        else:
            process_futures = [executor.submit(processor, data, *extra_paras)for data in dataset]
        for future in tqdm(futures.as_completed(process_futures), desc=name, total=len(dataset)):
            yield future.result()

# gen hostfile script code from sft2
def check_gpu_free(ip):
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
            return ip, False, "ssh failed"  # SSH 命令失败
        elif "No running processes found" in result.stdout:
            return ip, True, None  # GPU 空闲
        else:
            return ip, False, "gpu busy"  # GPU 正在被使用
    except subprocess.TimeoutExpired:
        return ip, False, "timeout"  # 连接超时

def get_gpu_count(ip):
    """获取指定 IP 的机器上的 GPU 数量"""
    try:
        result = subprocess.run(
            ["ssh", ip, "nvidia-smi -L | wc -l"],
            text=True,
            capture_output=True,
            timeout=10
        )
        return int(result.stdout.strip())
    except subprocess.TimeoutExpired:
        print(f"Timeout when connecting to {ip}")
        return 0

def read_ips(file_path):
    """从文件中读取IP列表"""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def list_nodes(ips):
    """列出可用和不可用的节点"""
    available = []
    unavailable = []
    ip_status = thread_parallel(check_gpu_free, ips, 16)
    for ip, free, status in ip_status:
        if free:
            available.append(ip)
        else:
            unavailable.append((ip, status))
    return available, unavailable

def main(ip_file, num_required_hosts, outpath):
    ips = read_ips(ip_file)
    available, unavailable = list_nodes(ips)
    # import random
    # random.shuffle(available)
    if len(available) < num_required_hosts:
        print(f"Not enough hosts with free GPUs available. Only {len(available)} available.")
        print(f"Available nodes(only {len(available)}): ")
        for ip in available[:num_required_hosts]:
            print(ip)
        print("Unavailable nodes:")
        for node, status in unavailable:
            print(f"{node} - {status}")
        raise ValueError("可用节点不足！！！")

    # 创建 hostfile
    with open(outpath, "w") as f:
        for ip in available[:num_required_hosts]:
            num_gpus = get_gpu_count(ip)
            f.write(f"{ip} slots={num_gpus}\n")
    
    print("Hostfile created.")
    print("Available nodes used:")
    for ip in available[:num_required_hosts]:
        print(ip)
    print("Unavailable nodes:")
    for node, status in unavailable:
        print(f"{node} - {status}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python generate_hostfile.py ip_list_file num_required_hosts outpath")
        sys.exit(1)

    ip_file_path = sys.argv[1]
    required_hosts = int(sys.argv[2])
    outpath = sys.argv[3]
    main(ip_file_path, required_hosts, outpath)
