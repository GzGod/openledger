import os
import json
import random
import asyncio
from typing import List, Dict
from websocket import create_connection
import requests
from uuid import uuid4

# 全局变量用于存储最新信息
total_heartbeats = 0
total_points = 0
account_ids = {}

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
        return [{'token': line.split(':')[0].strip(), 'workerID': line.split(':')[1].strip(), 'id': line.split(':')[2].strip(), 'ownerAddress': line.split(':')[3].strip()} for line in lines if len(line.split(':')) == 4]

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
async def get_account_id(token, index, use_proxy, proxies, delay=60000):
    url = 'https://apitn.openledger.xyz/api/v1/users/me'
    headers = {'Authorization': f'Bearer {token}'}
    proxy = proxies[index] if use_proxy else None
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
            print(f"\033[33m[{index + 1}]\033[0m 账户ID \033[36m{account_id}\033[0m, 代理: \033[36m{proxy_text}\033[0m")
            return account_id
        except requests.RequestException as e:
            print(f"获取 token 索引 {index} 的账户ID时出错，尝试 {attempt}: {str(e)}")
            print(f"在 {delay / 1000} 秒后重试...")
            await asyncio.sleep(delay / 1000)
            attempt += 1

# 获取账号详细信息
async def get_account_details(token, index, use_proxy, proxies, account_id, retries=3, delay=60000):
    urls = [
        'https://rewardstn.openledger.xyz/api/v1/reward_realtime',
        'https://rewardstn.openledger.xyz/api/v1/reward_history',
        'https://rewardstn.openledger.xyz/api/v1/reward'
    ]
    headers = {'Authorization': f'Bearer {token}'}
    proxy = proxies[index] if use_proxy else None
    proxy_text = proxy or 'False'

    for attempt in range(1, retries + 1):
        try:
            if proxy:
                proxy_components = proxy.split('@')
                if len(proxy_components) == 2:
                    user_pass, host_port = proxy_components
                    user, password = user_pass.split(':')
                    host, port = host_port.split(':')
                    proxies_dict = {'https': f'http://{user}:{password}@{host}:{port}'}
                    response_realtime = requests.get(urls[0], headers=headers, proxies=proxies_dict, timeout=10)
                    response_history = requests.get(urls[1], headers=headers, proxies=proxies_dict, timeout=10)
                    response_reward = requests.get(urls[2], headers=headers, proxies=proxies_dict, timeout=10)
                else:
                    response_realtime = requests.get(urls[0], headers=headers, proxies={'https': f'http://{proxy}'}, timeout=10)
                    response_history = requests.get(urls[1], headers=headers, proxies={'https': f'http://{proxy}'}, timeout=10)
                    response_reward = requests.get(urls[2], headers=headers, proxies={'https': f'http://{proxy}'}, timeout=10)
            else:
                response_realtime = requests.get(urls[0], headers=headers, timeout=10)
                response_history = requests.get(urls[1], headers=headers, timeout=10)
                response_reward = requests.get(urls[2], headers=headers, timeout=10)
            
            response_realtime.raise_for_status()
            response_history.raise_for_status()
            response_reward.raise_for_status()
            
            global total_heartbeats, total_points
            total_heartbeats = int(response_realtime.json()['data'][0]['total_heartbeats'])
            total_points = int(response_history.json()['data'][0]['total_points']) + float(response_reward.json()['data']['totalPoint'])
            epoch_name = response_reward.json()['data']['name']

            print(f"\033[33m[{index + 1}]\033[0m 账户ID \033[36m{account_id}\033[0m, 总心跳数 \033[32m{total_heartbeats}\033[0m, 总积分 \033[32m{total_points:.2f}\033[0m (\033[33m{epoch_name}\033[0m), 代理: \033[36m{proxy_text}\033[0m")
            return
        except requests.RequestException as e:
            print(f"获取 token 索引 {index} 的账户详细信息时出错，尝试 {attempt}: {str(e)}")
            if attempt < retries:
                print(f"在 {delay / 1000} 秒后重试...")
                await asyncio.sleep(delay / 1000)
            else:
                print(f"所有重试尝试失败。")

