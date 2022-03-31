FROM ubuntu
COPY ./ /home/SUSTechStore
RUN apt update \
    && apt install python3 -y \
    && apt install python3-pip -y \
    && export DEBIAN_FRONTEND=noninteractive apt install postgresql \
    && apt install postgresql-contrib -y \
    && apt install libpq-dev -y \
    && apt install redis-server -y \
    && pip3 install -r /home/SUSTechStore/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /home/SUSTechStore
# CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
