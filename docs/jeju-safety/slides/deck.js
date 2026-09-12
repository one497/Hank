const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625
pres.title = "진짜 지도";

const NAVY="0E1F33", DEEP="123048", PRIMARY="0A6B8A", TEAL="1C7293",
      ICE="CFE3EE", SOFT="F3F7FA", WHITE="FFFFFF", GRAY="5A6A78",
      AMBER="D9822B", LINEC="E2EAF0", MUTE="8FB0C4";
const F = "맑은 고딕";
const sh = () => ({ type:"outer", color:"0B1B2B", blur:8, offset:2, angle:90, opacity:0.12 });

function title(s, t, sub, dark, size){
  s.addText(t, { x:0.7, y:0.45, w:8.6, h:0.7, fontFace:F, fontSize:size||32, bold:true,
    color: dark?WHITE:NAVY, isTextBox:true, margin:0 });
  if(sub) s.addText(sub, { x:0.7, y:1.12, w:8.6, h:0.36, fontFace:F, fontSize:13,
    color: dark?MUTE:GRAY, isTextBox:true, margin:0 });
}
function card(s,o){
  s.addShape(pres.ShapeType.roundRect, { x:o.x, y:o.y, w:o.w, h:o.h, rectRadius:0.06,
    fill:{color:o.fill||SOFT}, line:{color:o.line||(o.fill?o.fill:LINEC), width:1}, shadow: sh() });
}

/* 1. 표지 */
let s = pres.addSlide();
s.background = { color: NAVY };
s.addText("진짜 지도", { x:0.8, y:1.75, w:8.4, h:1.15, fontFace:F, fontSize:54, bold:true, color:WHITE, isTextBox:true, margin:0 });
s.addText("\"귤보디아\"라는 말이 싫어서 — 땅을 재던 사람이 시작한 일", {
  x:0.82, y:2.95, w:8.4, h:0.45, fontFace:F, fontSize:17, color:ICE, isTextBox:true, margin:0 });
s.addText("2026 코리아스타트업포럼 제주 혁신 대담", { x:0.82, y:4.35, w:8.4, h:0.3, fontFace:F, fontSize:12, color:MUTE, isTextBox:true, margin:0 });
s.addText("[회사명]  ·  [OOO]  ·  2026. 9. 18.", { x:0.82, y:4.68, w:8.4, h:0.3, fontFace:F, fontSize:11, color:"6E8598", isTextBox:true, margin:0 });
s.addNotes("인사. 정책을 제안하러 온 것이 아니라는 점을 톤으로 먼저 전한다.");

/* 2. 귤보디아 */
s = pres.addSlide();
s.background = { color: NAVY };
s.addText("귤보디아", { x:0.6, y:2.1, w:8.8, h:1.4, fontFace:F, fontSize:72, bold:true,
  color:WHITE, align:"center", valign:"middle", isTextBox:true, margin:0 });
s.addNotes("이 발표의 승부처. \"요즘 제주를 부르는 별명이 하나 생겼습니다\" 라고만 말하고 3초 침묵한다. 설명하지 않는다.\n\n[대체 버전] 단어를 쓰지 않기로 했다면 이 슬라이드의 텍스트를 \"요즘 제주를 부르는 별명\" 으로 바꾼다.");

