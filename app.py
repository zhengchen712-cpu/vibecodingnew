#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书图文生成器 - AGI188 统一风格
功能：1. 封面生成 2. 文章链接→爆款文案生成
"""

import os
import sys
import subprocess
import uuid
from flask import Flask, request, send_file, jsonify, render_template_string

app = Flask(__name__)

# 配置 - Vercel只允许/tmp目录写文件
OUTPUT_DIR = "/tmp/xiaohongshu-output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 火山方舟API配置 - 封面生成
ARK_API_KEY = os.environ.get("ARK_API_KEY", "2dab1b72-989e-494c-8f58-06b86464e9cd")

# AGI188 统一风格 HTML 模板
INDEX_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎨</text></svg>">
<link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎨</text></svg>">
<title>小红书图文生成器 - AGI188</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#000;--text:#f5f5f7;--sub:#86868b;--dim:#48484a;--blue:#2997ff;--purple:#bf5af2;--border:#333;--success:#30d158}
html{scroll-behavior:smooth}
body{font-family:-apple-system,BlinkMacSystemFont,'SF Pro Display','Helvetica Neue','Microsoft YaHei',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;-webkit-font-smoothing:antialiased}

/* 导航 */
.nav{position:fixed;top:0;left:0;right:0;z-index:99;background:rgba(0,0,0,0.72);backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);border-bottom:1px solid rgba(255,255,255,0.04)}
.nav-in{max-width:960px;margin:0 auto;padding:0 24px;height:48px;display:flex;justify-content:space-between;align-items:center}
.nav-brand{font-size:16px;font-weight:700;letter-spacing:0.02em;text-decoration:none;background:linear-gradient(135deg,var(--blue),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent}

/* Tab */
.tabs{display:flex;gap:8px;margin-bottom:32px;background:rgba(255,255,255,0.04);padding:6px;border-radius:12px}
.tab{flex:1;padding:12px 16px;border-radius:8px;text-align:center;font-size:14px;font-weight:600;cursor:pointer;transition:all 0.2s;border:none;background:transparent;color:var(--sub)}
.tab.active{background:linear-gradient(135deg,var(--blue),var(--purple));color:#fff}
.tab:hover:not(.active){background:rgba(255,255,255,0.08);color:var(--text)}

/* 主内容区 */
.main{max-width:700px;margin:0 auto;padding:100px 24px 80px}

/* 头部 */
.hero{text-align:center;margin-bottom:48px}
.hero-icon{font-size:64px;margin-bottom:16px}
.hero h1{font-size:40px;font-weight:700;letter-spacing:-0.03em;margin-bottom:8px;background:linear-gradient(180deg,#f5f5f7,#a1a1a6);-webkit-background-clip:text;-webkit-text-fill-color:transparent}

/* 表单 */
.form-group{margin-bottom:24px}
.form-label{display:block;font-size:13px;font-weight:600;color:var(--sub);margin-bottom:8px;text-transform:uppercase;letter-spacing:0.08em}
.form-input{width:100%;padding:16px 20px;background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:16px;color:var(--text);font-size:16px;font-family:inherit;transition:all 0.2s;outline:none}
.form-input:focus{border-color:var(--purple);background:rgba(255,255,255,0.06)}
.form-input::placeholder{color:var(--dim)}

/* 按钮 */
.btn{width:100%;padding:18px 24px;background:linear-gradient(135deg,var(--blue),var(--purple));border:none;border-radius:16px;color:#fff;font-size:16px;font-weight:700;cursor:pointer;transition:all 0.2s;display:flex;align-items:center;justify-content:center;gap:8px}
.btn:hover{transform:translateY(-2px);box-shadow:0 12px 40px rgba(75,118,252,0.25)}
.btn:active{transform:translateY(0)}
.btn:disabled{opacity:0.5;cursor:not-allowed;transform:none}

/* 结果卡片 */
.result-card{background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:16px;padding:24px;margin-bottom:16px}
.result-card h3{font-size:18px;margin-bottom:16px;color:var(--success)}
.result-text{white-space:pre-wrap;line-height:1.8;font-size:15px;color:var(--text);margin-bottom:16px}
.copy-btn{padding:10px 20px;background:rgba(255,255,255,0.08);border:1px solid var(--border);border-radius:12px;color:var(--text);font-size:14px;font-weight:600;cursor:pointer;transition:all 0.2s}
.copy-btn:hover{background:rgba(255,255,255,0.12)}

/* 隐藏 */
.hidden{display:none!important}

/* 加载 */
.loading{text-align:center;padding:40px}
.spinner{width:40px;height:40px;border:3px solid var(--border);border-top-color:var(--purple);border-radius:50%;animation:spin 1s linear infinite;margin:0 auto 16px}
@keyframes spin{to{transform:rotate(360deg)}}

/* 提示 */
.toast{position:fixed;bottom:32px;left:50%;transform:translateX(-50%);padding:12px 24px;background:var(--success);color:#fff;border-radius:12px;font-size:14px;font-weight:600;z-index:1000;animation:fadeInUp 0.3s ease}
@keyframes fadeInUp{from{opacity:0;transform:translateX(-50%) translateY(20px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}
</style>
</head>
<body>
<nav class="nav">
  <div class="nav-in">
    <div class="nav-brand">🎨 小红书图文生成器</div>
  </div>
</nav>

<main class="main">
  <div class="hero">
    <div class="hero-icon">🚀</div>
    <h1>10秒出爆款</h1>
    <p style="color:var(--sub);font-size:17px">AI 自动写文案 + 生成封面，一站式搞定</p>
  </div>

  <!-- Tab 切换 -->
  <div class="tabs">
    <button class="tab active" onclick="switchTab('cover')">🎨 封面生成</button>
    <button class="tab" onclick="switchTab('copywriting')">📝 爆款文案</button>
  </div>

  <!-- 封面生成 Tab -->
  <div id="tab-cover">
    <div class="form-group">
      <label class="form-label">主标题</label>
      <input class="form-input" id="title" placeholder="例如：天津落户最新政策2026">
    </div>
    <div class="form-group">
      <label class="form-label">副标题</label>
      <input class="form-input" id="subtitle" placeholder="例如：这5类人直接落户，别再跑冤枉路了">
    </div>
    <div class="form-group">
      <label class="form-label">地标建筑</label>
      <input class="form-input" id="landmark" placeholder="例如：天津之眼 / 不填就不用地标">
    </div>
    <button class="btn" onclick="generateCover()">🚀 生成封面</button>
    <div id="cover-result" class="hidden" style="margin-top:32px;text-align:center"></div>
  </div>

  <!-- 爆款文案 Tab -->
  <div id="tab-copywriting" class="hidden">
    <div class="form-group">
      <label class="form-label">粘贴文章内容</label>
      <textarea class="form-input" id="article-content" rows="10" placeholder="把公众号文章的正文内容粘贴到这里..."></textarea>
    </div>
    <button class="btn" onclick="generateCopywriting()">🚀 一键生成爆款文案</button>
    <div id="copywriting-loading" class="hidden loading">
      <div class="spinner"></div>
      <p style="color:var(--sub)">AI 正在分析文章，生成3版文案...</p>
    </div>
    <div id="copywriting-result" class="hidden" style="margin-top:32px"></div>
  </div>
</main>

<script>
// Tab 切换
function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('tab-cover').classList.toggle('hidden', tab !== 'cover');
  document.getElementById('tab-copywriting').classList.toggle('hidden', tab !== 'copywriting');
}

// 生成封面
async function generateCover() {
  const title = document.getElementById('title').value.trim();
  const subtitle = document.getElementById('subtitle').value.trim();
  const landmark = document.getElementById('landmark').value.trim();
  
  if (!title) {
    showToast('请输入主标题');
    return;
  }
  
  const btn = event.target;
  btn.disabled = true;
  btn.textContent = '生成中...';
  
  try {
    const res = await fetch('/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: `title=${encodeURIComponent(title)}&subtitle=${encodeURIComponent(subtitle)}&landmark=${encodeURIComponent(landmark)}`
    });
    const data = await res.json();
    
    if (data.success) {
      document.getElementById('cover-result').innerHTML = `
        <img src="${data.url}" style="max-width:100%;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,0.5)">
        <div style="margin-top:16px">
          <a href="${data.url}" download="xiaohongshu-cover.png" style="display:inline-block;padding:12px 24px;background:var(--success);color:#fff;border-radius:12px;text-decoration:none;font-weight:600">📥 下载封面</a>
        </div>
      `;
      document.getElementById('cover-result').classList.remove('hidden');
      showToast('封面生成成功！');
    } else {
      showToast('生成失败: ' + data.error);
    }
  } catch (e) {
    showToast('出错了: ' + e.message);
  }
  
  btn.disabled = false;
  btn.textContent = '🚀 生成封面';
}

// 生成爆款文案 - 纯前端调用火山方舟API
async function generateCopywriting() {
  const content = document.getElementById('article-content').value.trim();
  
  if (!content) {
    showToast('请粘贴文章内容');
    return;
  }
  
  const btn = event.target;
  btn.disabled = true;
  document.getElementById('copywriting-loading').classList.remove('hidden');
  document.getElementById('copywriting-result').classList.add('hidden');
  
  try {
    // 构建Prompt
    const prompt = `
请基于以下文章内容，生成3个不同风格的小红书爆款文案。

文章内容：
${content.slice(0, 4000)}

要求：
1. 每个文案包含：吸睛标题 + 正文（带emoji分点） + 5-8个精准标签
2. 三个版本风格不同：
   - 版本1【爆款标题党】：标题夸张有冲突感，抓人眼球，适合流量
   - 版本2【干货长文版】：内容详实，有条理，适合收藏
   - 版本3【情感共鸣版】：用第一人称讲故事，有代入感，容易引发评论
3. 语言风格：小红书风格，口语化，用emoji，不用太正式
4. 每段不要太长，适合手机阅读

返回纯JSON格式，不要有其他解释：
{
    "version1": {"title": "标题", "content": "正文", "tags": ["标签1", "标签2"]},
    "version2": {"title": "标题", "content": "正文", "tags": ["标签1", "标签2"]},
    "version3": {"title": "标题", "content": "正文", "tags": ["标签1", "标签2"]}
}
`;
    
    // 直接从浏览器调用火山方舟API
    const res = await fetch('https://ark.cn-beijing.volces.com/api/v3/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 2dab1b72-989e-494c-8f58-06b86464e9cd'
      },
      body: JSON.stringify({
        model: 'ep-20260429170019-522hs',
        messages: [{role: 'user', content: prompt}],
        temperature: 0.7,
        max_tokens: 2000
      })
    });
    
    const data = await res.json();
    console.log('API响应:', data);
    
    if (data.error) {
      showToast('生成失败: ' + data.error.message);
      return;
    }
    
    if (!data.choices || !data.choices[0]) {
      showToast('API返回格式不对');
      return;
    }
    
    // 提取内容并解析JSON
    let resultText = data.choices[0].message.content;
    const jsonMatch = resultText.match(/\{[\s\S]*\}/);
    
    if (!jsonMatch) {
      showToast('生成格式不对，请重试');
      return;
    }
    
    const result = JSON.parse(jsonMatch[0]);
    
    // 渲染结果
    let html = '';
    const versions = [
      {key: 'version1', name: '🔥 版本1：爆款标题党'},
      {key: 'version2', name: '📚 版本2：干货长文版'},
      {key: 'version3', name: '💖 版本3：情感共鸣版'}
    ];
    
    for (let i = 0; i < versions.length; i++) {
      const v = versions[i];
      if (result[v.key]) {
        const fullText = result[v.key].title + '\n\n' + result[v.key].content + '\n\n' + result[v.key].tags.map(t => '#' + t).join(' ');
        window['copyText' + i] = fullText;
        html += `
          <div class="result-card">
            <h3>${v.name}</h3>
            <div class="result-text">${escapeHtml(fullText)}</div>
            <button class="copy-btn" onclick="copyText(copyText${i})">📋 复制文案</button>
          </div>
        `;
      }
    }
    
    document.getElementById('copywriting-result').innerHTML = html;
    document.getElementById('copywriting-result').classList.remove('hidden');
    showToast('文案生成成功！');
  } catch (e) {
    console.error('错误:', e);
    showToast('出错了: ' + e.message);
  }
  
  btn.disabled = false;
  document.getElementById('copywriting-loading').classList.add('hidden');
}

// 复制文本
function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('已复制到剪贴板！');
  });
}

// 提示
function showToast(msg) {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2500);
}

// 转义
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

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
