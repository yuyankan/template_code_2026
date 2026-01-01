import googlemaps

import requests
import pandas as pd

PROXY_HOST = "127.0.0.1" 
PROXY_PORT = "9000"
PROXY_URL = f"http://{PROXY_HOST}:{PROXY_PORT}"

# requests 库使用的代理字典
PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL,
}

# google api key
GOOGLE_API_KEY  = 'AIzaSyBxBSmxUmfUV6bkAnzJS5kTXMtmB7S1oyY'

def geocode_address_google(address):
    """
    使用 googlemaps 库将地址转换为经纬度。

    """
    # 初始化 Google Maps 客户端
    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
    lon = None
    lat = None
    try:
        # 调用 geocode 方法
        geocode_result = gmaps.geocode(address)

        if geocode_result:
            # 提取第一个结果的位置信息
            location = geocode_result[0]['geometry']['location']
            lat = location['lat']
            lon = location['lng']
         
        else:
            print(f"Google Geocoding failed for {address}: No result found.")
          
            
    except Exception as e:
        print(f"Google API request error for {address}: {e}")
    
    df = pd.DataFrame([[address, lat, lon]], columns=['address', 'lat','lon'])
    
    return df


# use gaode

key_gaode = '7cdc431fbc1a34d3e085684d8df920b2'
def geocode_address_gaode(address,proxies=PROXIES, key=key_gaode):
    """
    使用高德地图 Web API 将地址转换为 (纬度 lat, 经度 lon)。

    参数:
    address (str): 要查询的地址字符串。
    key (str): 您的 Web 服务 API Key。

    返回:
    tuple: (latitude, longitude) 或 (None, None) 如果失败。
    """
    url = "https://restapi.amap.com/v3/geocode/geo"
    lon= None
    lat = None
    
    # 构造请求参数
    params = {
        "key": key,
        "address": address
    }

    try:
        response = requests.get(url, params=params, proxies=proxies, timeout=10) 
        response.raise_for_status()  # 检查 HTTP 错误 (如 4xx 或 5xx)
        data = response.json()

        # 检查 API 返回状态和结果数量
        if data['status'] == '1' and data['count'] == '1':
            
            # 1. 高德返回的 location 格式是 "lon,lat" (经度在前，纬度在后)
            location = data['geocodes'][0]['location']
            
            # 2. 分割字符串并转换为浮点数
            lon_str, lat_str = location.split(',')
            
            lon = float(lon_str)
            lat = float(lat_str)
            
            # 3. 严格按照要求返回 (lat, lon)
            #return lat, lon 
        else:
            # 查无此地址或 API 逻辑错误 (例如 'status' != '1' 或 'count' != '1')
            info = data.get('info', '未知错误')
            print(f"Geocoding failed for '{address}': {info}")
            #return None, None
            
    except requests.exceptions.RequestException as e:
        # 处理网络连接、超时等请求异常
        print(f"API request error for '{address}': {e}")
        #return None, None
    except ValueError:
        # 处理 location 字符串解析错误 (如果格式不是 "lon,lat")
        print(f"Location parsing error for '{address}': {location}")
        #return None, None
    
    df = pd.DataFrame([[address, lat, lon]], columns=['address', 'lat','lon'])
    return df



