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
| `도곽` | 도곽 경계와 도면번호 | 1 (빨강) | 0.50 mm |
| `표고점` | 표고점 십자 마커 | 5 (파랑) | 0.13 mm |
| `표고점-문자` | 표고값·좌표 문자 | 7 | 0.13 mm |
| `표제란` | 표제란 테두리와 항목 | 7 | 0.35 mm |
| `중첩-지적` | 겹쳐 넣은 기존 도면 | 2 (노랑) | 0.18 mm |

레이어 이름·색·굵기는 `terrain2dxf/config.py`의 `LayerScheme`에서 회사 도면
규약에 맞게 고칠 수 있다.

## CAD에서 손으로 하던 것들

등고선만으로는 도면이 되지 않는다. 아래 세 가지가 자동으로 들어간다.

### 표고점

격자 간격으로 표고점을 찍고 십자 마커와 표고값을 기입한다. 간격은 축척에
맞춰 자동으로 잡히고(1/1000은 20 m), 도면 좌표의 배수에 정렬되므로 인접한
도면끼리 표고점이 어긋나지 않는다.

```bash
--spot-heights                # 격자 표고점
--spot-spacing 25             # 간격을 직접 지정
--spot-coords                 # 표고와 함께 E/N 좌표도 기입
--spot-extremes 3             # 최고·최저 주요 지점을 각각 3개씩
```

### 도곽 분할과 표제란

축척과 용지에서 한 장이 덮는 실제 범위를 계산해 현장을 여러 매로 나눈다.
도곽 격자는 현장 **중앙에 정렬**되므로 마지막 열이 빈 도면이 되지 않는다.
매 장마다 페이퍼공간 레이아웃과 뷰포트, 표제란이 만들어진다.

```bash
--sheet-split --paper A1 --sheet-prefix "C-01-02-" \
--project "원삼면 용수선 일원" --title "현황측량도" --surveyor "한크건설"
```

파일명은 기존 규칙을 따라 `C-01-02-001~008.현황측량도.dxf` 형태가 되고,
레이아웃 이름은 `C-01-02-001` … 처럼 도면번호가 된다. 현장명을 주지 않으면
DEM 파일 이름이 현장명이 되므로, 무인 실행에서 표제란이 비지 않는다.

| 용지 | 1/1000에서 한 장이 덮는 범위 |
|---|---|
| A0 | 약 974 × 821 m |
| A1 | 약 626 × 574 m |
| A2 | 약 379 × 400 m |
| A3 | 약 205 × 277 m |

모델공간은 실좌표를 그대로 유지하므로, 도면을 나눠도 기존 `XREF_` 체계에
그대로 얹을 수 있다.

### 지적선 등 기존 도면 중첩

`XREF_지적도_GRS80`, `연속주제도` 같은 도면을 등고선 도면에 자동으로 포갠다.
같은 EPSG:5186을 쓰므로 좌표 변환 없이 그대로 겹친다.

```bash
--overlay 지적도.dxf --overlay 구역계.dxf
```

가져온 도형은 모두 `중첩-지적` 레이어로 몰아넣어, 원본 도면의 레이어가 수십
개여도 중첩분을 한 번에 켜고 끌 수 있다. **DWG는 읽지 못하므로** ODA File
Converter로 DXF로 바꿔서 넣어야 한다. 파일이 없으면 경고만 남기고 나머지
작업은 계속된다.

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
| `spot_heights` | `false` | 격자 표고점 기입 |
| `spot_spacing` | `0` | 0이면 축척별 기본 간격 |
| `spot_coords` | `false` | 표고와 함께 좌표도 기입 |
| `spot_extremes` | `0` | 최고·최저 주요 지점 개수 |
| `sheet_split` | `false` | 도곽 분할과 레이아웃 생성 |
| `paper` | `A1` | `A0`~`A3` |
| `sheet_overlap` | `20.0` | 인접 도면이 겹치는 폭(m) |
| `sheet_prefix` | `""` | 도면번호 접두사 |
| `overlay_dxf` | `[]` | 겹칠 기존 도면 목록 |
| `project_name` | `""` | 표제란 현장명. 비우면 파일명 |
| `drawing_title` | `현황측량도` | 표제란 도면명 |
| `surveyor` | `""` | 표제란 작성자 |
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

**3DF Zephyr 단계는 자동화되지 않는다.** 3Dflow는 Zephyr에 커맨드라인 처리를
제공하지 않는다. 사진에서 3D를 만드는 단계는 Zephyr를 열어야 하고, 이 도구는
Zephyr가 **DEM을 GeoTIFF로 내보낸 다음부터** 이어받는다. Zephyr Aerial/Pro라면
배치 처리(XML)로 그 앞단도 일부 줄일 수 있다.

**표제란은 기본 양식이다.** 회사 표제란 양식이 따로 있으면
`terrain2dxf/dxf.py`의 `_draw_titleblock()` 한 함수만 고치면 된다.

**구조물·지장물 표기는 만들지 않는다.** 표고점·지적선·표제란까지가 이 도구의
범위다.

## 시험

```bash
pip install pytest
python -m pytest tests/test_terrain2dxf.py -q
```
