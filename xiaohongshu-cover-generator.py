#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书招聘封面自动生成器
功能：根据用户输入，自动生成标志性建筑背景图，合成最终封面
直接调用 ARK API 生成图片，不依赖本地脚本
"""

import os
import sys
import json
import requests
from PIL import Image, ImageDraw, ImageFont

def generate_building_image(building_name, api_key):
    """使用 ARK API 直接生成标志性建筑图片"""
    
    prompt = f"{building_name}，标志性建筑，专业摄影，高清，蓝色调渐变背景，适合做封面背景，构图下半部分是建筑，上半部分留白，安静专业氛围"
    
    url = "https://ark.cn-beijing.volces.com/api/coding/v3/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # ARK 图片生成请求
    data = {
        "model": "doubao-seed-code",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "max_tokens": 2048,
        "image_generation": True
    }
    
    print(f"🔄 正在调用 ARK API 生成 {building_name} 图片...")
    response = requests.post(url, headers=headers, json=data, timeout=180)
    
    if response.status_code != 200:
        print(f"❌ API 请求失败: {response.status_code} {response.text}")
        return None
    
    result = response.json
    
    # 解析返回，获取图片 URL
    try:
        result_json = response.json()
        if "choices" not in result_json:
            print(f"❌ 响应格式错误: {json.dumps(result_json, indent=2)}")
            return None
        
        content = result_json["choices"][0]["message"]["content"]
        
        # 查找图片 URL
        import re
        image_url_match = re.search(r'https?://[^\s]+\.png', content)
        if image_url_match:
            image_url = image_url_match.group(0)
            # 下载图片
            print(f"✅ 获取图片 URL: {image_url}")
            image_response = requests.get(image_url, timeout=60)
            if image_response.status_code == 200:
                # 保存到临时文件
                generated_path = f"generated_{building_name.replace(' ', '_')}.png"
                with open(generated_path, "wb") as f:
                    f.write(image_response.content)
                print(f"✅ 图片已下载: {generated_path}")
                return os.path.abspath(generated_path)
            else:
                print(f"❌ 下载图片失败: {image_response.status_code}")
                return None
        else:
            print(f"❌ 未找到图片 URL: {content}")
            return None
    except Exception as e:
        print(f"❌ 解析响应错误: {e}")
        return None

def compose_cover(main_title, sub_title, building_image_path, output_path):
    """合成最终封面 - 1:1 正方形"""
    
    # 创建 1024x1024 正方形画布，深蓝色背景
    size = 1024
    background_color = (10, 30, 68)  # #0a1e44 深蓝色
    image = Image.new('RGB', (size, size), background_color)
    draw = ImageDraw.Draw(image)
    
    # 中文字体候选路径 - Vercel 安装字体
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
    
    # 添加主标题（金色大字）
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
    
    # 计算文字位置（参考效果图：标题占上方，15% 位置）
    main_bbox = draw.textbbox((0, 0), main_title, font=main_font)
    main_width = main_bbox[2] - main_bbox[0]
    main_height = main_bbox[3] - main_bbox[1]
    main_x = (size - main_width) // 2
    main_y = int(size * 0.15)
    
    # 绘制文字阴影增加可读性
    shadow_color = (0, 0, 0)
    draw.text((main_x + 2, main_y + 2), main_title, font=main_font, fill=shadow_color)
    draw.text((main_x, main_y), main_title, font=main_font, fill=main_color)
    print("✅ 主标题已添加")
    
    # 添加副标题（银色小字）
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
    
    # 计算文字位置（副标题在标题下方，40% 位置）
    sub_bbox = draw.textbbox((0, 0), sub_title, font=sub_font)
    sub_width = sub_bbox[2] - sub_bbox[0]
    sub_height = sub_bbox[3] - sub_bbox[1]
    sub_x = (size - sub_width) // 2
    sub_y = int(size * 0.40)
    
    # 绘制文字阴影
    draw.text((sub_x + 2, sub_y + 2), sub_title, font=sub_font, fill=shadow_color)
    draw.text((sub_x, sub_y), sub_title, font=sub_font, fill=sub_color)
    print("✅ 副标题已添加")
    
    # 添加右上角 logo
    logo_text = "天津就业服务"
    logo_font = None
    for font_path in font_candidates:
        try:
            logo_font = ImageFont.truetype(font_path, 24)
            break
        except:
            continue
    if logo_font is None:
        logo_font = ImageFont.load_default(size=24)
    
    # 浅色文字
    logo_color = (150, 150, 150)
    logo_bbox = draw.textbbox((0, 0), logo_text, font=logo_font)
    logo_width = logo_bbox[2] - logo_bbox[0]
    logo_x = size - logo_width - 30
    logo_y = 20
    draw.text((logo_x, logo_y), logo_text, font=logo_font, fill=logo_color)
    print("✅ Logo 已添加")
    
    # 保存最终图片
    image.save(output_path, "PNG")
    print(f"✅ 封面已保存到: {output_path}")
    return True

def main():
    if len(sys.argv) != 4:
        print("Usage: python xiaohongshu-cover-generator.py \"主标题\" \"副标题\" \"标志性建筑\"")
        sys.exit(1)
    
    main_title = sys.argv[1]
    sub_title = sys.argv[2]
    building = sys.argv[3]
    
    # 从环境变量获取 ARK API KEY
    ark_api_key = os.environ.get("ARK_API_KEY")
    if not ark_api_key:
        print("❌ 环境变量 ARK_API_KEY 未设置")
        sys.exit(1)
    
    # 生成建筑图片
    building_image_path = generate_building_image(building, ark_api_key)
    if not building_image_path:
        sys.exit(1)
    
    # 生成输出文件名
    import uuid
    output_dir = "/tmp/xiaohongshu-output/web"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"cover_{building.replace(' ', '_')}_{str(uuid.uuid4())[:8]}.png"
    output_path = os.path.join(output_dir, output_filename)
    
    # 合成封面
    success = compose_cover(main_title, sub_title, building_image_path, output_path)
    if success:
        print(f"🎉 生成完成！输出文件: {os.path.abspath(output_path)}")
        sys.exit(0)
    else:
        print("❌ 生成失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
