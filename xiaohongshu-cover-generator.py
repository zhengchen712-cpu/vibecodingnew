#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书招聘封面自动生成器
功能：根据用户输入，自动生成标志性建筑背景图，合成最终封面
使用已有的 image-generate 技能生成图片
"""

import os
import sys
import re
import subprocess
from PIL import Image, ImageDraw, ImageFont

def generate_building_image(building_name):
    """使用 AI 生成标志性建筑图片 - 调用现有的 image-generate 脚本"""
    
    prompt = f"{building_name}，标志性建筑，专业摄影，高清，蓝色调渐变背景，适合做封面背景，构图下半部分是建筑，上半部分留白，安静专业氛围"
    
    print(f"🔄 正在生成 {building_name} 图片...")
    
    # 调用现有的 image-generate 脚本，它已经能正常工作
    script_dir = "/root/.openclaw/workspace/skills/image-generate/scripts"
    script_path = os.path.join(script_dir, "image_generate.py")
    
    # 运行脚本生成图片 - 脚本生成的文件在脚本目录
    result = subprocess.run(
        ["python", script_path, prompt],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=script_dir
    )
    
    if result.returncode != 0:
        print(f"❌ 生成失败: {result.stderr}")
        return None
    
    # 从输出提取图片路径
    output = result.stdout
    print(output)
    
    # 打印完整输出方便调试
    print("--- 脚本输出 ---")
    print(output)
    print("----------------")
    # 查找 Downloaded to: ./generated_image_*.png
    match = re.search(r'Downloaded to:\s*(.+\.png)', output)
    if match:
        image_filename = match.group(1)
        # 如果是相对路径，相对于脚本目录
        if image_filename.startswith('./'):
            image_filename = image_filename[2:]
        image_path = os.path.join(script_dir, image_filename)
        abs_path = os.path.abspath(image_path)
        if os.path.exists(abs_path):
            print(f"✅ 图片生成成功: {abs_path}")
            return abs_path
        else:
            print(f"❌ 文件不存在: {abs_path}")
            # 尝试当前目录
            cwd = os.getcwd()
            image_path2 = os.path.join(cwd, image_filename)
            if os.path.exists(image_path2):
                print(f"✅ 找到图片在当前目录: {image_path2}")
                return image_path2
            return None
    else:
        print(f"❌ 未能找到生成的图片路径")
        return None

def download_image(url, save_path):
    """这个函数现在不用了，因为 image-generate 已经下载好了"""
    pass

def compose_cover(main_title, sub_title, building_image_path, output_path):
    """合成最终封面 - 1:1 正方形"""
    
    # 创建 1024x1024 正方形画布，深蓝色背景
    size = 1024
    background_color = (10, 30, 68)  # #0a1e44 深蓝色
    image = Image.new('RGB', (size, size), background_color)
    draw = ImageDraw.Draw(image)
    
    # 中文字体候选路径
    font_candidates = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "simhei.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    
    # 粘贴建筑背景图（放在底部，占 30% 高度 - 参考效果图布局）
    try:
        building_img = Image.open(building_image_path).convert('RGBA')
        building_img = building_img.resize((size, int(size * 0.30)))
        
        # 放在底部
        image.paste(building_img, (0, size - building_img.height), building_img)
        print("✅ 建筑背景已粘贴")
    except Exception as e:
        print(f"⚠️ 粘贴建筑背景失败: {e}，只用纯色背景")
    
    # 添加主标题（金色）
    # 尝试加载中文字体 - 系统中文字体路径
    font_candidates = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "simhei.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    main_font = None
    for font_path in font_candidates:
        try:
            main_font = ImageFont.truetype(font_path, 88)
            break
        except:
            continue
    if main_font is None:
        main_font = ImageFont.load_default(size=88)
    
    # 金色 #d4af37
    main_color = (212, 175, 55)
    shadow_color = (0, 0, 0)
    
    # 计算文字位置（参考效果图：标题占上方，15% 位置）
    main_bbox = draw.textbbox((0, 0), main_title, font=main_font)
    main_width = main_bbox[2] - main_bbox[0]
    main_height = main_bbox[3] - main_bbox[1]
    main_x = (size - main_width) // 2
    main_y = int(size * 0.15)
    
    # 画文字阴影
    draw.text((main_x + 2, main_y + 2), main_title, font=main_font, fill=shadow_color)
    # 画主文字
    draw.text((main_x, main_y), main_title, font=main_font, fill=main_color)
    
    # 添加副标题（银色）
    # 尝试加载中文字体 - 系统中文字体路径
    sub_font = None
    for font_path in font_candidates:
        try:
            sub_font = ImageFont.truetype(font_path, 56)
            break
        except:
            continue
    if sub_font is None:
        sub_font = ImageFont.load_default(size=56)
    
    # 银色 #c0c0c0
    sub_color = (192, 192, 192)
    
    # 计算文字位置（参考效果图：副标题在标题下方，40% 位置）
    sub_bbox = draw.textbbox((0, 0), sub_title, font=sub_font)
    sub_width = sub_bbox[2] - sub_bbox[0]
    sub_height = sub_bbox[3] - sub_bbox[1]
    sub_x = (size - sub_width) // 2
    sub_y = int(size * 0.40)
    
    # 阴影
    draw.text((sub_x + 1, sub_y + 1), sub_title, font=sub_font, fill=shadow_color)
    # 主文字
    draw.text((sub_x, sub_y), sub_title, font=sub_font, fill=sub_color)
    
    # 添加 logo（右上角浅色）
    logo_text = "天津就业服务"
    logo_color = (212, 175, 55)
    # 尝试加载中文字体 - 系统中文字体路径
    logo_font = None
    for font_path in font_candidates:
        try:
            logo_font = ImageFont.truetype(font_path, 24)
            break
        except:
            continue
    if logo_font is None:
        logo_font = ImageFont.load_default(size=24)
    
    # 右上角
    logo_bbox = draw.textbbox((0, 0), logo_text, font=logo_font)
    logo_width = logo_bbox[2] - logo_bbox[0]
    logo_x = size - logo_width - 30
    logo_y = 30
    draw.text((logo_x, logo_y), logo_text, font=logo_font, fill=logo_color)
    
    # 保存
    image.save(output_path, 'PNG')
    print(f"✅ 封面已保存到: {output_path}")
    return True

def main():
    """主函数"""
    print("🎨 小红书招聘封面生成器")
    print("-" * 40)
    
    # 获取用户输入
    if len(sys.argv) >= 4:
        main_title = sys.argv[1]
        sub_title = sys.argv[2]
        building = sys.argv[3]
    else:
        print("请输入信息：")
        main_title = input("主标题（金色大字）: ").strip()
        sub_title = input("副标题（银色小字）: ").strip()
        building = input("标志性建筑名称: ").strip()
    
    if not main_title or not sub_title or not building:
        print("❌ 信息不全，请重新运行")
        sys.exit(1)
    
    # 创建输出目录
    output_dir = "./xiaohongshu-output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = int(os.times()[4])
    building_safe = building.replace(' ', '_').replace('/', '_')
    output_path = os.path.join(output_dir, f"cover_{building_safe}_{timestamp}.png")
    
    # 1. 生成建筑图片
    image_path = generate_building_image(building)
    if not image_path:
        print("❌ 生成图片失败")
        sys.exit(1)
    
    # 2. 合成封面
    if not compose_cover(main_title, sub_title, image_path, output_path):
        print("❌ 合成封面失败")
        sys.exit(1)
    
    print("-" * 40)
    print(f"🎉 生成完成！输出文件: {os.path.abspath(output_path)}")
    print("\n使用示例：")
    print(f"  python {sys.argv[0]} \"天津河北区消防救援支队招聘\" \"19个名额，高中毕业就能报\" \"天津消防救援支队标志性建筑\"")

if __name__ == "__main__":
    main()
