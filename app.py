#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书招聘封面生成器 - Flask Web 服务
前端：用户输入表单 → 后端调用生成脚本 → 返回生成好的图片下载
"""

import os
import sys
import subprocess
import uuid
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

    # 生成唯一文件名
    generate_id = str(uuid.uuid4())[:8]
    building_safe = secure_filename(building.replace(' ', '_'))
    output_filename = f"cover_{building_safe}_{generate_id}.png"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # 调用生成脚本
    script_path = os.path.join(os.path.dirname(__file__), 'xiaohongshu-cover-generator.py')

    try:
        result = subprocess.run(
            [sys.executable, script_path, main_title, sub_title, building],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else "生成脚本执行失败"
            return jsonify({'success': False, 'error': error_msg})

        # 检查输出文件是否生成
        if not os.path.exists(output_path):
            # 脚本会输出最终文件路径，尝试从输出提取
            print(result.stdout)
            return jsonify({'success': False, 'error': '输出文件未生成'})

        # 返回成功，提供下载链接
        image_url = f"/download/{output_filename}"
        return jsonify({
            'success': True,
            'imageUrl': image_url,
            'filename': output_filename
        })

    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': '生成超时，请稍后重试'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'error': '文件不存在'}), 404
    return send_file(file_path, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
