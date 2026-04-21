#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书招聘封面生成器 - Flask Web 服务
前端：用户输入表单 → 后端调用生成脚本 → 返回生成好的图片下载
"""

import os
import sys
import json
import uuid
import requests
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, send_file, jsonify, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 配置
OUTPUT_DIR = "/tmp/xiaohongshu-output/web"
# Vercel 只有 /tmp 可写，所以输出到这里
os.makedirs(OUTPUT_DIR, exist_ok=True)

# HTML 模板
INDEX_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小红书招聘封面生成器 - 天津就业服务</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }

        h1 {
            text-align: center;
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 28px;
        }

        .subtitle {
            text-align: center;
            color: #718096;
            margin-bottom: 40px;
            font-size: 16px;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #2d3748;
            font-weight: 600;
            font-size: 15px;
        }

        input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        input:focus {
            outline: none;
            border-color: #667eea;
        }

        .generate-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .generate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
        }

        .generate-btn:active {
            transform: translateY(0);
        }

        .generate-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .result-area {
            margin-top: 40px;
            display: none;
        }

        .result-area.show {
            display: block;
        }

        .result-title {
            color: #2d3748;
            margin-bottom: 20px;
            font-size: 18px;
            font-weight: 600;
        }

        .preview {
            width: 100%;
            max-width: 500px;
            margin: 0 auto;
            aspect-ratio: 1/1;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            margin-bottom: 20px;
        }

        .preview img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .download-btn {
            display: block;
            width: fit-content;
            margin: 0 auto;
            padding: 12px 30px;
            background: #2f855a;
            color: white;
            border-radius: 10px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.3s;
        }

        .download-btn:hover {
            background: #276749;
        }

        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }

        .loading.show {
            display: block;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .tips {
            margin-top: 30px;
            padding: 20px;
            background: #f7fafc;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        .tips h4 {
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 15px;
        }

        .tips ul {
            margin-left: 20px;
            color: #718096;
            font-size: 14px;
            line-height: 1.8;
        }

        @media (max-width: 768px) {
            .container {
                padding: 25px;
            }

            h1 {
                font-size: 22px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 小红书招聘封面生成器</h1>
        <p class="subtitle">天津就业服务 · AI 一键生成专业招聘封面</p>

        <form id="generateForm">
            <div class="form-group">
                <label for="mainTitle">主标题（金色大字）</label>
                <input type="text" id="mainTitle" placeholder="例如：天津河北区消防救援支队招聘" required>
            </div>

            <div class="form-group">
                <label for="subTitle">副标题（银色小字）</label>
                <input type="text" id="subTitle" placeholder="例如：19个名额，高中毕业就能报" required>
            </div>

            <div class="form-group">
                <label for="building">标志性建筑/机构描述</label>
                <input type="text" id="building" placeholder="例如：天津消防救援总队大门建筑" required>
            </div>

            <button type="submit" class="generate-btn" id="generateBtn">生成封面</button>
        </form>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>正在生成中，请稍候... AI 生成图片需要 30-60 秒</p>
        </div>

        <div class="result-area" id="resultArea">
            <div class="result-title">📸 生成完成</div>
            <div class="preview">
                <img id="previewImg" alt="生成封面">
            </div>
            <a href="#" id="downloadBtn" class="download-btn" download>💾 下载封面图片</a>
        </div>

        <div class="tips">
            <h4>💡 使用说明</h4>
            <ul>
                <li>标准 1:1 正方形，小红书直接能用</li>
                <li>深蓝色背景 + 金色标题 + 银色副标题，专业沉稳风格</li>
                <li>AI 自动生成标志性建筑图片放在底部半透明</li>
                <li>生成后右键图片也能保存，下载按钮更方便</li>
            </ul>
        </div>
    </div>

    <script>
        document.getElementById('generateForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const mainTitle = document.getElementById('mainTitle').value.trim();
            const subTitle = document.getElementById('subTitle').value.trim();
            const building = document.getElementById('building').value.trim();

            if (!mainTitle || !subTitle || !building) {
                alert('请填写完整信息');
                return;
            }

            document.getElementById('generateBtn').disabled = true;
            document.getElementById('loading').classList.add('show');
            document.getElementById('resultArea').classList.remove('show');

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        mainTitle: mainTitle,
                        subTitle: subTitle,
                        building: building
                    })
                });

                const data = await response.json();

                if (data.success) {
                    document.getElementById('previewImg').src = data.imageUrl;
                    document.getElementById('downloadBtn').href = data.imageUrl;
                    document.getElementById('downloadBtn').download = data.filename;
                    document.getElementById('resultArea').classList.add('show');
                } else {
                    alert('生成失败: ' + (data.error || '未知错误'));
                }
            } catch (error) {
                alert('请求失败: ' + error.message);
            }

            document.getElementById('generateBtn').disabled = false;
            document.getElementById('loading').classList.remove('show');
        });
    </script>
</body>
</html>
"""