/* 3. 부탁으로는 그림을 못 이깁니다 */
s = pres.addSlide();
s.background = { color: NAVY };
title(s, "부탁으로는 그림을 못 이깁니다", null, true, 30);
s.addShape(pres.ShapeType.roundRect, { x:0.9, y:1.9, w:3.5, h:2.2, rectRadius:0.06, fill:{color:DEEP}, line:{color:"1E4560", width:1} });
s.addText("지도 한 장", { x:1.1, y:2.15, w:3.1, h:0.45, fontFace:F, fontSize:20, bold:true, color:WHITE, isTextBox:true, margin:0 });
s.addText("점을 찍어 올렸습니다.\n하루 만에 퍼졌습니다.", { x:1.1, y:2.7, w:3.1, h:0.8, fontFace:F, fontSize:13, color:ICE, isTextBox:true, margin:0, lineSpacingMultiple:1.25 });
s.addText("＞", { x:4.5, y:1.9, w:1.0, h:2.2, fontFace:F, fontSize:30, bold:true, color:AMBER, align:"center", valign:"middle", isTextBox:true, margin:0 });
s.addShape(pres.ShapeType.roundRect, { x:5.6, y:1.9, w:3.5, h:2.2, rectRadius:0.06, fill:{color:DEEP}, line:{color:"1E4560", width:1} });
s.addText("부탁 한 줄", { x:5.8, y:2.15, w:3.1, h:0.45, fontFace:F, fontSize:20, bold:true, color:MUTE, isTextBox:true, margin:0 });
s.addText("\"유포를 자제해 주십시오.\"\n이미 퍼진 뒤였습니다.", { x:5.8, y:2.7, w:3.1, h:0.8, fontFace:F, fontSize:13, color:MUTE, isTextBox:true, margin:0, lineSpacingMultiple:1.25 });
s.addText("그림을 이기는 건 더 정확한 그림입니다.", { x:0.7, y:4.45, w:8.6, h:0.4, fontFace:F, fontSize:15, bold:true, color:WHITE, align:"center", isTextBox:true, margin:0 });
s.addNotes("괴담 이미지 원본은 절대 띄우지 않는다. 이 슬라이드의 카드로 대체한다.");

/* 4. 저는 땅을 재는 사람입니다 */
s = pres.addSlide();
title(s, "저는 땅을 재는 사람입니다", "안전 전문가도, 치안 전문가도 아닙니다");
const me = [
  ["토목 · 시공", "땅을 재고 설계하고\n구조물을 짓습니다"],
  ["수자원", "하천과 저수지, 사면을\n다룹니다"],
  ["드론 측량", "사흘 걸리던 측량을\n반나절에 합니다"],
];
me.forEach((m,i)=>{
  const x = 0.7 + i*2.94;
  card(s,{x, y:1.85, w:2.8, h:2.3});
  s.addShape(pres.ShapeType.ellipse, { x:x+0.26, y:2.12, w:0.46, h:0.46, fill:{color:PRIMARY}, line:{color:PRIMARY, width:0} });
  s.addText(String(i+1), { x:x+0.26, y:2.12, w:0.46, h:0.46, fontFace:F, fontSize:15, bold:true, color:WHITE, align:"center", valign:"middle", isTextBox:true, margin:0 });
  s.addText(m[0], { x:x+0.26, y:2.75, w:2.28, h:0.4, fontFace:F, fontSize:17, bold:true, color:NAVY, isTextBox:true, margin:0 });
  s.addText(m[1], { x:x+0.26, y:3.2, w:2.28, h:0.7, fontFace:F, fontSize:12, color:GRAY, isTextBox:true, margin:0, lineSpacingMultiple:1.25 });
});
s.addNotes("포럼이 대표 소개 슬라이드를 따로 만들어 주면 이 장은 덜어낸다.");

/* 5. 위험한 곳일수록 직접 가야 합니다 */
s = pres.addSlide();
title(s, "위험한 곳일수록, 직접 가야 합니다", "제 일에는 오래된 문제가 하나 있습니다");
s.addText("비가 온 다음 날\n하천 제방을 봐야 합니다.\n사면이 무너졌는지\n확인해야 합니다.\n\n그런데 그런 곳은\n대부분 차가\n들어가지 못합니다.", {
  x:0.7, y:1.85, w:3.6, h:2.9, fontFace:F, fontSize:16, color:NAVY, isTextBox:true, margin:0, lineSpacingMultiple:1.35 });
s.addShape(pres.ShapeType.roundRect, { x:4.7, y:1.85, w:4.6, h:2.9, rectRadius:0.06,
  fill:{color:SOFT}, line:{color:MUTE, width:1.5, dashType:"dash"} });
