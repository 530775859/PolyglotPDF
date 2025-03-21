# 使用Python 3.8作为基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1-mesa-glx \
    git \
    && rm -rf /var/lib/apt/lists/*

# 克隆项目代码
# RUN git clone https://github.com/530775859/PolyglotPDF.git .
# 复制本地项目代码到镜像中
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=5100

# 暴露端口
EXPOSE 5100

# 启动命令
CMD ["python", "app.py"]
