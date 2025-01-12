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

# 读取钱包地址
def read_wallets() -> List[str]:
    try:
        with open('wallets.txt', 'r') as f:
            return [line.strip() for line in f.read().split('\n') if line.strip()]
    except FileNotFoundError:
        print('读取 wallets.txt 时出错：文件未找到')
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
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print('未找到现有的数据存储，初始化新存储。')
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
async def get_or_generate_token(address, use_proxy, proxies, index, retries=3, delay=3000):
    data_store = read_or_init_data_store()
    if address in data_store and data_store[address].get('token'):
        return data_store[address]['token']

    url = 'https://apitn.openledger.xyz/api/v1/auth/generate_token'
    proxy = proxies[index % len(proxies)] if use_proxy and proxies else None
    headers = {'Content-Type': 'application/json'}
    data = {'address': address}

    attempt = 1
    while attempt <= retries:
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
                'id': str(uuid4())
            }
            with open('data.json', 'w') as f:
                json.dump(data_store, f, indent=2)
            return token
        except requests.RequestException as e:
            print(f"为地址 {address} 生成 token 时出错，第 {attempt} 次尝试: {str(e)}")
            if attempt < retries:
                print(f"在 {delay / 1000} 秒后重试...")
                await asyncio.sleep(delay / 1000)
                attempt += 1
            else:
                print(f"所有重试尝试失败。")
                return None

# 获取账号ID
async def get_account_id(address, index, use_proxy, proxies):
    token = await get_or_generate_token(address, use_proxy, proxies, index)
    if not token:
        return None

    url = 'https://apitn.openledger.xyz/api/v1/users/me'
    headers = {'Authorization': f'Bearer {token}'}
    proxy = proxies[index % len(proxies)] if use_proxy and proxies else None
    proxy_text = proxy or 'False'

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
        print(f"获取地址 {address} 的账户ID时出错: {str(e)}")
        return None

# 获取账号详细信息
async def get_account_details(token, index, use_proxy, proxies, account_id, retries=3, delay=60000):
    # ... (保持不变)

# 检查并领取奖励
async def check_and_claim_reward(token, index, use_proxy, proxies, retries=3, delay=60000):
    # ... (保持不变)

# 定期检查和领取奖励
async def check_and_claim_rewards_periodically(use_proxy, wallets, proxies):
    while True:
        tasks = [asyncio.create_task(check_and_claim_reward(await get_or_generate_token(wallet, use_proxy, proxies, idx), idx, use_proxy, proxies)) for idx, wallet in enumerate(wallets)]
        await asyncio.gather(*tasks)
        await asyncio.sleep(12 * 60 * 60)  # 每12小时检查一次

