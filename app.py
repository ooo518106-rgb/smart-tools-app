import streamlit as st
import datetime
import pandas as pd
import urllib.parse
from io import BytesIO

from helpers import (
    money, save_result, quick_save_button, copy_box,
    export_to_excel, page_header, share_buttons,
    fetch_currency_rates, currency_label,
    check_pin, render_reminders,
    get_hijri_date, print_button,
    pdf_download_button, quick_print,
    backup_restore_ui,
    safe_date, get_gosi_rates,
)

try:
    from dateutil.relativedelta import relativedelta
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False

try:
    import qrcode
    HAS_QR = True
except ImportError:
    HAS_QR = False

st.set_page_config(
    page_title="أدوات التاجر الذكي",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="expanded",
)

defaults = {
    "ecommerce_history": [],
    "all_results": [],
    "theme": "تلقائي",
    "search_query": "",
    "reminders": [],
    "customers": [],
    "pin_ok": False,
    "tool": "🏠 الرئيسية",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def apply_theme(theme_name):
    themes = {
        "فاتح": {
            "bg": "linear-gradient(135deg, #eef2ff 0%, #fce7f3 100%)",
            "card": "rgba(255, 255, 255, 0.85)",
            "accent": "#6366f1", "accent2": "#ec4899",
            "text": "#1e293b", "sub": "#64748b",
            "sidebar1": "#4f46e5", "sidebar2": "#7c3aed",
            "field_bg": "rgba(255, 255, 255, 0.95)",
            "field_border": "#e2e8f0", "field_text": "#1e293b",
            "border": "rgba(99, 102, 241, 0.15)",
        },
        "داكن": {
            "bg": "linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)",
            "card": "rgba(30, 41, 59, 0.85)",
            "accent": "#818cf8", "accent2": "#f472b6",
            "text": "#e2e8f0", "sub": "#94a3b8",
            "sidebar1": "#1e1b4b", "sidebar2": "#312e81",
            "field_bg": "rgba(30, 41, 59, 0.9)",
            "field_border": "#334155", "field_text": "#e2e8f0",
            "border": "rgba(129, 140, 248, 0.2)",
        },
        "غروب": {
            "bg": "linear-gradient(135deg, #fff7ed 0%, #fee2e2 100%)",
            "card": "rgba(255, 255, 255, 0.85)",
            "accent": "#ea580c", "accent2": "#dc2626",
            "text": "#7c2d12", "sub": "#9a3412",
            "sidebar1": "#c2410c", "sidebar2": "#ea580c",
            "field_bg": "rgba(255, 255, 255, 0.95)",
            "field_border": "#fed7aa", "field_text": "#7c2d12",
            "border": "rgba(234, 88, 12, 0.15)",
        },
        "محيط": {
            "bg": "linear-gradient(135deg, #ecfeff 0%, #cffafe 100%)",
            "card": "rgba(255, 255, 255, 0.85)",
            "accent": "#0891b2", "accent2": "#06b6d4",
            "text": "#164e63", "sub": "#155e75",
            "sidebar1": "#0e7490", "sidebar2": "#0891b2",
            "field_bg": "rgba(255, 255, 255, 0.95)",
            "field_border": "#a5f3fc", "field_text": "#164e63",
            "border": "rgba(8, 145, 178, 0.15)",
        },
        "غابة": {
            "bg": "linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)",
            "card": "rgba(255, 255, 255, 0.85)",
            "accent": "#059669", "accent2": "#10b981",
            "text": "#064e3b", "sub": "#065f46",
            "sidebar1": "#047857", "sidebar2": "#059669",
            "field_bg": "rgba(255, 255, 255, 0.95)",
            "field_border": "#a7f3d0", "field_text": "#064e3b",
            "border": "rgba(5, 150, 105, 0.15)",
        },
    }

    if theme_name == "تلقائي":
        try:
            _hour = datetime.datetime.now().hour
            theme_name = "داكن" if (_hour >= 19 or _hour < 6) else "فاتح"
        except Exception:
            theme_name = "فاتح"

    th = themes.get(theme_name, themes["فاتح"])

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap');
* {{ font-family: 'Cairo', sans-serif; }}
html, body, [class*="css"] {{ font-family: 'Cairo', sans-serif; }}
.stApp {{ background: {th['bg']}; background-attachment: fixed; }}
footer {{visibility: hidden;}}
#MainMenu {{visibility: hidden;}}
[data-testid="stStatusWidget"] {{visibility: hidden;}}

@keyframes fadeSlideIn {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.page-hero {{ text-align: center; padding: 20px 10px 24px; margin-bottom: 12px; animation: fadeSlideIn 0.5s ease-out; }}
.page-hero-icon {{ font-size: 3.2rem; margin-bottom: 8px; display: inline-block; }}
.page-title {{
    background: linear-gradient(135deg, {th['sidebar1']} 0%, {th['accent2']} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 1.9rem;
    font-weight: 900;
    margin: 0;
    padding: 0;
    letter-spacing: -0.5px;
}}
.page-subtitle {{ color: {th['sub']}; font-size: 0.9rem; margin: 8px 0 0; font-weight: 500; }}
.section-title {{
    color: {th['text']};
    font-size: 1.3rem;
    font-weight: 800;
    margin: 24px 0 12px;
    padding-right: 10px;
    border-right: 4px solid {th['accent']};
}}

.stat-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    margin: 16px 0;
}}
.stat-card {{
    background: {th['card']};
    backdrop-filter: blur(10px);
    padding: 18px 16px;
    border-radius: 20px;
    border: 1px solid {th['border']};
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
    text-align: center;
    animation: fadeSlideIn 0.5s ease-out;
    transition: all 0.25s ease;
}}
.stat-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}}
.stat-icon {{ font-size: 1.8rem; margin-bottom: 6px; }}
.stat-value {{
    font-size: 1.8rem;
    font-weight: 900;
    background: linear-gradient(135deg, {th['sidebar1']}, {th['accent2']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}}
.stat-label {{ color: {th['sub']}; font-size: 0.8rem; font-weight: 600; margin-top: 4px; }}

[data-testid="stMetric"] {{
    background: {th['card']};
    backdrop-filter: blur(10px);
    padding: 16px 14px;
    border-radius: 18px;
    border: 1px solid {th['border']};
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
    animation: fadeSlideIn 0.4s ease-out;
    transition: all 0.25s ease;
}}
[data-testid="stMetric"]:hover {{
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}}
[data-testid="stMetricLabel"] {{
    color: {th['sub']} !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
}}
[data-testid="stMetricValue"] {{
    color: {th['text']} !important;
    font-weight: 800 !important;
}}

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {th['sidebar1']} 0%, {th['sidebar2']} 100%);
}}
section[data-testid="stSidebar"] * {{ color: #ffffff !important; }}
section[data-testid="stSidebar"] .stRadio label {{
    background: rgba(255, 255, 255, 0.08);
    padding: 10px 14px;
    border-radius: 12px;
    margin-bottom: 5px;
    cursor: pointer;
    display: block;
    font-size: 0.88rem;
    font-weight: 500;
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: all 0.2s;
}}
section[data-testid="stSidebar"] .stRadio label:hover {{
    background: rgba(255, 255, 255, 0.18);
    transform: translateX(-3px);
}}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {{
    background: rgba(255, 255, 255, 0.12) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 10px !important;
}}

.stButton > button {{
    background: linear-gradient(135deg, {th['sidebar1']} 0%, {th['accent2']} 100%);
    color: white !important;
    border: none;
    border-radius: 14px;
    padding: 12px 20px;
    font-weight: 700;
    width: 100%;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
    transition: all 0.2s;
    animation: fadeSlideIn 0.3s ease-out;
}}
.stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
    color: white !important;
}}
.stButton > button:active {{ transform: scale(0.97); }}

.stDownloadButton > button {{
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white !important;
    border: none;
    border-radius: 14px;
    padding: 12px 20px;
    font-weight: 700;
    width: 100%;
    box-shadow: 0 6px 16px rgba(16, 185, 129, 0.25);
    transition: all 0.2s;
}}
.stDownloadButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(16, 185, 129, 0.35);
    color: white !important;
}}

.stTextInput input, .stNumberInput input, .stTextArea textarea {{
    border-radius: 12px !important;
    border: 1.5px solid {th['field_border']} !important;
    background: {th['field_bg']} !important;
    color: {th['field_text']} !important;
    padding: 10px 14px !important;
    transition: all 0.2s;
}}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {{
    border-color: {th['accent']} !important;
    box-shadow: 0 0 0 3px {th['border']} !important;
}}
.stSelectbox > div > div {{
    border-radius: 12px !important;
    border: 1.5px solid {th['field_border']} !important;
}}
.stAlert {{ border-radius: 14px !important; border: none !important; }}
h1, h2, h3, h4 {{ color: {th['text']} !important; }}

div[data-testid="stDataFrame"] {{
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid {th['border']};
}}
div[data-testid="stExpander"] {{
    border-radius: 14px !important;
    border: 1px solid {th['border']} !important;
    background: {th['card']} !important;
}}
.share-btn {{
    display: block;
    text-align: center;
    padding: 12px 8px;
    border-radius: 12px;
    color: white !important;
    font-weight: 700;
    text-decoration: none !important;
    font-size: 0.9rem;
    transition: transform 0.2s;
}}
.share-btn:hover {{
    transform: translateY(-2px);
    color: white !important;
}}
hr {{ border-color: {th['border']} !important; margin: 20px 0 !important; }}