# 地球半径，单位：公里 (km)
R = 6371
import numpy as np

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    使用 Haversine 公式计算两点间的距离 (单位：公里)。
    适用于 Numpy 向量化操作。
    """
    # 转换为弧度
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    # 经纬度差值
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Haversine 公式
    a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance_km = R * c
    return distance_km


def calclate_distance(df_meta_clean, df_visit_1):
        # --- 2. 执行 Cross Join (笛卡尔积) ---
    # 将 df_visit_1 的每行与 df_meta_clean 的每行组合
    '''
    df_meta_clean:lon, lat, rename to lat12, lon13
    both dataframe have the column: address
    '''
    df_meta_clean.rename(columns={'lon':'lon12','lat':'lat12','address':'address_customer'}, inplace=True)
    df_visit_1.rename(columns={'address':'address_visit'}, inplace=True)
    df_visit_1['key'] = 1
    df_meta_clean['key'] = 1

    df_cross = pd.merge(df_visit_1, df_meta_clean, on='key').drop('key', axis=1)

    # --- 3. 计算所有点对的距离 ---
    df_cross['distance_km'] = haversine_distance(
    df_cross['lat'], df_cross['lon'],
    df_cross['lat12'], df_cross['lon12']
    )

    # --- 4. 找出最近邻居 ---
    # 找出每个 V_id 对应的最小距离的索引
    idx_min = df_cross.groupby('address_visit')['distance_km'].idxmin()

    # 选取最小距离对应的行
    df_nearest = df_cross.loc[idx_min]

    
    # --- 5. 整理输出 ---
    df_output = df_nearest[['address_visit',  'lat', 'lon', 
                            'address_customer', 'lat12', 'lon12', 'distance_km']].copy()

    df_output.rename(columns={'distance_km': 'Min_Distance_km',
                            'address_customer': 'Nearest_CUSTOMER_NAME',
                            'lat12': 'Nearest_lat',
                            'lon12': 'Nearest_lon',
                            #'address':'visited_address',
                            'lat':'visited_lat',
                            'lon':'visited_lon',

                            }, inplace=True)

    df_output['Min_Distance_km'] = df_output['Min_Distance_km'].round(4)

    # --- 1. 定义分箱边界和标签 ---

    # 定义边界 (bins): 必须包含最小和最大值
    # 0 (最小值) -> 5 -> 10 -> 20 -> 30 -> 50 -> 100 -> 无穷大 (np.inf)
    bins = [0, 1,2,5, 10, 20, 30, 50, 100, np.inf]

    # 定义标签 (labels)
    # 标签的数量必须比边界少一个
    labels = [
        '< 1 km (精确匹配/楼宇级别)',
        '1 - 2 km',
        '2 - 5 km',
        '5 - 10 km (街区/街道级别)',
        '10 - 20 km (乡镇/次区域级别)',
        '20 - 30 km (区/县级别)',
        '30 - 50 km (中等区域/市级别)',
        '50 - 100 km (城市/跨市级别)',
        '> 100 km (远距离/非匹配)'
    ]

    # --- 2. 执行分箱操作 ---
    df_output['Distance_Level'] = pd.cut(
        df_output['Min_Distance_km'], 
        bins=bins, 
        labels=labels, 
        right=False  # 设置为 False 意味着区间是 [a, b)，左闭右开。
    )
    return df_output



def search_poi_gaode(query_address, key=key_gaode):
    """调用高德POI搜索API并处理结果"""

    params = {
    'key': key,
    'keywords': query_address,
    'offset': 1,
    'extensions': 'base'
    # 'city': '',  # 广域搜索时不设置此参数
    }
    url = 'https://restapi.amap.com/v3/place/text'
    print(f"--- 正在查询：{params['keywords']} ---")
    
    try:
        response = requests.get(url, params=params, proxies=PROXIES)
        response.raise_for_status() # 检查HTTP请求是否成功
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误：{e}")
        return

    # 检查高德API返回的状态码
    if data['status'] == '1' and int(data['count']) > 0  and len(data.get('pois', [])) > 0:
        # 取第一个（匹配度最高）的结果
        poi = data['pois'][0]
        
        # 提取关键信息
        name = poi.get('name', 'N/A')
        address_raw = poi.get('address', 'N/A')
        location = poi.get('location', 'N/A')

        # 检查 address 是否为列表且是否为空
        if isinstance(address_raw, list) and len(address_raw) == 0:
            address = 'N/A' # 或 ''，确保它是一个标量
        else:
            address = address_raw
        
        # 解析经纬度
        try:
            lon, lat = location.split(',')
        except:
            lon, lat = 'N/A', 'N/A'
            
        print("✅ 找到最佳匹配结果：")
        print(f"   名称: {name}")
        print(f"   地址: {address}")
        print(f"   经度: {lon}")
        print(f"   纬度: {lat}")
        print("-" * 30)
        
        # 返回找到的坐标和完整名称，方便后续批量处理
        result= {
          
            'query': query_address,
            'name': name,
            'lon': lon,
            'lat': lat,
            'address': address
        }
        return pd.DataFrame(result, index=[0])
        
    else:
        # 如果 count=0 或 status!=1，则未找到
        info = data.get('infocode', 'N/A')
        print(f"❌ 未找到匹配结果或API错误。错误码: {info}")
        print("-" * 30)
        return None





def reverse_geocode_amap(address_query,lon, lat, key=key_gaode):
    """
    通过高德地图API进行逆地理编码，获取省市信息。

    Args:
        lon (float): 经度 (Longitude)。
        lat (float): 纬度 (Latitude)。
        key (str): 你的高德 Web 服务 Key。

    Returns:
        dict: 包含 'province', 'city', 'district' 的字典，如果失败则返回 None。
    """
    url = "https://restapi.amap.com/v3/geocode/regeo"
    
    # 高德 API 接收经纬度格式为 lon,lat
    location = f"{lon},{lat}"
    
    params = {
        "key": key,
        "location": location,
        "extensions": "base",  # 只返回基础信息，加快速度
        "output": "json"
    }
    
    try:
        response = requests.get(url, params=params,proxies=PROXIES)
        response.raise_for_status() # 检查HTTP请求是否成功 (状态码200)
        data = response.json()
        
        if data['status'] == '1' and data.get('regeocode'):
            address = data['regeocode']['addressComponent']
            
            # 高德返回的 'city' 字段，如果该点位于直辖市，则 city 字段为空
            # 此时 province 字段就是直辖市的名称
            result =  {
                'province': address.get('province', '') or address.get('city', ''),
                'city': address.get('city', '') or address.get('district', ''),
                'district': address.get('district', ''),
                'query':address_query,
                'lon':lon,
                'lat':lat
            }
            #print(result)
            # 检查 address 是否为列表且是否为空
            if isinstance(result['province'], list) and len(result['province']) == 0:
                result['province'] = 'N/A' # 或 ''，确保它是一个标量


            if isinstance(result['city'], list) and len(result['city']) == 0:
                result['city'] = 'N/A' # 或 ''，确保它是一个标量

            if isinstance(result['district'], list) and len(result['district']) == 0:
                result['district'] = 'N/A' # 或 ''，确保它是一个标量
           



            return pd.DataFrame(result, index=[0])
        
        else:
            print(f"API调用失败或结果为空: {data.get('info')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        return None
    except json.JSONDecodeError:
        print("API返回数据格式错误。")
        return None
