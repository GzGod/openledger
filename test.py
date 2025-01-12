import os
import json
import random
import asyncio
from typing import List, Dict
from websocket import create_connection
import requests
from uuid import uuid4
import base64

# 全局变量用于存储最新信息
total_heartbeats = 0
total_points = 0
account_ids = {}
data_store = {}

# 定义头部显示函数
def display_header():
    header_lines = [
        "╔═╗╔═╦╗─╔╦═══╦═══╦═══╦═══╗",
        "╚╗╚╝╔╣║─║║╔══╣╔═╗║╔═╗║╔═╗║",
        "─╚╗╔╝║║─║║╚══╣║─╚╣║─║║║─║║",
        "─╔╝╚╗║║─║║╔══╣╔═╣╚═╝║║─║║",
        "╔╝╔╗╚╣╚═╝║╚══╣╚╩═║╔═╗║╚═╝║",
        "╚═╝╚═╩═══╩═══╩═══╩╝─╚╩═══╝",
        "我的gihub：github.com/Gzgod",
        "我的推特：推特雪糕战神@Hy78516012 "
    ]
    for line in header_lines:
        print(f"\033[36m{line:^50}\033[0m")

# 读取钱包地址
def read_wallets() -> List[str]:
    try:
        with open('account.txt', 'r') as f:
            return [line.strip() for line in f.read().split('\n') if line.strip()]
    except FileNotFoundError:
        print('读取 account.txt 时出错：文件未找到')
        return []

# 读取代理信息
def read_proxies() -> List[str]:
    try:
        with open('proxy.txt', 'r') as f:
            return f.read().strip().split()
    except FileNotFoundError:
        print('读取 proxy.txt 时出错：文件未找到')
        return []

# 读取或初始化数据存储
def read_or_init_data_store() -> Dict[str, Dict]:
    global data_store
    try:
        with open('data.json', 'r') as f:
            data_store = json.load(f)
    except FileNotFoundError:
        print('未找到现有的数据存储，初始化新存储。')
    return data_store

gpu_list = [
    "NVIDIA GTX 1050",
    "NVIDIA GTX 1050 Ti",
    "NVIDIA GTX 1060",
    "NVIDIA GTX 1070",
    "NVIDIA GTX 1070 Ti",
    "NVIDIA GTX 1080",
    "NVIDIA GTX 1080 Ti",
    "NVIDIA GTX 1650",
    "NVIDIA GTX 1650 Super",
    "NVIDIA GTX 1660",
    "NVIDIA GTX 1660 Super",
    "NVIDIA GTX 1660 Ti",
    "NVIDIA RTX 2060",
    "NVIDIA RTX 2060 Super",
    "NVIDIA RTX 2070",
    "NVIDIA RTX 2070 Super",
    "NVIDIA RTX 2080",
    "NVIDIA RTX 2080 Super",
    "NVIDIA RTX 2080 Ti",
    "NVIDIA RTX 3060",
    "NVIDIA RTX 3060 Ti",
    "NVIDIA RTX 3070",
    "NVIDIA RTX 3070 Ti",
    "NVIDIA RTX 3080",
    "NVIDIA RTX 3080 Ti",
    "NVIDIA RTX 3090",
    "NVIDIA RTX 3090 Ti",
    "AMD Radeon RX 460",
    "AMD Radeon RX 470",
    "AMD Radeon RX 480",
        "AMD Radeon RX 550",
    "AMD Radeon RX 560",
    "AMD Radeon RX 570",
    "AMD Radeon RX 580",
    "AMD Radeon RX 590",
    "AMD Radeon RX 5500 XT",
    "AMD Radeon RX 5600 XT",
    "AMD Radeon RX 5700",
    "AMD Radeon RX 5700 XT",
    "AMD Radeon RX 6600",
    "AMD Radeon RX 6600 XT",
    "AMD Radeon RX 6700 XT",
    "AMD Radeon RX 6800",
    "AMD Radeon RX 6800 XT",
    "AMD Radeon RX 6900 XT",
    "AMD Radeon RX 6950 XT"
]

# 分配或获取资源
def get_or_assign_resources(address, data_store):
    if address not in data_store or not data_store[address].get('gpu') or not data_store[address].get('storage'):
        random_gpu = random.choice(gpu_list)
        random_storage = round(random.uniform(0, 500), 2)
        data_store[address] = {
            **data_store.get(address, {}),
            'gpu': random_gpu,
            'storage': random_storage
        }
        try:
            with open('data.json', 'w') as f:
                json.dump(data_store, f, indent=2)
        except Exception as e:
            print(f'写入 GPU/存储到 data.json 时出错: {str(e)}')
    return data_store[address]