::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{
    background: {th['accent']};
    border-radius: 10px;
}}
::-webkit-scrollbar-thumb:hover {{ background: {th['accent2']}; }}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<link rel="manifest" href="./app/static/manifest.json">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="أدوات التاجر">
<meta name="theme-color" content="#4f46e5">
""", unsafe_allow_html=True)

if not check_pin():
    st.stop()

apply_theme(st.session_state.theme)

st.sidebar.markdown("### 💼 أدوات التاجر الذكي")

search_query = st.sidebar.text_input(
    "🔍 ابحث",
    value=st.session_state.search_query,
    placeholder="ابحث عن أداة...",
)
st.session_state.search_query = search_query

theme_options = ["🌗 تلقائي", "☀️ فاتح", "🌙 داكن", "🌅 غروب", "🌊 محيط", "🌲 غابة"]
theme_names = ["تلقائي", "فاتح", "داكن", "غروب", "محيط", "غابة"]
default_idx = 0
for i, name in enumerate(theme_names):
    if name == st.session_state.theme:
        default_idx = i
        break

theme_pick = st.sidebar.selectbox("🎨 الثيم", theme_options, index=default_idx)
theme_key = theme_pick.split()[-1]
if theme_key != st.session_state.theme:
    st.session_state.theme = theme_key
    st.rerun()

st.sidebar.markdown("---")

ALL_TOOLS = [
    "🏠 الرئيسية",
    "📊 لوحة التقارير",
    "📦 التجارة الإلكترونية",
    "💳 تابي وتمارا",
    "🏪 عمولة المنصات",
    "📢 الإعلانات ROAS",
    "💬 روابط واتساب",
    "🏦 القروض والأقساط",
    "💳 البطاقة الائتمانية",
    "🕋 زكاة المال",
    "💸 الرواتب",
    "🛡️ نهاية الخدمة",
    "👥 تكلفة الموظف",
    "📅 الدوام الدقيقة",
    "⚖️ توزيع الشحن",
    "🏷️ الخصومات",
    "🎁 العروض الترويجية",
    "📦 نقطة إعادة الطلب",
    "📈 نمو المبيعات",
    "📊 LTV / CAC",
    "⏳ حاسبة العمر",
    "📉 نقطة التعادل",
    "🧾 ضريبة VAT",
    "📈 أرباح الكريبتو",
    "🛡️ إدارة المخاطر",
    "💱 محول العملات",
    "🗓️ أيام العمل",
    "📅 أرقام الفواتير",
    "🔲 مولد QR",
    "🔐 مولد كلمات السر",
    "🎯 أهداف المبيعات",
    "📧 مولّد البريد الاحترافي",
    "🎨 مولّد الشعار",
    "📞 حاسبة الاتصال الدولي",
    "👥 إدارة العملاء",
    "💾 النسخ الاحتياطي",
    "📄 القوالب الجاهزة",
    "📜 سياسة الخصوصية",
]

if search_query.strip():
    filtered = [x for x in ALL_TOOLS if search_query.lower().strip() in x.lower()]
else:
    filtered = ALL_TOOLS

if not filtered:
    st.sidebar.warning("لا توجد نتائج")
    st.session_state.tool = "🏠 الرئيسية"
    tool_choice = "🏠 الرئيسية"
else:
    if st.session_state.tool not in filtered:
        st.session_state.tool = filtered[0]

    try:
        current_index = filtered.index(st.session_state.tool)
    except ValueError:
        current_index = 0

    tool_choice = st.sidebar.radio(
        "الأدوات",
        filtered,
        key="tool",
        index=current_index,
    )

if st.session_state.all_results:
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**📊 {len(st.session_state.all_results)} عملية محفوظة**")

CURRENCIES = ["ر.س", "د.إ", "د.ك", "ر.ع", "ج.م", "$", "€", "£"]


# ============================================================
# 🏠 الرئيسية
# ============================================================
if tool_choice == "🏠 الرئيسية":
    page_header("💼", "أدوات التاجر الذكي", "مجموعتك المتكاملة للحسابات التجارية والمالية")

    hijri = get_hijri_date()
    today_g = datetime.date.today().strftime("%Y-%m-%d")
    if hijri:
        st.markdown(
            '<div style="text-align:center; padding:8px; color:#64748b; font-size:0.85rem;">'
            '🌙 ' + hijri + ' &nbsp;·&nbsp; 📅 ' + today_g + ' م'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="text-align:center; padding:8px; color:#64748b; font-size:0.85rem;">'
            '📅 ' + today_g +
            '</div>',
            unsafe_allow_html=True,
        )

    total_ops = len(st.session_state.all_results)
    total_customers = len(st.session_state.get("customers", []))

    st.markdown(
        '<div class="stat-grid">'
        '<div class="stat-card">'
        '<div class="stat-icon">🛠️</div>'
        '<div class="stat-value">38</div>'
        '<div class="stat-label">أداة متاحة</div>'
        '</div>'
        '<div class="stat-card">'
        '<div class="stat-icon">📊</div>'
        '<div class="stat-value">' + str(total_ops) + '</div>'
        '<div class="stat-label">عملية محفوظة</div>'
        '</div>'
        '<div class="stat-card">'
        '<div class="stat-icon">👥</div>'
        '<div class="stat-value">' + str(total_customers) + '</div>'
        '<div class="stat-label">عميل مسجّل</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<h2 class="section-title">🚀 ابدأ من هنا</h2>', unsafe_allow_html=True)

    categories = {
        "💰 محاسبات التجارة": [
            "📦 التجارة الإلكترونية",
            "💳 تابي وتمارا",
            "🏪 عمولة المنصات",
            "📢 الإعلانات ROAS",
            "⚖️ توزيع الشحن",
            "🏷️ الخصومات",
            "🎁 العروض الترويجية",
        ],
        "👔 الموارد البشرية": [
            "💸 الرواتب",
            "🛡️ نهاية الخدمة",
            "👥 تكلفة الموظف",
            "📅 الدوام الدقيقة",
            "🗓️ أيام العمل",
        ],
        "📈 التحليل المالي": [
            "📊 لوحة التقارير",
            "📈 نمو المبيعات",
            "📊 LTV / CAC",
            "📉 نقطة التعادل",
            "📦 نقطة إعادة الطلب",
            "🎯 أهداف المبيعات",
        ],
        "🧾 الضرائب والزكاة": [
            "🕋 زكاة المال",
            "🧾 ضريبة VAT",
        ],
        "💱 التحويل والعملات": [
            "💱 محول العملات",
            "📈 أرباح الكريبتو",
            "🛡️ إدارة المخاطر",
            "📞 حاسبة الاتصال الدولي",
        ],
        "👥 العملاء والبيانات": [
            "👥 إدارة العملاء",
            "💾 النسخ الاحتياطي",
        ],
        "🛠️ أدوات مساعدة": [
            "💬 روابط واتساب",
            "🏦 القروض والأقساط",
            "💳 البطاقة الائتمانية",
            "⏳ حاسبة العمر",
            "📅 أرقام الفواتير",
            "🔲 مولد QR",
            "🔐 مولد كلمات السر",
            "📧 مولّد البريد الاحترافي",
            "🎨 مولّد الشعار",
            "📄 القوالب الجاهزة",
        ],
    }

    for cat_name, tools in categories.items():
        st.markdown(
            '<h3 style="margin-top:20px; color:#6366f1;">' + cat_name + '</h3>',
            unsafe_allow_html=True,
        )
        cols = st.columns(2)
        for i, t in enumerate(tools):
            with cols[i % 2]:
                def open_tool(name=t):
                    st.session_state.tool = name
                    st.session_state.search_query = ""
                st.button(
                    t,
                    key=f"home_{cat_name}_{t}",
                    on_click=open_tool,
                    use_container_width=True,
                )

    if total_ops > 0:
        st.markdown('<h2 class="section-title">📈 آخر العمليات</h2>', unsafe_allow_html=True)
        recent = st.session_state.all_results[-5:][::-1]
        for r in recent:
            with st.expander(f"• {r.get('الأداة', 'عملية')} — {r.get('التاريخ', '')}"):
                st.json(r)

    st.markdown('<hr>', unsafe_allow_html=True)
    render_reminders()


# ============================================================
# 📊 لوحة التقارير
# ============================================================
elif tool_choice == "📊 لوحة التقارير":
    page_header("📊", "لوحة التقارير", "جميع نتائجك المحفوظة في مكان واحد")

    if not st.session_state.all_results:
        st.info("📭 لا توجد نتائج محفوظة بعد.")
    else:
        df_all = pd.DataFrame(st.session_state.all_results)

        c1, c2, c3 = st.columns(3)
        c1.metric("📊 إجمالي العمليات", len(df_all))
        c2.metric("🛠️ أدوات مستخدمة", df_all["الأداة"].nunique())
        c3.metric("📅 أول عملية", df_all["التاريخ"].iloc[0].split()[0])

        st.markdown('<hr>', unsafe_allow_html=True)
        st.dataframe(df_all, use_container_width=True, hide_index=True)

        st.markdown('<h2 class="section-title">📊 إحصائيات</h2>', unsafe_allow_html=True)

        try:
            import plotly.express as px
            HAS_PLOTLY = True
        except ImportError:
            HAS_PLOTLY = False

        tool_counts = df_all["الأداة"].value_counts()

        if HAS_PLOTLY:
            fig = px.bar(
                x=tool_counts.values,
                y=tool_counts.index,
                orientation="h",
                labels={"x": "عدد المرات", "y": "الأداة"},
                color=tool_counts.values,
                color_continuous_scale="Purples",
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                font=dict(family="Cairo"),
                margin=dict(l=10, r=10, t=30, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(tool_counts)

        df_all["اليوم"] = df_all["التاريخ"].str.split(" ").str[0]
        daily = df_all.groupby("اليوم").size()

        if HAS_PLOTLY:
            fig2 = px.area(
                x=daily.index,
                y=daily.values,
                labels={"x": "اليوم", "y": "عدد العمليات"},
            )
            fig2.update_traces(line_color="#ec4899", fillcolor="rgba(236,72,153,0.2)")
            fig2.update_layout(
                height=300,
                font=dict(family="Cairo"),
                margin=dict(l=10, r=10, t=30, b=10),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.line_chart(daily)

        df_all["الشهر"] = df_all["التاريخ"].str.slice(0, 7)
        monthly = df_all.groupby("الشهر").size()

        if HAS_PLOTLY:
            fig3 = px.bar(
                x=monthly.index,
                y=monthly.values,
                labels={"x": "الشهر", "y": "عدد العمليات"},
                color=monthly.values,
                color_continuous_scale="Blues",
            )
            fig3.update_layout(
                height=300,
                showlegend=False,
                font=dict(family="Cairo"),
                margin=dict(l=10, r=10, t=30, b=10),
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.bar_chart(monthly)

        if len(monthly) >= 2:
            current_m = monthly.iloc[-1]
            prev_m = monthly.iloc[-2]
            diff = current_m - prev_m
            pct = (diff / prev_m * 100) if prev_m > 0 else 0

            c1, c2, c3 = st.columns(3)
            c1.metric("الشهر الحالي", current_m)
            c2.metric("الشهر الماضي", prev_m)
            c3.metric("التغيير", f"{diff:+d}", delta=f"{pct:+.1f}%")

        st.markdown('<h2 class="section-title">📥 التصدير</h2>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            csv_all = df_all.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 CSV",
                data=csv_all,
                file_name="Report.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col2:
            sheets = {"الكل": df_all}
            for tool in df_all["الأداة"].unique():
                sheets[tool[:28]] = df_all[df_all["الأداة"] == tool]
            excel_bytes = export_to_excel(sheets, "Merchant_Report.xlsx")
            if excel_bytes:
                st.download_button(
                    "📥 Excel",
                    data=excel_bytes,
                    file_name="Merchant_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
        with col3:
            if st.button("🗑️ مسح الكل", use_container_width=True):
                st.session_state.all_results = []
                st.session_state.ecommerce_history = []
                st.toast("تم المسح", icon="🗑️")
                st.rerun()
                

# ============================================================
# 📦 التجارة الإلكترونية
# ============================================================
elif tool_choice == "📦 التجارة الإلكترونية":
    page_header("📦", "حاسبة التجارة الإلكترونية", "احسب هوامش الربح الصافية")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    col1, col2 = st.columns(2)
    with col1:
        cost_price = st.number_input(f"تكلفة المنتج ({currency})", min_value=0.0, value=50.0, step=1.0)
        shipping_cost = st.number_input(f"تكلفة الشحن ({currency})", min_value=0.0, value=15.0, step=1.0)
    with col2:
        selling_price = st.number_input(f"سعر البيع ({currency})", min_value=0.0, value=150.0, step=1.0)
        gateway_fee_percent = st.number_input("رسوم بوابة الدفع (%)", min_value=0.0, value=2.2, step=0.1)

    fixed_fee = st.number_input(f"الرسوم الثابتة ({currency})", min_value=0.0, value=1.0, step=0.5)
    total_cost = cost_price + shipping_cost
    gateway_fees = (selling_price * (gateway_fee_percent / 100)) + fixed_fee
    net_profit = selling_price - total_cost - gateway_fees
    margin = (net_profit / selling_price * 100) if selling_price > 0 else 0

    st.markdown('<hr>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("التكلفة", money(total_cost, currency))
    c2.metric("رسوم الدفع", money(gateway_fees, currency))
    c3.metric("الربح", money(net_profit, currency), delta="ربح" if net_profit > 0 else "خسارة")
    c4.metric("الهامش", f"{margin:.1f}%")

    if net_profit <= 0:
        st.warning("⚠️ المنتج غير مربح!")

    copy_box(
        f"التكلفة: {money(total_cost, currency)}\n"
        f"الرسوم: {money(gateway_fees, currency)}\n"
        f"الربح: {money(net_profit, currency)}\n"
        f"الهامش: {margin:.1f}%"
    )

    st.markdown("**📤 تصدير النتائج:**")
    exp_c1, exp_c2 = st.columns(2)
    with exp_c1:
        pdf_download_button(
            "حاسبة التجارة الإلكترونية",
            [
                ("التكلفة الإجمالية", money(total_cost, currency)),
                ("رسوم الدفع", money(gateway_fees, currency)),
                ("سعر البيع", money(selling_price, currency)),
                ("الربح الصافي", money(net_profit, currency)),
                ("هامش الربح", f"{margin:.1f}%"),
            ],
            filename="ecommerce_report.pdf",
            key_suffix="ecom",
        )
    with exp_c2:
        quick_print(
            "حاسبة التجارة الإلكترونية",
            "التكلفة: " + money(total_cost, currency) + "\n"
            "الرسوم: " + money(gateway_fees, currency) + "\n"
            "الربح: " + money(net_profit, currency) + "\n"
            "الهامش: " + f"{margin:.1f}%"
        )

    share_buttons(
        f"📦 نتيجة حاسبة التجارة:\n"
        f"الربح الصافي: {money(net_profit, currency)}\n"
        f"الهامش: {margin:.1f}%\n"
        f"من تطبيق أدوات التاجر الذكي 💼"
    )

    st.markdown('<hr>', unsafe_allow_html=True)
    product_name = st.text_input("اسم المنتج (اختياري):", placeholder="سماعة بلوتوث")

    if st.button("➕ حفظ في السجل"):
        if not product_name.strip():
            st.warning("أدخل اسم المنتج")
        else:
            record = {
                "اسم المنتج": product_name.strip(),
                "التكلفة": round(total_cost, 2),
                "سعر البيع": round(selling_price, 2),
                "الربح الصافي": round(net_profit, 2),
                "هامش %": round(margin, 1),
                "العملة": currency,
            }
            st.session_state.ecommerce_history.append(record)
            save_result("التجارة الإلكترونية", **record)
            st.rerun()

    if st.session_state.ecommerce_history:
        df_hist = pd.DataFrame(st.session_state.ecommerce_history)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)


# ============================================================
# 💳 تابي وتمارا
# ============================================================
elif tool_choice == "💳 تابي وتمارا":
    page_header("💳", "رسوم تابي وتمارا", "احسب صافي المبلغ بعد العمولة والضريبة")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    price = st.number_input(f"السعر ({currency})", min_value=0.0, value=100.0, step=1.0)

    col1, col2, col3 = st.columns(3)
    with col1:
        fee_percent = st.number_input("العمولة (%)", min_value=0.0, value=7.0, step=0.1)
    with col2:
        fixed_fee = st.number_input(f"رسوم ثابتة ({currency})", min_value=0.0, value=1.5, step=0.5)
    with col3:
        vat = st.number_input("ضريبة (%)", min_value=0.0, value=15.0, step=1.0)

    fee_amount = (price * (fee_percent / 100)) + fixed_fee
    vat_amount = fee_amount * (vat / 100)
    total_deduction = fee_amount + vat_amount
    net = price - total_deduction

    st.markdown('<hr>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("العمولة", money(fee_amount, currency))
    c2.metric("الضريبة", money(vat_amount, currency))
    c3.metric("الصافي", money(net, currency))

    exp_c1, exp_c2 = st.columns(2)
    with exp_c1:
        pdf_download_button(
            "رسوم تابي وتمارا",
            [
                ("السعر", money(price, currency)),
                ("العمولة", money(fee_amount, currency)),
                ("الضريبة", money(vat_amount, currency)),
                ("الصافي للتاجر", money(net, currency)),
            ],
            filename="tabby_tamara.pdf",
            key_suffix="tamara",
        )
    with exp_c2:
        quick_print(
            "رسوم تابي وتمارا",
            "السعر: " + money(price, currency) + "\n"
            "العمولة: " + money(fee_amount, currency) + "\n"
            "الصافي: " + money(net, currency)
        )

    share_buttons(f"💳 الصافي بعد تابي/تمارا: {money(net, currency)}\nمن تطبيق أدوات التاجر الذكي")
    quick_save_button("tamara", "تابي/تمارا", {
        "السعر": price, "العمولة": round(fee_amount, 2),
        "الضريبة": round(vat_amount, 2), "الصافي": round(net, 2), "العملة": currency,
    })


# ============================================================
# 🏪 عمولة المنصات
# ============================================================
elif tool_choice == "🏪 عمولة المنصات":
    page_header("🏪", "عمولة المنصات", "سلة، زد، شوبيفاي")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    platform = st.selectbox("المنصة", ["سلة", "زد", "شوبيفاي", "مخصصة"])
    pd_defaults = {"سلة": (2.0, 2.5), "زد": (2.0, 2.5), "شوبيفاي": (2.9, 2.9), "مخصصة": (0.0, 0.0)}

    price = st.number_input(f"السعر ({currency})", min_value=0.0, value=100.0, step=1.0)
    product_cost = st.number_input(f"تكلفة المنتج ({currency})", min_value=0.0, value=40.0, step=1.0)
    shipping = st.number_input(f"الشحن ({currency})", min_value=0.0, value=15.0, step=1.0)

    col1, col2 = st.columns(2)
    with col1:
        commission = st.number_input("عمولة المنصة (%)", min_value=0.0, value=pd_defaults[platform][0], step=0.1)
    with col2:
        payment = st.number_input("رسوم الدفع (%)", min_value=0.0, value=pd_defaults[platform][1], step=0.1)

    payment_fixed = st.number_input(f"دفع ثابت ({currency})", min_value=0.0, value=1.0, step=0.5)
    vat = st.number_input("ضريبة (%)", min_value=0.0, value=15.0, step=1.0)

    platform_fee = price * (commission / 100)
    payment_amount = (price * (payment / 100)) + payment_fixed
    vat_amount = (platform_fee + payment_amount) * (vat / 100)
    total_deductions = platform_fee + payment_amount + vat_amount
    net_profit = price - product_cost - shipping - total_deductions

    st.markdown('<hr>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("عمولة المنصة", money(platform_fee, currency))
    c2.metric("رسوم الدفع", money(payment_amount, currency))
    c3.metric("الضريبة", money(vat_amount, currency))
    c4, c5, c6 = st.columns(3)
    c4.metric("إجمالي الخصم", money(total_deductions, currency))
    c5.metric("الصافي", money(price - total_deductions, currency))
    c6.metric("الربح", money(net_profit, currency), delta="ربح" if net_profit > 0 else "خسارة")

    quick_save_button("platform", f"عمولة {platform}", {
        "المنصة": platform, "السعر": price,
        "الربح الصافي": round(net_profit, 2), "العملة": currency,
    })


# ============================================================
# 📢 الإعلانات ROAS
# ============================================================
elif tool_choice == "📢 الإعلانات ROAS":
    page_header("📢", "حاسبة الإعلانات", "ROAS · CPA · AOV")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    ad_spend = st.number_input(f"الإنفاق الإعلاني ({currency})", min_value=0.0, value=1000.0, step=100.0)

    col1, col2 = st.columns(2)
    with col1:
        orders = st.number_input("عدد الطلبات", min_value=1, value=50, step=1)
    with col2:
        aov = st.number_input(f"متوسط قيمة الطلب ({currency})", min_value=0.0, value=150.0, step=10.0)

    margin_percent = st.number_input("هامش الربح (%)", min_value=0.0, value=40.0, step=1.0)
    revenue = orders * aov
    roas = (revenue / ad_spend) if ad_spend > 0 else 0
    cpa = (ad_spend / orders) if orders > 0 else 0
    gross_profit = revenue * (margin_percent / 100)
    net_profit = gross_profit - ad_spend
    breakeven_roas = 100 / margin_percent if margin_percent > 0 else 0
    max_cpa = aov * (margin_percent / 100)

    st.markdown('<hr>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("الإيراد", money(revenue, currency))
    c2.metric("ROAS", f"{roas:.2f}x")
    c3.metric("CPA", money(cpa, currency))
    c4, c5, c6 = st.columns(3)
    c4.metric("ربح إجمالي", money(gross_profit, currency))
    c5.metric("ربح صافي", money(net_profit, currency), delta="ربح" if net_profit > 0 else "خسارة")
    c6.metric("أقصى CPA", money(max_cpa, currency))

    st.info(f"🎯 ROAS التعادل: **{breakeven_roas:.2f}x**")
    if roas < breakeven_roas:
        st.error("⚠️ حملة خاسرة!")
    elif roas < breakeven_roas * 1.5:
        st.warning("⚡ الربح ضعيف.")
    else:
        st.success("🎉 حملة مربحة!")

    quick_save_button("roas", "الإعلانات", {
        "الإنفاق": ad_spend, "الإيراد": revenue, "ROAS": round(roas, 2),
        "الربح الصافي": round(net_profit, 2), "العملة": currency,
    })


# ============================================================
# 💬 روابط واتساب
# ============================================================
elif tool_choice == "💬 روابط واتساب":
    page_header("💬", "صانع روابط واتساب", "رابط مباشر لبدء محادثة")

    phone = st.text_input("رقم الجوال:", placeholder="966500000000")
    msg = st.text_area("الرسالة:", placeholder="مرحباً، أود الاستفسار...")

    if st.button("🔗 توليد الرابط"):
        clean = "".join(filter(str.isdigit, phone))
        if clean and len(clean) >= 10:
            link = f"https://wa.me/{clean}?text={urllib.parse.quote(msg)}"
            st.success("✅ تم!")
            st.code(link, language="")
            st.markdown(f"[📲 تجربة الرابط]({link})")
        else:
            st.error("رقم غير صحيح.")


# ============================================================
# 🏦 القروض والأقساط
# ============================================================
elif tool_choice == "🏦 القروض والأقساط":
    page_header("🏦", "حاسبة القروض والأقساط", "قارن بين الفائدة المتناقصة والثابتة")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    loan = st.number_input(f"المبلغ ({currency})", min_value=0.0, value=10000.0, step=100.0)

    col1, col2 = st.columns(2)
    with col1:
        rate = st.number_input("نسبة الفائدة/الربح السنوية (%)", min_value=0.0, value=5.0, step=0.1)
    with col2:
        months = st.number_input("المدة (أشهر)", min_value=1, value=60, step=1)

    method = st.radio(
        "طريقة الحساب:",
        ["متناقصة (تنخفض الفائدة مع الرصيد)", "ثابتة (مرابحة - شائعة في البنوك الخليجية)"],
        horizontal=False,
    )

    if loan > 0 and months > 0:
        if "متناقصة" in method:
            if rate > 0:
                mr = (rate / 100) / 12
                f = (1 + mr) ** months
                payment = loan * (mr * f) / (f - 1)
            else:
                payment = loan / months
        else:
            # مرابحة: البنك يحسب ربحاً ثابتاً على كامل المبلغ
            total_profit_fixed = loan * (rate / 100) * (months / 12)
            total_fixed = loan + total_profit_fixed
            payment = total_fixed / months

        total = payment * months
        interest = total - loan

        st.markdown('<hr>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("القسط الشهري", money(payment, currency))
        c2.metric("إجمالي الفوائد/الربح", money(interest, currency))
        c3.metric("الإجمالي المسدد", money(total, currency))

        st.caption(f"💡 الطريقة: {'متناقصة' if 'متناقصة' in method else 'مرابحة (ثابتة)'}")

        quick_save_button("loan", "قرض", {
            "المبلغ": loan, "القسط": round(payment, 2),
            "الفوائد": round(interest, 2), "الأشهر": months, "العملة": currency,
        })


# ============================================================
# 💳 البطاقة الائتمانية
# ============================================================
elif tool_choice == "💳 البطاقة الائتمانية":
    page_header("💳", "القسط على البطاقة", "احسب مدة السداد وتكلفة الفوائد")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    balance = st.number_input(f"المستحق ({currency})", min_value=0.0, value=5000.0, step=100.0)
    rate = st.number_input("الفائدة السنوية (%)", min_value=0.0, value=24.0, step=0.5)
    payment = st.number_input(f"الدفعة الشهرية ({currency})", min_value=1.0, value=300.0, step=50.0)

    mr = (rate / 100) / 12
    if payment <= balance * mr:
        st.error("⚠️ الدفعة أقل من الفائدة الشهرية!")
    else:
        remaining = balance
        total_interest = 0
        months = 0
        while remaining > 0 and months < 600:
            interest = remaining * mr
            principal = payment - interest
            if principal <= 0:
                break
            remaining -= principal
            total_interest += interest
            months += 1

        st.markdown('<hr>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("المدة", f"{months} شهر")
        c2.metric("الفوائد", money(total_interest, currency))
        c3.metric("الإجمالي", money(balance + total_interest, currency))


# ============================================================
# 🕋 زكاة المال
# ============================================================
elif tool_choice == "🕋 زكاة المال":
    page_header("🕋", "حاسبة الزكاة", "2.5% من المال")

    st.info("💡 النصاب = 85 غرام ذهب. أدخل سعر الغرام لحساب النصاب تلقائياً.")

    col1, col2 = st.columns(2)
    with col1:
        gold_price = st.number_input("سعر غرام الذهب:", min_value=0.0, value=280.0, step=5.0)
    with col2:
        wealth = st.number_input("إجمالي المال:", min_value=0.0, value=10000.0, step=100.0)

    nisab = gold_price * 85
    zakat = wealth * 0.025
    st.caption(f"📊 النصاب الحالي: {money(nisab)}")

    st.markdown('<hr>', unsafe_allow_html=True)

    if wealth < nisab:
        st.warning(f"⚠️ مالك ({money(wealth)}) أقل من النصاب ({money(nisab)}) - لا زكاة.")
    else:
        st.metric("💰 مقدار الزكاة", money(zakat))

        exp_c1, exp_c2 = st.columns(2)
        with exp_c1:
            pdf_download_button(
                "حاسبة الزكاة",
                [
                    ("إجمالي المال", money(wealth)),
                    ("النصاب", money(nisab)),
                    ("مقدار الزكاة", money(zakat)),
                ],
                filename="zakat.pdf",
                key_suffix="zakat",
            )
        with exp_c2:
            quick_print(
                "حاسبة الزكاة",
                "إجمالي المال: " + money(wealth) + "\n"
                "النصاب: " + money(nisab) + "\n"
                "الزكاة: " + money(zakat)
            )

        quick_save_button("zakat", "زكاة", {"المال": wealth, "الزكاة": round(zakat, 2)})


# ============================================================
# 💸 الرواتب
# ============================================================
elif tool_choice == "💸 الرواتب":
    page_header("💸", "حاسبة الرواتب", "احسب الراتب المستحق")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    basic = st.number_input(f"الراتب الأساسي ({currency})", min_value=0.0, value=5000.0, step=100.0)

    col1, col2 = st.columns(2)
    with col1:
        allow = st.number_input(f"البدلات ({currency})", min_value=0.0, value=0.0, step=100.0)
    with col2:
        deduct = st.number_input(f"الخصومات ({currency})", min_value=0.0, value=0.0, step=100.0)

    net = basic + allow - deduct
    st.markdown('<hr>', unsafe_allow_html=True)

    if net < 0:
        st.error("⚠️ الخصومات تتجاوز الراتب!")
    else:
        st.metric("💰 الراتب المستحق", money(net, currency))


# ============================================================
# 🛡️ نهاية الخدمة
# ============================================================
elif tool_choice == "🛡️ نهاية الخدمة":
    page_header("🛡️", "نهاية الخدمة + التأمينات", "النظام السعودي - محدّث 2026")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    salary = st.number_input(f"الراتب الأخير ({currency})", min_value=0.0, value=5000.0, step=100.0)

    col1, col2 = st.columns(2)
    with col1:
        years = st.number_input("سنوات", min_value=0, value=5, step=1)
    with col2:
        months = st.number_input("أشهر", min_value=0, max_value=11, value=0, step=1)

    reason = st.radio("السبب:", ["استقالة", "إنهاء"], horizontal=True)
    nationality = st.radio("الجنسية:", ["سعودي", "غير سعودي"], horizontal=True)

    join_date = st.date_input(
        "تاريخ الالتحاق بالعمل (اختياري - لحساب نسب التأمينات الصحيحة):",
        value=datetime.date.today() - datetime.timedelta(days=years * 365),
    )

    total_years = years + months / 12
    first5 = min(total_years, 5)
    after5 = max(total_years - 5, 0)
    gratuity = (first5 * salary * 0.5) + (after5 * salary)

    if reason == "استقالة":
        if total_years < 2:
            gratuity = 0
        elif total_years < 5:
            gratuity /= 3
        elif total_years < 10:
            gratuity *= 2 / 3

    st.markdown('<hr>', unsafe_allow_html=True)
    if nationality == "سعودي":
        emp_rate, er_rate = get_gosi_rates(join_date)
        emp = salary * emp_rate
        er = salary * er_rate
        st.caption(f"💡 نسب 2026: الموظف {emp_rate*100:.2f}% | صاحب العمل {er_rate*100:.2f}%")
    else:
        emp = 0
        er = salary * 0.02

    c1, c2 = st.columns(2)
    c1.metric("حصة الموظف", money(emp, currency))
    c2.metric("حصة صاحب العمل", money(er, currency))
    st.metric("💰 المكافأة", money(gratuity, currency))

    quick_save_button("end_service", "نهاية خدمة", {
        "الراتب": salary, "السنوات": total_years,
        "المكافأة": round(gratuity, 2), "السبب": reason, "العملة": currency,
    })


# ============================================================
# 👥 تكلفة الموظف
# ============================================================
elif tool_choice == "👥 تكلفة الموظف":
    page_header("👥", "تكلفة الموظف الإجمالية", "التكلفة الحقيقية السنوية")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    salary = st.number_input(f"الراتب الأساسي ({currency})", min_value=0.0, value=5000.0, step=100.0)

    col1, col2 = st.columns(2)
    with col1:
        housing = st.number_input(f"بدل السكن ({currency})", min_value=0.0, value=1250.0, step=100.0)
        transport = st.number_input(f"بدل المواصلات ({currency})", min_value=0.0, value=500.0, step=50.0)
    with col2:
        other = st.number_input(f"بدلات أخرى ({currency})", min_value=0.0, value=0.0, step=100.0)
        bonus = st.number_input(f"مكافآت سنوية ({currency})", min_value=0.0, value=0.0, step=500.0)

    nationality = st.radio("الجنسية:", ["سعودي", "غير سعودي"], horizontal=True)

    total_sal = salary + housing + transport + other

    if nationality == "سعودي":
        # التأمينات تُحسب على الأساسي + السكن بحد أقصى 45,000
        gosi_base = min(salary + housing, 45000)
        _, er_rate = get_gosi_rates()
        gosi = gosi_base * er_rate
    else:
        gosi = total_sal * 0.02

    monthly = total_sal + gosi
    annual = (monthly * 12) + bonus

    st.markdown('<hr>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("شهرياً", money(monthly, currency))
    c2.metric("سنوياً", money(annual, currency))
    st.caption(f"💡 التأمينات تُحسب على أساس {money(min(salary + housing, 45000), currency)} (حد أقصى 45,000)")


# ============================================================
# 📅 الدوام الدقيقة
# ============================================================
elif tool_choice == "📅 الدوام الدقيقة":
    page_header("📅", "حاسبة الدوام الدقيقة", "احسب راتبك حسب الساعات الفعلية")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    salary = st.number_input(f"الراتب الشهري ({currency})", min_value=0.0, value=5000.0, step=100.0)

    col1, col2 = st.columns(2)
    with col1:
        sd = st.date_input("تاريخ البداية:", value=datetime.date.today().replace(day=1))
        stime = st.time_input("وقت البداية:", value=datetime.time(8, 0))
    with col2:
        ed = st.date_input("تاريخ النهاية:", value=datetime.date.today())
        etime = st.time_input("وقت النهاية:", value=datetime.time(16, 0))

    sdt = datetime.datetime.combine(sd, stime)
    edt = datetime.datetime.combine(ed, etime)

    st.markdown('<hr>', unsafe_allow_html=True)

    if sdt >= edt:
        st.error("⚠️ تاريخ/وقت النهاية يجب أن يكون بعد البداية!")
    else:
        diff = edt - sdt
        secs = diff.total_seconds()
        d = diff.days
        h, rem = divmod(diff.seconds, 3600)
        m, s = divmod(rem, 60)
        month_secs = 30 * 24 * 3600
        earned = (secs / month_secs) * salary

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("أيام", d)
        c2.metric("ساعات", h)
        c3.metric("دقائق", m)
        c4.metric("ثواني", s)
        st.success(f"💰 الراتب: **{money(earned, currency)}**")


# ============================================================
# ⚖️ توزيع الشحن
# ============================================================
elif tool_choice == "⚖️ توزيع الشحن":
    page_header("⚖️", "توزيع مصاريف الشحن", "وزّع المصاريف على الأصناف")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    total = st.number_input(f"الفاتورة ({currency})", min_value=0.01, value=1000.0, step=100.0)
    expenses = st.number_input(f"الشحن ({currency})", min_value=0.0, value=200.0, step=10.0)
    item = st.number_input(f"سعر الصنف ({currency})", min_value=0.0, value=50.0, step=10.0)

    if total > 0:
        ratio = expenses / total
        item_exp = item * ratio
        st.markdown('<hr>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("النسبة", f"{ratio * 100:.2f}%")
        c2.metric("النصيب", money(item_exp, currency))
        c3.metric("الإجمالي", money(item + item_exp, currency))


# ============================================================
# 🏷️ الخصومات
# ============================================================
elif tool_choice == "🏷️ الخصومات":
    page_header("🏷️", "حاسبة الخصومات", "احسب السعر النهائي")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    price = st.number_input(f"السعر ({currency})", min_value=0.0, value=100.0, step=10.0)

    dtype = st.radio("النوع:", ["نسبة %", "مبلغ ثابت"], horizontal=True)

    if dtype == "نسبة %":
        p = st.number_input("النسبة (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
        disc = price * (p / 100)
    else:
        max_val = float(price) if price > 0 else 0.0
        safe_value = min(20.0, max_val)
        disc = st.number_input(
            f"الخصم ({currency})",
            min_value=0.0,
            max_value=max_val,
            value=safe_value,
            step=5.0,
        )

    st.markdown('<hr>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("التوفير", money(disc, currency))
    c2.metric("النهائي", money(price - disc, currency))


# ============================================================
# 🎁 العروض الترويجية
# ============================================================
elif tool_choice == "🎁 العروض الترويجية":
    page_header("🎁", "حاسبة العروض", "هل عرضك مربح؟")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    offer = st.selectbox("نوع العرض", ["اشترِ X واحصل Y", "خصم على الثاني", "خصم كمية", "منتج مجاني"])

    cost = st.number_input(f"تكلفة القطعة ({currency})", min_value=0.0, value=40.0, step=5.0)
    price = st.number_input(f"سعر البيع ({currency})", min_value=0.0, value=100.0, step=5.0)

    st.markdown('<hr>', unsafe_allow_html=True)

    if offer == "اشترِ X واحصل Y":
        buy = st.number_input("اشترِ", min_value=1, value=2, step=1)
        free = st.number_input("احصل مجاناً", min_value=1, value=1, step=1)
        revenue = price * buy
        total_cost = cost * (buy + free)
        profit = revenue - total_cost
        eff_disc = (free / (buy + free)) * 100

        c1, c2, c3 = st.columns(3)
        c1.metric("الإيراد", money(revenue, currency))
        c2.metric("التكلفة", money(total_cost, currency))
        c3.metric("الربح", money(profit, currency), delta="ربح" if profit > 0 else "خسارة")
        st.info(f"الخصم الفعلي: **{eff_disc:.1f}%**")

    elif offer == "خصم على الثاني":
        disc = st.number_input("الخصم على الثاني (%)", min_value=0.0, max_value=100.0, value=50.0, step=5.0)
        revenue = price + price * (1 - disc / 100)
        total_cost = cost * 2
        profit = revenue - total_cost

        c1, c2, c3 = st.columns(3)
        c1.metric("الإيراد", money(revenue, currency))
        c2.metric("التكلفة", money(total_cost, currency))
        c3.metric("الربح", money(profit, currency), delta="ربح" if profit > 0 else "خسارة")

    elif offer == "خصم كمية":
        qty = st.number_input("الكمية", min_value=2, value=3, step=1)
        dp = st.number_input("الخصم (%)", min_value=0.0, max_value=100.0, value=15.0, step=1.0)
        revenue = price * qty * (1 - dp / 100)
        total_cost = cost * qty
        profit = revenue - total_cost

        c1, c2, c3 = st.columns(3)
        c1.metric("الإيراد", money(revenue, currency))
        c2.metric("التكلفة", money(total_cost, currency))
        c3.metric("الربح", money(profit, currency), delta="ربح" if profit > 0 else "خسارة")

    else:
        free_n = st.number_input("منتجات مجانية", min_value=1, value=1, step=1)
        paid_n = st.number_input("منتجات مدفوعة", min_value=1, value=1, step=1)
        revenue = price * paid_n
        total_cost = cost * (paid_n + free_n)
        profit = revenue - total_cost

        c1, c2, c3 = st.columns(3)
        c1.metric("الإيراد", money(revenue, currency))
        c2.metric("التكلفة", money(total_cost, currency))
        c3.metric("الربح", money(profit, currency), delta="ربح" if profit > 0 else "خسارة")


# ============================================================
# 📦 نقطة إعادة الطلب
# ============================================================
elif tool_choice == "📦 نقطة إعادة الطلب":
    page_header("📦", "نقطة إعادة الطلب", "متى تطلب مخزوناً؟")

    daily = st.number_input("البيع اليومي (قطعة)", min_value=0.0, value=10.0, step=1.0)
    lead = st.number_input("مدة التوريد (أيام)", min_value=0, value=7, step=1)
    safety = st.number_input("مخزون الأمان", min_value=0, value=20, step=5)
    current = st.number_input("المخزون الحالي", min_value=0, value=100, step=10)

    rop = (daily * lead) + safety
    days_left = current / daily if daily > 0 else 9999

    st.markdown('<hr>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("نقطة الطلب", f"{rop:,.0f}")
    c2.metric("أيام حتى النفاذ", f"{days_left:.1f}")
    c3.metric("المخزون الحالي", current)

    if current <= rop:
        st.error("🚨 اطلب الآن!")
    else:
        st.success(f"✅ متبقي **{current - rop:.0f}** قطعة قبل الحاجة للطلب")


# ============================================================
# 📈 نمو المبيعات
# ============================================================
elif tool_choice == "📈 نمو المبيعات":
    page_header("📈", "نمو المبيعات CAGR", "نسبة النمو السنوية المركبة")

    start = st.number_input("قيمة البداية", min_value=0.0, value=10000.0, step=1000.0)
    end = st.number_input("قيمة النهاية", min_value=0.0, value=25000.0, step=1000.0)
    years = st.number_input("السنوات", min_value=1, value=3, step=1)

    st.markdown('<hr>', unsafe_allow_html=True)
    if start > 0:
        cagr = ((end / start) ** (1 / years) - 1) * 100
        total = ((end - start) / start) * 100
        c1, c2 = st.columns(2)
        c1.metric("CAGR", f"{cagr:.2f}%")
        c2.metric("النمو الإجمالي", f"{total:.2f}%")


# ============================================================
# 📊 LTV / CAC
# ============================================================
elif tool_choice == "📊 LTV / CAC":
    page_header("📊", "حاسبة LTV / CAC", "قيّم حملات التسويق")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    aov = st.number_input(f"متوسط الطلب ({currency})", min_value=0.0, value=150.0, step=10.0)
    margin = st.number_input("هامش (%)", min_value=0.0, value=40.0, step=1.0)
    orders = st.number_input("طلبات سنوياً", min_value=1, value=4, step=1)
    years = st.number_input("سنوات بقاء العميل", min_value=1, value=3, step=1)
    cac = st.number_input(f"CAC ({currency})", min_value=0.0, value=50.0, step=10.0)

    ltv = aov * (margin / 100) * orders * years
    ratio = ltv / cac if cac > 0 else 0

    st.markdown('<hr>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("LTV", money(ltv, currency))
    c2.metric("CAC", money(cac, currency))
    c3.metric("النسبة", f"{ratio:.2f}x")

    if ratio >= 3:
        st.success("✅ ممتاز!")
    elif ratio >= 1:
        st.warning("⚡ مقبول، الأفضل 3x")
    else:
        st.error("🚨 تخسر في التسويق!")


# ============================================================
# ⏳ حاسبة العمر
# ============================================================
elif tool_choice == "⏳ حاسبة العمر":
    page_header("⏳", "حاسبة العمر الدقيقة", "احسب عمرك بالسنوات والأيام")

    today = datetime.date.today()
    dob = st.date_input("تاريخ الميلاد:", value=datetime.date(2000, 1, 1),
                         min_value=datetime.date(1900, 1, 1), max_value=today)

    if dob <= today:
        total_days = (today - dob).days
        total_weeks = total_days // 7

        if HAS_DATEUTIL:
            diff = relativedelta(today, dob)
            y, m, d = diff.years, diff.months, diff.days
        else:
            y = today.year - dob.year
            m = today.month - dob.month
            d = today.day - dob.day
            if d < 0:
                m -= 1
                prev_m = today.month - 1 if today.month > 1 else 12
                prev_y = today.year if today.month > 1 else today.year - 1
                dim = (datetime.date(prev_y, prev_m + 1, 1) - datetime.date(prev_y, prev_m, 1)).days
                d += dim
            if m < 0:
                y -= 1
                m += 12

        st.markdown('<hr>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("سنة", y)
        c2.metric("شهر", m)
        c3.metric("يوم", d)

        c4, c5, c6 = st.columns(3)
        c4.metric("الأيام", f"{total_days:,}")
        c5.metric("الأسابيع", f"{total_weeks:,}")
        c6.metric("الأشهر", f"{y * 12 + m:,}")

        nb = safe_date(today.year, dob.month, dob.day)
        if nb < today:
            nb = safe_date(today.year + 1, dob.month, dob.day)
        dtb = (nb - today).days

        if dtb == 0:
            st.balloons()
            st.success("🎉 عيد ميلاد سعيد!")
        else:
            st.info(f"🎂 متبقي {dtb} يوماً لعيد ميلادك.")


# ============================================================
# 📉 نقطة التعادل
# ============================================================
elif tool_choice == "📉 نقطة التعادل":
    page_header("📉", "حاسبة نقطة التعادل", "عدد القطع لتغطية التكاليف")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    fixed = st.number_input(f"المصاريف الثابتة ({currency})", min_value=0.0, value=1000.0, step=100.0)
    var = st.number_input(f"تكلفة القطعة ({currency})", min_value=0.0, value=50.0, step=5.0)
    price = st.number_input(f"سعر البيع ({currency})", min_value=0.0, value=100.0, step=5.0)

    st.markdown('<hr>', unsafe_allow_html=True)
    if price <= var:
        st.error("⚠️ السعر يجب أن يزيد عن التكلفة.")
    else:
        cm = price - var
        be_units = fixed / cm
        be_rev = be_units * price
        c1, c2, c3 = st.columns(3)
        c1.metric("القطع للتعادل", f"{be_units:,.0f}")
        c2.metric("إيراد التعادل", money(be_rev, currency))
        c3.metric("هامش المساهمة", money(cm, currency))


# ============================================================
# 🧾 ضريبة VAT
# ============================================================
elif tool_choice == "🧾 ضريبة VAT":
    page_header("🧾", "ضريبة القيمة المضافة", "أضف أو استخرج الضريبة")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    mode = st.radio("الطريقة:", ["إضافة", "استخراج"], horizontal=True)
    price = st.number_input(f"المبلغ ({currency})", min_value=0.0, value=1000.0, step=100.0)
    rate = st.number_input("النسبة (%)", min_value=0.0, value=15.0, step=1.0)

    st.markdown('<hr>', unsafe_allow_html=True)
    if mode == "إضافة":
        vat = price * (rate / 100)
        total = price + vat
        c1, c2 = st.columns(2)
        c1.metric("الضريبة", money(vat, currency))
        c2.metric("مع الضريبة", money(total, currency))
    else:
        base = price / (1 + rate / 100)
        vat = price - base
        c1, c2 = st.columns(2)
        c1.metric("قبل الضريبة", money(base, currency))
        c2.metric("الضريبة", money(vat, currency))


# ============================================================
# 📈 أرباح الكريبتو
# ============================================================
elif tool_choice == "📈 أرباح الكريبتو":
    page_header("📈", "أرباح الكريبتو", "صافي الربح بعد الرسوم")

    entry = st.number_input("سعر الدخول ($)", min_value=0.0, value=60000.0, step=100.0)
    amt = st.number_input("الكمية", min_value=0.0, value=0.1, step=0.01, format="%.4f")
    exit_p = st.number_input("سعر الخروج ($)", min_value=0.0, value=62000.0, step=100.0)
    fee = st.number_input("الرسوم (%)", min_value=0.0, value=0.1, step=0.05)

    entry_v = entry * amt
    exit_v = exit_p * amt
    gross = exit_v - entry_v
    fees = (entry_v + exit_v) * (fee / 100)
    net = gross - fees
    roi = (net / entry_v * 100) if entry_v > 0 else 0

    st.markdown('<hr>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي", f"${money(gross)}")
    c2.metric("الرسوم", f"${money(fees)}")
    c3.metric("صافي", f"${money(net)}", delta=f"{roi:.2f}%" if net != 0 else None)


# ============================================================
# 🛡️ إدارة المخاطر
# ============================================================
elif tool_choice == "🛡️ إدارة المخاطر":
    page_header("🛡️", "إدارة المخاطر", "حجم الصفقة المناسب")

    capital = st.number_input("المحفظة (USDT)", min_value=0.0, value=1000.0, step=100.0)
    risk = st.number_input("المخاطرة (%)", min_value=0.0, value=2.0, step=0.5)

    col1, col2 = st.columns(2)
    with col1:
        entry_p = st.number_input("سعر الدخول", min_value=0.0, value=50000.0, step=100.0)
    with col2:
        stop = st.number_input("وقف الخسارة", min_value=0.0, value=48000.0, step=100.0)

    risk_amt = capital * (risk / 100)
    st.markdown('<hr>', unsafe_allow_html=True)

    if entry_p <= 0 or stop <= 0:
        st.warning("أدخل أسعاراً صحيحة.")
    elif entry_p == stop:
        st.error("⚠️ سعر الدخول = وقف الخسارة!")
    else:
        size = risk_amt / abs(entry_p - stop)
        value = size * entry_p
        c1, c2, c3 = st.columns(3)
        c1.metric("المخاطرة", f"{money(risk_amt)} USDT")
        c2.metric("الكمية", f"{size:.6f}")
        c3.metric("حجم الصفقة", f"{money(value)} USDT")


# ============================================================
# 💱 محول العملات
# ============================================================
elif tool_choice == "💱 محول العملات":
    page_header("💱", "محول العملات", "أسعار محدثة تلقائياً · +160 عملة")

    with st.spinner("🌍 جلب الأسعار..."):
        rates = fetch_currency_rates()

    if not rates:
        st.error("⚠️ تعذر جلب الأسعار.")
    else:
        codes = sorted(rates.keys())
        common = ["USD", "SAR", "AED", "KWD", "OMR", "QAR", "BHD", "EGP",
                  "JOD", "EUR", "GBP", "TRY", "INR", "PKR", "CNY", "JPY"]
        ordered = [c for c in common if c in codes] + [c for c in codes if c not in common]

        col1, col2 = st.columns(2)
        with col1:
            fr = st.selectbox("من", ordered, index=1 if "SAR" in ordered else 0, format_func=currency_label)
        with col2:
            to = st.selectbox("إلى", ordered, index=0, format_func=currency_label)

        amt = st.number_input("المبلغ", min_value=0.0, value=100.0, step=10.0)
        usd = amt / rates[fr]
        result = usd * rates[to]

        st.markdown('<hr>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("النتيجة", f"{money(result, '', 4)} {to}")
        c2.metric("المبلغ الأصلي", f"{money(amt)} {fr}")

        st.info(f"💱 1 {fr} = {money(rates[to] / rates[fr], '', 4)} {to}")
        st.info(f"💱 1 {to} = {money(rates[fr] / rates[to], '', 4)} {fr}")
        st.caption(f"✅ {len(rates)} عملة مدعومة · تُحدّث كل ساعة")


# ============================================================
# 🗓️ أيام العمل
# ============================================================
elif tool_choice == "🗓️ أيام العمل":
    page_header("🗓️", "حاسبة أيام العمل", "احسب أيام العمل الفعلية")

    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("من:", value=datetime.date.today())
    with col2:
        end = st.date_input("إلى:", value=datetime.date.today() + datetime.timedelta(days=30))

    exclude_fri = st.checkbox("استبعاد الجمعة", value=True)
    exclude_sat = st.checkbox("استبعاد السبت", value=False)
    exclude_sun = st.checkbox("استبعاد الأحد", value=False)

    holidays = st.text_input("عطلات رسمية (تواريخ مفصولة بفاصلة):", placeholder="2025-01-01")

    holiday_set = set()
    if holidays.strip():
        for h in holidays.split(","):
            try:
                holiday_set.add(datetime.datetime.strptime(h.strip(), "%Y-%m-%d").date())
            except ValueError:
                pass

    st.markdown('<hr>', unsafe_allow_html=True)
    if start <= end:
        total = (end - start).days + 1
        work = 0
        cur = start
        while cur <= end:
            wd = cur.weekday()
            skip = (exclude_fri and wd == 4) or (exclude_sat and wd == 5) or (exclude_sun and wd == 6)
            if not skip and cur not in holiday_set:
                work += 1
            cur += datetime.timedelta(days=1)

        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي", total)
        c2.metric("أيام العمل", work)
        c3.metric("راحة", total - work)
        

# ============================================================
# 📅 أرقام الفواتير
# ============================================================
elif tool_choice == "📅 أرقام الفواتير":
    page_header("📅", "مولد أرقام الفواتير", "أرقام تلقائية متسلسلة")

    prefix = st.text_input("البادئة:", value="INV")
    year = st.number_input("السنة:", min_value=2000, max_value=2100, value=datetime.date.today().year, step=1)
    sep = st.selectbox("الفاصل:", ["-", "/", "_", "."], index=0)

    col1, col2 = st.columns(2)
    with col1:
        start_num = st.number_input("ابدأ من:", min_value=1, value=1, step=1)
    with col2:
        padding = st.number_input("الخانات:", min_value=1, max_value=10, value=4, step=1)

    count = st.number_input("عدد الفواتير:", min_value=1, max_value=500, value=10, step=1)

    if st.button("🔢 توليد"):
        nums = [f"{prefix}{sep}{year}{sep}{start_num + i:0{padding}d}" for i in range(count)]
        df = pd.DataFrame({"رقم الفاتورة": nums})
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("📥 تحميل CSV", data=df.to_csv(index=False).encode("utf-8-sig"),
                          file_name="invoice_numbers.csv", mime="text/csv")


# ============================================================
# 🔲 مولد QR
# ============================================================
elif tool_choice == "🔲 مولد QR":
    page_header("🔲", "مولد QR Code", "أنشئ رمز QR لأي محتوى")

    content = st.text_area("المحتوى:", placeholder="https://example.com")

    col1, col2 = st.columns(2)
    with col1:
        size = st.number_input("الحجم:", min_value=100, max_value=1000, value=300, step=50)
    with col2:
        color = st.color_picker("اللون:", "#4f46e5")

    if st.button("✨ توليد QR"):
        if not content.strip():
            st.warning("أدخل محتوى.")
        elif not HAS_QR:
            st.error("مكتبة qrcode غير مثبتة.")
        else:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H,
                               box_size=10, border=2)
            qr.add_data(content.strip())
            qr.make(fit=True)
            img = qr.make_image(fill_color=color, back_color="white")
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            st.image(buf, width=size)
            st.download_button("📥 تحميل PNG", data=buf.getvalue(),
                              file_name="qrcode.png", mime="image/png")


# ============================================================
# 🔐 مولّد كلمات السر
# ============================================================
elif tool_choice == "🔐 مولد كلمات السر":
    import secrets
    import string

    page_header("🔐", "مولّد كلمات السر", "كلمات سر قوية ومأمونة")

    length = st.slider("طول كلمة السر", min_value=8, max_value=64, value=16)
    col1, col2, col3 = st.columns(3)
    with col1:
        use_upper = st.checkbox("أحرف كبيرة A-Z", value=True)
    with col2:
        use_lower = st.checkbox("أحرف صغيرة a-z", value=True)
    with col3:
        use_digits = st.checkbox("أرقام 0-9", value=True)

    use_symbols = st.checkbox("رموز !@#$%", value=True)
    count = st.number_input("عدد كلمات السر", min_value=1, max_value=20, value=5, step=1)

    if st.button("🎲 توليد كلمات السر"):
        chars = ""
        if use_upper:
            chars += string.ascii_uppercase
        if use_lower:
            chars += string.ascii_lowercase
        if use_digits:
            chars += string.digits
        if use_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not chars:
            st.error("⚠️ اختر نوعاً واحداً على الأقل")
        else:
            passwords = []
            for _ in range(int(count)):
                pw = "".join(secrets.choice(chars) for _ in range(length))
                passwords.append(pw)

            for pw in passwords:
                st.code(pw, language="")

            st.download_button(
                "📥 تحميل كـ TXT",
                data="\n".join(passwords).encode("utf-8"),
                file_name="passwords.txt",
                mime="text/plain",
                use_container_width=True,
            )


# ============================================================
# 🎯 أهداف المبيعات
# ============================================================
elif tool_choice == "🎯 أهداف المبيعات":
    page_header("🎯", "حاسبة أهداف المبيعات", "خطط لتحقيق هدفك الشهري")

    currency = st.selectbox("العملة", CURRENCIES, index=0)

    target = st.number_input(f"الهدف الشهري ({currency})", min_value=0.0, value=50000.0, step=1000.0)
    avg_sale = st.number_input(f"متوسط قيمة الطلب ({currency})", min_value=1.0, value=200.0, step=10.0)
    work_days = st.number_input("أيام العمل شهرياً", min_value=1, max_value=31, value=26, step=1)
    current = st.number_input(f"المبيعات الحالية ({currency})", min_value=0.0, value=0.0, step=500.0)

    remaining = max(target - current, 0)
    if avg_sale > 0:
        orders_needed = remaining / avg_sale
        orders_per_day = orders_needed / work_days
    else:
        orders_needed = 0
        orders_per_day = 0

    progress = (current / target * 100) if target > 0 else 0

    st.markdown('<hr>', unsafe_allow_html=True)
    st.metric("📊 التقدم الحالي", f"{progress:.1f}%")
    st.progress(min(progress / 100, 1.0))

    st.markdown('<hr>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("المتبقي", money(remaining, currency))
    c2.metric("طلبات مطلوبة", f"{orders_needed:.0f}")
    c3.metric("طلبات يومياً", f"{orders_per_day:.1f}")

    if progress >= 100:
        st.success("🎉 تحقق الهدف! مبروك!")
    elif progress >= 75:
        st.info("💪 قريب جداً! واصل!")
    elif progress >= 50:
        st.warning("⚡ نصف الطريق!")
    else:
        st.error("🚀 تحتاج جهداً أكبر!")


# ============================================================
# 📧 مولّد البريد الاحترافي
# ============================================================
elif tool_choice == "📧 مولّد البريد الاحترافي":
    page_header("📧", "مولّد البريد الاحترافي", "أنشئ توقيع بريد رسمي")

    sender_name = st.text_input("اسمك:")
    sender_title = st.text_input("منصبك:", placeholder="مدير المبيعات")
    company = st.text_input("الشركة:", placeholder="شركة XYZ")
    phone = st.text_input("رقم الجوال:", placeholder="+966 5X XXX XXXX")
    email = st.text_input("البريد الإلكتروني:", placeholder="name@company.com")
    website = st.text_input("الموقع الإلكتروني (اختياري):", placeholder="www.company.com")
    color = st.color_picker("اللون المميز:", "#6366f1")

    if st.button("📧 توليد التوقيع"):
        if not sender_name.strip():
            st.warning("أدخل اسمك على الأقل")
        else:
            signature = (
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 {sender_name}\n"
                f"💼 {sender_title}\n"
                f"🏢 {company}\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📱 {phone}\n"
                f"📧 {email}\n"
            )
            if website.strip():
                signature += f"🌐 {website}\n"
            signature += "━━━━━━━━━━━━━━━━━━━━━━"

            st.code(signature, language="")
            st.success("✅ تم التوليد! انسخه والصقه في بريدك")

            html_sig = (
                '<div style="font-family:Cairo,Arial; padding:16px; '
                'border-right:4px solid ' + color + '; background:#f8fafc; '
                'border-radius:8px; direction:rtl;">'
                '<div style="font-size:1.1rem; font-weight:800; color:' + color + ';">'
                + sender_name +
                '</div>'
                '<div style="color:#64748b; font-size:0.85rem;">' + sender_title + ' · ' + company + '</div>'
                '<div style="margin-top:10px; font-size:0.85rem; color:#1e293b;">'
                '📱 ' + phone + '<br>📧 ' + email
            )
            if website.strip():
                html_sig += '<br>🌐 ' + website
            html_sig += '</div></div>'

            st.markdown("### 👁️ معاينة:")
            st.markdown(html_sig, unsafe_allow_html=True)


# ============================================================
# 🎨 مولّد الشعار
# ============================================================
elif tool_choice == "🎨 مولّد الشعار":
    page_header("🎨", "مولّد الشعار", "أنشئ شعاراً بسيطاً لمشروعك")

    brand_name = st.text_input("اسم البراند:", placeholder="متجر XYZ")
    tagline = st.text_input("الشعار الفرعي (اختياري):", placeholder="جودة تستحق الثقة")
    icon = st.text_input("الأيقونة (إيموجي):", value="🛍️", max_chars=3)

    col1, col2 = st.columns(2)
    with col1:
        bg_color = st.color_picker("لون الخلفية:", "#6366f1")
    with col2:
        text_color = st.color_picker("لون النص:", "#ffffff")

    if st.button("🎨 توليد الشعار"):
        if not brand_name.strip():
            st.warning("أدخل اسم البراند")
        else:
            html_logo = (
                '<div style="text-align:center; padding:40px 20px; '
                'background:' + bg_color + '; border-radius:20px; '
                'box-shadow:0 10px 30px rgba(0,0,0,0.15);">'
                '<div style="font-size:4rem; margin-bottom:10px;">' + icon + '</div>'
                '<div style="color:' + text_color + '; font-size:2rem; '
                'font-weight:900; font-family:Cairo, Arial;">' + brand_name + '</div>'
            )
            if tagline.strip():
                html_logo += (
                    '<div style="color:' + text_color + '; opacity:0.85; '
                    'font-size:1rem; margin-top:8px; font-family:Cairo, Arial;">'
                    + tagline + '</div>'
                )
            html_logo += '</div>'

            st.markdown("### 👁️ معاينة الشعار:")
            st.markdown(html_logo, unsafe_allow_html=True)
            st.info("💡 التقط صورة للشاشة لحفظ الشعار.")


# ============================================================
# 📞 حاسبة الاتصال الدولي
# ============================================================
elif tool_choice == "📞 حاسبة الاتصال الدولي":
    page_header("📞", "حاسبة الاتصال الدولي", "احسب تكلفة مكالماتك الدولية")

    st.warning("⚠️ الأسعار المعروضة تقريبية وقد تختلف حسب مزوّد الخدمة والباقة.")

    minutes = st.number_input("عدد الدقائق", min_value=1, value=10, step=1)

    countries = {
        "مصر": 0.30, "السعودية": 0.15, "الإمارات": 0.18,
        "الكويت": 0.20, "قطر": 0.22, "البحرين": 0.20,
        "عمان": 0.20, "الأردن": 0.25, "لبنان": 0.28,
        "سوريا": 0.35, "العراق": 0.32, "اليمن": 0.30,
        "المغرب": 0.28, "تونس": 0.30, "الجزائر": 0.30,
        "ليبيا": 0.30, "السودان": 0.35, "تركيا": 0.20,
        "أمريكا": 0.10, "بريطانيا": 0.12, "فرنسا": 0.12,
        "ألمانيا": 0.12,
    }

    country = st.selectbox("الدولة", list(countries.keys()))
    rate = countries[country]

    custom_rate = st.number_input("أو أدخل سعر الدقيقة يدوياً ($)", min_value=0.0, value=rate, step=0.01)

    total = minutes * custom_rate

    st.markdown('<hr>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("الدقائق", minutes)
    c2.metric("سعر الدقيقة", f"${custom_rate:.2f}")
    c3.metric("التكلفة", f"${total:.2f}")

    if minutes >= 30:
        st.info("💡 **نصيحة:** للمكالمات الطويلة، جرّب باقات الاتصال الشهرية — غالباً أوفر.")


# ============================================================
# 👥 إدارة العملاء
# ============================================================
elif tool_choice == "👥 إدارة العملاء":
    page_header("👥", "إدارة العملاء", "سجل عملائك وفواتيرهم")

    customers = st.session_state.get("customers", [])

    tab1, tab2, tab3 = st.tabs(["➕ إضافة عميل", "📋 قائمة العملاء", "📊 إحصائيات"])

    with tab1:
        st.markdown("### إضافة عميل جديد")
        c_name = st.text_input("اسم العميل:", key="cust_name")
        c_phone = st.text_input("رقم الجوال:", key="cust_phone", placeholder="966500000000")
        c_email = st.text_input("البريد (اختياري):", key="cust_email")
        c_city = st.text_input("المدينة (اختياري):", key="cust_city")

        col1, col2 = st.columns(2)
        with col1:
            c_total = st.number_input("إجمالي المشتريات:", min_value=0.0, value=0.0, step=100.0, key="cust_total")
        with col2:
            c_orders = st.number_input("عدد الطلبات:", min_value=0, value=0, step=1, key="cust_orders")

        c_notes = st.text_area("ملاحظات:", key="cust_notes", height=80)

        if st.button("➕ إضافة العميل", use_container_width=True):
            if not c_name.strip():
                st.warning("أدخل اسم العميل")
            else:
                record = {
                    "الاسم": c_name.strip(),
                    "الجوال": c_phone.strip(),
                    "البريد": c_email.strip(),
                    "المدينة": c_city.strip(),
                    "إجمالي المشتريات": round(c_total, 2),
                    "عدد الطلبات": c_orders,
                    "ملاحظات": c_notes.strip(),
                    "تاريخ الإضافة": datetime.datetime.now().strftime("%Y-%m-%d"),
                }
                customers.append(record)
                st.session_state.customers = customers
                st.toast("✅ تمت الإضافة", icon="👥")
                st.rerun()

    with tab2:
        if not customers:
            st.info("📭 لا يوجد عملاء بعد")
        else:
            df_c = pd.DataFrame(customers)
            st.dataframe(df_c, use_container_width=True, hide_index=True)

            st.markdown("### 🗑️ حذف عميل")
            names = [c["الاسم"] for c in customers]
            del_name = st.selectbox("اختر العميل", names, key="del_cust")
            if st.button("🗑️ حذف", use_container_width=True):
                st.session_state.customers = [c for c in customers if c["الاسم"] != del_name]
                st.toast("تم الحذف", icon="🗑️")
                st.rerun()

            st.markdown("### 📥 تصدير")
            csv = df_c.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 تحميل CSV",
                data=csv,
                file_name="customers.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with tab3:
        if customers:
            total_revenue = sum(c.get("إجمالي المشتريات", 0) for c in customers)
            total_orders = sum(c.get("عدد الطلبات", 0) for c in customers)

            c1, c2, c3 = st.columns(3)
            c1.metric("👥 عدد العملاء", len(customers))
            c2.metric("💰 إجمالي المشتريات", money(total_revenue))
            c3.metric("📦 إجمالي الطلبات", total_orders)

            if total_orders > 0:
                avg_order = total_revenue / total_orders
                st.metric("📊 متوسط قيمة الطلب", money(avg_order))

            city_counts = {}
            for c in customers:
                city = c.get("المدينة", "").strip() or "غير محدد"
                city_counts[city] = city_counts.get(city, 0) + 1
            st.bar_chart(pd.Series(city_counts))
        else:
            st.info("📊 لا توجد إحصائيات بعد")


# ============================================================
# 💾 النسخ الاحتياطي
# ============================================================
elif tool_choice == "💾 النسخ الاحتياطي":
    page_header("💾", "النسخ الاحتياطي", "احفظ بياناتك واستعدها في أي وقت")

    st.info("💡 احفظ نسخة من بياناتك (العمليات، العملاء، التنبيهات) واستعدها لاحقاً.")

    backup_restore_ui()


# ============================================================
# 📄 القوالب الجاهزة
# ============================================================
elif tool_choice == "📄 القوالب الجاهزة":
    page_header("📄", "القوالب الجاهزة", "قوالب CSV احترافية")

    templates = {
        "دفتر أستاذ الموردين": (
            "التاريخ,المورد,الفاتورة,البيان,مدين,دائن,الرصيد\n"
            "2025-01-01,مورد أ,INV-001,شراء,1000.00,,1000.00\n"
            "2025-01-05,مورد أ,PAY-001,سداد,,500.00,500.00\n"
        ),
        "جرد المخزون": (
            "الكود,الصنف,الوحدة,دفتر,فعلي,الفرق,التكلفة\n"
            "SKU-001,سماعة,قطعة,100,98,-2,50.00\n"
        ),
        "فاتورة مبيعات": (
            "بند,الوصف,الكمية,السعر,الإجمالي,الضريبة,الإجمالي مع الضريبة\n"
            "1,منتج,2,100.00,200.00,30.00,230.00\n"
        ),
        "سجل المصروفات": (
            "التاريخ,البند,الوصف,المبلغ,الدفع\n"
            "2025-01-01,إيجار,المكتب,3000.00,تحويل\n"
        ),
        "تسعير المنتجات": (
            "المنتج,التكلفة,الشحن,الرسوم,هامش %,السعر,الربح\n"
            "سماعة,50.00,15.00,4.30,40,140.00,70.70\n"
        ),
        "عرض سعر": (
            "بند,الوصف,الكمية,السعر,الإجمالي\n"
            "1,منتج,5,100.00,500.00\n"
        ),
    }

    for name, content in templates.items():
        with st.expander(f"📄 {name}"):
            st.download_button(
                "📥 تحميل",
                data=content.encode("utf-8-sig"),
                file_name=f"{name.replace(' ', '_')}.csv",
                mime="text/csv",
                key=f"dl_{name}",
            )


# ============================================================
# 📜 سياسة الخصوصية
# ============================================================
elif tool_choice == "📜 سياسة الخصوصية":
    page_header("📜", "سياسة الخصوصية", "التزاماتنا تجاهك")

    st.info("🔒 جميع العمليات تُحسب محلياً في جلسة المتصفح.")

    st.subheader("📋 التزاماتنا:")
    st.markdown(
        "- ✅ لا نجمع بيانات شخصية.\n"
        "- ✅ لا نستخدم تتبع أو إعلانات.\n"
        "- ✅ البيانات مؤقتة في جلسة الجلسة وتُمسح بإغلاق الصفحة.\n"
        "- ✅ ننصح بحفظ نسخة احتياطية دورية من قسم النسخ الاحتياطي.\n"
        "- ✅ الأداة للأغراض التعليمية والإرشادية.\n"
    )

    st.subheader("⚠️ إخلاء المسؤولية:")
    st.warning("النتائج إرشادية فقط. راجع مختصاً مالياً أو محاسبياً قانونياً للقرارات المهمة.")

    st.markdown('<hr>', unsafe_allow_html=True)
    st.write("**📧 للتواصل:** admin@smart-merchant-tools.com")
