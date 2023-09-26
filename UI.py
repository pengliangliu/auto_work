import json
import sys
import pandas as pd
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt as QtCoreQt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QFileDialog


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.len = None
        self.df = None
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 1000, 800)  # 设置固定窗口大小

        self.initUI()

        # 从Excel文件加载数据
        print("loading")
        file_path, _ = QFileDialog.getOpenFileName(None, "", "打开文件", "Excel Files (*.xlsx)")
        self.load_data_from_excel(file_path)
        print("load finished")

        # 初始化当前行索引
        self.current_row = 0
        self.load_current_row()

        # 显示第一张图片
        self.display_current_image()

    def load_current_row(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.current_row = config.get("current_row", 0)
        except FileNotFoundError:
            self.current_row = config.get("current_row", 0) - 1

    def save_current_row(self):
        config = {"current_row": self.current_row}
        with open("config.json", "w") as f:
            json.dump(config, f)

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.image_label = QLabel()
        self.image_label.setFixedSize(500, 800)  # 设置图像显示区域大小
        self.layout.addWidget(self.image_label)

        self.text_label = QLabel()
        self.text_label.setAlignment(Qt.AlignCenter)  # Align text label to center
        self.layout.addWidget(self.text_label)

        self.button_layout = QVBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.next_button = QPushButton("下一张图片")
        self.next_button.clicked.connect(self.next_image)
        self.button_layout.addWidget(self.next_button)

        self.delete_button = QPushButton("删除")
        self.delete_button.clicked.connect(self.delete_image)
        self.button_layout.addWidget(self.delete_button)

        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_data)
        self.button_layout.addWidget(self.save_button)

        self.central_widget.setFocusPolicy(QtCoreQt.StrongFocus)
        self.central_widget.keyPressEvent = self.key_press_event

    def load_data_from_excel(self, excel_file):
        self.df = pd.read_excel(excel_file)
        self.len = len(self.df)

    def display_current_image(self):
        if self.current_row < self.len:
            self.save_current_row()
            print("当前是第", self.current_row + 1, "/", self.len, "张")
            image_url = self.df.iloc[self.current_row, 1]
            text = self.df.iloc[self.current_row, 2]  # Get text from the 3rd column
            self.image_label.setPixmap(self.get_pixmap_from_url(image_url))
            self.text_label.setText(text)
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
                scaled_image = image.scaled(self.image_label.size(), Qt.KeepAspectRatio)

                pixmap = QPixmap.fromImage(scaled_image)
                return pixmap
            else:
                print(f"无法从URL获取图像：{url}")
                return None
        except Exception as e:
            print(f"发生错误：{e}")
            return None

    def next_image(self):
        self.current_row += 1
        if self.current_row + 1 > self.len:
            print("已完成")
            self.save_data()

        self.display_current_image()

    def last_image(self):
        self.current_row -= 1
        if self.current_row + 1 <= 0:
            self.current_row = 0
        self.display_current_image()

    def delete_image(self):
        if self.current_row < self.len:
            # self.df.drop(index=self.current_row, inplace=True)
            # self.df.reset_index(drop=True, inplace=True)
            self.df.at[self.current_row, 4] = True
            self.current_row += 1
            self.display_current_image()

    def save_data(self):

        #  过滤掉第五列值为True的行,可以手动执行
        # self.df = self.df[self.df.iloc[:, 4] != True]

        save_path, _ = QFileDialog.getSaveFileName(self, "保存 Excel 文件", "", "Excel Files (*.xlsx)")
        if save_path:
            self.df.to_excel(save_path, index=False)

    def key_press_event(self, event):
        key = event.key()
        if key == QtCoreQt.Key_Right:
            self.next_image()
        elif key == QtCoreQt.Key_Enter or key == QtCoreQt.Key_Return:
            self.delete_image()
        elif key == QtCoreQt.Key_3:
            self.save_data()
        elif key == QtCoreQt.Key_Left:
            self.last_image()

    def closeEvent(self, event):
        self.save_current_row()
        self.save_data()
        event.accept()


def main():
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
