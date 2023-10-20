import json
import sys

import pandas as pd
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QFileDialog, QComboBox, QLineEdit, QInputDialog, QSizePolicy


class ImageViewer(QMainWindow):
    def __init__(self):
        self.selected_indices = []
        self.submit_flag = 0
        super().__init__()
        self.text_value = None
        self.data = []
        with open('csv_config.json', 'r') as json_file:
            self.data = json.load(json_file)
        self.combo_boxes = None
        self.len = None

        self.df = None
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 1400, 1200)
        self.current_row = 0
        self.load_current_row()
        print("loading")
        file_path, _ = QFileDialog.getOpenFileName(None, "", "打开文件", " (*.csv)")
        self.load_data_from_csv(file_path)
        print("load finished")
        #初始化UI
        self.initUI()
        # 创建包含 14 个独立下拉框的小部件
        self.create_combo_box_widget()
        # 显示第一张图片
        self.display_current_image()
        # 创建包含三个按钮的小部件
        self.create_button_widget()
    def load_current_row(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.current_row = config.get("current_row", 0)
        except FileNotFoundError:
            self.current_row = config.get("current_row", 0)

    def save_current_row(self):
        config = {"current_row": self.current_row}
        with open("config.json", "w") as f:
            json.dump(config, f)

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.vertical_layout = QVBoxLayout()

        self.load_label = QLabel()
        self.load_label.setFixedSize(600,200)
        font = QFont("Arial", 20)  # 20 是字体大小
        self.load_label.setFont(font)  # 设置组件的字体
        self.load_label.setAlignment(Qt.AlignCenter)
        # self.load_label.setContentsMargins(500,0,0,0)
        self.load_label.setText(f"当前是{self.current_row + 1}/总计{self.len}")
        self.vertical_layout.addWidget(self.load_label)

        # self.layout.addWidget(self.load_label)

        self.image_label = QLabel()
        self.image_label.setFixedSize(600, 600)
        self.vertical_layout.addWidget(self.image_label)
        self.vertical_layout.setContentsMargins(10, 10, 10, 200)  # 设置
        # self.layout.addWidget(self.image_label)

        self.layout.setContentsMargins(10, 10, 10, 10)  # 设置边距
        self.layout.addLayout(self.vertical_layout)

    def create_button_widget(self):
        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)

        self.save_button = QPushButton("保存")
        self.save_button.setFixedSize(200,50)
        self.save_button.setFont(QFont("Arial", 15))
        self.save_button.clicked.connect(self.save_data)
        button_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("删除")
        self.delete_button.setFixedSize(200,50)
        self.delete_button.setFont(QFont("Arial", 15))
        self.delete_button.clicked.connect(self.delete_image)
        button_layout.addWidget(self.delete_button)

        self.next_button = QPushButton("上一张图片")
        self.next_button.setFixedSize(200, 50)
        self.next_button.setFont(QFont("Arial", 15))
        self.next_button.clicked.connect(self.last_image)
        button_layout.addWidget(self.next_button)


        self.next_button = QPushButton("下一张图片")
        self.next_button.setFixedSize(200,50)
        self.next_button.setFont(QFont("Arial", 15))
        self.next_button.clicked.connect(self.next_image)
        button_layout.addWidget(self.next_button)

        self.layout.addWidget(button_widget)

    def create_combo_box_widget(self):
        combo_box_widget = QWidget()
        combo_box_layout = QVBoxLayout(combo_box_widget)

        self.combo_boxes = []
        for i in range(14):
            label = self.data[i][0]
            # print(label)
            combo_box_label = QLabel(label)  # 添加标签
            combo_box = QComboBox(self)
            combo_box.setFixedSize(400, 35)
            combo_box.setFont(QFont("Arial", 15)) # 20 是字体大小)
            combo_box.activated.connect(self.update_combo)
            combo_box.setContentsMargins(700,100,0,0)
            self.populate_combo_box(combo_box, i)
            combo_box_layout.addWidget(combo_box_label)
            combo_box_layout.addWidget(combo_box)
            self.combo_boxes.append(combo_box)
        combo_box_layout.addStretch(1)

        self.layout.addWidget(combo_box_widget)

    def populate_combo_box(self, combo_box, i):
        for r in range(len(self.data[i][1])):
            label1 = str(self.data[i][1][r])
            # print(label1)
            combo_box.addItem(label1)

    def update_combo(self):
        self.selected_indices = [combo_box.currentIndex() for combo_box in self.combo_boxes]
        self.update_feature()
        # print(self.selected_indices)

    def update_combo_value(self):
        for i, combo_box in enumerate(self.combo_boxes):
            combo_box.clear()  # 清空下拉框
            for r in range(len(self.data[i][1])):
                label2 = str(self.data[i][1][r])
                combo_box.addItem(label2)  # 添加新的项目
        # print(self.selected_indices)


    def update_feature(self):
        self.selected_indices = [combo_box.currentIndex() for combo_box in self.combo_boxes]
        for index, item in enumerate(self.selected_indices):
            col = index + 2
            # print(col)
            len_data = len(self.data[index][1]) - 1
            # print(len_data)
            if self.data[index][1][item] != '其他，请输入':
                value = self.data[index][1][item]
            else:
                value, ok = QInputDialog.getText(self, "输入标签", "请输入文本:", QLineEdit.Normal,
                                                 "")
                # value = self.text_value
                self.data[index][1].remove('其他，请输入')
                self.data[index][1].append(value)
                self.data[index][1].append('其他，请输入')
                with open("csv_config.json", "w") as f:
                    json.dump(self.data, f, indent=4)
                with open('csv_config.json', 'r') as json_file:
                    self.data = json.load(json_file)
                self.update_combo_value()

                    # 创建包含 14 个独立下拉框的小部件
            # print(self.df.iloc[self.current_row][col])

            self.df.iat[self.current_row, col] = value
            # print(self.df.iloc[self.current_row][col])

    def load_data_from_csv(self, excel_file):
        self.df = pd.read_csv(excel_file)
        # self.df = self.df.iloc[1:, :]
        self.len = len(self.df)

    def display_current_image(self):
        self.load_label.setText(f"当前是{self.current_row + 1}/总计{self.len}")
        if self.current_row < self.len:
            self.save_current_row()
            # print("当前是第", self.current_row + 1, "/", self.len, "张")
            image_url = self.df.iloc[self.current_row, 1]
            # print(image_url)
            # text = self.df.iloc[self.current_row, 2]  # Get text from the 3rd column
            self.image_label.setPixmap(self.get_pixmap_from_url(image_url))
            # self.text_label.setText(text)
        else:
            self.image_label.clear()

    def get_pixmap_from_url(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                image_data = response.content
                # 将图像数据加载到 QImage
                image = QImage.fromData(image_data)
                # 保持纵横比缩放图像
                scaled_image = image.scaled(self.image_label.size(), Qt.KeepAspectRatio,Qt.FastTransformation)
                pixmap = QPixmap.fromImage(scaled_image)
                return pixmap
            else:
                print(f"无法从URL获取图像：{url}")
                return None
        except Exception as e:
            self.save_data()
            print(f"发生错误：{e}")
            return None

    def next_image(self):
        # self.update_feature()
        self.current_row += 1
        self.display_current_image()
        if self.current_row + 1 > self.len:
            print("已完成")
            self.save_data()

    def last_image(self):

        self.current_row -= 1
        if self.current_row + 1 <= 0:
            self.current_row = 0
        self.display_current_image()

    def delete_image(self):

        if self.current_row < self.len:
            # self.df.drop(index=self.current_row, inplace=True)
            # self.df.reset_index(drop=True, inplace=True)
            # self.df.iat[self.current_row, :] = null
            self.df.iloc[self.current_row, 2:16] = 0
            self.current_row += 1
            self.display_current_image()

    def save_data(self):

        #  过滤掉第五列值为True的行,可以手动执行
        # self.df = self.df[self.df.iloc[:, 4] != True]

        save_path, _ = QFileDialog.getSaveFileName(self, "保存文件", "", " (*.csv)")
        if save_path:
            self.df.to_csv(save_path, index=False)

    # def key_press_event(self, event):
    #     key = event.key()
    #     if key == QtCoreQt.Key_Right:
    #         self.next_image()
    #     elif key == QtCoreQt.Key_Enter or key == QtCoreQt.Key_Return:
    #         self.delete_image()
    #     elif key == QtCoreQt.Key_3:
    #         self.save_data()
    #     elif key == QtCoreQt.Key_Left:
    #         self.last_image()

    def closeEvent(self, event):
        self.save_current_row()
        self.save_data()
        event.accept()


def main():
    # 读取JSON文件
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(f"发生错误: {e}")
        viewer.save_data()


if __name__ == "__main__":
    main()
