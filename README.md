# 小红书招聘封面生成器

AI 一键生成小红书招聘封面图，专为天津就业服务新媒体打造。

## ✨ 功能特点

- 🎨 固定专业模板：深蓝色背景 + 金色大字标题 + 银色小字说明
- 🏢 底部半透明标志性建筑，营造专业沉稳招聘氛围
- 📐 标准 1:1 正方形，完美适配小红书
- 🤖 AI 自动生成标志性建筑背景
- 🌐 完整前后端，开箱即用

## 🚀 部署方式

### 方式一：服务器部署（推荐自己用）

```bash
# 克隆代码
git clone https://github.com/zhengchen712-cpu/zctools.git
cd zctools

# 安装依赖
apt-get install -y python3-flask python3-pillow

# 创建输出目录
mkdir -p xiaohongshu-output/web

# 启动服务
nohup python3 app.py > app.log 2>&1 &

# 开放 5000 端口后访问
# http://你的服务器IP:5000
```

### 方式二：Vercel 部署

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/zhengchen712-cpu/zctools)

1. 点击上面按钮一键部署
2. 等待 Vercel 自动构建完成
3. 直接访问你的 Vercel 域名即可使用

## 📖 使用方法

1. 打开网页
2. 输入：
   - **主标题**：比如 `天津大学招聘`
   - **副标题**：比如 `2026最新岗位汇总`
   - **标志性建筑描述**：比如 `天津大学校门`
3. 点击「生成封面」，等待 30-60 秒
4. 预览效果，点击下载图片
5. 直接上传小红书发布 ✨

## 📁 项目结构

```
├── app.py                 # Flask Web 服务
├── xiaohongshu-cover-generator.py  # 核心生成脚本
├── requirements.txt      # Python 依赖
├── vercel.json          # Vercel 配置
├── xiaohongshu-output/   # 生成封面输出目录
└── README.md           # 项目说明
```

## 🎯 适用场景

- 招聘信息新媒体运营
- 公众号/小红书封面快速生成
- 机构招聘宣传图制作

## 💡 技术栈

- Python + Flask
- Pillow 图片合成
- ARK API AI 图片生成

---

为北漂来津人员就业服务新媒体项目 🇨🇳
