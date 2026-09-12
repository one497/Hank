const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625
pres.title = "3분 안에 뜨는 제주";

const NAVY = "10243A", PRIMARY = "065A82", TEAL = "1C7293",
      ICE = "CADCFC", SOFT = "F2F6F9", WHITE = "FFFFFF",
      GRAY = "5A6A78", CORAL = "E0523C", MIST = "8FB4C9", LINEC = "E3EAF0";
const F = "맑은 고딕";
const sh = () => ({ type: "outer", color: "0B1B2B", blur: 8, offset: 2, angle: 90, opacity: 0.12 });

function titleBlock(s, t, sub, dark, size) {
  s.addText(t, { x: 0.6, y: 0.42, w: 8.8, h: 0.62, fontFace: F, fontSize: size || 30, bold: true,
    color: dark ? WHITE : NAVY, isTextBox: true, margin: 0 });
  if (sub) s.addText(sub, { x: 0.6, y: 1.03, w: 8.8, h: 0.36, fontFace: F, fontSize: 13,
    color: dark ? MIST : GRAY, isTextBox: true, margin: 0 });
}
function card(s, o) {
  s.addShape(pres.ShapeType.roundRect, { x: o.x, y: o.y, w: o.w, h: o.h, rectRadius: 0.06,
    fill: { color: o.fill || SOFT }, line: { color: o.line || (o.fill ? o.fill : LINEC), width: 1 }, shadow: sh() });
}
function foot(s, t, dark) {
  s.addText(t, { x: 0.6, y: 4.82, w: 8.8, h: 0.4, fontFace: F, fontSize: 12,
    color: dark ? MIST : NAVY, isTextBox: true, margin: 0 });
}
function src(s, t) {
  s.addText(t, { x: 0.6, y: 5.22, w: 8.8, h: 0.28, fontFace: F, fontSize: 8.5, color: "8895A2", isTextBox: true, margin: 0 });
}

/* ---------- 1. 표지 ---------- */
let s = pres.addSlide();
s.background = { color: NAVY };
s.addText("2026 코리아스타트업포럼 · 제주 혁신 대담 / 정책제안 세션", {
  x: 0.75, y: 1.15, w: 8.5, h: 0.32, fontFace: F, fontSize: 12, color: MIST, isTextBox: true, margin: 0 });
s.addText("3분 안에 뜨는 제주", {
  x: 0.75, y: 1.62, w: 8.5, h: 0.95, fontFace: F, fontSize: 44, bold: true, color: WHITE, isTextBox: true, margin: 0 });
s.addText("드론 기반 선제 치안 · 구조 체계", {
  x: 0.75, y: 2.62, w: 8.5, h: 0.5, fontFace: F, fontSize: 22, color: ICE, isTextBox: true, margin: 0 });
s.addText("안전한 제주를 만들기 위한 정책 제언", {
  x: 0.75, y: 4.25, w: 8.5, h: 0.34, fontFace: F, fontSize: 14, color: MIST, isTextBox: true, margin: 0 });
s.addText("[회사명]  ·  [OOO 대표]  ·  2026. 9. 18.", {
  x: 0.75, y: 4.62, w: 8.5, h: 0.34, fontFace: F, fontSize: 12, color: "7E93A4", isTextBox: true, margin: 0 });
s.addNotes("제주가 위험하다는 말로 시작하지 않는다. 자료를 먼저 확인했다는 태도로 연다.");

