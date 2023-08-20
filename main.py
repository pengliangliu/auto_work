import pandas as pd
import psutil
import requests
from PIL import Image
from io import BytesIO
import threading
import  random


def display_image_from_url(url):
    global  img
    response = requests.get(url)
    if response.status_code == 200:
        image_data = BytesIO(response.content)
        img = Image.open(image_data)
        img.show()
    else:
        print(f"Failed to fetch image from URL: {url}")

def process_excel(excel_file):
    df = pd.read_excel(excel_file)  # 读取Excel文件
    print("load ok")
    current_row = 200 #
    total_rows = len(df)
    save_interval = 200  # 设置保存间隔

    while current_row < total_rows:
        process_list = []
        for proc in psutil.process_iter():
            process_list.append(proc)
        print("当前是第",current_row,"张")
        if random.random() < 0.15:
            df = df.drop(index=current_row)  # 删除当前行
            total_rows -= 1  # 更新总行数
            current_row += 1
        else :
            image_url = df.iloc[current_row, 1]  # 获取当前行的图片URL

            display_image_from_url(image_url)
            user_input = input("按1下一个,按2删除: ")
            for proc in psutil.process_iter():
                if not proc in process_list:
                    proc.kill()
            if user_input == '1':
                current_row += 1
            elif user_input == '2':
                df = df.drop(index=current_row)  # 删除当前行
                total_rows -= 1  # 更新总行数
                current_row += 1
            elif user_input == '3':
                df.to_excel("save.xlsx", index=False)  # 每隔20次保存一次
                print("save successfully")
            else:
                print("Please press 1 or 2 or 3.")

            if current_row % save_interval == 0:
                df.to_excel("save.xlsx", index=False)  # 每隔20次保存一次
                print("save successfully")

    # 最后保存剩余数据
    df.to_excel("save.xlsx", index=False)



def main():
    excel_file = "save.xlsx"  # 替换为你的Excel文件路径
    process_excel(excel_file)


if __name__ == "__main__":
    main()
