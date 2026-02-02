import requests
import urllib3
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 配置区域 ---
authToken = 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI3Zjg4OThiMjRjYzI3NTkyYWMxNWQ4NTU4MTQyMTFhNCIsImV4cCI6MTc3MDExMTU2OSwiaWF0IjoxNzcwMDI1MTY5fQ.MGB2-cpEaExUDYEZVQI-WGT4IxGjOvRzEANsiNO_KrBaZdJEGV_spJEhYS0Ziob8fXp3Q3a_rUMglqBNzZtpdw'
kcListSelect = 'kkxn=2025-2026&kkxqm=1&pageNo=1&pageSize=1000&pageNum=1&'

# 分数范围配置 
MIN_SCORE = 95
MAX_SCORE = 99

# 超时设置 (秒)
TIMEOUT_SETTING = 120

# --- Session设置 (自动重试与长连接) ---
session = requests.Session()
retry_strategy = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)

session.headers.update({
    'accept': 'application/json, text/plain, */*',
    'authorization': authToken,
    'origin': 'https://gs2.v.zzu.edu.cn',
    'referer': 'https://gs2.v.zzu.edu.cn/stu/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
})

def PingJiao(tkxsmdId):
    url = 'https://gs2.v.zzu.edu.cn/api/studentClient/kcpjzbXs/add'
    headers = {'content-type': 'application/json'}
    
    json_data = {
        'tkxsmdId': tkxsmdId,
        'pjnl': '无',
        'dfList': []
    }
    
 
    for i in range(1, 5):
        main_id = f'PJ0{i}'
        sub_list = []
        for j in range(1, 6):

            random_score = str(random.randint(MIN_SCORE, MAX_SCORE))
            sub_list.append({'kcpjzbId': f'{main_id}0{j}', 'df': random_score})
            
        json_data['dfList'].append({'kcpjzbId': main_id, 'dfList': sub_list})

    try:
        res = session.post(url, headers=headers, json=json_data, verify=False, timeout=TIMEOUT_SETTING)
        return res.json()
    except Exception as e:
        return {'status': 0, 'msg': str(e)}

if __name__ == '__main__':
    list_url = 'https://gs2.v.zzu.edu.cn/api/studentClient/kcpjzbXs/list'
    
    print(">>> 开始获取课程列表...")
    try:
        res = session.post(list_url, headers={'content-type': 'application/x-www-form-urlencoded'}, data=kcListSelect, verify=False, timeout=TIMEOUT_SETTING)
        data = res.json()
        
        if 'data' in data and 'rows' in data['data']:
            kcList = data['data']['rows']
            print(f">>> 共发现 {len(kcList)} 门课程，开始评教 (分数范围: {MIN_SCORE}-{MAX_SCORE})。\n")
            
            for index, kc in enumerate(kcList):
                print(f"[{index+1}/{len(kcList)}] {kc['kcmc']} ...", end="", flush=True)
                
                result = PingJiao(kc['tkxsmdId'])
                
                if result.get('status') == 1:
                    print(" [成功]")
                else:
                    print(f" [失败] {result}")
                
                time.sleep(0.5)
            print("\n>>> 全部完成。")
        else:
            print(f">>> 获取列表失败: {data}")

    except Exception as e:
        print(f"\n[错误] {e}")