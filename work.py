import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import threading

# def download_image(url, save_path):
#     response = requests.get(url)
#
#     if response.status_code == 200:
#         with open(save_path, 'wb') as file:
#             file.write(response.content)
#         print(f"Image downloaded and saved as {save_path}")
#     else:
#         print(f"Failed to download image from URL: {url}")


def display_image_from_url(url):
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
    current_row = 0
    total_rows = len(df)
    save_interval = 20  # 设置保存间隔

    while current_row < total_rows:
        image_url = df.iloc[current_row, 1]  # 获取当前行的图片URL（根据实际情况修改列索引）
        print("当前是第{current_row}张")
        display_image_from_url(image_url)

        user_input = input("按1下一个,按2删除: ")

        if user_input == '1':
            current_row += 1
        elif user_input == '2':
            df = df.drop(index=current_row)  # 删除当前行
            total_rows -= 1  # 更新总行数
        else:
            print("Please press 1 or 2.")

        if current_row % save_interval == 0:
            df.to_excel("save.xlsx", index=False)  # 每隔20次保存一次

    # 最后保存剩余数据
    df.to_excel("save.xlsx", index=False)

    # for index, row in df.iterrows():
    #     image_url = row[1]  # 根据实际情况进行修改
    #     display_image_from_url(image_url)

        # save_path = f"downloaded_images/image_{index + 1}.jpg"  # 图片保存的路径

        # download_image(image_url, save_path)

        # # 可以在此处添加更多的图像处理操作，如显示、裁剪等
        # img = Image.open(save_path)
        # img.show()


def main():
    excel_file = "sleeve_type.xlsx"  # 替换为你的Excel文件路径
    process_excel(excel_file)


if __name__ == "__main__":
    main()
