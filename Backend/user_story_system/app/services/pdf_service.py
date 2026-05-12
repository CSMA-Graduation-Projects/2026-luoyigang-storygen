from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
import re
from datetime import datetime


# ========================
# 注册中文字体
# ========================
font_path = "C:/Windows/Fonts/simsun.ttc"
pdfmetrics.registerFont(TTFont("SimSun", font_path))


# ========================
#  Markdown 清洗函数
# ========================
def strip_markdown(text: str) -> str:
    if not text:
        return ""

    # 标题加粗
    text = re.sub(r"###\s*(.*)", r"<b>\1</b>", text)
    text = re.sub(r"##\s*(.*)", r"<b>\1</b>", text)
    text = re.sub(r"#\s*(.*)", r"<b>\1</b>", text)

    # 加粗斜体
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)

    # 列表
    text = re.sub(r"^\s*-\s+(.*)", r"• \1", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\*\s+(.*)", r"• \1", text, flags=re.MULTILINE)

    # 去掉多余代码符号
    text = re.sub(r"`(.*?)`", r"\1", text)

    # 换行
    text = text.replace("\n", "<br/>")

    return text


#  PDF 生成函数
def generate_pdf(requirement, sub_requirements, final_stories):
    filename = f"user_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join("outputs", filename)

    os.makedirs("outputs", exist_ok=True)

    doc = SimpleDocTemplate(filepath, pagesize=A4)

    styles = getSampleStyleSheet()

    # 标题样式
    title_style = ParagraphStyle(
        "TitleCN",
        parent=styles["Title"],
        fontName="SimSun",
        fontSize=18,
        leading=24,
        spaceAfter=12
    )

    # 小标题
    heading_style = ParagraphStyle(
        "HeadingCN",
        parent=styles["Heading2"],
        fontName="SimSun",
        fontSize=14,
        leading=20,
        spaceBefore=10,
        spaceAfter=6
    )

    # 正文
    body_style = ParagraphStyle(
        "BodyCN",
        parent=styles["BodyText"],
        fontName="SimSun",
        fontSize=11,
        leading=18
    )
    content = []
    # 标题
    content.append(Paragraph("多智能体用户故事生成报告", title_style))
    content.append(Spacer(1, 12))

    # 原始需求
    content.append(Paragraph("一、原始需求", heading_style))
    content.append(Paragraph(strip_markdown(requirement), body_style))
    content.append(Spacer(1, 12))

    # 子需求
    content.append(Paragraph("二、需求拆分", heading_style))
    for i, req in enumerate(sub_requirements, 1):
        clean_req = strip_markdown(req)
        content.append(Paragraph(f"{i}. {clean_req}", body_style))

    content.append(Spacer(1, 12))

    # 用户故事
    content.append(Paragraph("三、用户故事", heading_style))

    for i, story in enumerate(final_stories, 1):
        content.append(Paragraph(f"【子需求{i}】", heading_style))

        clean_story = strip_markdown(story)

        content.append(Paragraph(clean_story, body_style))
        content.append(Spacer(1, 10))

    # 构建 PDF
    doc.build(content)

    return filepath