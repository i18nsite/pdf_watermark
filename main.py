#!/usr/bin/env python

import csv
from os import listdir
from pikepdf import Pdf, Rectangle
from pathlib import Path
from reportlab.lib import units
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sys
from os.path import dirname, join, abspath
from datetime import datetime
from config import 水印视图宽度, 水印列数, 水印行数, 水印后缀

# 兼容 PyInstaller 打包后的路径获取
if getattr(sys, 'frozen', False):
    # 如果是打包后的环境
    PWD = dirname(abspath(sys.executable))
else:
    # 如果是普通的 python 环境
    PWD = dirname(abspath(__file__))

INPUT = join(PWD, "input")
OUT = join(PWD, "out", str(datetime.today())[:10])
DONE = join(PWD, "done")

for dirpath in [OUT, INPUT, DONE]:
    result = Path(dirpath)
    result.mkdir(exist_ok=True, parents=True)


def 加水印(input_fp, name, file):
    # 必须每次重新打开PDF，因为添加水印是inplace的操作
    target = Pdf.open(join(INPUT, input_fp))
    water_mark_pdf = Pdf.open(str(file))
    water_mark = water_mark_pdf.pages[0]

    for page in target.pages:
        for x in range(水印列数):  # 每一行显示多少列水印
            for y in range(水印行数):  # 每一页显示多少行PDF
                page.add_overlay(
                    water_mark,
                    Rectangle(
                        page.trimbox[2] * x / 水印列数,
                        page.trimbox[3] * y / 水印行数,
                        page.trimbox[2] * (x + 1) / 水印列数,
                        page.trimbox[3] * (y + 1) / 水印行数,
                    ),
                )

    result_name = Path(OUT, input_fp[:-4] + f"-{name}.pdf")
    print(result_name)
    target.save(str(result_name))


with open(join(PWD, "user.csv"), encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    li = [x["name"] for x in reader]

FONT = "AliHYAiHei"

pdfmetrics.registerFont(TTFont(FONT, join(PWD, FONT + ".ttf")))  # 加载中文字体

INPUT_PDF = list(i for i in listdir(INPUT) if i.endswith(".pdf"))
print(f"当前目录 {PWD}\n输入文件 {INPUT_PDF}")

for name in li:
    path = PWD / Path("tmp.pdf")
    # 生成画布，长宽都是水印视图宽度毫米
    c = canvas.Canvas(
        str(path), pagesize=(水印视图宽度 * units.mm, 水印视图宽度 * units.mm)
    )
    padding = 0.1
    c.translate(
        padding * 水印视图宽度 * units.mm, (1 - padding) * 水印视图宽度 * units.mm
    )
    c.rotate(315)  # 把水印文字旋转315°
    c.setFont(FONT, 35)  # 字体大小
    c.setStrokeColorRGB(0, 0, 0)  # 设置字体颜色
    c.setFillColorRGB(0, 0, 0)  # 设置填充颜色
    c.setFillAlpha(0.1)  # 设置透明度，越小越透明
    c.drawString(0, 0, f"{name}{水印后缀}")
    c.save()
    input_fp = join(PWD, "input.pdf")
    for i in INPUT_PDF:
        加水印(i, name, path)
    path.unlink()

DONE = Path(DONE)
for i in INPUT_PDF:
    (Path(INPUT) / i).rename(DONE / i)

if sys.platform.startswith('win'):
    input("\n运行完成，按任意键退出...")
