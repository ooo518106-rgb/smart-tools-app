import streamlit as st
import datetime
import pandas as pd
import urllib.parse
from io import BytesIO

from helpers import (
    money, save_result, quick_save_button, copy_box,
    export_to_excel, page_header, share_buttons,
    fetch_currency_rates,
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
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="expanded",
)

defaults = {
    "ecommerce_history": [],
    "all_results": [],
    "theme": "فاتح",
    "search_query": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def apply_theme(theme_name):
    themes = {
        "فاتح": {
            "bg": "linear-gradient(135deg, #f5f7fa 0%, #e8ecf5 100%)",
            "card": "#ffffff", "accent": "#2a5298",
            "text": "#1e3c72", "sub": "#5a6c8a",
            "sidebar1": "#1e3c72", "sidebar2": "#2a5298",
            "field_bg": "#ffffff", "field_border": "#e0e6f0",
            "field_text": "#1e3c72",
        },
        "داكن": {
            "bg": "linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%)",
            "card": "#16213e", "accent": "#4a7cff",
            "text": "#a8c0ff", "sub": "#8899bb",
            "sidebar1": "#0a0a15", "sidebar2": "#16213e",
            "field_bg": "#1a1a2e", "field_border": "#2a3a5e",
            "field_text": "#e0e0e0",
        },
        "محيط": {
            "bg": "linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%)",
            "card": "#ffffff", "accent": "#00838f",
            "text": "#006064", "sub": "#4dd0e1",
            "sidebar1": "#006064", "sidebar2": "#00838f",
            "field_bg": "#ffffff", "field_border": "#80deea",
            "field_text": "#006064",
        },
        "غروب": {
            "bg": "linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)",
            "card": "#ffffff", "accent": "#e65100",
            "text": "#bf360c", "sub": "#ff8a65",
            "sidebar1": "#bf360c", "sidebar2": "#e65100",
            "field_bg": "#ffffff", "field_border": "#ffcc80",
            "field_text": "#bf360c",
        },
        "غابة": {
            "bg": "linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)",
            "card": "#ffffff", "accent": "#2e7d32",
            "text": "#1b5e20", "sub": "#66bb6a",
            "sidebar1": "#1b5e20", "sidebar2": "#2e7d32",
            "field_bg": "#ffffff", "field_border": "#a5d6a7",
            "field_text": "#1b5e20",
        },
    }

    t = themes.get(theme_name, themes["فاتح"])

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
html, body {{ font-family: 'Cairo', sans-serif; }}
.stApp {{ background: {t['bg']}; }}
footer {{visibility: hidden;}}
#MainMenu {{visibility: hidden;}}
.main-title {{
    background: linear-gradient(90deg, {t['sidebar1']} 0%, {t['accent']} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 1.9rem;
    font-weight: 900;
    text-align: center;
    margin-bottom: 0.3rem;
    line-height: 1.4;
}}
.sub-title {{
    text-align: center;
    color: {t['sub']};
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}}
[data-testid="stMetric"] {{
    background: {t['card']};
    padding: 14px 12px;
    border-radius: 12px;
    border-right: 4px solid {t['accent']};
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
}}
[data-testid="stMetricLabel"] {{
    color: {t['sub']} !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}}
[data-testid="stMetricValue"] {{
    color: {t['text']} !important;
    font-weight: 700 !important;
}}
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {t['sidebar1']} 0%, {t['sidebar2']} 100%);
}}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {{
    color: #ffffff !important;
}}
section[data-testid="stSidebar"] .stRadio label {{
    background: rgba(255, 255, 255, 0.08);
    padding: 8px 12px;
    border-radius: 10px;
    margin-bottom: 6px;
    cursor: pointer;
    display: block;
}}
.stButton > button {{
    background: linear-gradient(90deg, {t['sidebar1']} 0%, {t['accent']} 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
    font-family: 'Cairo', sans-serif;
    width: 100%;
}}
.stDownloadButton > button {{
    background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    width: 100%;
}}
.stTextInput input, .stNumberInput input, .stTextArea textarea {{
    border-radius: 10px !important;
    border: 2px solid {t['field_border']} !important;
    font-family: 'Cairo', sans-serif !important;
    background: {t['field_bg']} !important;
    color: {t['field_text']} !important;
}}
h1, h2, h3 {{
    font-family: 'Cairo', sans-serif !important;
    color: {t['text']} !important;
}}
</style>
""", unsafe_allow_html=True)


apply_theme(st.session_state.theme)

st.sidebar.markdown("### 💰 أدوات التاجر الذكي")

search_query = st.sidebar.text_input(
    "🔍 ابحث عن أداة",
    value=st.session_state.search_query,
    placeholder="مثال: زكاة، ضريبة...",
)
st.session_state.search_query = search_query

theme_options = ["☀️ فاتح", "🌙 داكن", "🌊 محيط", "🌅 غروب", "🌲 غابة"]
theme_names = ["فاتح", "داكن", "محيط", "غروب", "غابة"]
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
    "📊 لوحة التقارير الموحدة",
    "📦 حاسبة التجارة الإلكترونية",
    "💳 رسوم تابي وتمارا",
    "🏪 عمولة المنصات (سلة/زد)",
    "📢 حاسبة الإعلانات ROAS",
    "💬 صانع روابط واتساب",
    "🏦 حاسبة القروض والأقساط",
    "💳 القسط على البطاقة الائتمانية",
    "🕋 حاسبة زكاة المال",
    "💸 حاسبة الرواتب",
    "🛡️ نهاية الخدمة والتأمينات",
    "👥 تكلفة الموظف الإجمالية",
    "📅 حاسبة الدوام الدقيقة",
    "⚖️ توزيع مصاريف الشحن",
    "🏷️ حاسبة الخصومات",
    "🎁 حاسبة العروض الترويجية",
    "📦 نقطة إعادة الطلب",
    "📈 نمو المبيعات CAGR",
    "📊 حاسبة LTV / CAC",
    "⏳ حاسبة العمر",
    "📉 حاسبة نقطة التعادل",
    "🧾 حاسبة الضريبة VAT",
    "📈 حاسبة أرباح الكريبتو",
    "🛡️ حاسبة إدارة المخاطر",
    "💱 محول العملات",
    "🗓️ حاسبة أيام العمل",
    "📅 مولد أرقام الفواتير",
    "🔲 مولد QR Code",
    "📄 القوالب الجاهزة",
    "📜 سياسة الخصوصية",
]

if search_query.strip():
    filtered = [t for t in ALL_TOOLS if search_query.lower().strip() in t.lower()]
else:
    filtered = ALL_TOOLS

if not filtered:
    st.sidebar.warning("لا توجد نتائج")
    tool_choice = "🏠 الرئيسية"
else:
    tool_choice = st.sidebar.radio("القائمة:", filtered)

if st.session_state.all_results:
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**📊 عمليات محفوظة:** {len(st.session_state.all_results)}")

CURRENCIES = ["ر.س", "د.إ", "د.ك", "ر.ع", "ج.م", "$", "€", "£"]


# ============================================================
# 🏠 الرئيسية
# ============================================================
if tool_choice == "🏠 الرئيسية":
    page_header("💰", "أدوات التاجر الذكي", "مجموعة أدوات متكاملة لحساباتك التجارية والمالية")

    total_ops = len(st.session_state.all_results)

    c1, c2, c3 = st.columns(3)
    c1.metric("🛠️ عدد الأدوات", "30")
    c2.metric("📊 عمليات محفوظة", total_ops)
    c3.metric("💰 عملات مدعومة", "8")

    st.divider()

    st.subheader("🚀 ابدأ من هنا")
    st.markdown("""
    - 📊 **لوحة التقارير** — لمشاهدة كل ما حفظته
    - 📦 **حاسبة التجارة** — احسب أرباح منتجاتك
    - 🏪 **عمولة المنصات** — سلة، زد، شوبيفاي
    - 📢 **حاسبة الإعلانات** — ROAS و CPA
    - 🕋 **زكاة المال** — حساب سنوي
    """)

    if total_ops > 0:
        st.divider()
        st.subheader("📈 آخر العمليات")
        recent = st.session_state.all_results[-5:][::-1]
        for r in recent:
            with st.expander(f"• {r.get('الأداة', 'عملية')} — {r.get('التاريخ', '')}"):
                st.json(r)


# ============================================================
# 📊 لوحة التقارير
# ============================================================
elif tool_choice == "📊 لوحة التقارير الموحدة":
    page_header("📊", "لوحة التقارير الموحدة", "جميع النتائج المحفوظة + تصدير Excel")

    if not st.session_state.all_results:
        st.info("ℹ️ لا توجد نتائج محفوظة بعد. استخدم الحاسبات واحفظ النتائج.")
    else:
        df_all = pd.DataFrame(st.session_state.all_results)

        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي العمليات", len(df_all))
        c2.metric("عدد الأدوات المستخدمة", df_all["الأداة"].nunique())
        c3.metric("أول عملية", df_all["التاريخ"].iloc[0].split()[0])

        st.divider()
        st.dataframe(df_all, use_container_width=True)

        st.divider()
        st.subheader("📊 إحصائيات سريعة")
        tool_counts = df_all["الأداة"].value_counts()
        st.bar_chart(tool_counts)

        st.divider()
        st.subheader("📈 النشاط اليومي")
        df_all["اليوم"] = df_all["التاريخ"].str.split(" ").str[0]
        daily = df_all.groupby("اليوم").size()
        st.line_chart(daily)

        st.divider()
        st.subheader("🥧 توزيع الأدوات")
        dist = tool_counts.reset_index()
        dist.columns = ["الأداة", "عدد المرات"]
        st.dataframe(dist, use_container_width=True)

        st.divider()
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
                sub = df_all[df_all["الأداة"] == tool]
                sheets[tool[:28]] = sub

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
# 1. حاسبة التجارة الإلكترونية
# ============================================================
elif tool_choice == "📦 حاسبة التجارة الإلكترونية":
    page_header("📦", "حاسبة أرباح التجارة", "احسب هوامش الربح بعد الشحن والرسوم")

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

    st.divider()
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

    share_buttons(
        f"📦 نتيجة حاسبة التجارة:\n"
        f"التكلفة: {money(total_cost, currency)}\n"
        f"الربح الصافي: {money(net_profit, currency)}\n"
        f"الهامش: {margin:.1f}%\n"
        f"من تطبيق أدوات التاجر الذكي 💰"
    )

    st.divider()
    product_name = st.text_input("اسم المنتج (اختياري للحفظ):", placeholder="سماعة بلوتوث")

    if st.button("➕ حفظ في سجل المنتجات"):
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
        st.dataframe(df_hist, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                "📥 CSV",
                data=df_hist.to_csv(index=False).encode("utf-8-sig"),
                file_name="products.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_b:
            if st.button("🗑️ مسح السجل", use_container_width=True):
                st.session_state.ecommerce_history = []
                st.rerun()


# ============================================================
# 2. تابي وتمارا
# ============================================================
elif tool_choice == "💳 رسوم تابي وتمارا":
    page_header("💳", "رسوم تابي وتمارا", "احسب الصافي بعد العمولة والضريبة")

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

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("العمولة", money(fee_amount, currency))
    c2.metric("الضريبة", money(vat_amount, currency))
    c3.metric("الصافي", money(net, currency))

    share_buttons(
        f"💳 الصافي بعد تابي/تمارا: {money(net, currency)}\n"
        f"من تطبيق أدوات التاجر الذكي"
    )

    quick_save_button("tamara", "تابي/تمارا", {
        "السعر": price,
        "العمولة": round(fee_amount, 2),
        "الضريبة": round(vat_amount, 2),
        "الصافي": round(net, 2),
        "العملة": currency,
    })


# ============================================================
# 3. عمولة المنصات
# ============================================================
elif tool_choice == "🏪 عمولة المنصات (سلة/زد)":
    page_header("🏪", "عمولة المنصات", "سلة، زد، شوبيفاي")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    platform = st.selectbox("المنصة", ["سلة", "زد", "شوبيفاي", "مخصصة"])

    defaults = {"سلة": (2.0, 2.5), "زد": (2.0, 2.5), "شوبيفاي": (2.9, 2.9), "مخصصة": (0.0, 0.0)}

    price = st.number_input(f"السعر ({currency})", min_value=0.0, value=100.0, step=1.0)
    product_cost = st.number_input(f"تكلفة المنتج ({currency})", min_value=0.0, value=40.0, step=1.0)
    shipping = st.number_input(f"الشحن ({currency})", min_value=0.0, value=15.0, step=1.0)

    col1, col2 = st.columns(2)
    with col1:
        commission = st.number_input("عمولة المنصة (%)", min_value=0.0, value=defaults[platform][0], step=0.1)
    with col2:
        payment = st.number_input("رسوم الدفع (%)", min_value=0.0, value=defaults[platform][1], step=0.1)

    payment_fixed = st.number_input(f"دفع ثابت ({currency})", min_value=0.0, value=1.0, step=0.5)
    vat = st.number_input("ضريبة (%)", min_value=0.0, value=15.0, step=1.0)

    platform_fee = price * (commission / 100)
    payment_amount = (price * (payment / 100)) + payment_fixed
    vat_amount = (platform_fee + payment_amount) * (vat / 100)
    total_deductions = platform_fee + payment_amount + vat_amount
    net_profit = price - product_cost - shipping - total_deductions

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("عمولة المنصة", money(platform_fee, currency))
    c2.metric("رسوم الدفع", money(payment_amount, currency))
    c3.metric("الضريبة", money(vat_amount, currency))

    c4, c5, c6 = st.columns(3)
    c4.metric("إجمالي الخصم", money(total_deductions, currency))
    c5.metric("الصافي", money(price - total_deductions, currency))
    c6.metric("الربح", money(net_profit, currency), delta="ربح" if net_profit > 0 else "خسارة")

    share_buttons(
        f"🏪 نتيجة عمولة {platform}:\n"
        f"السعر: {money(price, currency)}\n"
        f"الربح الصافي: {money(net_profit, currency)}\n"
        f"من تطبيق أدوات التاجر الذكي"
    )

    quick_save_button("platform", f"عمولة {platform}", {
        "المنصة": platform,
        "السعر": price,
        "الربح الصافي": round(net_profit, 2),
        "العملة": currency,
    })


# ============================================================
# 4. الإعلانات ROAS
# ============================================================
elif tool_choice == "📢 حاسبة الإعلانات ROAS":
    page_header("📢", "حاسبة الإعلانات", "ROAS, CPA, AOV")

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

    st.divider()
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

    share_buttons(
        f"📢 نتيجة حاسبة الإعلانات:\n"
        f"ROAS: {roas:.2f}x\n"
        f"الربح الصافي: {money(net_profit, currency)}\n"
        f"من تطبيق أدوات التاجر الذكي"
    )

    quick_save_button("roas", "الإعلانات", {
        "الإنفاق": ad_spend,
        "الإيراد": revenue,
        "ROAS": round(roas, 2),
        "الربح الصافي": round(net_profit, 2),
        "العملة": currency,
    })


# ============================================================
# 5. واتساب
# ============================================================
elif tool_choice == "💬 صانع روابط واتساب":
    page_header("💬", "صانع روابط واتساب")

    phone = st.text_input("رقم الجوال:", placeholder="966500000000")
    msg = st.text_area("الرسالة:", placeholder="مرحباً...")

    if st.button("🔗 توليد"):
        clean = "".join(filter(str.isdigit, phone))
        if clean and len(clean) >= 10:
            link = f"https://wa.me/{clean}?text={urllib.parse.quote(msg)}"
            st.success("تم!")
            st.code(link, language="")
            st.markdown(f"[📲 تجربة]({link})")
        else:
            st.error("رقم غير صحيح.")


# ============================================================
# 6. القروض
# ============================================================
elif tool_choice == "🏦 حاسبة القروض والأقساط":
    page_header("🏦", "حاسبة القروض")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    loan = st.number_input(f"المبلغ ({currency})", min_value=0.0, value=10000.0, step=100.0)

    col1, col2 = st.columns(2)
    with col1:
        rate = st.number_input("الفائدة (%)", min_value=0.0, value=5.0, step=0.1)
    with col2:
        months = st.number_input("الأشهر", min_value=1, value=60, step=1)

    if loan > 0 and months > 0:
        if rate > 0:
            mr = (rate / 100) / 12
            f = (1 + mr) ** months
            payment = loan * (mr * f) / (f - 1)
        else:
            payment = loan / months

        total = payment * months
        interest = total - loan

        c1, c2, c3 = st.columns(3)
        c1.metric("القسط", money(payment, currency))
        c2.metric("الفوائد", money(interest, currency))
        c3.metric("الإجمالي", money(total, currency))

        share_buttons(
            f"🏦 القسط الشهري: {money(payment, currency)}\n"
            f"الإجمالي: {money(total, currency)}\n"
            f"من تطبيق أدوات التاجر الذكي"
        )

        quick_save_button("loan", "قرض", {
            "المبلغ": loan,
            "القسط": round(payment, 2),
            "الفوائد": round(interest, 2),
            "الأشهر": months,
            "العملة": currency,
        })


# ============================================================
# 7. بطاقة ائتمانية
# ============================================================
elif tool_choice == "💳 القسط على البطاقة الائتمانية":
    page_header("💳", "القسط على البطاقة")

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

        c1, c2, c3 = st.columns(3)
        c1.metric("المدة", f"{months} شهر")
        c2.metric("الفوائد", money(total_interest, currency))
        c3.metric("الإجمالي", money(balance + total_interest, currency))


# ============================================================
# 8. زكاة
# ============================================================
elif tool_choice == "🕋 حاسبة زكاة المال":
    page_header("🕋", "حاسبة الزكاة", "2.5% من المال")

    nisab = st.number_input("النصاب (اختياري):", min_value=0.0, value=0.0, step=100.0)
    wealth = st.number_input("إجمالي المال:", min_value=0.0, value=10000.0, step=100.0)

    zakat = wealth * 0.025

    if nisab > 0 and wealth < nisab:
        st.warning("⚠️ أقل من النصاب.")
    else:
        st.metric("الزكاة", money(zakat))

        share_buttons(
            f"🕋 مقدار الزكاة: {money(zakat)}\n"
            f"من تطبيق أدوات التاجر الذكي"
        )

        quick_save_button("zakat", "زكاة", {"المال": wealth, "الزكاة": round(zakat, 2)})


# ============================================================
# 9. الرواتب
# ============================================================
elif tool_choice == "💸 حاسبة الرواتب":
    page_header("💸", "حاسبة الرواتب")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    basic = st.number_input(f"الراتب الأساسي ({currency})", min_value=0.0, value=5000.0, step=100.0)

    col1, col2 = st.columns(2)
    with col1:
        allow = st.number_input(f"البدلات ({currency})", min_value=0.0, value=0.0, step=100.0)
    with col2:
        deduct = st.number_input(f"الخصومات ({currency})", min_value=0.0, value=0.0, step=100.0)

    net = basic + allow - deduct

    if net < 0:
        st.error("⚠️ الخصومات تتجاوز الراتب!")
    else:
        st.metric("💰 الراتب المستحق", money(net, currency))


# ============================================================
# 10. نهاية الخدمة
# ============================================================
elif tool_choice == "🛡️ نهاية الخدمة والتأمينات":
    page_header("🛡️", "نهاية الخدمة + التأمينات", "النظام السعودي")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    salary = st.number_input(f"الراتب الأخير ({currency})", min_value=0.0, value=5000.0, step=100.0)

    col1, col2 = st.columns(2)
    with col1:
        years = st.number_input("سنوات", min_value=0, value=5, step=1)
    with col2:
        months = st.number_input("أشهر", min_value=0, max_value=11, value=0, step=1)

    reason = st.radio("السبب:", ["استقالة", "إنهاء"], horizontal=True)
    nationality = st.radio("الجنسية:", ["سعودي", "غير سعودي"], horizontal=True)

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

    st.divider()
    if nationality == "سعودي":
        emp = salary * 0.0975
        er = salary * 0.1175
    else:
        emp = 0
        er = salary * 0.02

    c1, c2 = st.columns(2)
    c1.metric("حصة الموظف", money(emp, currency))
    c2.metric("حصة صاحب العمل", money(er, currency))

    st.metric("💰 المكافأة", money(gratuity, currency))

    quick_save_button("end_service", "نهاية خدمة", {
        "الراتب": salary,
        "السنوات": total_years,
        "المكافأة": round(gratuity, 2),
        "السبب": reason,
        "العملة": currency,
    })


# ============================================================
# 11. تكلفة الموظف
# ============================================================
elif tool_choice == "👥 تكلفة الموظف الإجمالية":
    page_header("👥", "تكلفة الموظف", "التكلفة الحقيقية")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    salary = st.number_input(f"الراتب ({currency})", min_value=0.0, value=5000.0, step=100.0)

    col1, col2 = st.columns(2)
    with col1:
        housing = st.number_input(f"سكن ({currency})", min_value=0.0, value=1250.0, step=100.0)
        transport = st.number_input(f"مواصلات ({currency})", min_value=0.0, value=500.0, step=50.0)
    with col2:
        other = st.number_input(f"بدلات أخرى ({currency})", min_value=0.0, value=0.0, step=100.0)
        bonus = st.number_input(f"مكافآت سنوية ({currency})", min_value=0.0, value=0.0, step=500.0)

    nationality = st.radio("الجنسية:", ["سعودي", "غير سعودي"], horizontal=True)

    total_sal = salary + housing + transport + other
    gosi = total_sal * 0.1175 if nationality == "سعودي" else total_sal * 0.02
    monthly = total_sal + gosi
    annual = (monthly * 12) + bonus

    c1, c2 = st.columns(2)
    c1.metric("شهرياً", money(monthly, currency))
    c2.metric("سنوياً", money(annual, currency))


# ============================================================
# 12. دوام دقيق
# ============================================================
elif tool_choice == "📅 حاسبة الدوام الدقيقة":
    page_header("📅", "حاسبة الدوام الدقيقة")

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

    if sdt < edt:
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
    else:
        st.error("⚠️ تاريخ النهاية بعد البداية!")


# ============================================================
# 13. توزيع الشحن
# ============================================================
elif tool_choice == "⚖️ توزيع مصاريف الشحن":
    page_header("⚖️", "توزيع مصاريف الشحن")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    total = st.number_input(f"الفاتورة ({currency})", min_value=0.01, value=1000.0, step=100.0)
    expenses = st.number_input(f"الشحن ({currency})", min_value=0.0, value=200.0, step=10.0)
    item = st.number_input(f"سعر الصنف ({currency})", min_value=0.0, value=50.0, step=10.0)

    if total > 0:
        ratio = expenses / total
        item_exp = item * ratio

        c1, c2, c3 = st.columns(3)
        c1.metric("النسبة", f"{ratio * 100:.2f}%")
        c2.metric("النصيب", money(item_exp, currency))
        c3.metric("الإجمالي", money(item + item_exp, currency))


# ============================================================
# 14. الخصومات
# ============================================================
elif tool_choice == "🏷️ حاسبة الخصومات":
    page_header("🏷️", "حاسبة الخصومات")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    price = st.number_input(f"السعر ({currency})", min_value=0.0, value=100.0, step=10.0)

    dtype = st.radio("النوع:", ["نسبة %", "مبلغ ثابت"], horizontal=True)

    if dtype == "نسبة %":
        p = st.number_input("النسبة (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
        disc = price * (p / 100)
    else:
        disc = st.number_input(f"الخصم ({currency})", min_value=0.0, max_value=price, value=20.0, step=5.0)

    c1, c2 = st.columns(2)
    c1.metric("التوفير", money(disc, currency))
    c2.metric("النهائي", money(price - disc, currency))


# ============================================================
# 15. العروض الترويجية
# ============================================================
elif tool_choice == "🎁 حاسبة العروض الترويجية":
    page_header("🎁", "حاسبة العروض")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    offer = st.selectbox("نوع العرض", ["اشترِ X واحصل Y", "خصم على الثاني", "خصم كمية", "منتج مجاني"])

    cost = st.number_input(f"تكلفة القطعة ({currency})", min_value=0.0, value=40.0, step=5.0)
    price = st.number_input(f"سعر البيع ({currency})", min_value=0.0, value=100.0, step=5.0)

    st.divider()

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
# 16. نقطة إعادة الطلب
# ============================================================
elif tool_choice == "📦 نقطة إعادة الطلب":
    page_header("📦", "نقطة إعادة الطلب")

    daily = st.number_input("البيع اليومي (قطعة)", min_value=0.0, value=10.0, step=1.0)
    lead = st.number_input("مدة التوريد (أيام)", min_value=0, value=7, step=1)
    safety = st.number_input("مخزون الأمان", min_value=0, value=20, step=5)
    current = st.number_input("المخزون الحالي", min_value=0, value=100, step=10)

    rop = (daily * lead) + safety
    days_left = current / daily if daily > 0 else 9999

    c1, c2, c3 = st.columns(3)
    c1.metric("نقطة الطلب", f"{rop:,.0f}")
    c2.metric("أيام حتى النفاذ", f"{days_left:.1f}")
    c3.metric("المخزون الحالي", current)

    if current <= rop:
        st.error("🚨 اطلب الآن!")
    else:
        st.success(f"✅ متبقي **{current - rop:.0f}** قطعة قبل الحاجة للطلب")


# ============================================================
# 17. CAGR
# ============================================================
elif tool_choice == "📈 نمو المبيعات CAGR":
    page_header("📈", "حاسبة النمو CAGR")

    start = st.number_input("قيمة البداية", min_value=0.0, value=10000.0, step=1000.0)
    end = st.number_input("قيمة النهاية", min_value=0.0, value=25000.0, step=1000.0)
    years = st.number_input("السنوات", min_value=1, value=3, step=1)

    if start > 0:
        cagr = ((end / start) ** (1 / years) - 1) * 100
        total = ((end - start) / start) * 100

        c1, c2 = st.columns(2)
        c1.metric("CAGR", f"{cagr:.2f}%")
        c2.metric("النمو الإجمالي", f"{total:.2f}%")


# ============================================================
# 18. LTV / CAC
# ============================================================
elif tool_choice == "📊 حاسبة LTV / CAC":
    page_header("📊", "LTV / CAC")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    aov = st.number_input(f"متوسط الطلب ({currency})", min_value=0.0, value=150.0, step=10.0)
    margin = st.number_input("هامش (%)", min_value=0.0, value=40.0, step=1.0)
    orders = st.number_input("طلبات سنوياً", min_value=1, value=4, step=1)
    years = st.number_input("سنوات بقاء العميل", min_value=1, value=3, step=1)
    cac = st.number_input(f"CAC ({currency})", min_value=0.0, value=50.0, step=10.0)

    ltv = aov * (margin / 100) * orders * years
    ratio = ltv / cac if cac > 0 else 0

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
# 19. العمر
# ============================================================
elif tool_choice == "⏳ حاسبة العمر":
    page_header("⏳", "حاسبة العمر")

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

        c1, c2, c3 = st.columns(3)
        c1.metric("سنة", y)
        c2.metric("شهر", m)
        c3.metric("يوم", d)

        st.divider()
        c4, c5, c6 = st.columns(3)
        c4.metric("الأيام", f"{total_days:,}")
        c5.metric("الأسابيع", f"{total_weeks:,}")
        c6.metric("الأشهر", f"{y * 12 + m:,}")

        nb = datetime.date(today.year, dob.month, dob.day)
        if nb < today:
            nb = datetime.date(today.year + 1, dob.month, dob.day)
        dtb = (nb - today).days

        if dtb == 0:
            st.balloons()
            st.success("🎉 عيد ميلاد سعيد!")
        else:
            st.info(f"🎂 متبقي {dtb} يوماً لعيد ميلادك.")


# ============================================================
# 20. نقطة التعادل
# ============================================================
elif tool_choice == "📉 حاسبة نقطة التعادل":
    page_header("📉", "نقطة التعادل")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    fixed = st.number_input(f"ثابتة ({currency})", min_value=0.0, value=1000.0, step=100.0)
    var = st.number_input(f"تكلفة القطعة ({currency})", min_value=0.0, value=50.0, step=5.0)
    price = st.number_input(f"سعر البيع ({currency})", min_value=0.0, value=100.0, step=5.0)

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
# 21. VAT
# ============================================================
elif tool_choice == "🧾 حاسبة الضريبة VAT":
    page_header("🧾", "ضريبة القيمة المضافة")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    mode = st.radio("الطريقة:", ["إضافة", "استخراج"], horizontal=True)
    price = st.number_input(f"المبلغ ({currency})", min_value=0.0, value=1000.0, step=100.0)
    rate = st.number_input("النسبة (%)", min_value=0.0, value=15.0, step=1.0)

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
# 22. الكريبتو
# ============================================================
elif tool_choice == "📈 حاسبة أرباح الكريبتو":
    page_header("📈", "أرباح الكريبتو")

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

    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي", f"${money(gross)}")
    c2.metric("الرسوم", f"${money(fees)}")
    c3.metric("صافي", f"${money(net)}", delta=f"{roi:.2f}%" if net != 0 else None)


# ============================================================
# 23. إدارة المخاطر
# ============================================================
elif tool_choice == "🛡️ حاسبة إدارة المخاطر":
    page_header("🛡️", "إدارة المخاطر")

    capital = st.number_input("المحفظة (USDT)", min_value=0.0, value=1000.0, step=100.0)
    risk = st.number_input("المخاطرة (%)", min_value=0.0, value=2.0, step=0.5)

    col1, col2 = st.columns(2)
    with col1:
        entry_p = st.number_input("دخول", min_value=0.0, value=50000.0, step=100.0)
    with col2:
        stop = st.number_input("وقف", min_value=0.0, value=48000.0, step=100.0)

    risk_amt = capital * (risk / 100)

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
# 24. محول العملات (أسعار حية)
# ============================================================
elif tool_choice == "💱 محول العملات":
    page_header("💱", "محول العملات", "أسعار محدثة تلقائياً")

    with st.spinner("🌍 تحديث الأسعار..."):
        rates = fetch_currency_rates()

    col1, col2 = st.columns(2)
    with col1:
        fr = st.selectbox("من", list(rates.keys()), index=1)
    with col2:
        to = st.selectbox("إلى", list(rates.keys()), index=0)

    amt = st.number_input("المبلغ", min_value=0.0, value=100.0, step=10.0)

    usd = amt / rates[fr]
    result = usd * rates[to]

    st.metric("النتيجة", f"{money(result, '', 4)}")
    st.info(f"1 {fr} = {money(rates[to] / rates[fr], '', 4)} {to}")
    st.caption("✅ الأسعار تُحدّث تلقائياً كل ساعة | فشل الاتصال → قيم تقريبية")


# ============================================================
# 25. أيام العمل
# ============================================================
elif tool_choice == "🗓️ حاسبة أيام العمل":
    page_header("🗓️", "أيام العمل")

    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("من:", value=datetime.date.today())
    with col2:
        end = st.date_input("إلى:", value=datetime.date.today() + datetime.timedelta(days=30))

    exclude_fri = st.checkbox("استبعاد الجمعة", value=True)
    exclude_sat = st.checkbox("استبعاد السبت", value=False)
    exclude_sun = st.checkbox("استبعاد الأحد", value=False)

    holidays = st.text_input("عطلات رسمية (تواريخ مفصولة بفاصلة):", placeholder="2025-01-01, 2025-12-25")

    holiday_set = set()
    if holidays.strip():
        for h in holidays.split(","):
            try:
                holiday_set.add(datetime.datetime.strptime(h.strip(), "%Y-%m-%d").date())
            except ValueError:
                pass

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
# 26. أرقام الفواتير
# ============================================================
elif tool_choice == "📅 مولد أرقام الفواتير":
    page_header("📅", "مولد أرقام الفواتير")

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
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 تحميل", data=df.to_csv(index=False).encode("utf-8-sig"),
                          file_name="invoice_numbers.csv", mime="text/csv")


# ============================================================
# 27. QR Code
# ============================================================
elif tool_choice == "🔲 مولد QR Code":
    page_header("🔲", "مولد QR")

    content = st.text_area("المحتوى:", placeholder="https://example.com")

    col1, col2 = st.columns(2)
    with col1:
        size = st.number_input("الحجم:", min_value=100, max_value=1000, value=300, step=50)
    with col2:
        color = st.color_picker("اللون:", "#1e3c72")

    if st.button("✨ توليد QR"):
        if not content.strip():
            st.warning("أدخل محتوى.")
        elif not HAS_QR:
            st.error("مكتبة qrcode غير مثبتة.")
        else:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2)
            qr.add_data(content.strip())
            qr.make(fit=True)
            img = qr.make_image(fill_color=color, back_color="white")
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            st.image(buf, width=size)
            st.download_button("📥 تحميل PNG", data=buf.getvalue(), file_name="qrcode.png", mime="image/png")


# ============================================================
# 28. القوالب
# ============================================================
elif tool_choice == "📄 القوالب الجاهزة":
    page_header("📄", "قوالب جاهزة")

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
            "البند,الوصف,الكمية,السعر,الإجمالي\n"
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
# 29. الخصوصية
# ============================================================
elif tool_choice == "📜 سياسة الخصوصية":
    page_header("📜", "سياسة الخصوصية")

    st.info("🔒 جميع العمليات تُحسب محلياً في متصفحك.")

    st.subheader("📋 التزاماتنا:")
    st.markdown(
        "- ✅ لا نجمع بيانات شخصية.\n"
        "- ✅ لا نستخدم تتبع أو إعلانات.\n"
        "- ✅ البيانات مؤقتة وتُمسح بإغلاق الصفحة.\n"
    )

    st.subheader("⚠️ إخلاء المسؤولية:")
    st.warning("النتائج إرشادية فقط. راجع مختصاً مالياً.")

    st.divider()
    st.write("**📧 للتواصل:** admin@smart-merchant-tools.com")
