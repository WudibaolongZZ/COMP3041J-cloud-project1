# 1. 使用 Python 基础镜像
FROM python:3.9-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 复制依赖文件并安装
# 我们需要 flask, requests 和 tablestore SDK
RUN pip install flask requests tablestore -i https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 复制所有代码到容器
COPY . .

# 5. 暴露 5000 端口
EXPOSE 5000

# 6. 运行程序
CMD ["python", "app.py"]