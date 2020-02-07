FROM python:3.8
ENV PYTHONUNBUFFERED 1
##  添加国内镜像源
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list

ADD requirements.txt /filter-text/
WORKDIR /filter-text
ADD pip.conf /root/.pip/pip.conf

RUN pip install -r requirements.txt
# 修复时区
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
ENV PATH=/usr/local/bin:/usr/local/sbin:/sbin:/bin:/usr/sbin:/usr/bin:/root/bin