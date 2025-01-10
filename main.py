import os
import json
import random
import asyncio
from typing import List, Dict
from websocket import create_connection
import requests

# 定义头部显示函数
def display_header():
    header_lines = [
        "╔═╗╔═╦╗─╔╦═══╦═══╦═══╦═══╗",
        "╚╗╚╝╔╣║─║║╔══╣╔═╗║╔═╗║╔═╗║",
        "─╚╗╔╝║║─║║╚══╣║─╚╣║─║║║─║║",
        "─╔╝╚╗║║─║║╔══╣║╔═╣╚═╝║║─║║",
        "╔╝╔╗╚╣╚═╝║╚══╣╚╩═║╔═╗║╚═╝║",
        "╚═╝╚═╩═══╩═══╩═══╩╝─╚╩═══╝",
        "我的gihub：github.com/Gzgod",
        "我的推特：推特雪糕战神@Hy78516012 "
    ]
    for line in header_lines:
        print(f"\033[36m{line:^50}\033[0m")

# 读取token信息
def read_tokens() -> List[Dict[str, str]]:
    with open('account.txt', 'r') as f:
        lines = f.read().strip().split('\n')
        return [{'token': line.split(':')[0], 'workerID': line.split(':')[1], 'id': line.split(':')[2], 'ownerAddress': line.split(':')[3]} for line in lines]

# 读取代理信息
def read_proxies() -> List[str]:
    try:
        with open('proxy.txt', 'r') as f:
            return f.read().strip().split()
    except FileNotFoundError:
        print('读取 proxy.txt 时出错：文件未找到')
        return []

# 读取或初始化资源分配
def read_or_init_data_assignments() -> Dict[str, Dict[str, str]]:
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print('未找到现有的资源分配，初始化新分配。')
        return {}

# GPU列表
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
def get_or_assign_resources(workerID, data_assignments):
    if workerID not in data_assignments:
        random_gpu = random.choice(gpu_list)
        random_storage = round(random.uniform(0, 500), 2)
        data_assignments[workerID] = {
            'gpu': random_gpu,
            'storage': random_storage
        }
        with open('data.json', 'w') as f:
            json.dump(data_assignments, f, indent=2)
    return data_assignments[workerID]

# 获取账号ID
async def get_account_id(token, index, use_proxy, proxies):
    url = 'https://apitn.openledger.xyz/api/v1/users/me'
    headers = {'Authorization': f'Bearer {token}'}
    proxy = proxies[index] if use_proxy else None
    try:
        if proxy:
            proxy_components = proxy.split('@')
            if len(proxy_components) == 2:
                user_pass, host_port = proxy_components
                user, password = user_pass.split(':')
                host, port = host_port.split(':')
                proxies_dict = {'https': f'http://{user}:{password}@{host}:{port}'}
                response = requests.get(url, headers=headers, proxies=proxies_dict)
            else:
                response = requests.get(url, headers=headers, proxies={'https': f'http://{proxy}'})
        else:
            response = requests.get(url, headers=headers)
        response.raise_for_status()
        account_id = response.json()['data']['id']
        print(f"\033[33m[{index + 1}]\033[0m 账户ID \033[36m{account_id}\033[0m, 代理: \033[36m{proxy or 'False'}\033[0m")
        return account_id
    except requests.RequestException as e:
        print(f"获取 token 索引 {index} 的账户ID时出错：{str(e)}")
    return None

# 获取账号详细信息
async def get_account_details(token, index, use_proxy, proxies, account_id):
    urls = [
        'https://rewardstn.openledger.xyz/api/v1/reward_realtime',
        'https://rewardstn.openledger.xyz/api/v1/reward_history'
    ]
    headers = {'Authorization': f'Bearer {token}'}
    proxy = proxies[index] if use_proxy else None
    try:
        if proxy:
            proxy_components = proxy.split('@')
            if len(proxy_components) == 2:
                user_pass, host_port = proxy_components
                user, password = user_pass.split(':')
                host, port = host_port.split(':')
                proxies_dict = {'https': f'http://{user}:{password}@{host}:{port}'}
                response_realtime = requests.get(urls[0], headers=headers, proxies=proxies_dict)
                response_history = requests.get(urls[1], headers=headers, proxies=proxies_dict)
            else:
                response_realtime = requests.get(urls[0], headers=headers, proxies={'https': f'http://{proxy}'})
                response_history = requests.get(urls[1], headers=headers, proxies={'https': f'http://{proxy}'})
        else:
            response_realtime = requests.get(urls[0], headers=headers)
            response_history = requests.get(urls[1], headers=headers)
        
        response_realtime.raise_for_status()
        response_history.raise_for_status()
        total_heartbeats = int(response_realtime.json()['data'][0]['total_heartbeats'])
        total_points = int(response_history.json()['data'][0]['total_points'])
        total = total_heartbeats + total_points
        print(f"\033[33m[{index + 1}]\033[0m 账户ID \033[36m{account_id}\033[0m, 总心跳数 \033[32m{total_heartbeats}\033[0m, 总积分 \033[32m{total}\033[0m, 代理: \033[36m{proxy or 'False'}\033[0m")
    except requests.RequestException as e:
        print(f"获取 token 索引 {index} 的账户详细信息时出错：{str(e)}")

