#!/usr/bin/env python3
"""小红书图文生成器 - Flask 后端 (Vercel 部署版)"""
import os, io, base64, json, re, tempfile
from flask import Flask, request, jsonify, render_template
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests as http_requests
from urllib.parse import urljoin
from lxml import html as lxml_html

app = Flask(__name__)

# ── LLM API ──
LLM_KEY = os.environ.get("ARK_API_KEY", "2dab1b72-989e-494c-8f58-06b86464e9cd")
LLM_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
LLM_MODEL = "doubao-seed-2-0-pro-260215"

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def get_font(size, bold=False):
    candidates = [
        os.path.join(FONT_DIR, "NotoSansSC-Bold.ttf" if bold else "NotoSansSC-Regular.ttf"),
        os.path.join(FONT_DIR, "PingFang Bold.ttf" if bold else "PingFang Regular.ttf"),
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def generate_cover_image(title, subtitle, landmark):
    size = 1080
    img = Image.new("RGB", (size, size), "#0a0e27")
    draw = ImageDraw.Draw(img)
    
    # Gradient background
    for y in range(size):
        ratio = y / size
        r = int(10 + ratio * 40)
        g = int(14 + ratio * 50)
        b = int(39 + ratio * 80)
        draw.line([(0, y), (size, y)], fill=(r, g, b))
    
    # Decorative circles
    for i in range(6):
        cx = int(size * (0.15 + i * 0.14))
        cy = int(size * (0.25 + i * 0.10))
        radius = 70 + i * 35
        circle = Image.new("RGBA", (radius*2, radius*2), (0,0,0,0))
        cd = ImageDraw.Draw(circle)
        cd.ellipse([(0,0),(radius*2,radius*2)], fill=(255,215,0,12))
        circle = circle.filter(ImageFilter.GaussianBlur(25))
        img.paste(circle, (cx-radius, cy-radius), circle)
    
    # Top accent line
    for x_offset, w in [(80, 120), (80, 70)]:
        draw.rectangle([(80, 60 + (0 if x_offset==80 else 8)), (x_offset+w, 63 + (0 if x_offset==80 else 8))], fill="#ffd700")
    
    # Title
    try:
        font_title = get_font(68, bold=True)
        font_sub = get_font(30)
        font_bottom = get_font(22)
    except:
        font_title = font_sub = font_bottom = ImageFont.load_default()
    
    # Word wrap title
    lines = []
    current = ""
    for char in title:
        test = current + char
        bbox = draw.textbbox((0,0), test, font=font_title)
        if bbox[2] - bbox[0] > size - 160 and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current: lines.append(current)
    if not lines: lines = [title]
    
    y = int(size * 0.32)
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font_title)
        draw.text(((size - (bbox[2]-bbox[0]))//2, y), line, fill="#ffd700", font=font_title)
        y += 76
    
    # Subtitle
    if subtitle:
        bbox = draw.textbbox((0,0), subtitle, font=font_sub)
        draw.text(((size - (bbox[2]-bbox[0]))//2, y+30), subtitle, fill="#ffed4a", font=font_sub)
    
    # Bottom bar
    draw.rectangle([(80, size-120), (size-80, size-117)], fill=(255,215,0,38))
    draw.rectangle([(size//2-60, size-122), (size//2+60, size-119)], fill="#ffd700")
    
    # Bottom text
    bbox = draw.textbbox((0,0), "天津就业服务 · 每日更新", font=font_bottom)
    draw.text(((size - (bbox[2]-bbox[0]))//2, size-60), "天津就业服务 · 每日更新", fill=(255,237,74,128) if hasattr(ImageDraw.ImageDraw, 'fill_alpha') else "#ffed4a", font=font_bottom)
    
    # Border
    draw.rectangle([(20,20),(size-20,size-20)], outline="#ffd700", width=2)
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def fetch_article_content(url):
    try:
        resp = http_requests.get(url, headers={"User-Agent": UA}, timeout=15)
        resp.encoding = resp.apparent_encoding or "utf-8"
        tree = lxml_html.fromstring(resp.text)
        # Remove script/style
        for el in tree.xpath("//script|//style|//nav|//footer|//header"):
            el.getparent().remove(el) if el.getparent() is not None else None
        # Get main content
        content = tree.xpath("//article|//div[contains(@class,'content')]|//div[contains(@class,'article')]|//div[contains(@id,'content')]")
        if content:
            text = content[0].text_content()
        else:
            text = tree.xpath("//body")[0].text_content() if tree.xpath("//body") else ""
        text = re.sub(r'\n\s*\n', '\n', text).strip()
        if len(text) > 8000:
            text = text[:8000] + "..."
        return text or "无法提取文章内容，请手动粘贴"
    except Exception as e:
        return f"抓取失败: {str(e)}"

def generate_copy(content, style="all"):
    prompt = f"""你是小红书爆款文案专家。根据以下天津招聘/考试公告内容，生成3版小红书文案。

公告内容：
{content}

要求：
1. 每版都包含：标题（含emoji）、正文（3-5段，有emoji分段）、标签（5-8个）
2. 正文要提取关键信息：岗位/考试名称、报名时间、条件、待遇亮点
3. 口语化、有感染力，像真人写的
4. 版本1：🔥 爆款标题党（吸睛标题）
5. 版本2：📚 干货详细版（信息完整）
6. 版本3：💖 情感共鸣版（强调铁饭碗/稳定/机会）

输出JSON格式：
{{"version1":{{"title":"...","content":"...","tags":["..."]}},
"version2":{{"title":"...","content":"...","tags":["..."]}},
"version3":{{"title":"...","content":"...","tags":["..."]}}}}"""

    try:
        resp = http_requests.post(LLM_URL, json={
            "model": LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 3000
        }, headers={
            "Authorization": f"Bearer {LLM_KEY}",
            "Content-Type": "application/json"
        }, timeout=60)
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        # Extract JSON
        m = re.search(r'\{[\s\S]*\}', text)
        if m:
            return json.loads(m.group(0))
    except Exception as e:
        pass
    # Fallback
    return {
        "version1": {"title": "📢 天津最新招聘！速看", "content": content[:200] + "\n\n💡 关注获取更多招聘信息", "tags": ["天津招聘","天津就业"]},
        "version2": {"title": "📚 天津招聘详情", "content": content[:300] + "\n\n💡 详细条件查看原文", "tags": ["天津招聘","天津就业"]},
        "version3": {"title": "💖 机会来啦！天津好工作", "content": content[:200] + "\n\n🏛️ 稳定工作就在眼前", "tags": ["天津招聘","铁饭碗"]},
    }

# ── Routes ──
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate-cover", methods=["POST"])
def api_generate_cover():
    data = request.get_json()
    title = (data.get("title") or "").strip()
    subtitle = (data.get("subtitle") or "").strip()
    landmark = data.get("landmark", "")
    if not title:
        return jsonify({"success": False, "error": "请输入主标题"})
    try:
        b64 = generate_cover_image(title, subtitle, landmark)
        return jsonify({"success": True, "url": f"data:image/png;base64,{b64}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/fetch-content", methods=["POST"])
def api_fetch_content():
    data = request.get_json()
    url = (data.get("url") or "").strip()
    if not url:
        return jsonify({"error": "请输入URL"})
    content = fetch_article_content(url)
    return jsonify({"content": content})

@app.route("/generate-copy", methods=["POST"])
def api_generate_copy():
    data = request.get_json()
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "请输入内容"})
    if len(content) < 20:
        return jsonify({"error": "内容太短"})
    try:
        result = generate_copy(content)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

# Vercel serverless entry
def handler(event, context):
    from flask import Request
    # Minimal Vercel adapter
    pass

if __name__ == "__main__":
    app.run(debug=True, port=5050)