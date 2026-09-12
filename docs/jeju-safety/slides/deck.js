const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625
pres.author = "";
pres.title = "3분 안에 뜨는 제주";

const NAVY = "10243A", PRIMARY = "065A82", TEAL = "1C7293",
      ICE = "CADCFC", SOFT = "F2F6F9", WHITE = "FFFFFF",
      GRAY = "5A6A78", CORAL = "E0523C", MIST = "8FB4C9";
const F = "맑은 고딕";
const sh = () => ({ type: "outer", color: "0B1B2B", blur: 8, offset: 2, angle: 90, opacity: 0.12 });

function titleBlock(s, t, sub, dark, size) {
  s.addText(t, { x: 0.6, y: 0.42, w: 8.8, h: 0.62, fontFace: F, fontSize: size || 32, bold: true,
    color: dark ? WHITE : NAVY, isTextBox: true, margin: 0 });
  if (sub) s.addText(sub, { x: 0.6, y: 1.03, w: 8.8, h: 0.36, fontFace: F, fontSize: 13,
    color: dark ? MIST : GRAY, isTextBox: true, margin: 0 });
}
function card(s, o) {
  s.addShape(pres.ShapeType.roundRect, { x: o.x, y: o.y, w: o.w, h: o.h, rectRadius: 0.06,
    fill: { color: o.fill || SOFT }, line: { color: o.line || (o.fill ? o.fill : "E3EAF0"), width: 1 }, shadow: sh() });
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
s.addNotes("도정이 이미 잘하고 있는 것을 인정하는 데서 출발한다. 비판이 아니라 보완 제안임을 톤으로 전달할 것.");

/* ---------- 2. 제주가 이미 가진 것 ---------- */
s = pres.addSlide();
titleBlock(s, "제주가 이미 가진 것", "자산은 이미 갖춰져 있습니다");
const assets = [
  ["유일", "전국 유일 자치경찰단", "도지사가 직접 지휘하는\n치안 자원"],
  ["최초", "전국 최초 AI 치안드론", "2027년 현장 투입 예정\n(국비 8억 · 도비 2억)"],
  ["1,283㎢", "전국 최대 드론특구", "비가시권 · 야간 실증이\n제도적으로 가능"],
  ["1,543명", "민관 공동체 치안망", "주민자치경찰대 · 시니어\n민간경비 · 민간드론"],
];
assets.forEach((a, i) => {
  const x = 0.6 + i * 2.26;
  card(s, { x, y: 1.72, w: 2.06, h: 2.55 });
  s.addText(a[0], { x: x + 0.16, y: 1.95, w: 1.74, h: 0.55, fontFace: F, fontSize: 24, bold: true,
    color: PRIMARY, isTextBox: true, margin: 0 });
  s.addText(a[1], { x: x + 0.16, y: 2.55, w: 1.74, h: 0.6, fontFace: F, fontSize: 13, bold: true,
    color: NAVY, isTextBox: true, margin: 0 });
  s.addText(a[2], { x: x + 0.16, y: 3.18, w: 1.74, h: 0.95, fontFace: F, fontSize: 10,
    color: GRAY, isTextBox: true, margin: 0, lineSpacingMultiple: 1.15 });
});
s.addText("새 사업을 만들자는 제안이 아닙니다. 있는 자산을 잇자는 제안입니다.", {
  x: 0.6, y: 4.55, w: 8.8, h: 0.4, fontFace: F, fontSize: 14, color: NAVY, isTextBox: true, margin: 0 });

/* ---------- 3. 비어 있는 한 칸 ---------- */
s = pres.addSlide();
s.background = { color: NAVY };
titleBlock(s, "그런데 왜 불안은 줄지 않는가", "네 가지 자산을 잇는 한 칸이 비어 있습니다", true);
["자치경찰단", "AI 치안드론", "드론특구", "공동체 치안망"].forEach((t, i) => {
  const x = 0.6 + i * 2.26;
  s.addShape(pres.ShapeType.roundRect, { x, y: 1.75, w: 2.06, h: 0.85, rectRadius: 0.06,
    fill: { color: "1B3A57" }, line: { color: "1B3A57", width: 0 } });
  s.addText(t, { x, y: 1.75, w: 2.06, h: 0.85, fontFace: F, fontSize: 13, color: ICE,
    align: "center", valign: "middle", isTextBox: true, margin: 0 });
});
s.addShape(pres.ShapeType.roundRect, { x: 0.6, y: 3.0, w: 8.8, h: 1.15, rectRadius: 0.04,
  fill: { color: NAVY }, line: { color: CORAL, width: 2, dashType: "dash" } });
s.addText("비어 있는 것 :  신고 즉시 뜨는 '출동 체계'", {
  x: 0.7, y: 3.0, w: 8.6, h: 1.15, fontFace: F, fontSize: 22, bold: true, color: CORAL,
  align: "center", valign: "middle", isTextBox: true, margin: 0 });
s.addText("기체가 없어서가 아니라, 기체를 배치하는 방식이 비어 있습니다.", {
  x: 0.6, y: 4.4, w: 8.8, h: 0.4, fontFace: F, fontSize: 14, color: MIST, align: "center", isTextBox: true, margin: 0 });

/* ---------- 4. 문제는 시간이다 ---------- */
s = pres.addSlide();
titleBlock(s, "문제는 '시간'입니다", "신고가 접수된 시점과, 하늘에서 그곳을 처음 본 시점 사이");
function timeline(y, label, steps, result, color, resultColor) {
  s.addText(label, { x: 0.6, y: y + 0.12, w: 0.95, h: 0.4, fontFace: F, fontSize: 13, bold: true,
    color: NAVY, isTextBox: true, margin: 0 });
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
timeline(1.95, "", ["신고 접수", "인력 이동", "현장 도착", "이륙"], "수십 분", "FBE7E3", CORAL);
s.addText("제안  ·  상시 출동형", { x: 0.6, y: 3.05, w: 3.0, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: PRIMARY, isTextBox: true, margin: 0 });
timeline(3.38, "", ["신고 접수", "자동 이륙"], "3~5분", "E1EEF4", PRIMARY);
s.addText("실종·조난의 초기 3시간이, 장비를 현장까지 옮기는 데 소모되고 있습니다.", {
  x: 0.6, y: 4.55, w: 8.8, h: 0.4, fontFace: F, fontSize: 14, color: NAVY, isTextBox: true, margin: 0 });

/* ---------- 5. 지상 순찰이 닿지 않는 곳 ---------- */
s = pres.addSlide();
titleBlock(s, "지상 순찰이 닿지 않는 곳", "사고와 실종은 도심이 아니라 이곳에 몰립니다");
["올레길", "오름 · 곶자왈", "해안 절벽", "야간 해수욕장", "한라산 주요 탐방로"].forEach((t, i) => {
  const y = 1.72 + i * 0.62;
  s.addShape(pres.ShapeType.ellipse, { x: 0.62, y: y + 0.11, w: 0.2, h: 0.2, fill: { color: TEAL }, line: { color: TEAL, width: 0 } });
  s.addText(t, { x: 0.98, y, w: 3.6, h: 0.42, fontFace: F, fontSize: 15, color: NAVY,
    valign: "middle", isTextBox: true, margin: 0 });
});
card(s, { x: 5.1, y: 1.68, w: 4.3, h: 2.6, fill: NAVY, line: NAVY });
s.addText("순찰차가 들어갈 수 없는 곳", { x: 5.4, y: 2.0, w: 3.7, h: 0.6, fontFace: F, fontSize: 20,
  bold: true, color: WHITE, isTextBox: true, margin: 0 });
s.addText("지상 인력을 아무리 늘려도\n도달 시간은 줄지 않는 구조입니다.\n\n하늘에서 접근하는 수단이\n인력을 대신하는 것이 아니라,\n인력이 갈 곳을 정해 줍니다.", {
  x: 5.4, y: 2.62, w: 3.7, h: 1.5, fontFace: F, fontSize: 12, color: ICE, isTextBox: true, margin: 0, lineSpacingMultiple: 1.2 });
s.addText("면적 1,850㎢, 해안선과 중산간이 함께 있는 제주의 지형 조건", {
  x: 0.6, y: 4.85, w: 8.8, h: 0.35, fontFace: F, fontSize: 11, color: GRAY, isTextBox: true, margin: 0 });

/* ---------- 6. DFR ---------- */
s = pres.addSlide();
titleBlock(s, "DFR — 사람보다 먼저 도착하는 눈", "Drone as First Responder  ·  최초 출동 드론");
const steps = [
  ["112 · 119 신고 접수", "신고 정보가 관제센터로\n즉시 연동됩니다."],
  ["무인 격납고 자동 이륙", "사람이 출발하기 전에\n기체가 먼저 뜹니다."],
  ["실시간 영상 공유", "관제센터와 출동 인력이\n동시에 현장을 봅니다."],
];
steps.forEach((st, i) => {
  const x = 0.6 + i * 2.98;
  card(s, { x, y: 1.72, w: 2.84, h: 2.45 });
  s.addShape(pres.ShapeType.ellipse, { x: x + 0.24, y: 1.96, w: 0.5, h: 0.5, fill: { color: PRIMARY }, line: { color: PRIMARY, width: 0 } });
  s.addText(String(i + 1), { x: x + 0.24, y: 1.96, w: 0.5, h: 0.5, fontFace: F, fontSize: 16, bold: true,
    color: WHITE, align: "center", valign: "middle", isTextBox: true, margin: 0 });
  s.addText(st[0], { x: x + 0.24, y: 2.62, w: 2.36, h: 0.5, fontFace: F, fontSize: 14, bold: true,
    color: NAVY, isTextBox: true, margin: 0 });
  s.addText(st[1], { x: x + 0.24, y: 3.16, w: 2.36, h: 0.8, fontFace: F, fontSize: 11, color: GRAY,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.2 });
});
s.addText("AI가 아무리 좋아도 기체가 30분 뒤에 뜨면 소용이 없습니다. 그 AI를 태울 출동 체계가 필요합니다.", {
  x: 0.6, y: 4.5, w: 8.8, h: 0.4, fontFace: F, fontSize: 13, color: NAVY, isTextBox: true, margin: 0 });

/* ---------- 7. 비교표 ---------- */
s = pres.addSlide();
titleBlock(s, "무엇이 달라지는가", "같은 기체라도 배치를 바꾸면 역할이 달라집니다");
const hdr = o => ({ fill: { color: NAVY }, color: WHITE, bold: true });
const rows = [
  [{ text: "구분", options: hdr() }, { text: "현행  ·  동원형", options: hdr() }, { text: "제안  ·  상시 출동형", options: hdr() }],
  ["이륙 주체", "현장에 도착한 조종 인력", "관제센터 원격 · 자동"],
  ["상공 확보", "수십 분", "3 ~ 5분"],
  ["야간 · 저시정", "사실상 제한", "열화상 + 자동비행으로 상시"],
  ["역할", "사후 수색", "선제 인지 + 출동 유도"],
  ["인력 소모", "건당 다수 투입", "관제 1명이 다수 거점 운용"],
];
s.addTable(rows, {
  x: 0.6, y: 1.75, w: 8.8, colW: [2.0, 3.4, 3.4], rowH: 0.44,
  fontFace: F, fontSize: 12, color: NAVY, valign: "middle",
  border: { type: "solid", color: "DCE5EC", pt: 1 },
  fill: { color: WHITE }, margin: 0.08, autoPage: false,
});
s.addText("출동 인력이 '가기 전에' 현장을 봅니다. 한정된 인력을 꼭 필요한 곳에 쓰게 됩니다.", {
  x: 0.6, y: 4.65, w: 8.8, h: 0.4, fontFace: F, fontSize: 13, color: NAVY, isTextBox: true, margin: 0 });

/* ---------- 8. 제언 1 ---------- */
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
  s.addShape(pres.ShapeType.roundRect, { x, y, w: 2.62, h: 0.5, rectRadius: 0.06,
    fill: { color: SOFT }, line: { color: "E3EAF0", width: 1 } });
  s.addText(t, { x: x + 0.14, y, w: 2.4, h: 0.5, fontFace: F, fontSize: 11, color: NAVY,
    valign: "middle", isTextBox: true, margin: 0 });
});
s.addText("도달 시간과 발견율 데이터를 확보한 뒤 도 전역으로 확대", {
  x: 3.95, y: 4.78, w: 5.45, h: 0.35, fontFace: F, fontSize: 11, color: GRAY, isTextBox: true, margin: 0 });