def generate_building_image(building_name, api_key):
    """使用 ARK API 直接生成标志性建筑图片"""
    
    prompt = f"{building_name}，标志性建筑，专业摄影，高清，蓝色调渐变背景，适合做封面背景，构图下半部分是建筑，上半部分留白，安静专业氛围"
    
    # 图片生成使用专门的端点
    url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 图片生成请求格式
    data = {
        "model": "doubao-seedream-4-5-251128",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "response_format": "url"
    }
    
    print(f"🔄 正在调用 ARK API 生成 {building_name} 图片...")
    response = requests.post(url, headers=headers, json=data, timeout=180)
    
    if response.status_code != 200:
        print(f"❌ API 请求失败: {response.status_code} {response.text}")
        return None
    
    result_json = response.json()
    # 解析图片生成返回，获取图片 URL
    try:
        if "data" not in result_json or len(result_json["data"]) == 0:
            print(f"❌ 响应格式错误: {json.dumps(result_json, indent=2)}")
            return None
        
        # 获取第一张图片 URL
        image_url = result_json["data"][0]["url"]
        print(f"✅ 获取图片 URL: {image_url}")
        
        # 下载图片
        image_response = requests.get(image_url, timeout=60)
        if image_response.status_code == 200:
            # 保存到临时文件
            generated_path = f"/tmp/generated_{building_name.replace(' ', '_')}.png"
            with open(generated_path, "wb") as f:
                f.write(image_response.content)
            print(f"✅ 图片已下载: {generated_path}")
            return generated_path
        else:
            print(f"❌ 下载图片失败: {image_response.status_code}")
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
    
    # 中文字体候选路径 - Vercel 已有字体
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

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    main_title = data.get('mainTitle', '').strip()
    sub_title = data.get('subTitle', '').strip()
    building = data.get('building', '').strip()

    if not main_title or not sub_title or not building:
        return jsonify({'success': False, 'error': '信息不完整'})

    # 从环境变量获取 ARK API KEY
    ark_api_key = os.environ.get("ARK_API_KEY")
    if not ark_api_key:
        return jsonify({'success': False, 'error': '环境变量 ARK_API_KEY 未设置'})

    # 生成建筑图片
    building_image_path = generate_building_image(building, ark_api_key)
    if not building_image_path:
        return jsonify({'success': False, 'error': '生成建筑图片失败，请检查 API Key'})

    # 生成输出文件名
    generate_id = str(uuid.uuid4())[:8]
    building_safe = secure_filename(building.replace(' ', '_'))
    output_filename = f"cover_{building_safe}_{generate_id}.png"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # 合成封面
    success = compose_cover(main_title, sub_title, building_image_path, output_path)
    if not success:
        return jsonify({'success': False, 'error': '合成封面失败'})

    # 返回成功，提供下载链接
    image_url = f"/download/{output_filename}"
    return jsonify({
        'success': True,
        'imageUrl': image_url,
        'filename': output_filename
    })

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'error': '文件不存在'}), 404
    return send_file(file_path, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
