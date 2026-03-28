"""Hank - 나라장터 투찰률 분석 플랫폼
광고 잡지 스타일 홈페이지

실행:
    streamlit run app.py
"""

import streamlit as st

# ──────────────────────────────────────────────
# 페이지 설정
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="HANK | 나라장터 투찰률 분석 플랫폼",
    page_icon="H",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# 전체 커스텀 CSS — 매거진 스타일
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* ── 글로벌 리셋 ── */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Playfair+Display:ital,wght@0,700;0,900;1,700&display=swap');

    .stApp {
        background-color: #fafaf7;
    }
    [data-testid="stSidebar"] {
        background: #0a0a0a;
    }
    section[data-testid="stSidebarContent"] {
        padding-top: 2rem;
    }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* ── 네비게이션 바 ── */
    .mag-nav {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 9999;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 48px;
        background: rgba(250, 250, 247, 0.92);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(0,0,0,0.06);
    }
    .mag-nav-logo {
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 900;
        letter-spacing: -1px;
        color: #0a0a0a;
    }
    .mag-nav-links {
        display: flex;
        gap: 32px;
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 13px;
        font-weight: 500;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #555;
    }
    .mag-nav-links a {
        color: #555;
        text-decoration: none;
        transition: color 0.2s;
    }
    .mag-nav-links a:hover {
        color: #0a0a0a;
    }

    /* ── 히어로 섹션 ── */
    .hero-section {
        margin-top: 0;
        padding: 160px 48px 100px;
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 40%, #16213e 70%, #0f3460 100%);
        position: relative;
        overflow: hidden;
    }
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 800px;
        height: 800px;
        background: radial-gradient(circle, rgba(233, 69, 96, 0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-section::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -10%;
        width: 600px;
        height: 600px;
        background: radial-gradient(circle, rgba(74, 144, 217, 0.12) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-eyebrow {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 12px;
        font-weight: 500;
        letter-spacing: 6px;
        text-transform: uppercase;
        color: #e94560;
        margin-bottom: 28px;
        position: relative;
        z-index: 1;
    }
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: clamp(48px, 7vw, 96px);
        font-weight: 900;
        line-height: 1.05;
        color: #ffffff;
        margin-bottom: 32px;
        max-width: 900px;
        position: relative;
        z-index: 1;
    }
    .hero-title em {
        font-style: italic;
        color: #e94560;
    }
    .hero-subtitle {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 18px;
        font-weight: 300;
        line-height: 1.8;
        color: rgba(255,255,255,0.65);
        max-width: 560px;
        margin-bottom: 48px;
        position: relative;
        z-index: 1;
    }
    .hero-cta {
        display: inline-block;
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #ffffff;
        background: #e94560;
        padding: 18px 48px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        position: relative;
        z-index: 1;
    }
    .hero-cta:hover {
        background: #d63851;
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(233, 69, 96, 0.35);
        color: #ffffff;
    }
    .hero-stats {
        display: flex;
        gap: 64px;
        margin-top: 80px;
        padding-top: 48px;
        border-top: 1px solid rgba(255,255,255,0.1);
        position: relative;
        z-index: 1;
    }
    .hero-stat-item {
        text-align: left;
    }
    .hero-stat-number {
        font-family: 'Playfair Display', serif;
        font-size: 42px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1;
    }
    .hero-stat-label {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 12px;
        font-weight: 400;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: rgba(255,255,255,0.4);
        margin-top: 8px;
    }

    /* ── 에디토리얼 소개 섹션 ── */
    .editorial-section {
        padding: 120px 48px;
        background: #fafaf7;
    }
    .editorial-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 80px;
        max-width: 1200px;
        margin: 0 auto;
        align-items: center;
    }
    .editorial-label {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: #e94560;
        margin-bottom: 20px;
    }
    .editorial-heading {
        font-family: 'Playfair Display', serif;
        font-size: 42px;
        font-weight: 700;
        line-height: 1.2;
        color: #0a0a0a;
        margin-bottom: 28px;
    }
    .editorial-text {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 16px;
        font-weight: 300;
        line-height: 1.9;
        color: #666;
    }
    .editorial-visual {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 4px;
        padding: 48px;
        min-height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .visual-metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    .visual-metric-row:last-child {
        border-bottom: none;
    }
    .visual-metric-name {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 14px;
        color: rgba(255,255,255,0.5);
    }
    .visual-metric-value {
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
    }
    .visual-metric-bar {
        height: 3px;
        background: rgba(255,255,255,0.08);
        margin-top: 12px;
        border-radius: 2px;
        overflow: hidden;
    }
    .visual-metric-fill {
        height: 100%;
        background: linear-gradient(90deg, #e94560, #4A90D9);
        border-radius: 2px;
    }

    /* ── 기능 카드 섹션 ── */
    .features-section {
        padding: 120px 48px;
        background: #0a0a0a;
    }
    .features-header {
        text-align: center;
        max-width: 700px;
        margin: 0 auto 80px;
    }
    .features-header-label {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: #e94560;
        margin-bottom: 20px;
    }
    .features-header-title {
        font-family: 'Playfair Display', serif;
        font-size: 42px;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.2;
    }
    .features-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2px;
        max-width: 1200px;
        margin: 0 auto;
    }
    .feature-card {
        background: #111;
        padding: 56px 40px;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
    }
    .feature-card:hover {
        background: #1a1a2e;
    }
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #e94560, transparent);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    .feature-card:hover::before {
        opacity: 1;
    }
    .feature-number {
        font-family: 'Playfair Display', serif;
        font-size: 64px;
        font-weight: 700;
        color: rgba(255,255,255,0.04);
        line-height: 1;
        margin-bottom: 24px;
    }
    .feature-title {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 20px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 16px;
    }
    .feature-desc {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 14px;
        font-weight: 300;
        line-height: 1.8;
        color: rgba(255,255,255,0.45);
    }

    /* ── 풀-블리드 인용 섹션 ── */
    .quote-section {
        padding: 140px 48px;
        background: #fafaf7;
        text-align: center;
    }
    .quote-text {
        font-family: 'Playfair Display', serif;
        font-size: clamp(28px, 4vw, 52px);
        font-weight: 700;
        font-style: italic;
        line-height: 1.4;
        color: #0a0a0a;
        max-width: 900px;
        margin: 0 auto 32px;
    }
    .quote-attr {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 13px;
        font-weight: 500;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #999;
    }

    /* ── 프로세스 섹션 ── */
    .process-section {
        padding: 120px 48px;
        background: #ffffff;
    }
    .process-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0;
        max-width: 1200px;
        margin: 0 auto;
    }
    .process-step {
        padding: 48px 36px;
        text-align: center;
        border-right: 1px solid #eee;
        position: relative;
    }
    .process-step:last-child {
        border-right: none;
    }
    .process-number {
        font-family: 'Playfair Display', serif;
        font-size: 72px;
        font-weight: 900;
        color: rgba(0,0,0,0.04);
        line-height: 1;
        margin-bottom: 20px;
    }
    .process-title {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 17px;
        font-weight: 700;
        color: #0a0a0a;
        margin-bottom: 12px;
    }
    .process-desc {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 13px;
        font-weight: 300;
        line-height: 1.7;
        color: #888;
    }
    .process-arrow {
        position: absolute;
        right: -8px;
        top: 50%;
        transform: translateY(-50%);
        color: #ddd;
        font-size: 16px;
    }

    /* ── CTA 섹션 ── */
    .cta-section {
        padding: 140px 48px;
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        text-align: center;
    }
    .cta-title {
        font-family: 'Playfair Display', serif;
        font-size: clamp(36px, 5vw, 64px);
        font-weight: 900;
        color: #ffffff;
        line-height: 1.15;
        margin-bottom: 24px;
    }
    .cta-subtitle {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 16px;
        font-weight: 300;
        color: rgba(255,255,255,0.5);
        margin-bottom: 48px;
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.7;
    }
    .cta-button {
        display: inline-block;
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #0a0a0a;
        background: #ffffff;
        padding: 20px 56px;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    .cta-button:hover {
        background: #e94560;
        color: #ffffff;
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(233, 69, 96, 0.3);
    }

    /* ── 푸터 ── */
    .mag-footer {
        padding: 80px 48px 48px;
        background: #050505;
    }
    .footer-grid {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr;
        gap: 60px;
        max-width: 1200px;
        margin: 0 auto;
        padding-bottom: 48px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .footer-brand {
        font-family: 'Playfair Display', serif;
        font-size: 32px;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 16px;
    }
    .footer-brand-desc {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 13px;
        font-weight: 300;
        line-height: 1.8;
        color: rgba(255,255,255,0.3);
    }
    .footer-col-title {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: rgba(255,255,255,0.5);
        margin-bottom: 24px;
    }
    .footer-col-link {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 13px;
        font-weight: 300;
        color: rgba(255,255,255,0.3);
        display: block;
        margin-bottom: 12px;
        text-decoration: none;
        transition: color 0.2s;
    }
    .footer-col-link:hover {
        color: #e94560;
    }
    .footer-bottom {
        max-width: 1200px;
        margin: 0 auto;
        padding-top: 32px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .footer-copy {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 11px;
        color: rgba(255,255,255,0.2);
        letter-spacing: 1px;
    }

    /* ── 반응형 ── */
    @media (max-width: 768px) {
        .mag-nav { padding: 14px 24px; }
        .mag-nav-links { display: none; }
        .hero-section { padding: 120px 24px 80px; }
        .hero-stats { flex-direction: column; gap: 32px; }
        .editorial-grid { grid-template-columns: 1fr; gap: 48px; }
        .editorial-section { padding: 80px 24px; }
        .features-grid { grid-template-columns: 1fr; }
        .features-section { padding: 80px 24px; }
        .process-grid { grid-template-columns: 1fr 1fr; }
        .process-step { border-right: none; border-bottom: 1px solid #eee; }
        .footer-grid { grid-template-columns: 1fr 1fr; }
    }

    /* ── Streamlit 기본 요소 숨김 ── */
    .stDeployButton, footer, #MainMenu { display: none !important; }
    .stApp > header { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# 네비게이션 바
# ──────────────────────────────────────────────
st.markdown("""
<div class="mag-nav">
    <div class="mag-nav-logo">HANK</div>
    <div class="mag-nav-links">
        <a href="#features">기능</a>
        <a href="#process">프로세스</a>
        <a href="#about">소개</a>
    </div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# 히어로 섹션
# ──────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="hero-eyebrow">Data Intelligence Platform</div>
    <h1 class="hero-title">
        입찰의 흐름을<br/>
        <em>읽다.</em>
    </h1>
    <p class="hero-subtitle">
        나라장터 용역 입찰 데이터를 실시간으로 수집하고 분석합니다.<br/>
        투찰률, 낙찰률, 순위 패턴까지 — 데이터가 말하는 전략을 발견하세요.
    </p>
    <a href="/분석도구" target="_self" class="hero-cta">분석 시작하기</a>
    <div class="hero-stats">
        <div class="hero-stat-item">
            <div class="hero-stat-number">24/7</div>
            <div class="hero-stat-label">실시간 데이터 수집</div>
        </div>
        <div class="hero-stat-item">
            <div class="hero-stat-number">100%</div>
            <div class="hero-stat-label">나라장터 API 연동</div>
        </div>
        <div class="hero-stat-item">
            <div class="hero-stat-number">5+</div>
            <div class="hero-stat-label">핵심 분석 지표</div>
        </div>
        <div class="hero-stat-item">
            <div class="hero-stat-number">CSV</div>
            <div class="hero-stat-label">데이터 내보내기</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# 에디토리얼 소개 섹션
# ──────────────────────────────────────────────
st.markdown("""
<div class="editorial-section" id="about">
    <div class="editorial-grid">
        <div>
            <div class="editorial-label">Why Hank</div>
            <h2 class="editorial-heading">
                숫자 뒤에 숨겨진<br/>패턴을 찾아냅니다
            </h2>
            <p class="editorial-text">
                수천 건의 용역 입찰 데이터 속에는 기업의 전략이 담겨 있습니다.
                평균 투찰률, 구간별 분포, 시간에 따른 변화 추이까지 —
                HANK는 복잡한 공공조달 데이터를 명확한 인사이트로 바꿔줍니다.
                <br/><br/>
                사업자등록번호 하나만으로 경쟁사의 입찰 패턴을 파악하고,
                낙찰 확률을 높이는 최적의 전략을 수립할 수 있습니다.
            </p>
        </div>
        <div class="editorial-visual">
            <div class="visual-metric-row">
                <span class="visual-metric-name">평균 투찰률</span>
                <span class="visual-metric-value">92.4%</span>
            </div>
            <div class="visual-metric-bar"><div class="visual-metric-fill" style="width: 92.4%"></div></div>
            <div class="visual-metric-row">
                <span class="visual-metric-name">낙찰률</span>
                <span class="visual-metric-value">18.7%</span>
            </div>
            <div class="visual-metric-bar"><div class="visual-metric-fill" style="width: 65%"></div></div>
            <div class="visual-metric-row">
                <span class="visual-metric-name">평균 순위</span>
                <span class="visual-metric-value">3.2위</span>
            </div>
            <div class="visual-metric-bar"><div class="visual-metric-fill" style="width: 45%"></div></div>
            <div class="visual-metric-row">
                <span class="visual-metric-name">분석 건수</span>
                <span class="visual-metric-value">1,247건</span>
            </div>
            <div class="visual-metric-bar"><div class="visual-metric-fill" style="width: 78%"></div></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# 기능 카드 섹션
# ──────────────────────────────────────────────
st.markdown("""
<div class="features-section" id="features">
    <div class="features-header">
        <div class="features-header-label">Core Features</div>
        <h2 class="features-header-title">데이터를 전략으로<br/>전환하는 6가지 도구</h2>
    </div>
    <div class="features-grid">
        <div class="feature-card">
            <div class="feature-number">01</div>
            <div class="feature-title">투찰률 분석</div>
            <div class="feature-desc">
                투찰금액 대비 예정가격 비율을 산출하여
                기업별 입찰 전략의 공격성과 보수성을 정량화합니다.
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-number">02</div>
            <div class="feature-title">낙찰률 추적</div>
            <div class="feature-desc">
                전체 투찰 대비 낙찰 비율을 추적하여
                기업의 실질적인 수주 경쟁력을 측정합니다.
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-number">03</div>
            <div class="feature-title">순위 패턴 분석</div>
            <div class="feature-desc">
                입찰 순위의 분포와 변화를 분석하여
                경쟁 환경 속 기업의 포지셔닝을 파악합니다.
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-number">04</div>
            <div class="feature-title">구간별 분포</div>
            <div class="feature-desc">
                투찰률을 5% 단위 구간으로 나누어
                기업의 가격 전략 패턴을 히스토그램으로 시각화합니다.
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-number">05</div>
            <div class="feature-title">시계열 추이</div>
            <div class="feature-desc">
                시간에 따른 투찰률 변화를 추적하여
                전략의 일관성과 변화 시점을 포착합니다.
            </div>
        </div>
        <div class="feature-card">
            <div class="feature-number">06</div>
            <div class="feature-title">업체간 비교</div>
            <div class="feature-desc">
                복수 업체의 핵심 지표를 나란히 비교하여
                경쟁 구도와 상대적 강점을 한눈에 파악합니다.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# 인용 섹션
# ──────────────────────────────────────────────
st.markdown("""
<div class="quote-section">
    <p class="quote-text">
        "데이터 없는 입찰은<br/>지도 없는 항해와 같다"
    </p>
    <p class="quote-attr">HANK Philosophy</p>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# 프로세스 섹션
# ──────────────────────────────────────────────
st.markdown("""
<div class="process-section" id="process">
    <div class="features-header" style="margin-bottom: 80px;">
        <div class="features-header-label" style="color: #e94560;">How It Works</div>
        <h2 class="features-header-title" style="color: #0a0a0a;">4단계로 완성되는 분석</h2>
    </div>
    <div class="process-grid">
        <div class="process-step">
            <div class="process-number">01</div>
            <div class="process-title">API 키 등록</div>
            <div class="process-desc">
                공공데이터포털에서 발급받은<br/>
                나라장터 API 인증키를 입력합니다
            </div>
            <span class="process-arrow">&rarr;</span>
        </div>
        <div class="process-step">
            <div class="process-number">02</div>
            <div class="process-title">업체 정보 입력</div>
            <div class="process-desc">
                분석 대상 기업의<br/>
                사업자등록번호를 입력합니다
            </div>
            <span class="process-arrow">&rarr;</span>
        </div>
        <div class="process-step">
            <div class="process-number">03</div>
            <div class="process-title">데이터 수집</div>
            <div class="process-desc">
                나라장터 API를 통해<br/>
                입찰 데이터를 자동 수집합니다
            </div>
            <span class="process-arrow">&rarr;</span>
        </div>
        <div class="process-step">
            <div class="process-number">04</div>
            <div class="process-title">인사이트 도출</div>
            <div class="process-desc">
                투찰률, 낙찰률, 순위 패턴을<br/>
                차트와 통계로 시각화합니다
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# CTA 섹션
# ──────────────────────────────────────────────
st.markdown("""
<div class="cta-section">
    <h2 class="cta-title">지금 바로<br/>분석을 시작하세요</h2>
    <p class="cta-subtitle">
        데모 모드로 샘플 데이터를 먼저 체험하거나,
        API 키를 등록하여 실제 데이터 분석을 시작할 수 있습니다.
    </p>
    <a href="/분석도구" target="_self" class="cta-button">분석 도구 열기</a>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# 푸터
# ──────────────────────────────────────────────
st.markdown("""
<div class="mag-footer">
    <div class="footer-grid">
        <div>
            <div class="footer-brand">HANK</div>
            <p class="footer-brand-desc">
                나라장터 용역 투찰률 분석 플랫폼.<br/>
                공공조달 입찰 데이터를 전략적 인사이트로 전환합니다.
            </p>
        </div>
        <div>
            <div class="footer-col-title">플랫폼</div>
            <a href="/분석도구" target="_self" class="footer-col-link">분석 도구</a>
            <span class="footer-col-link">데모 모드</span>
            <span class="footer-col-link">CSV 내보내기</span>
        </div>
        <div>
            <div class="footer-col-title">데이터 소스</div>
            <span class="footer-col-link">나라장터 API</span>
            <span class="footer-col-link">공공데이터포털</span>
            <span class="footer-col-link">조달청</span>
        </div>
        <div>
            <div class="footer-col-title">분석 지표</div>
            <span class="footer-col-link">투찰률</span>
            <span class="footer-col-link">낙찰률</span>
            <span class="footer-col-link">순위 분석</span>
            <span class="footer-col-link">추이 분석</span>
        </div>
    </div>
    <div class="footer-bottom">
        <span class="footer-copy">&copy; 2026 HANK. All rights reserved.</span>
        <span class="footer-copy">Built with Streamlit</span>
    </div>
</div>
""", unsafe_allow_html=True)