/* ---------- 9. 제언 2 ---------- */
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
  x: 0.6, y: 4.4, w: 8.8, h: 0.62, fontFace: F, fontSize: 14, bold: true, color: WHITE,
  align: "center", valign: "middle", isTextBox: true, margin: 0 });

/* ---------- 10. 제언 3 ---------- */
s = pres.addSlide();
titleBlock(s, "제언 ③   거버넌스 — 조례가 곧 면허증", "기체를 띄우기 전에 원칙을 먼저 세웁니다", false, 28);
const rules = [
  ["촬영 사실 표시", "언제 어디서 촬영되는지\n도민이 알 수 있게 한다"],
  ["목적 외 이용 금지", "신고 기반 출동 원칙,\n상시 배회 감시가 아니다"],
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
s.addText("＋  민간 드론 인력 등록제 · 출동 계약제 — 자원봉사가 아니라 산업으로", {
  x: 0.6, y: 4.62, w: 8.8, h: 0.4, fontFace: F, fontSize: 14, bold: true, color: NAVY, isTextBox: true, margin: 0 });

/* ---------- 11. 다목적 ---------- */
s = pres.addSlide();
titleBlock(s, "하나의 인프라, 여러 임무", "치안 예산만으로 짓는 시설이 아닙니다");
function chip(x, y, w, t, d) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h: 0.82, rectRadius: 0.06, fill: { color: SOFT }, line: { color: "E3EAF0", width: 1 } });
  s.addText(t, { x: x + 0.16, y: y + 0.1, w: w - 0.32, h: 0.32, fontFace: F, fontSize: 13, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  s.addText(d, { x: x + 0.16, y: y + 0.42, w: w - 0.32, h: 0.3, fontFace: F, fontSize: 10, color: GRAY, isTextBox: true, margin: 0 });
}
chip(0.9, 1.62, 2.7, "치안 · 구조", "실종 수색 · 순찰 · 인파 관리");
chip(6.4, 1.62, 2.7, "재난 대응", "호우 · 산불 초기 확산 경로");
chip(0.9, 3.72, 2.7, "수자원 점검", "하천 · 저수지 · 급경사지");
chip(6.4, 3.72, 2.7, "환경 모니터링", "해안 침식 · 해양쓰레기 유입");
s.addShape(pres.ShapeType.roundRect, { x: 3.85, y: 2.5, w: 2.3, h: 1.0, rectRadius: 0.08, fill: { color: NAVY }, line: { color: NAVY, width: 0 }, shadow: sh() });
s.addText("드론 스테이션", { x: 3.85, y: 2.5, w: 2.3, h: 1.0, fontFace: F, fontSize: 15, bold: true, color: WHITE, align: "center", valign: "middle", isTextBox: true, margin: 0 });
s.addText("부서가 나눠 쓰면 비용은 줄고 가동률은 올라갑니다 — '기후경제수도 제주' 비전과 맞물리는 지점", {
  x: 0.6, y: 4.78, w: 8.8, h: 0.4, fontFace: F, fontSize: 12, color: NAVY, isTextBox: true, margin: 0 });

/* ---------- 12. 로드맵 · 지표 ---------- */
s = pres.addSlide();
s.background = { color: NAVY };
titleBlock(s, "로드맵과 지표", "2027년에 데이터로 증명합니다", true);
const phases = [
  ["2026. 4분기", "준비", "특구 연장 신청 반영\n조례안 입안\n대상지 선정"],
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
const kpis = ["신고~상공 도달 시간", "초기 3시간 내 발견율", "야간 순찰 커버리지", "체감 안전도", "출동 인력 절감"];
kpis.forEach((k, i) => {
  const x = 0.6 + i * 1.79;
  s.addShape(pres.ShapeType.roundRect, { x, y: 3.95, w: 1.66, h: 0.62, rectRadius: 0.06, fill: { color: "16334D" }, line: { color: "27506F", width: 1 } });
  s.addText(k, { x: x + 0.08, y: 3.95, w: 1.5, h: 0.62, fontFace: F, fontSize: 9.5, color: ICE, align: "center", valign: "middle", isTextBox: true, margin: 0 });
});
s.addText("\"신고가 들어오고 3분 뒤, 하늘에서 그곳을 볼 수 있는가\"  —  그것이 안전의 실질입니다.", {
  x: 0.6, y: 4.82, w: 8.8, h: 0.42, fontFace: F, fontSize: 14, bold: true, color: WHITE, isTextBox: true, margin: 0 });
s.addNotes("마무리: 제주가 먼저 하면 전국이 따라 쓰는 제주형 표준 모델이자, 제주가 수출하는 산업이 된다.");

pres.writeFile({ fileName: process.argv[2] }).then(f => console.log("saved", f));
