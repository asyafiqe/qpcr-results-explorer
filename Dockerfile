FROM python:3.10.13-slim-bullseye

ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /workspace
COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY app.py app.py

EXPOSE 8501

CMD ["streamlit", "run", "--server.maxUploadSize", "2", "/workspace/app.py"]