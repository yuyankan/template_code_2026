import requests
import json
import pandas as pd

#global variant:
#webhook for chat
YOUR_WEBHOOK_URL = f'''https://chat.googleapis.com/v1/spaces/AAQARHhbJxE/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=0D_SgC3KnOqbXh6iP2rK-qbL9n-1ciym4hZCQEcmp4k''' # 示例URL，请替换
#daily data link
web_link='http://dbpdksp03:8501'


def dataframe_to_markdown_string(df, max_rows=5, index=False):
    """
    将 Pandas DataFrame 转换为 Markdown 表格格式的字符串。

    参数:
    df (pd.DataFrame): 需要转换的 DataFrame。
    max_rows (int): 最多显示的行数。
    index (bool): 是否在 Markdown 输出中包含 DataFrame 的索引。

    返回:
    str: Markdown 格式的表格字符串。
    """
    if df.empty:
        return "没有数据可显示。"
    
    # 为了性能和输出简洁，只转换需要显示的行数
    df_subset = df.head(max_rows)
    return df_subset.to_markdown(index=index)



def send_to_google_chat(webhook_url, alert_title, subtitle, dataframe_for_table,use_code_block=True,web_link=''):
    """
    发送包含SPC报警信息（包括表格）到 Google Chat。
    """
    # DataFrame 的列名作为表格标题
  


    markdown_table_str = dataframe_to_markdown_string(dataframe_for_table, max_rows=5)

    # 根据选择，是否将 Markdown 表格包裹在代码块中
    if use_code_block:
        # 使用代码块可能会让 Chat 使用等宽字体，有助于对齐
        # 注意：如果 Markdown 表格内容本身包含 ```，可能会导致显示问题
        display_text = f"```\n{markdown_table_str}\n```"
    else:
        display_text = markdown_table_str
    print(display_text)

    message_payload ={
    "cardsV2": [
        {
        "cardId": "simple_test_card",
        "card": {
         
            "sections": [
            {
                    "widgets": [
                                     {"decoratedText": {
                                        # "topLabel": "报警详情:", # 可以在表格文本上方再加一个标签
                                        "text": f'<b><font color="#FF0000">{alert_title}:</font></b>',
                                        "wrapText": True # 允许文本换行，对于长文本或多行表格很重要
                                    }
                                },
                                {"decoratedText": {
                                        # "topLabel": "报警详情:", # 可以在表格文本上方再加一个标签
                                         "text": f'{subtitle}',
                                        "wrapText": True # 允许文本换行，对于长文本或多行表格很重要
                                    }
                                },
                                {
                                   
                                    "decoratedText": {
                                        # "topLabel": "报警详情:", # 可以在表格文本上方再加一个标签
                                        "text": display_text,
                                        "wrapText": True # 允许文本换行，对于长文本或多行表格很重要
                                    }}
                            ]
            
        }]
        }
    }
    ]
}
    #json_to_send = json.dumps(message_payload, ensure_ascii=False) # ensure_ascii=False 对中文字符友好
    #print("--- 即将发送的 JSON 负载 ---")
    #print(json_to_send)
    #print("---------------------------")


    try:
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        response = requests.post(webhook_url, headers=headers, data=json.dumps(message_payload))
        response.raise_for_status()  # 如果 HTTP 请求返回了错误状态码 (4xx or 5xx)，则会抛出异常
        print(f"消息发送成功！状态码: {response.status_code}")
        # print(f"响应内容: {response.text}") # 可以取消注释查看响应详情
    except requests.exceptions.RequestException as e:
        print(f"发送消息时发生错误: {e}")

def work(df_outlierdf_outlier, YOUR_WEBHOOK_URL=YOUR_WEBHOOK_URL):
    # ！！重要！！请将下面的 URL 替换成你自己的 Google Chat Webhook URL
    
    if df_outlierdf_outlier.empty:
        return
    
    alert_title="SPC ALARM: out of spec/control line"
    subtitle="part data as below (only show 5 rows): \nmore data could be found in link: http://dbpdksp03:8501/"
    send_to_google_chat(
        webhook_url=YOUR_WEBHOOK_URL,
        web_link='',
        alert_title=alert_title,
        subtitle=subtitle,
        dataframe_for_table=df_outlierdf_outlier
    )


if __name__=='__main__':
    df_test = pd.DataFrame([[1, 2, 3],[4, 5, 6]], columns=['a','b','c'])
    work(df_test)