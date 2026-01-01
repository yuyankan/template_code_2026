import requests
import pandas as pd


#google form url: sent destination
FORM_RESPONSE_URL = 'https://docs.google.com/forms/d/e/1FAIpQLSeZSnv-mHt5rm64RYmBqMk93p9vqYbP72m6-arbKBCIA1AMyQ/formResponse'
#columns to fill: have to use entry.: get from preview status
ENTRY_ID_RECIPIENT = 'entry.1188192507'
ENTRY_ID_SUBJECT = 'entry.1391353938'
ENTRY_ID_MESSAGE = 'entry.1686033344'


# --- 尝试本地代理 ---
# 这个本地代理应该能处理到 Zscaler 云的连接和认证
local_proxy_url = "http://127.0.0.1:9000"
proxies = {
  "http": local_proxy_url,
  "https": local_proxy_url, # 重要：HTTPS 流量也通过这个本地 HTTP 代理地址
}


def dataframe_to_html(df: pd.DataFrame, title: str = "", description: str = "") -> str:
    
    table_html = df.to_html(index=False, border=0, classes="dataframe-table", escape=False)
    return f"""
    <h3 style="color: #2c3e50;">{title}</h3>
    <p style="font-style: italic; color: #666;">{description}</p>
    {table_html}
    """

def generate_html_email_v2(content_title: str, content_detail: str,content_detail_link:str,
                           table_sections: list[dict],
                           image_sections: list[dict]) -> str:
    
    df_parts = "".join([dataframe_to_html(sec["df"], sec["title"], sec["description"]) for sec in table_sections])
    img_parts = "".join([
        f"""
        <div style="margin-bottom:20px;">
          <img src="{img['url']}" alt="图像" style="max-width:600px;" />
          <p style="font-style: italic; color: #555;">{img['caption']}</p>
        </div>
        """ for img in image_sections
    ])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: Arial, sans-serif; color: #333; }}
        h2 {{ color: #d32f2f; }}
        table.dataframe-table {{
          border-collapse: collapse;
          width: 100%;
          margin-bottom: 20px;
        }}
        table.dataframe-table th {{
          background-color: #f44336;
          color: white;
          font-weight: bold;
          padding: 8px;
          border: 1px solid #ddd;
        }}
        table.dataframe-table td {{
          padding: 8px;
          border: 1px solid #ddd;
          text-align: center;
        }}
      </style>
    </head>
    <body>
      <h2>{content_title}</h2>
      <p>{content_detail}<a href={content_detail_link}>Link</a></p>
      {df_parts}
      <h3>📷 图片部分</h3>
      {img_parts}
    </body>
    </html>
    """
    return html





def submit_email_request_to_form(recipient_email, subject, message_body):
    """
    recipient_email: destination, "r1@xxx, r2@xxx"
    subject: for email;
    message_body: content: html style
    
    """
    form_data = {
        ENTRY_ID_RECIPIENT: recipient_email,
        ENTRY_ID_SUBJECT: subject,
        ENTRY_ID_MESSAGE: message_body,
    }
    try:
        print(f"正在向 Google Form 提交数据...")
        print(f"目标 URL: {FORM_RESPONSE_URL}")
        print(f"表单数据: {form_data}")
        if proxies.get("https"):
             print(f"尝试使用本地代理: {proxies.get('https')}")

        response = requests.post(FORM_RESPONSE_URL, data=form_data, timeout=30, proxies=proxies)
        response.raise_for_status()

        if response.status_code == 200:
            print("表单数据已成功提交到 Google Form (通过本地代理)。")
            return True
        else:
            print(f"表单提交可能未成功，状态码: {response.status_code}")
            return False
    except requests.exceptions.ProxyError as pe:
        print(f"代理错误 (本地代理 {local_proxy_url}): {pe}")
        print("请确保本地代理服务 (如 Zscaler Client Connector) 正在运行并且端口正确。")
        return False
    except requests.exceptions.ConnectTimeout:
        print(f"错误：连接到本地代理 {local_proxy_url} 或通过代理连接到目标服务器超时。")
        return False
    except requests.exceptions.ConnectionError as ce:
        print(f"错误：无法连接到本地代理 {local_proxy_url} 或通过代理连接到目标服务器。错误: {ce}")
        return False
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误发生: {http_err} (状态码: {http_err.response.status_code})")
        print("服务器响应:", http_err.response.text)
        return False
    except requests.exceptions.RequestException as e:
        print(f"提交表单时发生未知请求错误: {e}")
        return False
    except Exception as e:
        print(f"在 submit_email_request_to_form 函数中发生意外错误: {e}")
        return False


def html_df(df_list, df_titles_list, df_description_list):
    table_sections = []
    for df , t, d in zip(df_list, df_titles_list, df_description_list):
        temp = { "title": t, 
                "df":df , 
                "description": d }
        table_sections.append(temp)
    
    return table_sections


def html_image( pic_url_list, pic_description_list):
    image_sections = []
    for p , c in zip(pic_url_list, pic_description_list):
        temp = { "url": p, 
                "caption":c  }
        image_sections.append(temp)

    return image_sections

from typing import List
def work(df_list, df_titles_list=[], df_description_list=[],pic_url_list=[],pic_description_list=[]):

    receivers = "caren.kan@ap.averydennison.com,caren.kan@ap.averydennison.com"
    content_title = "Hi,<br> SPC out of spec/control line. "
    content_detail = "Part data as below (only show 5 rows): more data could be found in:"
    content_detail_link = "http://dbpdksp03:8501/"
    table_sections = html_df(df_list, df_titles_list, df_description_list)
    image_sections = html_image( pic_url_list, pic_description_list)

   
    message_html = generate_html_email_v2(content_title=content_title, 
                                          content_detail=content_detail,
                                          content_detail_link=content_detail_link,
                                          table_sections=table_sections,
                                          image_sections=image_sections
                                          )
    
 
    subject = "SPC ALARM"

    print("开始尝试通过 Google Form 发送邮件 (使用本地代理配置)...")
    success = submit_email_request_to_form(recipient_email=receivers, subject=subject, message_body=message_html)
    if success:
        print("Python 脚本已将请求提交给 Google Form。请检查 Apps Script 日志和目标邮箱。")
    else:
        print("Python 脚本未能成功将请求提交给 Google Form。")


if __name__=="__main__":
    # 每个表格包含：标题 + df + 说明段 

    
    df_test = pd.DataFrame([[1, 2, 3],[4, 5, 6]], columns=['a','b','c'])

        #examples:
    table_sections = [{ "title": "🔌 电压异常设备", "df": df_test, 
                        "description": "检测到 2 台设备电压偏离正常值范围（210~250V）。" }, 
                        { "title": "🌡️ 温度超标设备", "df": df_test, 
                        "description": "连续监控发现 B 类设备长时间温度超 75°C，存在过热风险。" } 
                        ]
    # 每张图包含：图片地址 + 说明文字 
    image_sections = [ { "url": "https://example.com/image1.jpg", "caption": "电压异常现场图（A1 位置）" }, 
                    { "url": "https://example.com/image2.jpg", "caption": "温度曲线图（B 类设备）" } ]

    df_list = [df_test, df_test]
    df_titles_list = ["mail test", "mail 2m2m2"]
    df_description_list = ["hhh","h2h2"]
    pic_url_list = ["https://example.com/image1.jpg","https://example.com/image1.jpg"]
    pic_description_list = ["类设备长时间温度超","连续监控发现"]
    #work(df_list,df_titles_list,df_description_list,pic_url_list,pic_description_list)
    work(df_list)