s.addText("[ 현장 사진 ]\n\n대표님이 실제로 찍은 사진\n접근이 막힌 지형이 좋습니다", {
  x:4.9, y:1.85, w:4.2, h:2.9, fontFace:F, fontSize:13, color:GRAY, align:"center", valign:"middle", isTextBox:true, margin:0, lineSpacingMultiple:1.3 });
s.addNotes("★ 이 발표의 심장. 실제 현장 이야기를 여기서 한다. 언제 어디서 무엇을 확인하러 갔고 얼마나 걸렸는지, 그때 무슨 생각이 들었는지. 스톡 이미지는 쓰지 않는다.");

/* 6. 달라진 두 가지 */
s = pres.addSlide();
title(s, "드론을 쓰고 달라진 두 가지", null);
card(s,{x:0.7, y:1.8, w:8.6, h:1.2});
s.addText("가지 않고도 본다", { x:1.1, y:1.8, w:5.0, h:1.2, fontFace:F, fontSize:26, bold:true, color:NAVY, valign:"middle", isTextBox:true, margin:0 });
s.addText("반나절 → 5분", { x:6.2, y:1.8, w:2.8, h:1.2, fontFace:F, fontSize:16, color:GRAY, align:"right", valign:"middle", isTextBox:true, margin:0 });
card(s,{x:0.7, y:3.15, w:8.6, h:1.2, fill:NAVY, line:NAVY});
s.addText("본 것이 남는다", { x:1.1, y:3.15, w:5.0, h:1.2, fontFace:F, fontSize:26, bold:true, color:WHITE, valign:"middle", isTextBox:true, margin:0 });
s.addText("말이 아니라 파일로", { x:6.2, y:3.15, w:2.8, h:1.2, fontFace:F, fontSize:16, color:ICE, align:"right", valign:"middle", isTextBox:true, margin:0 });
s.addText("두 번째가 더 중요했습니다.", { x:0.7, y:4.6, w:8.6, h:0.4, fontFace:F, fontSize:15, bold:true, color:PRIMARY, isTextBox:true, margin:0 });

/* 7. 이번 일도 똑같았습니다 */
s = pres.addSlide();
title(s, "그런데 이번 일이 똑같았습니다", "제 현장에서 늘 겪던 두 가지가 그대로 있었습니다");
const same = [
  ["가야 볼 수 있는데,\n갈 수가 없었습니다", "제주 방범 카메라 19,096대\n인구 대비 전국 평균의 두 배\n\n그런데 전부 고정형입니다.\n사고는 오름에서, 해안 절벽에서,\n올레길에서 납니다."],
  ["확인했다는 기록이\n남지 않았습니다", "무엇을 확인했는지,\n확인하기는 했는지가\n남아 있지 않았습니다.\n\n\"가서 봤습니다\"라는 말만\n남던 제 현장과 같습니다."],
];
same.forEach((g,i)=>{
  const x = 0.7 + i*4.5;
  card(s,{x, y:1.8, w:4.1, h:2.85});
  s.addText(g[0], { x:x+0.28, y:2.0, w:3.54, h:0.75, fontFace:F, fontSize:17, bold:true, color:NAVY, isTextBox:true, margin:0, lineSpacingMultiple:1.2 });
  s.addText(g[1], { x:x+0.28, y:2.85, w:3.54, h:1.6, fontFace:F, fontSize:12, color:GRAY, isTextBox:true, margin:0, lineSpacingMultiple:1.3 });
});
s.addText("말은 지워지고, 파일은 남습니다.", { x:0.7, y:4.8, w:8.6, h:0.38, fontFace:F, fontSize:14, bold:true, color:PRIMARY, isTextBox:true, margin:0 });

