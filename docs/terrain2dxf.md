# terrain2dxf — 드론 DEM에서 등고선 도면 자동 생성

드론 촬영으로 만든 표고 격자(DEM/DSM GeoTIFF)를 읽어 **등고선 DXF 도면**을
만든다. AutoCAD·Civil3D·Pix4D 같은 상용 프로그램을 열지 않고, 사람이 붙어
있지 않아도 폴더에 파일만 들어오면 도면이 나오도록 하는 것이 목표다.

좌표 규약은 기존 작업물(`_ortho.json`)과 동일하게 **EPSG:5186(중부원점 GRS80),
1 m 격자**를 기본으로 삼는다.

## 무엇이 나오는가

DEM 한 장을 넣으면 폴더 하나가 만들어진다.

```
출력/고림동/
├── 고림동_등고선.dxf       주곡선·계곡선·표고가 레이어로 분리된 도면 (Z = 실제 표고)
├── 고림동_등고선_z0.dxf    Z를 0으로 눕힌 사본 — 평면도에 참조도면으로 얹을 때
├── 고림동_미리보기.png     음영기복 위에 등고선을 얹은 검산용 그림
└── 고림동_리포트.json      좌표 범위·표고·설정·경고를 담은 처리 기록
```

DXF 레이어 구성:

| 레이어 | 내용 | 색 | 선굵기 |
|---|---|---|---|
| `등고선-주곡선` | 1/1000 기준 1 m 간격 | 8 (회색) | 0.13 mm |
| `등고선-계곡선` | 1/1000 기준 5 m 간격 | 3 (초록) | 0.30 mm |
| `등고선-표고` | 계곡선 위 표고 문자 | 7 | 0.13 mm |
| `도곽` | DEM 유효 범위 사각형 | 1 (빨강) | 0.50 mm |

레이어 이름·색·굵기는 `terrain2dxf/config.py`의 `LayerScheme`에서 회사 도면
규약에 맞게 고칠 수 있다.

## 설치

```bash
pip install -r requirements-terrain.txt
```

`rasterio` 휠에 GDAL이 들어 있어 GDAL을 따로 설치할 필요가 없다.
미리보기 제목에 한글을 쓰려면 나눔고딕 같은 한글 폰트가 있어야 한다
(없으면 제목만 깨지고 도면에는 영향이 없다).

## 손으로 한 장씩 돌리기

```bash
# 가장 단순하게
python -m terrain2dxf convert 고림동_dem.tif -o 출력/

# 초목·건물을 걷어내고, 평면도용 z=0 사본까지
python -m terrain2dxf convert 고림동_dem.tif -o 출력/ --ground-filter --flatten-z

# 축척을 바꾸면 등고선 간격도 함께 바뀐다
python -m terrain2dxf convert 고림동_dem.tif -o 출력/ --scale 1/5000
```

시험용 지형이 필요하면 실제 현장 데이터 없이도 만들어 볼 수 있다.

```bash
python -m terrain2dxf sample 시험.tif --size 600
```

## 무인 실행

### 방법 1 — Windows 작업 스케줄러

`scripts/run_watch.bat`의 세 폴더 경로만 현장에 맞게 고친 뒤, 작업 스케줄러에
등록한다. 10분마다 돌려도 되고, 로그인할 때 한 번 돌려도 된다.

### 방법 2 — NAS 예약 작업

`scripts/run_watch.sh`의 세 폴더 경로를 고치고 cron에 건다.

```
*/10 * * * * /volume1/drone/scripts/run_watch.sh
```

`--once` 옵션이 붙어 있어 한 번 훑고 끝나므로 상주 프로세스가 남지 않는다.

### 방법 3 — NAS Docker 상주

```bash
docker build -t terrain2dxf -f scripts/Dockerfile .
docker run -d --name terrain2dxf --restart unless-stopped \
    -v /volume1/drone/입력:/data/입력 \
    -v /volume1/drone/출력:/data/출력 \
    -v /volume1/drone/처리완료:/data/처리완료 \
    terrain2dxf
```

어느 방법이든 동작은 같다.

1. 입력 폴더에서 `.tif`/`.tiff`를 찾는다.
2. **마지막 수정 후 5초가 지난 파일만** 건드린다. 네트워크 드라이브로 큰 DEM을
   복사하는 도중에 처리를 시작해 도면이 깨지는 일을 막기 위한 장치다.
3. 이미 처리한 파일은 건너뛴다(`출력/.terrain2dxf_state.json`에 기록).
   이름·크기·수정시각이 모두 같으면 같은 파일로 본다.
4. 한 파일이 실패해도 기록만 남기고 다음 파일로 넘어간다.
5. `--archive`를 주면 처리한 원본을 옮겨 입력 폴더를 비운다.

## 설정 파일

명령줄 옵션 대신 JSON으로 관리할 수 있다.

```bash
python -m terrain2dxf init-config 설정.json
python -m terrain2dxf convert 고림동_dem.tif -o 출력/ --config 설정.json
```

| 항목 | 기본값 | 설명 |
|---|---|---|
| `scale` | `1/1000` | `1/500`, `1/1000`, `1/1200`, `1/2500`, `1/5000` |
| `epsg` | `5186` | 기대하는 좌표계. 원본과 다르면 경고를 남긴다 |
| `smooth_sigma` | `1.5` | 가우시안 평활 강도. 0이면 끔 |
| `ground_filter` | `false` | 초목·건물을 걷어내는 간이 지면 필터 |
| `ground_max_window` | `20.0` | 지면 필터가 다룰 최대 지물 크기(m) |
| `min_length` | `2.0` | 이보다 짧은 등고선 조각은 버림(m) |
| `flatten_z` | `false` | z=0 사본도 생성 |
| `make_preview` | `true` | 검산용 PNG 생성 |

## 알아 두어야 할 한계

**지면 필터는 만능이 아니다.** 래스터 DSM만으로는 나무 밑 지면을 복원할 수
없다. 이 필터는 지면보다 솟은 덩어리를 걷어내고 주변 지면값으로 메우는 근사일
뿐이다. 숲이 우거진 구간은 원래의 포인트클라우드에서 지면점을 분류(CSF/PMF)해
DEM을 다시 만드는 편이 정확하다. `ground_max_window`보다 큰 지물은 지형으로
오인되어 남는다.

**DWG로는 바로 못 쓴다.** 이 도구는 DXF까지만 만든다. DWG가 필요하면 무료
배포되는 **ODA File Converter**로 폴더째 일괄 변환하면 된다. AutoCAD가 없어도
되고, 이 역시 명령줄로 자동화할 수 있다.

**재투영은 하지 않는다.** 원본 좌표계가 설정과 다르면 경고만 남기고 원본 좌표
그대로 도면을 만든다. 좌표계를 맞춰야 하면 `gdalwarp -t_srs EPSG:5186`으로
먼저 변환하고 넣는다.

**등고선은 도면의 일부일 뿐이다.** 표제란·범례·도곽 분할, 지적선 중첩,
구조물 표기는 이 도구가 만들지 않는다. 기존 `XREF_` 참조도면 체계에 등고선
DXF를 얹는 방식이 현재로서는 가장 손이 적게 간다.

## 시험

```bash
pip install pytest
python -m pytest tests/test_terrain2dxf.py -q
```
