#!/bin/bash
# 构建脚本 - 安装中文字体
apt-get update
apt-get install -y fonts-wqy-microhei fonts-wqy-zenhei
pip install -r requirements.txt