/* 8. 점만 있는 지도 / 진짜 지도 */
s = pres.addSlide();
title(s, "그건 지도가 아니라 공포입니다", "같은 섬을 그려도 전혀 다른 그림이 됩니다");
s.addShape(pres.ShapeType.roundRect, { x:0.7, y:1.8, w:4.1, h:2.95, rectRadius:0.06, fill:{color:"EDEFF1"}, line:{color:"DDE3E8", width:1} });
s.addText("떠도는 지도", { x:0.95, y:1.98, w:3.6, h:0.36, fontFace:F, fontSize:15, bold:true, color:"7A8894", isTextBox:true, margin:0 });
["점만 찍혀 있다", "누가 만들었는지 모른다", "\"여기서 사라졌다\"", "공포를 만든다"].forEach((t,i)=>{
  s.addText("· " + t, { x:0.95, y:2.45+i*0.55, w:3.6, h:0.4, fontFace:F, fontSize:13, color:"7A8894", isTextBox:true, margin:0 });
});
s.addShape(pres.ShapeType.roundRect, { x:5.2, y:1.8, w:4.1, h:2.95, rectRadius:0.06, fill:{color:NAVY}, line:{color:NAVY, width:0}, shadow: sh() });
s.addText("진짜 지도", { x:5.45, y:1.98, w:3.6, h:0.36, fontFace:F, fontSize:15, bold:true, color:AMBER, isTextBox:true, margin:0 });
["지형과 접근로가 있다", "누가 언제 쟀는지 남는다", "\"여기는 몇 분 만에 닿는다\"", "대응을 만든다"].forEach((t,i)=>{
  s.addText("· " + t, { x:5.45, y:2.45+i*0.55, w:3.6, h:0.4, fontFace:F, fontSize:13, color:WHITE, isTextBox:true, margin:0 });
});
s.addText("그리고 지도를 만드는 건, 제가 할 줄 아는 일입니다.", { x:0.7, y:4.85, w:8.6, h:0.38, fontFace:F, fontSize:14, bold:true, color:NAVY, isTextBox:true, margin:0 });

/* 9. 재고 짓고 남긴다 */
s = pres.addSlide();
title(s, "재고, 짓고, 남긴다", "자랑은 여기서 한 번만 하겠습니다");
const steps = [
  ["잰다", "사고·실종 다발 구간을\n정밀 측량해 지형·접근로·\n도달 시간 지도를 만든다", "드론 운용 · 촬영 · 측량"],
  ["짓는다", "그 지도 위에 거점을 놓는다.\n지구대·관제센터처럼 전기와\n통신이 있는 자리에 얹는다", "토목 · 시설 설계 및 시공"],
  ["남긴다", "신고가 오면 자동으로 뜨고,\n언제 어디를 봤는지가\n사람의 보고와 따로 남는다", "관제 · 소프트웨어 · 데이터"],
];
steps.forEach((st,i)=>{
  const x = 0.7 + i*2.94;
  card(s,{x, y:1.8, w:2.8, h:2.65});
  s.addText(st[0], { x:x+0.26, y:2.0, w:2.28, h:0.5, fontFace:F, fontSize:24, bold:true, color:PRIMARY, isTextBox:true, margin:0 });
  s.addText(st[1], { x:x+0.26, y:2.6, w:2.28, h:1.15, fontFace:F, fontSize:11.5, color:GRAY, isTextBox:true, margin:0, lineSpacingMultiple:1.3 });
  s.addText(st[2], { x:x+0.26, y:3.92, w:2.28, h:0.4, fontFace:F, fontSize:10, bold:true, color:NAVY, isTextBox:true, margin:0 });
});
s.addText("드론 업체는 짓지 못하고, 건설사는 날리지 못합니다.\n이 셋을 이어서 하는 것이 저희가 가진 전부입니다.", {
  x:0.7, y:4.6, w:8.6, h:0.72, fontFace:F, fontSize:12.5, color:NAVY, isTextBox:true, margin:0, lineSpacingMultiple:1.2 });
s.addNotes("효과를 과장하지 않는다. 질문이 오면: 드론 투입 시 약 3분 단축, 전체 발견율은 유사. 연구 결론은 '성패는 기체가 아니라 훈련과 절차'.");