/* ---------- 2. 자원 지표 ---------- */
s = pres.addSlide();
titleBlock(s, "제주는 자원이 부족한 곳이 아닙니다", "발제를 준비하며 공개 통계를 먼저 확인했습니다");
const assets = [
  ["314명", "경찰관 1인당 담당인구", "전국 평균 391명보다\n오히려 적습니다"],
  ["19,096대", "방범용 CCTV", "인구 1,000명당 28.8대\n전국 평균의 두 배"],
  ["85명", "통합관제센터 관제요원", "5조 3교대\n24시간 관제"],
  ["9,717건", "CCTV 관제 사고 예방", "전년 대비 40% 증가\n(2025년)"],
];
assets.forEach((a, i) => {
  const x = 0.6 + i * 2.26;
  card(s, { x, y: 1.72, w: 2.06, h: 2.55 });
  s.addText(a[0], { x: x + 0.16, y: 1.95, w: 1.74, h: 0.55, fontFace: F, fontSize: 22, bold: true,
    color: PRIMARY, isTextBox: true, margin: 0 });
  s.addText(a[1], { x: x + 0.16, y: 2.55, w: 1.74, h: 0.6, fontFace: F, fontSize: 12, bold: true,
    color: NAVY, isTextBox: true, margin: 0 });
  s.addText(a[2], { x: x + 0.16, y: 3.18, w: 1.74, h: 0.95, fontFace: F, fontSize: 10,
    color: GRAY, isTextBox: true, margin: 0, lineSpacingMultiple: 1.15 });
});
foot(s, "인력도, 장비도, 관제 체계도 전국 평균보다 앞서 있습니다.");
src(s, "출처: 경찰청 경찰통계연보(2024) · 제주특별자치도 CCTV 운영 현황(2025 상반기) — 원자료 재확인 필요");

/* ---------- 3. 범죄율 1위, 분모의 문제 ---------- */
s = pres.addSlide();
titleBlock(s, "'범죄율 전국 1위'는 분모의 문제입니다", "범죄 건수에는 관광객이 들어가고, 분모에는 들어가지 않습니다");
card(s, { x: 0.6, y: 1.7, w: 4.25, h: 1.5 });
s.addText("공표 범죄 발생비", { x: 0.85, y: 1.85, w: 3.7, h: 0.3, fontFace: F, fontSize: 11, color: GRAY, isTextBox: true, margin: 0 });
s.addText("4,193.8건", { x: 0.85, y: 2.15, w: 3.7, h: 0.55, fontFace: F, fontSize: 30, bold: true, color: CORAL, isTextBox: true, margin: 0 });
s.addText("인구 10만 명당 · 전국 1위 · 분모 66만 명", { x: 0.85, y: 2.72, w: 3.7, h: 0.3, fontFace: F, fontSize: 10, color: GRAY, isTextBox: true, margin: 0 });
card(s, { x: 5.15, y: 1.7, w: 4.25, h: 1.5, fill: NAVY, line: NAVY });
s.addText("생활인구 82만 명으로 보정", { x: 5.4, y: 1.85, w: 3.7, h: 0.3, fontFace: F, fontSize: 11, color: MIST, isTextBox: true, margin: 0 });
s.addText("약 3,390건", { x: 5.4, y: 2.15, w: 3.7, h: 0.55, fontFace: F, fontSize: 30, bold: true, color: WHITE, isTextBox: true, margin: 0 });
s.addText("전국 평균 3,343건과 거의 같습니다", { x: 5.4, y: 2.72, w: 3.7, h: 0.3, fontFace: F, fontSize: 10, color: ICE, isTextBox: true, margin: 0 });
[["1,384만 명", "2025년 제주 방문 관광객"], ["66만 명", "주민등록인구 (2026. 6.)"], ["82만 명", "도 추계 생활인구"]].forEach((d, i) => {
  const x = 0.6 + i * 2.98;
  s.addShape(pres.ShapeType.roundRect, { x, y: 3.45, w: 2.84, h: 0.82, rectRadius: 0.06, fill: { color: SOFT }, line: { color: LINEC, width: 1 } });
  s.addText(d[0], { x: x + 0.18, y: 3.55, w: 2.5, h: 0.36, fontFace: F, fontSize: 16, bold: true, color: PRIMARY, isTextBox: true, margin: 0 });
  s.addText(d[1], { x: x + 0.18, y: 3.92, w: 2.5, h: 0.28, fontFace: F, fontSize: 10, color: GRAY, isTextBox: true, margin: 0 });
});
foot(s, "그렇다면 질문이 달라져야 합니다 — 부족하지 않은데, 왜 불안은 줄지 않는가.");
src(s, "출처: 경찰청 2025 범죄통계 · 행정안전부 주민등록인구 · 제주도관광협회 / 보정치는 단순 안분에 따른 개략 검산");