# WebSocket连接
async def connect_websocket(address, index, use_proxy, proxies):
    token = await get_or_generate_token(address, use_proxy, proxies, index)
    if not token:
        print(f"无法获取token，跳过 {address}")
        return

    data_store = read_or_init_data_store()
    wallet_info = data_store.get(address, {})
    workerID = wallet_info.get('workerID', base64.b64encode(address.encode()).decode())
    id = wallet_info.get('id', str(uuid4()))
    
    ws_url = f"wss://apitn.openledger.xyz/ws/v1/orch?authToken={token}"
    proxy = proxies[index % len(proxies)] if use_proxy and proxies else None
    
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
                        'ownerAddress': address,
                        'type': 'LWEXT'
                    }
                }
            }
            ws.send(json.dumps(register_message))

            # 发送心跳
            while True:
                # 获取最新的账户详细信息
                await get_account_details(token, index, use_proxy, proxies, account_ids.get(token, ''), retries=1, delay=0)

                # 使用全局变量来获取最新数据
                heartbeat_message = {
                    'message': {
                        'Worker': {
                            'Identity': workerID,
                            'ownerAddress': address,
                            'type': 'LWEXT',
                            'Host': 'chrome-extension://ekbbplmjjgoobhdlffmgeokalelnmjjc'
                        },
                        'Capacity': {
                            'AvailableMemory': round(random.uniform(0, 32), 2),
                            'AvailableStorage': get_or_assign_resources(address, data_store)['storage'],
                            'AvailableGPU': get_or_assign_resources(address, data_store)['gpu'],
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
async def process_requests(use_proxy, wallets, proxies):
    tasks = []
    for index, address in enumerate(wallets):
        tasks.append(asyncio.create_task(get_account_id(address, index, use_proxy, proxies)))
    
    account_ids_list = await asyncio.gather(*tasks)
    
    tasks = []
    for index, (address, account_id) in enumerate(zip(wallets, account_ids_list)):
        if account_id:
            token = await get_or_generate_token(address, use_proxy, proxies, index)
            if token:
                account_ids[token] = account_id  # 使用token作为键
                tasks.append(asyncio.create_task(get_account_details(token, index, use_proxy, proxies, account_id)))
                tasks.append(asyncio.create_task(connect_websocket(address, index, use_proxy, proxies)))
    await asyncio.gather(*tasks)
    return account_ids

# 主函数
async def main():
    display_header()
    use_proxy = input('您想使用代理吗？(y/n): ').lower() == 'y'
    wallets = read_wallets()
    proxies = read_proxies()
    
    if len(proxies) < len(wallets) and use_proxy:
        print('代理数量少于钱包数量，请提供足够的代理。')
        return

    # 启动定期检查和领取奖励
    asyncio.create_task(check_and_claim_rewards_periodically(use_proxy, wallets, proxies))

    await process_requests(use_proxy, wallets, proxies)

    # 定期更新账号信息
    while True:
        tasks = [asyncio.create_task(get_account_details(await get_or_generate_token(wallet, use_proxy, proxies, idx), idx, use_proxy, proxies, account_ids.get(await get_or_generate_token(wallet, use_proxy, proxies, idx), ''))) for idx, wallet in enumerate(wallets)]
        await asyncio.gather(*tasks)
        await asyncio.sleep(300)  # 每5分钟更新一次

if __name__ == "__main__":
    asyncio.run(main())
account_ids = {}
data_store = {}

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

# WebSocket连接
async def connect_websocket(address, index, use_proxy, proxies):
    data_store = read_or_init_data_store()
    if address not in data_store or 'token' not in data_store[address]:
        print(f"Error: No token found for address {address}")
        return

    token = data_store[address]['token']
    workerID = data_store[address]['workerID']
    id = data_store[address]['id']

    ws_url = f"wss://apitn.openledger.xyz/ws/v1/orch?authToken={token}"
    # 修正代理获取方式
    proxy = proxies[index] if use_proxy and proxies else None
    
    while True:
        try:
            if proxy:
                # 确保这里的 proxy 是正确的格式
                proxy_parts = proxy.split('@')
                if len(proxy_parts) == 2:
                    proxy_user_pass, proxy_host_port = proxy_parts
                    proxy_user, proxy_pass = proxy_user_pass.split(':')
                    proxy_host, proxy_port = proxy_host_port.split(':')
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
                        'ownerAddress': address,
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
                            'ownerAddress': address,
                            'type': 'LWEXT',
                            'Host': 'chrome-extension://ekbbplmjjgoobhdlffmgeokalelnmjjc'
                        },
                        'Capacity': {
                            'AvailableMemory': round(random.uniform(0, 32), 2),
                            'AvailableStorage': get_or_assign_resources(address, data_store)['storage'],
                            'AvailableGPU': get_or_assign_resources(address, data_store)['gpu'],
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

# 检查并领取奖励
async def check_and_claim_rewards_periodically(use_proxy, wallets, proxies):
    while True:
        tasks = [asyncio.create_task(check_and_claim_reward(data_store[address]['token'], address, index, use_proxy, proxies)) for index, address in enumerate(wallets)]
        await asyncio.gather(*tasks)
        await asyncio.sleep(12 * 60 * 60)  # 每12小时检查一次

async def check_and_claim_reward(token, address, index, use_proxy, proxies, retries=3, delay=60000):
    url = 'https://rewardstn.openledger.xyz/api/v1/claim_details'
    claim_url = 'https://rewardstn.openledger.xyz/api/v1/claim_reward'
    headers = {'Authorization': f'Bearer {token}'}
    proxy = proxies[index % len(proxies)] if use_proxy and proxies else None

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
            print(f"领取地址 {address} 的奖励时出错，尝试 {attempt}: {str(e)}")
            if attempt < retries:
                print(f"在 {delay / 1000} 秒后重试...")
                await asyncio.sleep(delay / 1000)
            else:
                print(f"所有重试尝试都失败了。")

# 获取账号详细信息
async def get_account_details(token, index, use_proxy, proxies, account_id, retries=3, delay=60000):
    urls = [
        'https://rewardstn.openledger.xyz/api/v1/reward_realtime',
        'https://rewardstn.openledger.xyz/api/v1/reward_history',
        'https://rewardstn.openledger.xyz/api/v1/reward'
    ]
    headers = {'Authorization': f'Bearer {token}'}
    proxy = proxies[index % len(proxies)] if use_proxy and proxies else None
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
                else:
                    proxies_dict = {'https': f'http://{proxy}'}
            else:
                proxies_dict = None

            for url in urls:
                if proxies_dict:
                    response = requests.get(url, headers=headers, proxies=proxies_dict, timeout=10)
                else:
                    response = requests.get(url, headers=headers, timeout=10)
                
                response.raise_for_status()
                data = response.json()['data']

                if url == 'https://rewardstn.openledger.xyz/api/v1/reward_realtime':
                    print(f"\033[33m[{index + 1}]\033[0m 账户ID \033[36m{account_id}\033[0m 的实时奖励信息：")
                    print(f"    当前积分: \033[32m{data['points']}\033[0m")
                elif url == 'https://rewardstn.openledger.xyz/api/v1/reward_history':
                    print(f"\033[33m[{index + 1}]\033[0m 账户ID \033[36m{account_id}\033[0m 的奖励历史：")
                    for reward in data['history'][:5]:  # 只显示最近5条历史记录
                        print(f"    时间: \033[36m{reward['timestamp']}\033[0m, 类型: \033[36m{reward['type']}\033[0m, 数量: \033[32m{reward['amount']}\033[0m")
                elif url == 'https://rewardstn.openledger.xyz/api/v1/reward':
                    print(f"\033[33m[{index + 1}]\033[0m 账户ID \033[36m{account_id}\033[0m 的总奖励信息：")
                    print(f"    总积分: \033[32m{data['totalPoints']}\033[0m")
                    print(f"    总心跳次数: \033[32m{data['totalHeartbeats']}\033[0m")

            # 更新全局变量
            global total_heartbeats, total_points
            total_heartbeats = data['totalHeartbeats']
            total_points = data['totalPoints']

            return
        except requests.RequestException as e:
            print(f"获取账户ID {account_id} 的详细信息时出错，尝试 {attempt}: {str(e)}")
            if attempt < retries:
                print(f"在 {delay / 1000} 秒后重试...")
                await asyncio.sleep(delay / 1000)
            else:
                print(f"获取账户ID {account_id} 的详细信息失败，尝试次数已用尽。")
                return
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
