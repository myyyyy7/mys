from html.parser import HTMLParser
import csv
import os

# 定义一个继承自HTMLParser的自定义HTML解析器类
class TeachersHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        # 初始化数据结构以保存解析的教师信息
        self.teachers_info = []
        self.current_teacher = {}
        self.in_teacher_block = False
        self.in_name = False
        self.in_iden = False
        self.in_img = False

    # 遇到开始标签时的回调函数
    def handle_starttag(self, tag, attrs):
        if tag == "a" and any(attr[0] == "href" and "info" in attr[1] for attr in attrs):
            # 找到一个带有“info”的href属性的链接，表示教师块的开始
            self.in_teacher_block = True
        elif self.in_teacher_block and tag == "span":
            for attr, value in attrs:
                if attr == "class" and "name" in value:
                    # 找到一个带有“name”类的span，表示教师的姓名
                    self.in_name = True
                elif attr == "class" and "iden" in value:
                    # 找到一个带有“iden”类的span，表示教师的部门
                    self.in_iden = True
        elif self.in_teacher_block and tag == "img":
            for attr, value in attrs:
                if attr == "src":
                    # 找到一个图像标签，存储照片文件名（在最后一个斜杠之后的部分）
                    self.current_teacher["Photo"] = value.split("/")[-1]
                    self.in_img = True

    # 遇到标签内的数据时的回调函数
    def handle_data(self, data):
        if self.in_teacher_block:
            if self.in_name:
                # 在带有“name”类的span内的数据是教师的姓名
                self.current_teacher["Name"] = data.strip()
                self.in_name = False
            elif self.in_iden:
                # 在带有“iden”类的span内的数据是教师的部门
                self.current_teacher["Department"] = data.strip()
                # 从文件名中获取教师的职称
                self.current_teacher["Title"] = self.get_teacher_title()
                self.in_iden = False

    # 遇到结束标签时的回调函数
    def handle_endtag(self, tag):
        if tag == "a" and self.in_teacher_block:
            if self.in_img:
                self.in_img = False
            else:
                self.current_teacher["Photo"] = "未找到头像路径"  # 未找到照片的占位符
            self.in_teacher_block = False
            # 将当前教师的信息添加到列表中并清空current_teacher字典
            self.teachers_info.append(self.current_teacher.copy())
            self.current_teacher.clear()

    # 从HTML文件名中提取教师职称
    def get_teacher_title(self):
        filename = os.path.basename(self.html_filename)
        title = filename.split("-")[0].strip()
        return title

    # 设置HTML文件名以供参考
    def set_html_filename(self, filename):
        self.html_filename = filename

# 用实际的文件名替换'讲师-数字媒体与设计艺术学院.html'
html_filename = '讲师-数字媒体与设计艺术学院.html'

# 从文件中读取HTML内容
with open(html_filename, 'r', encoding='utf-8') as f:
    html_content = f.read()

# 创建自定义HTML解析器的实例
parser = TeachersHTMLParser()
parser.set_html_filename(html_filename)
# 解析HTML内容以提取教师信息
parser.feed(html_content)

# 将提取的信息写入CSV文件 不同的csv文件标题不同
with open('讲师.csv', 'w', encoding='utf-8', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # 写入标题行
    csvwriter.writerow(['Department', 'Name', 'Title', 'Photo'])

    # 将每位教师的信息写入CSV的一行
    for teacher in parser.teachers_info:
        csvwriter.writerow([
            teacher.get("Department", ""),
            teacher.get("Name", ""),
            teacher.get("Title", ""),
            teacher.get("Photo", "")
        ])

print("CSV文件保存成功！")