# 检查并领取奖励
async def check_and_claim_reward(token, index, use_proxy, proxies, retries=3, delay=60000):
    url = 'https://rewardstn.openledger.xyz/api/v1/claim_details'
    claim_url = 'https://rewardstn.openledger.xyz/api/v1/claim_reward'
    headers = {'Authorization': f'Bearer {token}'}
    proxy = proxies[index] if use_proxy else None

    for attempt in range(1, retries + 1):
        try:
            if proxy:
                proxy_components = proxy.split('@')
                if len(proxy_components) == 2:
                    user_pass, host_port = proxy_components
                    user, password = user_pass.split(':')
                    host, port = host_port.split(':')
                    proxies_dict = {'https': f'http://{user}:{password}@{host}:{port}'}
                    claim_details_response = requests.get(url, headers=headers, proxies=proxies_dict, timeout=10)
                else:
                    claim_details_response = requests.get(url, headers=headers, proxies={'https': f'http://{proxy}'}, timeout=10)
            else:
                claim_details_response = requests.get(url, headers=headers, timeout=10)
            
            claim_details_response.raise_for_status()
            claimed = claim_details_response.json()['data']['claimed']

            if not claimed:
                if proxy:
                    claim_reward_response = requests.get(claim_url, headers=headers, proxies=proxies_dict, timeout=10)
                else:
                    claim_reward_response = requests.get(claim_url, headers=headers, timeout=10)
                
                claim_reward_response.raise_for_status()
                if claim_reward_response.json()['status'] == 'SUCCESS':
                    print(f"\033[33m[{index + 1}]\033[0m 账户ID \033[36m{account_ids[token]}\033[0m \033[32m成功领取每日奖励！\033[0m")
            return
        except requests.RequestException as e:
            print(f"领取 token 索引 {index} 的奖励时出错，尝试 {attempt}: {str(e)}")
            if attempt < retries:
                print(f"在 {delay / 1000} 秒后重试...")
                await asyncio.sleep(delay / 1000)
            else:
                print(f"所有重试尝试失败。")

# 定期检查和领取奖励
async def check_and_claim_rewards_periodically(use_proxy, tokens, proxies):
    while True:
        tasks = [asyncio.create_task(check_and_claim_reward(token['token'], index, use_proxy, proxies)) for index, token in enumerate(tokens)]
        await asyncio.gather(*tasks)
        await asyncio.sleep(12 * 60 * 60)  # 每12小时检查一次

# WebSocket连接
async def connect_websocket(token, workerID, id, ownerAddress, index, use_proxy, proxies):
    ws_url = f"wss://apitn.openledger.xyz/ws/v1/orch?authToken={token}"
    proxy = proxies[index] if use_proxy else None
    
    while True:
        try:
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
                    await asyncio.sleep(30)
                    continue
            else:
                ws = create_connection(ws_url)

            browser_id = str(uuid4())
            connection_uuid = str(uuid4())

            print(f"\033[33m[{index + 1}]\033[0m 已连接到 workerID: \033[33m{workerID}\033[0m 的 WebSocket，代理: \033[36m{proxy or 'False'}\033[0m")

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
                # 获取最新的账户详细信息
                await get_account_details(token, index, use_proxy, proxies, account_ids[token], retries=1, delay=0)

                # 使用全局变量来获取最新数据
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
                            'AvailableStorage': get_or_assign_resources(workerID, read_or_init_data_assignments())['storage'],
                            'AvailableGPU': get_or_assign_resources(workerID, read_or_init_data_assignments())['gpu'],
                            'AvailableModels': []
                        },
                        'TotalHeartbeats': total_heartbeats,
                        'TotalPoints': total_points
                    },
                    'msgType': 'HEARTBEAT',
                    'workerType': 'LWEXT',
                    'workerID': workerID
                }
                
                print(f"\033[33m[{index + 1}]\033[0m 正在发送 workerID: \033[33m{workerID}\033[0m 的心跳，代理: \033[36m{proxy or 'False'}\033[0m")
                ws.send(json.dumps(heartbeat_message))
                await asyncio.sleep(30)  # 每30秒发送一次心跳
        except Exception as e:
            print(f"\033[33m[{index + 1}]\033[0m workerID \033[33m{workerID}\033[0m 的 WebSocket 错误：{str(e)}")
            if 'ws' in locals() and ws:
                ws.close()
            print(f"\033[33m[{index + 1}]\033[0m workerID \033[33m{workerID}\033[0m 的 WebSocket 连接已关闭，代理: \033[36m{proxy or 'False'}\033[0m")
            await asyncio.sleep(30)
        finally:
            if 'ws' in locals() and ws:
                ws.close()

# 处理请求
async def process_requests(use_proxy, tokens, proxies):
    tasks = []
    for index, token_data in enumerate(tokens):
        tasks.append(asyncio.create_task(get_account_id(token_data['token'], index, use_proxy, proxies)))
    
    account_ids_list = await asyncio.gather(*tasks)
    
    tasks = []
    for index, (token_data, account_id) in enumerate(zip(tokens, account_ids_list)):
        if account_id:
            account_ids[token_data['token']] = account_id
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

    # 启动定期检查和领取奖励
    asyncio.create_task(check_and_claim_rewards_periodically(use_proxy, tokens, proxies))

    await process_requests(use_proxy, tokens, proxies)

    # 定期更新账号信息
    while True:
        tasks = [asyncio.create_task(get_account_details(token['token'], index, use_proxy, proxies, account_ids[token['token']])) for index, token in enumerate(tokens)]
        await asyncio.gather(*tasks)
        await asyncio.sleep(300)  # 每5分钟更新一次

if __name__ == "__main__":
    asyncio.run(main())
