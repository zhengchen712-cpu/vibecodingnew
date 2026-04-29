#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书图文生成器 - AGI188 统一风格
功能：1. 封面生成 2. 爆款文案生成（前端调用API，后端负责抓网页内容）
"""

import os
import re
import sys
import subprocess
import uuid
import requests
from flask import Flask, request, send_file, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)

# 配置 - Vercel只允许/tmp目录写文件
OUTPUT_DIR = "/tmp/xiaohongshu-output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 读取静态HTML
with open('simple-index.html', 'r', encoding='utf-8') as f:
    INDEX_HTML = f.read()

@app.route('/')
def index():
    return INDEX_HTML

# 抓取网页正文（给前端用）
@app.route('/fetch-content', methods=['POST'])
def fetch_content():
    try:
        url = request.form.get('url', '').strip()
        if not url:
            return jsonify({"error": "请输入链接"})
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 移除不需要的标签
        for tag in soup(["script", "style", "nav", "footer", "aside", "header"]):
            tag.decompose()
        
        # 提取正文
        text = soup.get_text(separator="\n", strip=True)
        # 清理多余空行
        text = re.sub(r"\n{3,}", "\n\n", text)
        # 限制长度
        return jsonify({"content": text[:5000]})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/generate', methods=['POST'])
def generate():
    try:
        title = request.form.get('title', '')
        subtitle = request.form.get('subtitle', '')
        landmark = request.form.get('landmark', '')
        
        if not title:
            return jsonify({"success": False, "error": "请输入标题"})
        
        # 调用生成脚本
        filename = f"cover-{uuid.uuid4().hex[:8]}.png"
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        cmd = [
            sys.executable, "xiaohongshu-cover-generator.py",
            "--title", title,
            "--subtitle", subtitle,
            "--output", output_path
        ]
        if landmark:
            cmd.extend(["--landmark", landmark])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if os.path.exists(output_path):
            return jsonify({"success": True, "url": f"/output/{filename}"})
        else:
            return jsonify({"success": False, "error": result.stderr or "生成失败"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/output/<filename>')
def output_file(filename):
    return send_file(os.path.join(OUTPUT_DIR, filename))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