# WebSocket连接
async def connect_websocket(token, workerID, id, ownerAddress, index, use_proxy, proxies):
    ws_url = f"wss://apitn.openledger.xyz/ws/v1/orch?authToken={token}"
    proxy = proxies[index] if use_proxy else None
    
    if proxy:
        proxy_parts = proxy.split('@')
        if len(proxy_parts) == 2:
            proxy_user_pass, proxy_host_port = proxy_parts
            proxy_user, proxy_pass = proxy_user_pass.split(':')
            proxy_host, proxy_port = proxy_host_port.split(':')
            
            # 使用代理连接WebSocket
            ws = create_connection(ws_url, proxy_type='http', http_proxy_host=proxy_host, 
                                   http_proxy_port=int(proxy_port), http_proxy_auth=(proxy_user, proxy_pass))
        else:
            print(f"代理格式未识别，索引 {index}: {proxy}")
            return
    else:
        ws = create_connection(ws_url)

    try:
        print(f"\033[33m[{index + 1}]\033[0m 已连接到 workerID: \033[33m{workerID}\033[0m 的 WebSocket，使用代理: \033[36m{proxy or 'False'}\033[0m")

        # 注册消息
        register_message = {
            'workerID': workerID,
            'msgType': 'REGISTER',
            'workerType': 'LWEXT',
            'message': {
                'id': id,
                'type': 'REGISTER',
                'worker': {
                    'host': 'chrome-extension://ekbbplmjjgoobhdlffmgeokalelnmjjc',
                    'identity': workerID,
                    'ownerAddress': ownerAddress,
                    'type': 'LWEXT'
                }
            }
        }
        ws.send(json.dumps(register_message))

        # 发送心跳
        while True:
            assigned_resources = get_or_assign_resources(workerID, read_or_init_data_assignments())
            heartbeat_message = {
                'message': {
                    'Worker': {
                        'Identity': workerID,
                        'ownerAddress': ownerAddress,
                        'type': 'LWEXT',
                        'Host': 'chrome-extension://ekbbplmjjgoobhdlffmgeokalelnmjjc'
                    },
                    'Capacity': {
                        'AvailableMemory': round(random.uniform(0, 32), 2),
                        'AvailableStorage': assigned_resources['storage'],
                        'AvailableGPU': assigned_resources['gpu'],
                        'AvailableModels': []
                    }
                },
                'msgType': 'HEARTBEAT',
                'workerType': 'LWEXT',
                'workerID': workerID
            }
            print(f"\033[33m[{index + 1}]\033[0m 正在发送 workerID: \033[33m{workerID}\033[0m 的心跳包，使用代理: \033[36m{proxy or 'False'}\033[0m")
            ws.send(json.dumps(heartbeat_message))
            await asyncio.sleep(30)  # 每30秒发送一次心跳
    except Exception as e:
        print(f"\033[33m[{index + 1}]\033[0m workerID \033[33m{workerID}\033[0m 的 WebSocket 错误：{str(e)}")
    finally:
        if 'ws' in locals():
            ws.close()
        print(f"\033[33m[{index + 1}]\033[0m workerID \033[33m{workerID}\033[0m 的 WebSocket 连接已关闭，尝试重连中，代理: \033[36m{proxy or 'False'}\033[0m")
        await asyncio.sleep(30)
        await connect_websocket(token, workerID, id, ownerAddress, index, use_proxy, proxies)

# 处理请求
async def process_requests(use_proxy, tokens, proxies):
    tasks = []
    for index, token_data in enumerate(tokens):
        tasks.append(asyncio.create_task(get_account_id(token_data['token'], index, use_proxy, proxies)))
    account_ids = await asyncio.gather(*tasks)
    
    tasks = []
    for index, (token_data, account_id) in enumerate(zip(tokens, account_ids)):
        if account_id:
            tasks.append(asyncio.create_task(get_account_details(token_data['token'], index, use_proxy, proxies, account_id)))
            tasks.append(asyncio.create_task(connect_websocket(token_data['token'], token_data['workerID'], token_data['id'], token_data['ownerAddress'], index, use_proxy, proxies)))
    await asyncio.gather(*tasks)
    return account_ids

# 主函数
async def main():
    display_header()
    use_proxy = input('您想使用代理吗？(y/n): ').lower() == 'y'
    tokens = read_tokens()
    proxies = read_proxies()
    
    if len(proxies) < len(tokens) and use_proxy:
        print('代理数量少于账户数量，请提供足够的代理。')
        return

    account_ids = await process_requests(use_proxy, tokens, proxies)

    # 定期更新账号信息
    while True:
        tasks = [asyncio.create_task(get_account_details(token['token'], index, use_proxy, proxies, account_ids[index])) for index, token in enumerate(tokens)]
        await asyncio.gather(*tasks)
        await asyncio.sleep(300)  # 每5分钟更新一次

if __name__ == "__main__":
    asyncio.run(main())
