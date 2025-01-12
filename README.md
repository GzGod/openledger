# Openledger脚本
Openledger Bot 是一个简单的工具，旨在自动化节点交互。

## 功能
- **自动化节点交互**
- **代理支持**

## 环境要求
- Python3.11及以上

## 安装

1. 将仓库克隆到本地机器：
   ```bash
   git clone https://github.com/Gzgod/openledger.git
   ```
2. 进入项目目录：
   ```bash
   cd openledger
   ```
3. 安装必要的依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

1. 在运行脚本之前，设置 `account.txt` 和 `proxy.txt`（可选是否使用代理）。

   `account.txt` 文件格式（最新版本不需要，只需要把钱包地址填入wallets.txt即可）：
   ```
   token1:workerID1:id1:ownerAddress1
   token2:workerID2:id2:ownerAddress2
   ```
   
   （最新版本不需要此步骤 跳过即可）获取 `Token`、`WorkerID`、`id` 和 `ownerAddress`，教程如下：
   - 首先注册账户，您可以 [点击这里注册](https://testnet.openledger.xyz/?referral_code=ly6qkqged4)
   - 下载 [扩展程序](https://chromewebstore.google.com/detail/teneo-community-node/emcclcoaglgcpoognfiggmhnhgabppkm)
   - 打开扩展程序，在插件页面右键点击并选择 `检查` 注意先不要登录
   - ![1571736485417_ pic](https://github.com/user-attachments/assets/92b3f147-2f9a-43a2-be28-c355817ff22a)
   - 转到 `network` 标签 ![1581736485417_ pic](https://github.com/user-attachments/assets/f319cc05-ef98-4ce0-a900-0653f6fd7821)
   - 此时登录到您的账户，登录后再次选择 `network` 标签，搜索 `(orch?auth...)` 并打开 
   - 打开 `payload` 标签并复制 `bearer/authtoken`![1601736485417_ pic](https://github.com/user-attachments/assets/63023cf1-7e9b-4f4d-b864-032922485b84)
   - 打开 `message` 标签并复制 `WorkerID/identity`、`id` 和 `ownerAddress` ![1591736485417_ pic_hd](https://github.com/user-attachments/assets/1d9cd15a-d1e7-4efa-86d4-7756955ce15d)

3. 如果您想使用代理，请修改 `proxy.txt` 文件，格式如下：
   ```
   username:password@ip:port
   ```

4. 运行脚本：
   ```bash
   python main.py或者python3 main.py
   ```

## PS:不要删除 `data.json`！