# 获取或生成token
async def get_or_generate_token(address, use_proxy, proxies, index):
    data_store = read_or_init_data_store()
    if address in data_store and data_store[address].get('token'):
        return data_store[address]['token']

    url = 'https://apitn.openledger.xyz/api/v1/auth/generate_token'
    headers = {'Content-Type': 'application/json'}
    data = {'address': address}
    proxy = proxies[index % len(proxies)] if use_proxy and proxies else None

    try:
        if proxy:
            proxy_components = proxy.split('@')
            if len(proxy_components) == 2:
                user_pass, host_port = proxy_components
                user, password = user_pass.split(':')
                host, port = host_port.split(':')
                proxies_dict = {'https': f'http://{user}:{password}@{host}:{port}'}
                response = requests.post(url, headers=headers, json=data, proxies=proxies_dict, timeout=10)
            else:
                response = requests.post(url, headers=headers, json=data, proxies={'https': f'http://{proxy}'}, timeout=10)
        else:
            response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        token = response.json()['data']['token']
        data_store[address] = {
            **data_store.get(address, {}),
            'token': token,
            'workerID': base64.b64encode(address.encode()).decode(),
            'id': str(uuid4()),
            'gpu': None,
            'storage': None
        }
        with open('data.json', 'w') as f:
            json.dump(data_store, f, indent=2)
        return token
    except requests.RequestException as e:
        print(f"为地址 {address} 生成 token 时出错: {str(e)}")
        return None

# 获取账号ID
async def get_account_id(address, index, use_proxy, proxies, delay=60000):
    token = await get_or_generate_token(address, use_proxy, proxies, index)
    if not token:
        return None

    url = 'https://apitn.openledger.xyz/api/v1/users/me'
    headers = {'Authorization': f'Bearer {token}'}
    proxy = proxies[index % len(proxies)] if use_proxy and proxies else None
    proxy_text = proxy or 'False'

    attempt = 1
    while True:
        try:
            if proxy:
                proxy_components = proxy.split('@')
                if len(proxy_components) == 2:
                    user_pass, host_port = proxy_components
                    user, password = user_pass.split(':')
                    host, port = host_port.split(':')
                    proxies_dict = {'https': f'http://{user}:{password}@{host}:{port}'}
                    response = requests.get(url, headers=headers, proxies=proxies_dict, timeout=10)
                else:
                    response = requests.get(url, headers=headers, proxies={'https': f'http://{proxy}'}, timeout=10)
            else:
                response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            account_id = response.json()['data']['id']
            account_ids[token] = account_id
            print(f"\033[33m[{index + 1}]\033[0m 账户ID \033[36m{account_id}\033[0m, 代理: \033[36m{proxy_text}\033[0m")
            return account_id
        except requests.RequestException as e:
            print(f"获取地址 {address} 的账户ID时出错，尝试 {attempt}: {str(e)}")
            print(f"在 {delay / 1000} 秒后重试...")
            await asyncio.sleep(delay / 1000)
            attempt += 1

# 其余函数保持不变
# 以下是之前已有的函数

# 主函数
async def main():
    display_header()
    use_proxy = input('您想使用代理吗？(y/n): ').lower() == 'y'
    wallets = read_wallets()
    proxies = read_proxies()
    
    if len(proxies) > 0 and len(proxies) < len(wallets) and use_proxy:
        print('代理数量少于账户数量，请提供足够的代理。')
        return

    tasks = []
    for index, address in enumerate(wallets):
        tasks.append(asyncio.create_task(get_account_id(address, index, use_proxy, proxies)))
        tasks.append(asyncio.create_task(connect_websocket(address, index, use_proxy, proxies)))

    await asyncio.gather(*tasks)

    # 启动定期检查和领取奖励
    asyncio.create_task(check_and_claim_rewards_periodically(use_proxy, wallets, proxies))

    # 定期更新账号信息
    while True:
        tasks = [asyncio.create_task(get_account_details(data_store[address]['token'], index, use_proxy, proxies, account_ids[data_store[address]['token']])) for index, address in enumerate(wallets)]
        await asyncio.gather(*tasks)
        await asyncio.sleep(300)  # 每5分钟更新一次

if __name__ == "__main__":
    asyncio.run(main())