/* 10. 786 */
s = pres.addSlide();
title(s, "저도 이번에 찾아보고 알았습니다", null);
s.addText("786", { x:0.7, y:1.75, w:4.0, h:1.5, fontFace:F, fontSize:80, bold:true, color:PRIMARY, isTextBox:true, margin:0 });
s.addText("건", { x:3.15, y:2.75, w:1.0, h:0.5, fontFace:F, fontSize:22, color:GRAY, isTextBox:true, margin:0 });
s.addText("지난해 제주의 성인 실종 신고", { x:0.75, y:3.3, w:4.0, h:0.35, fontFace:F, fontSize:15, bold:true, color:NAVY, isTextBox:true, margin:0 });
card(s,{x:5.1, y:1.8, w:4.2, h:2.5});
s.addText("전국 70,814건의  1.1%", { x:5.4, y:2.1, w:3.6, h:0.45, fontFace:F, fontSize:18, bold:true, color:NAVY, isTextBox:true, margin:0 });
s.addText("제주 인구는 전국의 1.3%입니다.", { x:5.4, y:2.6, w:3.6, h:0.35, fontFace:F, fontSize:13, color:GRAY, isTextBox:true, margin:0 });
s.addText("인구 대비로는\n전국 평균보다 낮습니다.", { x:5.4, y:3.1, w:3.6, h:0.8, fontFace:F, fontSize:16, bold:true, color:PRIMARY, isTextBox:true, margin:0, lineSpacingMultiple:1.2 });
s.addText("진실은 있는데, 보여줄 형태로 만들어 놓지 않았습니다.", { x:0.7, y:4.6, w:8.6, h:0.4, fontFace:F, fontSize:15, bold:true, color:NAVY, isTextBox:true, margin:0 });
s.addText("출처: 경찰청 실종신고 처리 현황 (2025년) — 발표 전 원자료 재확인", { x:0.7, y:5.05, w:8.6, h:0.28, fontFace:F, fontSize:8.5, color:"8895A2", isTextBox:true, margin:0 });

/* 11. 부정하지 말고 증명하면 됩니다 */
s = pres.addSlide();
title(s, "부정하지 말고, 증명하면 됩니다", null);
["재서 지도로 만들고", "거점을 지어 몇 분 만에 닿는지 보여주고", "확인한 것을 기록으로 남기면 됩니다"].forEach((t,i)=>{
  s.addShape(pres.ShapeType.roundRect, { x:0.7, y:1.85+i*0.92, w:8.6, h:0.78, rectRadius:0.06, fill:{color:SOFT}, line:{color:LINEC, width:1} });
  s.addText(t, { x:1.05, y:1.85+i*0.92, w:8.0, h:0.78, fontFace:F, fontSize:17, color:NAVY, valign:"middle", isTextBox:true, margin:0 });
});
s.addText("그게 쌓이면, 다음에 누가 또 그렇게 부를 때 우리는 부탁하지 않아도 됩니다.\n지도를 하나 내놓으면 됩니다.", {
  x:0.7, y:4.72, w:8.6, h:0.7, fontFace:F, fontSize:14, bold:true, color:PRIMARY, isTextBox:true, margin:0, lineSpacingMultiple:1.2 });

/* 12. 맺음 */
s = pres.addSlide();
s.background = { color: NAVY };
s.addText("저는 제주가\n그런 말로 불리는 게 싫습니다.", {
  x:0.9, y:1.9, w:8.2, h:1.7, fontFace:F, fontSize:34, bold:true, color:WHITE, isTextBox:true, margin:0, lineSpacingMultiple:1.3 });
s.addText("싫으면 만들어야 한다고 생각했습니다.", { x:0.95, y:3.75, w:8.2, h:0.45, fontFace:F, fontSize:17, color:ICE, isTextBox:true, margin:0 });
s.addText("감사합니다.", { x:0.95, y:4.5, w:8.2, h:0.4, fontFace:F, fontSize:14, color:MUTE, isTextBox:true, margin:0 });

pres.writeFile({ fileName: process.argv[2] }).then(f=>console.log("saved", f));
