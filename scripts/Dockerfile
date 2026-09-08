# NAS(Synology/QNAP)의 Docker에서 상주 감시로 돌릴 때 쓰는 이미지.
#
#   docker build -t terrain2dxf -f scripts/Dockerfile .
#   docker run -d --name terrain2dxf --restart unless-stopped \
#       -v /volume1/drone/입력:/data/입력 \
#       -v /volume1/drone/출력:/data/출력 \
#       -v /volume1/drone/처리완료:/data/처리완료 \
#       terrain2dxf
FROM python:3.11-slim

# rasterio 휠에 GDAL이 포함되어 별도 설치가 필요 없다.
# 한글 폰트는 검산용 미리보기 제목에만 쓰인다.
RUN apt-get update \
    && apt-get install -y --no-install-recommends fonts-nanum \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements-terrain.txt .
RUN pip install --no-cache-dir -r requirements-terrain.txt

COPY terrain2dxf/ ./terrain2dxf/

ENV PYTHONPATH=/app PYTHONIOENCODING=utf-8
VOLUME ["/data"]

CMD ["python", "-m", "terrain2dxf", "watch", "/data/입력", "/data/출력", \
     "--archive", "/data/처리완료", "--interval", "60", \
     "--ground-filter", "--flatten-z", "--spot-heights", "--sheet-split", \
     "--scale", "1/1000", "--paper", "A1", "--sheet-prefix", "C-01-02-", \
     "--log", "/data/출력/자동처리.log"]