/* ---------- 4. 공백은 두 곳 ---------- */
s = pres.addSlide();
s.background = { color: NAVY };
titleBlock(s, "비어 있는 곳은 두 군데뿐입니다", "둘 다 사람을 더 뽑아서 메울 수 없는 공백입니다", true);
const gaps = [
  ["공백 ①", "자원이 닿지 않는 공간", [
    ["CCTV 19,096대", "전부 고정형 — 정해진 지점만 봅니다"],
    ["산악사고 5년 2,547건", "올해 실족·추락 107건 = 작년 한 해의 90.7%"],
    ["수난사고 6월 70건 → 7월 126건", "오름·곶자왈·해안절벽·올레길에는 카메라가 없습니다"]]],
  ["공백 ②", "자동으로 작동하지 않는 초동 절차", [
    ["성인 실종신고 70,814건", "전국, 지난해 접수 기준"],
    ["99.7% 수색 없이 종결", "89.4%는 하루 안에 해제"],
    ["판단은 담당자 재량", "올해 제주에서 흔들린 것은 범죄율이 아니라 초동대응 신뢰였습니다"]]],
];
gaps.forEach((g, i) => {
  const x = 0.6 + i * 4.5;
  s.addShape(pres.ShapeType.roundRect, { x, y: 1.6, w: 4.3, h: 3.1, rectRadius: 0.06,
    fill: { color: "1B3A57" }, line: { color: "27506F", width: 1 } });
  s.addText(g[0], { x: x + 0.24, y: 1.75, w: 3.8, h: 0.28, fontFace: F, fontSize: 11, bold: true, color: CORAL, isTextBox: true, margin: 0 });
  s.addText(g[1], { x: x + 0.24, y: 2.03, w: 3.8, h: 0.36, fontFace: F, fontSize: 16, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  g[2].forEach((r, j) => {
    const y = 2.52 + j * 0.7;
    s.addText(r[0], { x: x + 0.24, y, w: 3.8, h: 0.28, fontFace: F, fontSize: 12, bold: true, color: ICE, isTextBox: true, margin: 0 });
    s.addText(r[1], { x: x + 0.24, y: y + 0.27, w: 3.8, h: 0.38, fontFace: F, fontSize: 9.5, color: MIST, isTextBox: true, margin: 0, lineSpacingMultiple: 1.15 });
  });
});
foot(s, "하나는 공간의 문제, 하나는 기본 동작의 문제입니다.", true);
src(s, "출처: 제주도 CCTV 운영 현황 · 소방 구조활동 통계 · 경찰청 실종신고 처리 현황");

/* ---------- 5. 문제는 시간이다 ---------- */
s = pres.addSlide();
titleBlock(s, "공간의 공백은 '시간'으로 나타납니다", "신고가 접수된 시점과, 하늘에서 그곳을 처음 본 시점 사이");
function timeline(y, steps, result, color, resultColor) {
  steps.forEach((t, i) => {
    const x = 1.62 + i * 1.63;
    s.addShape(pres.ShapeType.roundRect, { x, y, w: 1.48, h: 0.62, rectRadius: 0.06,
      fill: { color: color }, line: { color: color, width: 1 } });
    s.addText(t, { x, y, w: 1.48, h: 0.62, fontFace: F, fontSize: 11, color: NAVY,
      align: "center", valign: "middle", isTextBox: true, margin: 0 });
    if (i < steps.length - 1) s.addText("›", { x: x + 1.48, y, w: 0.15, h: 0.62, fontFace: F,
      fontSize: 16, color: GRAY, align: "center", valign: "middle", isTextBox: true, margin: 0 });
  });
  s.addText(result, { x: 8.0, y, w: 1.45, h: 0.62, fontFace: F, fontSize: 19, bold: true,
    color: resultColor, align: "right", valign: "middle", isTextBox: true, margin: 0 });
}
s.addText("현행  ·  동원형", { x: 0.6, y: 1.62, w: 3.0, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: CORAL, isTextBox: true, margin: 0 });
timeline(1.95, ["신고 접수", "인력 이동", "현장 도착", "이륙"], "수십 분", "FBE7E3", CORAL);
s.addText("제안  ·  상시 출동형", { x: 0.6, y: 3.05, w: 3.0, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: PRIMARY, isTextBox: true, margin: 0 });
timeline(3.38, ["신고 접수", "자동 이륙"], "3~5분", "E1EEF4", PRIMARY);
foot(s, "실종·조난의 초기 시간이, 장비를 현장까지 옮기는 데 소모됩니다.");
src(s, "※ 제주의 112·119 현장 도착 소요시간 실측치는 미공개. '수십 분'은 현행 운용 방식에서 도출한 추정치 — 도가 보유한 실측치 공개를 제언에 포함");

/* ---------- 6. DFR ---------- */
s = pres.addSlide();
titleBlock(s, "DFR — 사람보다 먼저 도착하는 눈", "Drone as First Responder  ·  최초 출동 드론");
const steps = [
  ["112 · 119 신고 접수", "신고 정보가 관제센터로\n즉시 연동됩니다."],
  ["무인 격납고 자동 이륙", "사람이 출발하기 전에\n기체가 먼저 뜹니다."],
  ["실시간 영상 공유 · 자동 기록", "관제센터와 출동 인력이\n동시에 봅니다. 로그가 남습니다."],
];
steps.forEach((st, i) => {
  const x = 0.6 + i * 2.98;
  card(s, { x, y: 1.72, w: 2.84, h: 2.45 });
  s.addShape(pres.ShapeType.ellipse, { x: x + 0.24, y: 1.96, w: 0.5, h: 0.5, fill: { color: PRIMARY }, line: { color: PRIMARY, width: 0 } });
  s.addText(String(i + 1), { x: x + 0.24, y: 1.96, w: 0.5, h: 0.5, fontFace: F, fontSize: 16, bold: true,
    color: WHITE, align: "center", valign: "middle", isTextBox: true, margin: 0 });
  s.addText(st[0], { x: x + 0.24, y: 2.62, w: 2.36, h: 0.5, fontFace: F, fontSize: 13, bold: true,
    color: NAVY, isTextBox: true, margin: 0 });
  s.addText(st[1], { x: x + 0.24, y: 3.16, w: 2.36, h: 0.8, fontFace: F, fontSize: 10.5, color: GRAY,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.2 });
});
foot(s, "기술 제안이라기보다, 행정 절차 설계에 가까운 제안입니다.");

/* ---------- 7. 두 공백을 하나로 ---------- */
s = pres.addSlide();
titleBlock(s, "하나의 장치가 두 공백을 메웁니다", "새 감시망을 만들자는 제안이 아닙니다");
card(s, { x: 0.6, y: 1.7, w: 4.3, h: 1.55 });
s.addText("공백 ①  공간", { x: 0.85, y: 1.85, w: 3.8, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: CORAL, isTextBox: true, margin: 0 });
s.addText("고정형 관제망의 이동형 확장", { x: 0.85, y: 2.16, w: 3.8, h: 0.36, fontFace: F, fontSize: 15, bold: true, color: NAVY, isTextBox: true, margin: 0 });
s.addText("이미 19,096대의 카메라와 85명의 관제 인력이\n돌아갑니다. 여기에 날아가는 카메라를 붙입니다.", { x: 0.85, y: 2.55, w: 3.8, h: 0.6, fontFace: F, fontSize: 10.5, color: GRAY, isTextBox: true, margin: 0, lineSpacingMultiple: 1.2 });
card(s, { x: 5.1, y: 1.7, w: 4.3, h: 1.55, fill: NAVY, line: NAVY });
s.addText("공백 ②  절차", { x: 5.35, y: 1.85, w: 3.8, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: "F2A65A", isTextBox: true, margin: 0 });
s.addText("재량을 기본 동작으로 · 제3의 기록", { x: 5.35, y: 2.16, w: 3.8, h: 0.36, fontFace: F, fontSize: 15, bold: true, color: WHITE, isTextBox: true, margin: 0 });
s.addText("판단과 무관하게 공중 확인이 수행되고, 비행·촬영\n기록이 담당자 보고와 다른 계통에 남습니다.", { x: 5.35, y: 2.55, w: 3.8, h: 0.6, fontFace: F, fontSize: 10.5, color: ICE, isTextBox: true, margin: 0, lineSpacingMultiple: 1.2 });
const rows = [
  [{ text: "구분", options: { fill: { color: NAVY }, color: WHITE, bold: true } },
   { text: "현행  ·  동원형", options: { fill: { color: NAVY }, color: WHITE, bold: true } },
   { text: "제안  ·  상시 출동형", options: { fill: { color: NAVY }, color: WHITE, bold: true } }],
  ["상공 확보", "수십 분", "3 ~ 5분"],
  ["야간 · 저시정", "사실상 제한", "열화상 + 자동비행으로 상시"],
  ["역할", "사후 수색", "선제 인지 + 출동 유도"],
  ["기록", "담당자 보고에 의존", "출동 · 확인 자동 로그 (별도 계통)"],
];
s.addTable(rows, { x: 0.6, y: 3.45, w: 8.8, colW: [2.0, 3.4, 3.4], rowH: 0.33,
  fontFace: F, fontSize: 11, color: NAVY, valign: "middle",
  border: { type: "solid", color: "DCE5EC", pt: 1 }, fill: { color: WHITE }, margin: 0.08, autoPage: false });

/* ---------- 8. 검증된 모델 ---------- */
s = pres.addSlide();
titleBlock(s, "새로운 실험이 아닙니다", "이미 운영되고 있고, 국내에도 선례가 있습니다");
const cases = [
  ["미국 출라비스타 경찰", "2018년~", "누적 출동 25,000건 이상\n그중 17,170건 드론 선도착\n평균 3.5분 (순찰차 8분)\nOECD 혁신사례 등재"],
  ["전남경찰청 드론팀", "2026. 2. 출범", "지상·공중 입체순찰\n5월 담양 실종자를 CCTV로\n동선 파악 후 드론 수색으로\n담양호 상류에서 발견"],
  ["일본 지바현 이치노미야초", "운영 중", "쓰나미 경보 수신 시\n드론이 자동 이륙\n해안 대피 방송 + 촬영\n방재 부서가 운영"],
];
cases.forEach((c, i) => {
  const x = 0.6 + i * 2.98;
  card(s, { x, y: 1.7, w: 2.84, h: 2.5 });
  s.addText(c[0], { x: x + 0.22, y: 1.86, w: 2.4, h: 0.36, fontFace: F, fontSize: 13.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  s.addText(c[1], { x: x + 0.22, y: 2.22, w: 2.4, h: 0.26, fontFace: F, fontSize: 10, color: PRIMARY, isTextBox: true, margin: 0 });
  s.addText(c[2], { x: x + 0.22, y: 2.56, w: 2.4, h: 1.4, fontFace: F, fontSize: 10.5, color: GRAY, isTextBox: true, margin: 0, lineSpacingMultiple: 1.25 });
});
s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 4.38, w: 8.8, h: 0.66, rectRadius: 0.06, fill: { color: SOFT }, line: { color: LINEC, width: 1 } });
s.addText("다만 과장하지 않겠습니다 — 연구는 \"드론 투입 시 약 3분 단축, 전체 발견 성공률은 유사\"라고 말합니다.", { x: 0.8, y: 4.38, w: 8.4, h: 0.33, fontFace: F, fontSize: 11.5, color: NAVY, valign: "middle", isTextBox: true, margin: 0 });
s.addText("그리고 그 연구의 결론은 \"성패는 기체가 아니라 훈련과 절차에 달려 있다\"는 것입니다.", { x: 0.8, y: 4.68, w: 8.4, h: 0.33, fontFace: F, fontSize: 11.5, bold: true, color: PRIMARY, valign: "middle", isTextBox: true, margin: 0 });
src(s, "출처: City of Chula Vista · OECD OPSI · 머니투데이(2026.9.8) · DroneLife / Drone Efficacy Study(AOPA)");

/* ---------- 8. 왜 제주에서 가능한가 ---------- */
s = pres.addSlide();
titleBlock(s, "왜 제주에서 가능한가", "이 네 가지가 동시에 갖춰진 곳은 제주뿐입니다");
const why = [
  ["전국 유일", "자치경찰단 169명", "제주특별법 제88조\n도지사 소속"],
  ["전국 최초", "AI 치안드론", "국비 8억 · 도비 2억\n2027년 현장 투입"],
  ["전국 최대", "드론특별자유화구역", "1,283㎢\n3차 연장(2027.6) 신청"],
  ["1,543명", "민관 공동체 치안망", "주민자치경찰대 · 시니어\n민간경비 · 민간드론"],
];
why.forEach((a, i) => {
  const x = 0.6 + i * 2.26;
  card(s, { x, y: 1.72, w: 2.06, h: 2.55 });
  s.addText(a[0], { x: x + 0.16, y: 1.95, w: 1.74, h: 0.4, fontFace: F, fontSize: 17, bold: true, color: PRIMARY, isTextBox: true, margin: 0 });
  s.addText(a[1], { x: x + 0.16, y: 2.42, w: 1.74, h: 0.6, fontFace: F, fontSize: 13, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  s.addText(a[2], { x: x + 0.16, y: 3.1, w: 1.74, h: 0.95, fontFace: F, fontSize: 10, color: GRAY, isTextBox: true, margin: 0, lineSpacingMultiple: 1.15 });
});
foot(s, "새 사업을 만들자는 제안이 아닙니다. 있는 자산을 하나의 출동 체계로 잇자는 제안입니다.");

/* ---------- 9. 제언 1 ---------- */
s = pres.addSlide();
titleBlock(s, "제언 ①   거점 — '3분 도달' 네트워크", "새 부지가 아니라, 있는 시설 위에 얹는 방식입니다", false, 28);
card(s, { x: 0.6, y: 1.7, w: 3.0, h: 1.45, fill: NAVY, line: NAVY });
s.addText("3분", { x: 0.75, y: 1.76, w: 2.7, h: 0.82, fontFace: F, fontSize: 40, bold: true, color: WHITE, isTextBox: true, margin: 0 });
s.addText("이내 현장 상공 도달", { x: 0.78, y: 2.62, w: 2.7, h: 0.4, fontFace: F, fontSize: 13, color: ICE, isTextBox: true, margin: 0 });
card(s, { x: 0.6, y: 3.3, w: 3.0, h: 1.35 });
s.addText("신규 부지 불필요", { x: 0.78, y: 3.45, w: 2.7, h: 0.35, fontFace: F, fontSize: 14, bold: true, color: PRIMARY, isTextBox: true, margin: 0 });
s.addText("자치경찰 지구대 · CCTV\n통합관제센터에 무인 격납고를\n병설하는 구조", { x: 0.78, y: 3.8, w: 2.7, h: 0.8, fontFace: F, fontSize: 11, color: GRAY, isTextBox: true, margin: 0, lineSpacingMultiple: 1.2 });
s.addText("1단계 시범 대상지(안)   ·   8개소", { x: 3.95, y: 1.72, w: 5.45, h: 0.35, fontFace: F, fontSize: 13, bold: true, color: NAVY, isTextBox: true, margin: 0 });
const sites = ["제주시 동부 권역", "제주시 서부 권역", "서귀포 시가지", "애월 해안",
               "성산", "중문", "한라산 주요 탐방로 진입부", "올레길 위험 구간"];
sites.forEach((t, i) => {
  const x = 3.95 + (i % 2) * 2.78;
  const y = 2.2 + Math.floor(i / 2) * 0.62;
  s.addShape(pres.ShapeType.roundRect, { x, y, w: 2.62, h: 0.5, rectRadius: 0.06, fill: { color: SOFT }, line: { color: LINEC, width: 1 } });
  s.addText(t, { x: x + 0.14, y, w: 2.4, h: 0.5, fontFace: F, fontSize: 11, color: NAVY, valign: "middle", isTextBox: true, margin: 0 });
});
s.addText("배치 우선순위는 도가 이미 운영 중인 인구빅데이터(생활인구·입도객)로 결정", { x: 3.95, y: 4.78, w: 5.45, h: 0.35, fontFace: F, fontSize: 10.5, color: GRAY, isTextBox: true, margin: 0 });

/* ---------- 10. 제언 2 ---------- */
s = pres.addSlide();
titleBlock(s, "제언 ②   규제 — 특구 연장에 한 줄", "세 가지 제언 중 가장 빠르고, 가장 적은 비용으로 가능합니다", false, 28);
s.addText("1,283㎢", { x: 0.6, y: 1.75, w: 4.1, h: 0.85, fontFace: F, fontSize: 42, bold: true, color: PRIMARY, isTextBox: true, margin: 0 });
s.addText("전국 최대 규모\n드론특별자유화구역", { x: 0.65, y: 2.62, w: 4.1, h: 0.7, fontFace: F, fontSize: 15, bold: true, color: NAVY, isTextBox: true, margin: 0, lineSpacingMultiple: 1.15 });
s.addText("2021년 1차 지정 이후 운영 중이며,\n3차 연장(2027. 6.)을 신청한 상태입니다.", { x: 0.65, y: 3.38, w: 4.1, h: 0.7, fontFace: F, fontSize: 11, color: GRAY, isTextBox: true, margin: 0, lineSpacingMultiple: 1.2 });
card(s, { x: 5.1, y: 1.72, w: 4.3, h: 2.4, fill: NAVY, line: NAVY });
s.addText("연장 신청서에 담아 주십시오", { x: 5.4, y: 1.95, w: 3.7, h: 0.4, fontFace: F, fontSize: 13, color: MIST, isTextBox: true, margin: 0 });
s.addText("치안 · 구조 목적\n비가시권(BVLOS) · 야간비행\n상시 승인 트랙", { x: 5.4, y: 2.4, w: 3.7, h: 1.1, fontFace: F, fontSize: 18, bold: true, color: WHITE, isTextBox: true, margin: 0, lineSpacingMultiple: 1.2 });
s.addText("DFR 체계의 기술적 전제가 바로 이 두 가지입니다.", { x: 5.4, y: 3.6, w: 3.7, h: 0.4, fontFace: F, fontSize: 11, color: ICE, isTextBox: true, margin: 0 });
s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 4.4, w: 8.8, h: 0.62, rectRadius: 0.08, fill: { color: CORAL }, line: { color: CORAL, width: 0 } });
s.addText("국회 입법을 기다릴 필요가 없습니다 — 제주도 권한 안에서, 신청서 한 줄로 열리는 문입니다", {
  x: 0.6, y: 4.4, w: 8.8, h: 0.62, fontFace: F, fontSize: 14, bold: true, color: WHITE, align: "center", valign: "middle", isTextBox: true, margin: 0 });

/* ---------- 11. 제언 3 ---------- */
s = pres.addSlide();
titleBlock(s, "제언 ③   거버넌스 — 조례가 곧 면허증", "기체를 띄우기 전에 원칙을 먼저 세웁니다", false, 28);
const rules = [
  ["촬영 사실 표시", "언제 어디서 촬영되는지\n도민이 알 수 있게 한다"],
  ["목적 외 이용 금지", "신고 기반 출동 원칙.\n특정 집단 감시 수단이 아니다"],
  ["보관기간 · 접근 로그", "누가 언제 어떤 영상을\n열람했는지 자동 기록"],
  ["도민 감시기구", "운영 실태를 도민이\n직접 점검한다"],
];
rules.forEach((r, i) => {
  const x = 0.6 + (i % 2) * 4.5;
  const y = 1.72 + Math.floor(i / 2) * 1.38;
  card(s, { x, y, w: 4.3, h: 1.22 });
  s.addText(r[0], { x: x + 0.22, y: y + 0.14, w: 3.9, h: 0.36, fontFace: F, fontSize: 15, bold: true, color: PRIMARY, isTextBox: true, margin: 0 });
  s.addText(r[1], { x: x + 0.22, y: y + 0.52, w: 3.9, h: 0.6, fontFace: F, fontSize: 11, color: GRAY, isTextBox: true, margin: 0, lineSpacingMultiple: 1.2 });
});
s.addText("＋  민간 드론 인력 등록제 · 출동 계약제 — 자원봉사가 아니라 산업으로", { x: 0.6, y: 4.55, w: 8.8, h: 0.32, fontFace: F, fontSize: 12.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
s.addText("＋  '제주 안전 대시보드' — 신고와 해제 건수, 초동 확인 시간을 도가 직접 공개", { x: 0.6, y: 4.9, w: 8.8, h: 0.32, fontFace: F, fontSize: 12.5, bold: true, color: PRIMARY, isTextBox: true, margin: 0 });

/* ---------- 12. 다목적 ---------- */
s = pres.addSlide();
titleBlock(s, "하나의 인프라, 여러 임무", "치안 예산만으로 짓는 시설이 아닙니다");
function chip(x, y, w, t, d) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h: 0.82, rectRadius: 0.06, fill: { color: SOFT }, line: { color: LINEC, width: 1 } });
  s.addText(t, { x: x + 0.16, y: y + 0.1, w: w - 0.32, h: 0.32, fontFace: F, fontSize: 13, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  s.addText(d, { x: x + 0.16, y: y + 0.42, w: w - 0.32, h: 0.3, fontFace: F, fontSize: 10, color: GRAY, isTextBox: true, margin: 0 });
}
chip(0.9, 1.62, 2.7, "치안 · 구조", "실종 수색 · 순찰 · 인파 관리");
chip(6.4, 1.62, 2.7, "재난 대응", "호우 · 산불 초기 확산 경로");
chip(0.9, 3.72, 2.7, "수자원 점검", "하천 · 저수지 · 급경사지");
chip(6.4, 3.72, 2.7, "환경 모니터링", "해안 침식 · 해양쓰레기 유입");
s.addShape(pres.ShapeType.roundRect, { x: 3.85, y: 2.5, w: 2.3, h: 1.0, rectRadius: 0.08, fill: { color: NAVY }, line: { color: NAVY, width: 0 }, shadow: sh() });
s.addText("드론 스테이션", { x: 3.85, y: 2.5, w: 2.3, h: 1.0, fontFace: F, fontSize: 15, bold: true, color: WHITE, align: "center", valign: "middle", isTextBox: true, margin: 0 });
foot(s, "부서가 나눠 쓰면 비용은 줄고 가동률은 올라갑니다 — '기후경제수도 제주' 비전과 맞물리는 지점");

/* ---------- 13. 로드맵 · 지표 ---------- */
s = pres.addSlide();
s.background = { color: NAVY };
titleBlock(s, "로드맵과 지표", "2027년에 데이터로 증명합니다", true);
const phases = [
  ["2026. 4분기", "준비", "특구 연장 신청 반영\n조례안 입안\n도착시간 실측 공개"],
  ["2027. 상반기", "실증", "스테이션 2~3개소\nAI 치안드론 연계\n도달시간 측정"],
  ["2027. 하반기", "확산", "8개소 확대\n112·119·해경 공동대응\n민간 출동 계약제"],
  ["2028", "정착", "도 전역 운영\n부서 공동 활용\n제주형 표준모델"],
];
phases.forEach((p, i) => {
  const x = 0.6 + i * 2.24;
  s.addShape(pres.ShapeType.roundRect, { x, y: 1.62, w: 2.08, h: 1.85, rectRadius: 0.06,
    fill: { color: "1B3A57" }, line: { color: "27506F", width: 1 } });
  s.addText(p[0], { x: x + 0.16, y: 1.74, w: 1.76, h: 0.28, fontFace: F, fontSize: 10, color: MIST, isTextBox: true, margin: 0 });
  s.addText(p[1], { x: x + 0.16, y: 2.02, w: 1.76, h: 0.34, fontFace: F, fontSize: 16, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText(p[2], { x: x + 0.16, y: 2.42, w: 1.76, h: 0.95, fontFace: F, fontSize: 9.5, color: ICE, isTextBox: true, margin: 0, lineSpacingMultiple: 1.25 });
});
s.addText("성과 지표", { x: 0.6, y: 3.62, w: 3.0, h: 0.28, fontFace: F, fontSize: 11, bold: true, color: MIST, isTextBox: true, margin: 0 });
const kpis = ["신고~상공 도달 시간", "초동 확인 자동 수행률", "야간 순찰 커버리지", "체감 안전도", "출동 인력 절감"];
kpis.forEach((k, i) => {
  const x = 0.6 + i * 1.79;
  s.addShape(pres.ShapeType.roundRect, { x, y: 3.95, w: 1.66, h: 0.62, rectRadius: 0.06, fill: { color: "16334D" }, line: { color: "27506F", width: 1 } });
  s.addText(k, { x: x + 0.08, y: 3.95, w: 1.5, h: 0.62, fontFace: F, fontSize: 9.5, color: ICE, align: "center", valign: "middle", isTextBox: true, margin: 0 });
});
s.addText("\"신고 3분 뒤 하늘에서 그곳을 볼 수 있는가, 그 확인이 기록으로 남는가\"", {
  x: 0.6, y: 4.82, w: 8.8, h: 0.42, fontFace: F, fontSize: 14, bold: true, color: WHITE, isTextBox: true, margin: 0 });
s.addNotes("마무리: 제주가 먼저 하면 전국이 따라 쓰는 제주형 표준 모델이자, 제주가 수출하는 산업이 된다.");

pres.writeFile({ fileName: process.argv[2] }).then(f => console.log("saved", f));
