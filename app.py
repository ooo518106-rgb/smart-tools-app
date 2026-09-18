import streamlit as st
import datetime
import pandas as pd
import urllib.parse

try:
    from dateutil.relativedelta import relativedelta
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False

try:
    import qrcode
    from io import BytesIO
    HAS_QR = True
except ImportError:
    HAS_QR = False

st.set_page_config(
    page_title="أدوات التاجر الذكي",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

html, body {
    font-family: 'Cairo', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf5 100%);
}

footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

.main-title {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 50%, #00b4db 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 1.9rem;
    font-weight: 900;
    text-align: center;
    margin-bottom: 0.3rem;
    line-height: 1.4;
}

.sub-title {
    text-align: center;
    color: #5a6c8a;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

[data-testid="stMetric"] {
    background: #ffffff;
    padding: 14px 12px;
    border-radius: 12px;
    border-right: 4px solid #2a5298;
    box-shadow: 0 2px 10px rgba(30, 60, 114, 0.08);
}

[data-testid="stMetricLabel"] {
    color: #5a6c8a !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: #1e3c72 !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] .stRadio label {
    background: rgba(255, 255, 255, 0.08);
    padding: 8px 12px;
    border-radius: 10px;
    margin-bottom: 6px;
    cursor: pointer;
    display: block;
}

section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255, 255, 255, 0.18);
}

.stButton > button {
    background: linear-gradient(90deg, #2a5298 0%, #00b4db 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
    font-family: 'Cairo', sans-serif;
    width: 100%;
}

.stButton > button:hover {
    color: white;
    box-shadow: 0 6px 16px rgba(42, 82, 152, 0.3);
}

.stDownloadButton > button {
    background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    font-family: 'Cairo', sans-serif;
    width: 100%;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    border-radius: 10px !important;
    border: 2px solid #e0e6f0 !important;
    font-family: 'Cairo', sans-serif !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: #2a5298 !important;
}

.stAlert {
    border-radius: 12px !important;
    font-family: 'Cairo', sans-serif !important;
}

h1, h2, h3 {
    font-family: 'Cairo', sans-serif !important;
    color: #1e3c72 !important;
}

div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)


def fmt(n, decimals=2):
    if n is None:
        return "0.00"
    return f"{n:,.{decimals}f}"


def page_header(icon, title, subtitle=""):
    st.markdown(
        f'<div class="main-title">{icon} {title}</div>',
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(
            f'<div class="sub-title">{subtitle}</div>',
            unsafe_allow_html=True,
        )


CURRENCIES = ["ر.س", "د.إ", "د.ك", "ر.ع", "ج.م", "$", "€", "£"]

if "ecommerce_history" not in st.session_state:
    st.session_state.ecommerce_history = []

if "all_results" not in st.session_state:
    st.session_state.all_results = []


st.sidebar.markdown("### 💰 أدوات التاجر الذكي")
st.sidebar.markdown("---")

tool_choice = st.sidebar.radio(
    "القائمة:",
    [
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
        "📊 لوحة التقارير الموحدة",
        "📄 القوالب الجاهزة",
        "📜 سياسة الخصوصية",
    ],
)


# ==========================================
# 1. حاسبة التجارة الإلكترونية
# ==========================================
if tool_choice == "📦 حاسبة التجارة الإلكترونية":
    page_header("📦", "حاسبة أرباح التجارة الإلكترونية", "احسب هوامش الربح الصافية بعد خصم الشحن ورسوم الدفع")

    currency = st.selectbox("العملة", CURRENCIES, index=0)

    col1, col2 = st.columns(2)
    with col1:
        cost_price = st.number_input(f"تكلفة المنتج ({currency})", min_value=0.0, value=50.0, step=1.0)
        shipping_cost = st.number_input(f"تكلفة الشحن ({currency})", min_value=0.0, value=15.0, step=1.0)
    with col2:
        selling_price = st.number_input(f"سعر البيع ({currency})", min_value=0.0, value=150.0, step=1.0)
        gateway_fee_percent = st.number_input("رسوم بوابة الدفع (%)", min_value=0.0, value=2.2, step=0.1)

    fixed_fee = st.number_input(f"الرسوم الثابتة ({currency})", min_value=0.0, value=1.0, step=0.5)

    total_item_cost = cost_price + shipping_cost
    payment_gateway_fees = (selling_price * (gateway_fee_percent / 100)) + fixed_fee
    net_profit = selling_price - total_item_cost - payment_gateway_fees

    if selling_price > 0:
        margin = (net_profit / selling_price) * 100
    else:
        margin = 0

    st.divider()
    st.subheader("📊 ملخص الأرباح")

    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
    res_col1.metric("التكلفة الإجمالية", f"{fmt(total_item_cost)} {currency}")
    res_col2.metric("رسوم الدفع", f"{fmt(payment_gateway_fees)} {currency}")
    res_col3.metric("الربح الصافي", f"{fmt(net_profit)} {currency}", delta="ربح" if net_profit > 0 else "خسارة")
    res_col4.metric("هامش الربح", f"{margin:.1f}%")

    if net_profit <= 0:
        st.warning("⚠️ هذا المنتج لا يحقق ربحاً! راجع التسعير.")

    st.divider()
    st.subheader("💾 سجل الحسابات")

    product_name = st.text_input("اسم المنتج:", placeholder="مثال: سماعة بلوتوث")

    if st.button("➕ حفظ النتيجة في السجل"):
        if not product_name.strip():
            st.warning("يرجى إدخال اسم المنتج قبل الحفظ")
        else:
            record = {
                "اسم المنتج": product_name.strip(),
                "التكلفة الواصلة": round(total_item_cost, 2),
                "سعر البيع": round(selling_price, 2),
                "رسوم الدفع": round(payment_gateway_fees, 2),
                "الربح الصافي": round(net_profit, 2),
                "هامش الربح %": round(margin, 1),
                "العملة": currency,
            }
            st.session_state.ecommerce_history.append(record)
            result_entry = {"الأداة": "التجارة الإلكترونية", **record}
            st.session_state.all_results.append(result_entry)
            st.toast("تم الحفظ", icon="💾")
            st.rerun()

    if len(st.session_state.ecommerce_history) > 0:
        df_history = pd.DataFrame(st.session_state.ecommerce_history)
        st.dataframe(df_history, use_container_width=True)
        csv_data = df_history.to_csv(index=False).encode("utf-8-sig")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.download_button("📥 تحميل السجل (CSV)", data=csv_data, file_name="Ecommerce_Calculations.csv", mime="text/csv")
        with col_btn2:
            if st.button("🗑️ مسح السجل"):
                st.session_state.ecommerce_history = []
                st.rerun()


# ==========================================
# 2. رسوم تابي وتمارا
# ==========================================
elif tool_choice == "💳 رسوم تابي وتمارا":
    page_header("💳", "حاسبة رسوم الدفع الآجل", "احسب المبلغ الصافي بعد خصم رسوم التقسيط والضريبة")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    price = st.number_input(f"سعر المنتج ({currency})", min_value=0.0, value=100.0, step=1.0)

    col1, col2, col3 = st.columns(3)
    with col1:
        fee_percent = st.number_input("عمولة الشركة (%)", min_value=0.0, value=7.0, step=0.1)
    with col2:
        fixed_fee = st.number_input(f"رسوم ثابتة ({currency})", min_value=0.0, value=1.5, step=0.5)
    with col3:
        vat_on_fee = st.number_input("ضريبة القيمة المضافة (%)", min_value=0.0, value=15.0, step=1.0)

    fee_amount = (price * (fee_percent / 100)) + fixed_fee
    vat_amount = fee_amount * (vat_on_fee / 100)
    total_deduction = fee_amount + vat_amount
    net_to_merchant = price - total_deduction

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("رسوم الشركة", f"{fmt(fee_amount)} {currency}")
    c2.metric("الضريبة", f"{fmt(vat_amount)} {currency}")
    c3.metric("إجمالي الخصم", f"{fmt(total_deduction)} {currency}")

    st.success(f"💰 الصافي للتاجر: **{fmt(net_to_merchant)} {currency}**")


# ==========================================
# 3. عمولة المنصات (سلة/زد/شوبيفاي)
# ==========================================
elif tool_choice == "🏪 عمولة المنصات (سلة/زد)":
    page_header("🏪", "حاسبة عمولة المنصات", "سلة، زد، شوبيفاي - اعرف صافي أرباحك")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    platform = st.selectbox("المنصة", ["سلة", "زد", "شوبيفاي", "مخصصة"])

    default_commission = {"سلة": 2.0, "زد": 2.0, "شوبيفاي": 2.9, "مخصصة": 0.0}
    default_payment = {"سلة": 2.5, "زد": 2.5, "شوبيفاي": 2.9, "مخصصة": 0.0}

    selling_price = st.number_input(f"سعر البيع ({currency})", min_value=0.0, value=100.0, step=1.0)
    product_cost = st.number_input(f"تكلفة المنتج ({currency})", min_value=0.0, value=40.0, step=1.0)
    shipping = st.number_input(f"الشحن الذي يدفعه التاجر ({currency})", min_value=0.0, value=15.0, step=1.0)

    col1, col2 = st.columns(2)
    with col1:
        commission = st.number_input("عمولة المنصة (%)", min_value=0.0, value=default_commission[platform], step=0.1)
    with col2:
        payment_fee = st.number_input("رسوم بوابة الدفع (%)", min_value=0.0, value=default_payment[platform], step=0.1)

    payment_fixed = st.number_input(f"رسوم دفع ثابتة ({currency})", min_value=0.0, value=1.0, step=0.5)
    vat = st.number_input("ضريبة القيمة المضافة (%)", min_value=0.0, value=15.0, step=1.0)

    platform_fee = selling_price * (commission / 100)
    payment_amount = (selling_price * (payment_fee / 100)) + payment_fixed
    vat_amount = (platform_fee + payment_amount) * (vat / 100)
    total_deductions = platform_fee + payment_amount + vat_amount
    net_profit = selling_price - product_cost - shipping - total_deductions

    st.divider()
    st.subheader("📊 التفصيل")

    c1, c2, c3 = st.columns(3)
    c1.metric("عمولة المنصة", f"{fmt(platform_fee)} {currency}")
    c2.metric("رسوم الدفع", f"{fmt(payment_amount)} {currency}")
    c3.metric("الضريبة على الرسوم", f"{fmt(vat_amount)} {currency}")

    c4, c5, c6 = st.columns(3)
    c4.metric("إجمالي الخصومات", f"{fmt(total_deductions)} {currency}")
    c5.metric("صافي الإيراد", f"{fmt(selling_price - total_deductions)} {currency}")
    c6.metric("الربح الصافي", f"{fmt(net_profit)} {currency}", delta="ربح" if net_profit > 0 else "خسارة")

    if net_profit > 0:
        margin = (net_profit / selling_price) * 100
        st.success(f"✅ هامش الربح: **{margin:.1f}%**")
    else:
        st.error("⚠️ المنتج غير مربح على هذه المنصة!")


# ==========================================
# 4. حاسبة الإعلانات ROAS
# ==========================================
elif tool_choice == "📢 حاسبة الإعلانات ROAS":
    page_header("📢", "حاسبة الإعلانات", "ROAS, CPA, AOV - قيّم حملاتك بدقة")

    currency = st.selectbox("العملة", CURRENCIES, index=0)

    st.subheader("بيانات الحملة")
    ad_spend = st.number_input(f"إجمالي الإنفاق الإعلاني ({currency})", min_value=0.0, value=1000.0, step=100.0)

    col1, col2 = st.columns(2)
    with col1:
        orders_count = st.number_input("عدد الطلبات", min_value=1, value=50, step=1)
    with col2:
        avg_order_value = st.number_input(f"متوسط قيمة الطلب ({currency})", min_value=0.0, value=150.0, step=10.0)

    product_margin = st.number_input("هامش الربح على المنتج (%)", min_value=0.0, value=40.0, step=1.0)

    revenue = orders_count * avg_order_value
    roas = (revenue / ad_spend) if ad_spend > 0 else 0
    cpa = (ad_spend / orders_count) if orders_count > 0 else 0
    gross_profit = revenue * (product_margin / 100)
    net_profit = gross_profit - ad_spend
    break_even_roas = 100 / product_margin if product_margin > 0 else 0
    max_cpa = avg_order_value * (product_margin / 100)

    st.divider()
    st.subheader("📊 النتائج")

    c1, c2, c3 = st.columns(3)
    c1.metric("الإيراد", f"{fmt(revenue)} {currency}")
    c2.metric("ROAS", f"{roas:.2f}x")
    c3.metric("CPA (تكلفة الطلب)", f"{fmt(cpa)} {currency}")

    c4, c5, c6 = st.columns(3)
    c4.metric("الربح الإجمالي", f"{fmt(gross_profit)} {currency}")
    c5.metric("الربح الصافي", f"{fmt(net_profit)} {currency}", delta="ربح" if net_profit > 0 else "خسارة")
    c6.metric("أقصى CPA مقبول", f"{fmt(max_cpa)} {currency}")

    st.info(f"🎯 ROAS التعادل المطلوب: **{break_even_roas:.2f}x** — أي أقل من هذا خسارة")

    if roas < break_even_roas:
        st.error(f"⚠️ حملتك خاسرة! ROAS الحالي ({roas:.2f}x) أقل من التعادل ({break_even_roas:.2f}x)")
    elif roas < break_even_roas * 1.5:
        st.warning("⚡ الربح ضعيف، جرب تحسين الحملة.")
    else:
        st.success("🎉 حملة ناجحة ومربحة!")


# ==========================================
# 5. صانع روابط واتساب
# ==========================================
elif tool_choice == "💬 صانع روابط واتساب":
    page_header("💬", "صانع روابط واتساب", "رابط مباشر لبدء محادثة بضغطة زر")

    phone = st.text_input("رقم الجوال (مع رمز الدولة):", placeholder="مثال: 966500000000")
    msg = st.text_area("الرسالة (اختياري):", placeholder="مرحباً، أود الاستفسار...")

    if st.button("🔗 توليد الرابط"):
        clean_phone = "".join(filter(str.isdigit, phone))
        if clean_phone and len(clean_phone) >= 10:
            encoded_msg = urllib.parse.quote(msg)
            wa_link = f"https://wa.me/{clean_phone}?text={encoded_msg}"
            st.success("تم الإنشاء!")
            st.code(wa_link, language="")
            st.markdown(f"[📲 تجربة الرابط]({wa_link})")
        else:
            st.error("رقم غير صحيح (10 أرقام على الأقل).")


# ==========================================
# 6. حاسبة القروض والأقساط
# ==========================================
elif tool_choice == "🏦 حاسبة القروض والأقساط":
    page_header("🏦", "حاسبة القروض والأقساط", "احسب القسط الشهري بدقة")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    loan_amount = st.number_input(f"مبلغ القرض ({currency})", min_value=0.0, value=10000.0, step=100.0)

    col1, col2 = st.columns(2)
    with col1:
        interest_rate = st.number_input("الفائدة السنوية (%)", min_value=0.0, value=5.0, step=0.1)
    with col2:
        months = st.number_input("المدة (أشهر)", min_value=1, value=60, step=1)

    st.divider()

    if loan_amount <= 0:
        st.warning("⚠️ أدخل مبلغ قرض صحيح.")
    else:
        if interest_rate > 0:
            monthly_rate = (interest_rate / 100) / 12
            factor = (1 + monthly_rate) ** months
            monthly_payment = loan_amount * (monthly_rate * factor) / (factor - 1)
        else:
            monthly_payment = loan_amount / months

        total_paid = monthly_payment * months
        total_interest = total_paid - loan_amount

        c1, c2, c3 = st.columns(3)
        c1.metric("القسط الشهري", f"{fmt(monthly_payment)} {currency}")
        c2.metric("الفوائد", f"{fmt(total_interest)} {currency}")
        c3.metric("الإجمالي", f"{fmt(total_paid)} {currency}")


# ==========================================
# 7. القسط على البطاقة الائتمانية
# ==========================================
elif tool_choice == "💳 القسط على البطاقة الائتمانية":
    page_header("💳", "القسط على البطاقة الائتمانية", "اعرف مدة السداد وتكلفة الفوائد")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    balance = st.number_input(f"المبلغ المستحق ({currency})", min_value=0.0, value=5000.0, step=100.0)
    annual_rate = st.number_input("نسبة الفائدة السنوية (%)", min_value=0.0, value=24.0, step=0.5,
                                   help="عادة 20%-30% سنوياً على البطاقات الائتمانية")
    monthly_payment = st.number_input(f"الدفعة الشهرية ({currency})", min_value=1.0, value=300.0, step=50.0)

    st.divider()

    if monthly_payment <= balance * (annual_rate / 100 / 12):
        st.error("⚠️ الدفعة الشهرية أقل من الفائدة الشهرية! لن تسدد الدين أبداً.")
    else:
        monthly_rate = (annual_rate / 100) / 12
        remaining = balance
        total_interest = 0
        months = 0

        while remaining > 0 and months < 600:
            interest = remaining * monthly_rate
            principal = monthly_payment - interest
            if principal <= 0:
                break
            remaining -= principal
            total_interest += interest
            months += 1

        total_paid = balance + total_interest

        c1, c2, c3 = st.columns(3)
        c1.metric("المدة", f"{months} شهر")
        c2.metric("إجمالي الفوائد", f"{fmt(total_interest)} {currency}")
        c3.metric("إجمالي المسدد", f"{fmt(total_paid)} {currency}")

        st.warning(f"💡 ستدفع **{fmt(total_interest)} {currency}** فوائد إضافية. جرب زيادة الدفعة الشهرية لتوفير الفوائد.")


# ==========================================
# 8. حاسبة زكاة المال
# ==========================================
elif tool_choice == "🕋 حاسبة زكاة المال":
    page_header("🕋", "حاسبة زكاة المال", "احسب مقدار الزكاة 2.5%")

    nisab = st.number_input("قيمة النصاب (اختياري):", min_value=0.0, value=0.0, step=100.0)
    wealth = st.number_input("إجمالي المال:", min_value=0.0, value=10000.0, step=100.0)

    zakat_amount = wealth * 0.025
    st.divider()

    if nisab > 0 and wealth < nisab:
        st.warning("⚠️ مالك أقل من النصاب، لا زكاة.")
    else:
        st.metric("مقدار الزكاة", f"{fmt(zakat_amount)}")


# ==========================================
# 9. حاسبة الرواتب
# ==========================================
elif tool_choice == "💸 حاسبة الرواتب":
    page_header("💸", "حاسبة الرواتب", "احسب الراتب المستحق بدقة")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    basic_salary = st.number_input(f"الراتب الأساسي ({currency})", min_value=0.0, value=500.0, step=50.0)

    col1, col2 = st.columns(2)
    with col1:
        allowances = st.number_input(f"البدلات ({currency})", min_value=0.0, value=0.0, step=50.0)
    with col2:
        deductions = st.number_input(f"الخصومات ({currency})", min_value=0.0, value=0.0, step=50.0)

    net_salary = basic_salary + allowances - deductions
    st.divider()

    if net_salary < 0:
        st.error("⚠️ الخصومات تتجاوز الراتب!")
    else:
        st.metric("💰 الراتب المستحق", f"{fmt(net_salary)} {currency}")


# ==========================================
# 10. نهاية الخدمة والتأمينات
# ==========================================
elif tool_choice == "🛡️ نهاية الخدمة والتأمينات":
    page_header("🛡️", "نهاية الخدمة والتأمينات", "حساب مكافأة نهاية الخدمة وحصص التأمينات (السعودية)")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    salary = st.number_input(f"الراتب الأخير ({currency})", min_value=0.0, value=5000.0, step=100.0)

    col1, col2 = st.columns(2)
    with col1:
        years = st.number_input("سنوات الخدمة", min_value=0, value=5, step=1)
    with col2:
        months = st.number_input("أشهر إضافية", min_value=0, max_value=11, value=0, step=1)

    reason = st.radio("سبب إنهاء العلاقة:", ["استقالة", "إنهاء من صاحب العمل"], horizontal=True)
    nationality = st.radio("الجنسية:", ["سعودي", "غير سعودي"], horizontal=True)

    total_years = years + (months / 12)
    first_5 = min(total_years, 5)
    after_5 = max(total_years - 5, 0)

    gratuity = (first_5 * salary * 0.5) + (after_5 * salary * 1.0)

    if reason == "استقالة":
        if total_years < 2:
            gratuity = 0
        elif total_years < 5:
            gratuity = gratuity / 3
        elif total_years < 10:
            gratuity = gratuity * (2 / 3)

    st.divider()
    st.subheader("🛡️ التأمينات الاجتماعية (شهرياً)")

    if nationality == "سعودي":
        gosi_employee = salary * 0.0975
        gosi_employer = salary * 0.1175
    else:
        gosi_employee = 0
        gosi_employer = salary * 0.02

    c1, c2 = st.columns(2)
    c1.metric("حصة الموظف", f"{fmt(gosi_employee)} {currency}")
    c2.metric("حصة صاحب العمل", f"{fmt(gosi_employer)} {currency}")

    st.divider()
    st.subheader("💰 مكافأة نهاية الخدمة")

    st.metric("المكافأة المستحقة", f"{fmt(gratuity)} {currency}")
    st.info(f"📅 مدة الخدمة: **{years} سنة و {months} شهر** | السبب: **{reason}**")


# ==========================================
# 11. تكلفة الموظف الإجمالية
# ==========================================
elif tool_choice == "👥 تكلفة الموظف الإجمالية":
    page_header("👥", "تكلفة الموظف الإجمالية", "اعرف التكلفة الحقيقية للموظف سنوياً")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    salary = st.number_input(f"الراتب الأساسي ({currency})", min_value=0.0, value=5000.0, step=100.0)

    col1, col2 = st.columns(2)
    with col1:
        housing = st.number_input(f"بدل السكن ({currency})", min_value=0.0, value=1250.0, step=100.0)
        transport = st.number_input(f"بدل المواصلات ({currency})", min_value=0.0, value=500.0, step=50.0)
    with col2:
        other_allowances = st.number_input(f"بدلات أخرى ({currency})", min_value=0.0, value=0.0, step=100.0)
        annual_bonus = st.number_input(f"مكافآت سنوية ({currency})", min_value=0.0, value=0.0, step=500.0)

    nationality = st.radio("الجنسية:", ["سعودي", "غير سعودي"], horizontal=True)
    vacation_days = st.number_input("أيام الإجازة السنوية", min_value=0, value=21, step=1)

    total_salary = salary + housing + transport + other_allowances
    gosi_employer = total_salary * 0.1175 if nationality == "سعودي" else total_salary * 0.02

    monthly_cost = total_salary + gosi_employer
    annual_cost = (monthly_cost * 12) + annual_bonus

    daily_cost = total_salary / 30
    vacation_cost = daily_cost * vacation_days

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("التكلفة الشهرية", f"{fmt(monthly_cost)} {currency}")
    c2.metric("التكلفة السنوية", f"{fmt(annual_cost)} {currency}")
    c3.metric("تكلفة الإجازات", f"{fmt(vacation_cost)} {currency}")

    st.info(f"💡 التكلفة اليومية الفعلية: **{fmt(annual_cost / 365)} {currency}**")


# ==========================================
# 12. حاسبة الدوام الدقيقة
# ==========================================
elif tool_choice == "📅 حاسبة الدوام الدقيقة":
    page_header("📅", "حاسبة الدوام والراتب", "احسب راتبك حسب الساعات الفعلية")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    monthly_salary = st.number_input(f"الراتب الشهري ({currency})", min_value=0.0, value=500.0, step=50.0)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("تاريخ البداية:", value=datetime.date.today().replace(day=1))
        start_time = st.time_input("وقت البداية:", value=datetime.time(8, 0, 0))
    with col2:
        end_date = st.date_input("تاريخ النهاية:", value=datetime.date.today())
        end_time = st.time_input("وقت النهاية:", value=datetime.time(16, 0, 0))

    start_datetime = datetime.datetime.combine(start_date, start_time)
    end_datetime = datetime.datetime.combine(end_date, end_time)

    if start_datetime < end_datetime:
        time_diff = end_datetime - start_datetime
        total_seconds = time_diff.total_seconds()
        days = time_diff.days
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        total_month_seconds = 30 * 24 * 3600
        earned_salary = (total_seconds / total_month_seconds) * monthly_salary

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("أيام", days)
        c2.metric("ساعات", hours)
        c3.metric("دقائق", minutes)
        c4.metric("ثواني", seconds)
        st.success(f"💰 الراتب: **{fmt(earned_salary)} {currency}**")
    else:
        st.error("⚠️ تاريخ النهاية يجب أن يكون بعد البداية!")


# ==========================================
# 13. توزيع مصاريف الشحن
# ==========================================
elif tool_choice == "⚖️ توزيع مصاريف الشحن":
    page_header("⚖️", "توزيع مصاريف الشحن", "وزّع المصاريف على الأصناف بعدالة")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    total_invoice = st.number_input(f"إجمالي الفاتورة ({currency})", min_value=0.01, value=1000.0, step=100.0)
    total_expenses = st.number_input(f"إجمالي الشحن ({currency})", min_value=0.0, value=200.0, step=10.0)
    item_price = st.number_input(f"سعر الصنف ({currency})", min_value=0.0, value=50.0, step=10.0)

    if total_invoice > 0:
        expense_ratio = total_expenses / total_invoice
        item_expense = item_price * expense_ratio
        c1, c2, c3 = st.columns(3)
        c1.metric("نسبة المصاريف", f"{expense_ratio * 100:.2f}%")
        c2.metric("نصيب القطعة", f"{fmt(item_expense)} {currency}")
        c3.metric("التكلفة النهائية", f"{fmt(item_price + item_expense)} {currency}")


# ==========================================
# 14. حاسبة الخصومات
# ==========================================
elif tool_choice == "🏷️ حاسبة الخصومات":
    page_header("🏷️", "حاسبة الخصومات", "احسب السعر النهائي بعد الخصم")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    price_before = st.number_input(f"السعر الأساسي ({currency})", min_value=0.0, value=100.0, step=10.0)

    discount_type = st.radio("نوع الخصم:", ["نسبة مئوية (%)", "مبلغ ثابت"], horizontal=True)

    if discount_type == "نسبة مئوية (%)":
        disc_percent = st.number_input("نسبة الخصم (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)
        disc_amount = price_before * (disc_percent / 100)
    else:
        disc_amount = st.number_input(f"مبلغ الخصم ({currency})", min_value=0.0, max_value=price_before, value=20.0, step=5.0)

    c1, c2 = st.columns(2)
    c1.metric("التوفير", f"{fmt(disc_amount)} {currency}")
    c2.metric("السعر النهائي", f"{fmt(price_before - disc_amount)} {currency}")


# ==========================================
# 15. حاسبة العروض الترويجية
# ==========================================
elif tool_choice == "🎁 حاسبة العروض الترويجية":
    page_header("🎁", "حاسبة العروض الترويجية", "هل عرضك مربح؟ احسبه بدقة")

    currency = st.selectbox("العملة", CURRENCIES, index=0)

    offer_type = st.selectbox("نوع العرض", [
        "اشترِ X واحصل على Y",
        "خصم على الثاني",
        "خصم على الكمية",
        "منتج مجاني",
    ])

    unit_cost = st.number_input(f"تكلفة القطعة ({currency})", min_value=0.0, value=40.0, step=5.0)
    unit_price = st.number_input(f"سعر بيع القطعة ({currency})", min_value=0.0, value=100.0, step=5.0)

    st.divider()

    if offer_type == "اشترِ X واحصل على Y":
        buy = st.number_input("اشترِ", min_value=1, value=2, step=1)
        free = st.number_input("احصل مجاناً على", min_value=1, value=1, step=1)

        total_units = buy + free
        revenue = unit_price * buy
        cost = unit_cost * total_units
        profit = revenue - cost
        effective_discount = (free / total_units) * 100

        c1, c2, c3 = st.columns(3)
        c1.metric("الإيراد", f"{fmt(revenue)} {currency}")
        c2.metric("التكلفة", f"{fmt(cost)} {currency}")
        c3.metric("الربح", f"{fmt(profit)} {currency}", delta="ربح" if profit > 0 else "خسارة")

        st.info(f"📊 قيمة الخصم الفعلية: **{effective_discount:.1f}%**")

    elif offer_type == "خصم على الثاني":
        second_discount = st.number_input("نسبة الخصم على الثاني (%)", min_value=0.0, max_value=100.0, value=50.0, step=5.0)

        revenue = unit_price + (unit_price * (1 - second_discount / 100))
        cost = unit_cost * 2
        profit = revenue - cost

        c1, c2, c3 = st.columns(3)
        c1.metric("الإيراد", f"{fmt(revenue)} {currency}")
        c2.metric("التكلفة", f"{fmt(cost)} {currency}")
        c3.metric("الربح", f"{fmt(profit)} {currency}", delta="ربح" if profit > 0 else "خسارة")

        effective_discount = (second_discount / 2)
        st.info(f"📊 قيمة الخصم الفعلية: **{effective_discount:.1f}%**")

    elif offer_type == "خصم على الكمية":
        qty = st.number_input("الكمية المطلوبة", min_value=2, value=3, step=1)
        discount_percent = st.number_input("نسبة الخصم (%)", min_value=0.0, max_value=100.0, value=15.0, step=1.0)

        revenue = unit_price * qty * (1 - discount_percent / 100)
        cost = unit_cost * qty
        profit = revenue - cost

        c1, c2, c3 = st.columns(3)
        c1.metric("الإيراد", f"{fmt(revenue)} {currency}")
        c2.metric("التكلفة", f"{fmt(cost)} {currency}")
        c3.metric("الربح", f"{fmt(profit)} {currency}", delta="ربح" if profit > 0 else "خسارة")

    else:
        free_count = st.number_input("عدد المنتجات المجانية", min_value=1, value=1, step=1)
        paid_count = st.number_input("عدد المنتجات المدفوعة", min_value=1, value=1, step=1)

        revenue = unit_price * paid_count
        cost = unit_cost * (paid_count + free_count)
        profit = revenue - cost

        c1, c2, c3 = st.columns(3)
        c1.metric("الإيراد", f"{fmt(revenue)} {currency}")
        c2.metric("التكلفة", f"{fmt(cost)} {currency}")
        c3.metric("الربح", f"{fmt(profit)} {currency}", delta="ربح" if profit > 0 else "خسارة")


# ==========================================
# 16. نقطة إعادة الطلب
# ==========================================
elif tool_choice == "📦 نقطة إعادة الطلب":
    page_header("📦", "حاسبة نقطة إعادة الطلب", "متى يجب أن أطلب مخزوناً جديداً؟")

    avg_daily_sales = st.number_input("متوسط البيع اليومي (قطعة)", min_value=0.0, value=10.0, step=1.0)
    lead_time_days = st.number_input("مدة التوريد (أيام)", min_value=0, value=7, step=1)
    safety_stock = st.number_input("مخزون الأمان (قطعة)", min_value=0, value=20, step=5)
    current_stock = st.number_input("المخزون الحالي (قطعة)", min_value=0, value=100, step=10)

    reorder_point = (avg_daily_sales * lead_time_days) + safety_stock
    daily_consumption = avg_daily_sales if avg_daily_sales > 0 else 1
    days_until_stockout = current_stock / daily_consumption

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("نقطة إعادة الطلب", f"{reorder_point:,.0f} قطعة")
    c2.metric("الأيام حتى النفاذ", f"{days_until_stockout:.1f} يوم")
    c3.metric("المخزون الحالي", f"{current_stock} قطعة")

    if current_stock <= reorder_point:
        st.error(f"🚨 يجب أن تطلب مخزوناً الآن! المخزون ({current_stock}) أقل من نقطة الطلب ({reorder_point:.0f})")
    else:
        remaining = current_stock - reorder_point
        st.success(f"✅ المخزون جيد. متبقي **{remaining}** قطعة قبل الحاجة للطلب.")
        st.info(f"📅 اطلب بعد **{(remaining / daily_consumption):.1f}** يوم")


# ==========================================
# 17. نمو المبيعات CAGR
# ==========================================
elif tool_choice == "📈 نمو المبيعات CAGR":
    page_header("📈", "حاسبة نمو المبيعات", "نسبة النمو السنوية المركبة")

    start_value = st.number_input("قيمة البداية", min_value=0.0, value=10000.0, step=1000.0)
    end_value = st.number_input("قيمة النهاية", min_value=0.0, value=25000.0, step=1000.0)
    years = st.number_input("عدد السنوات", min_value=1, value=3, step=1)

    st.divider()

    if start_value <= 0 or years <= 0:
        st.warning("⚠️ أدخل قيماً صحيحة.")
    else:
        cagr = ((end_value / start_value) ** (1 / years) - 1) * 100
        total_growth = ((end_value - start_value) / start_value) * 100

        c1, c2, c3 = st.columns(3)
        c1.metric("النمو السنوي CAGR", f"{cagr:.2f}%")
        c2.metric("النمو الإجمالي", f"{total_growth:.2f}%")
        c3.metric("الفرق", f"{fmt(end_value - start_value)}")

        if cagr > 0:
            st.success(f"📈 نمو إيجابي بمعدل **{cagr:.2f}%** سنوياً")
        else:
            st.error(f"📉 انخفاض بمعدل **{cagr:.2f}%** سنوياً")


# ==========================================
# 18. LTV / CAC
# ==========================================
elif tool_choice == "📊 حاسبة LTV / CAC":
    page_header("📊", "حاسبة LTV / CAC", "قيمة العميل مدى الحياة مقابل تكلفة اكتسابه")

    currency = st.selectbox("العملة", CURRENCIES, index=0)

    avg_order = st.number_input(f"متوسط قيمة الطلب ({currency})", min_value=0.0, value=150.0, step=10.0)
    margin_percent = st.number_input("هامش الربح (%)", min_value=0.0, value=40.0, step=1.0)
    orders_per_year = st.number_input("عدد الطلبات سنوياً", min_value=1, value=4, step=1)
    customer_years = st.number_input("عدد سنوات بقاء العميل", min_value=1, value=3, step=1)
    marketing_cost = st.number_input(f"تكلفة التسويق لاكتساب عميل ({currency})", min_value=0.0, value=50.0, step=10.0)

    ltv = avg_order * (margin_percent / 100) * orders_per_year * customer_years
    ratio = ltv / marketing_cost if marketing_cost > 0 else 0

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("LTV", f"{fmt(ltv)} {currency}")
    c2.metric("CAC", f"{fmt(marketing_cost)} {currency}")
    c3.metric("LTV / CAC", f"{ratio:.2f}x")

    if ratio >= 3:
        st.success(f"✅ نسبة ممتازة! كل ريال تسويق يعود بـ **{ratio:.2f}**")
    elif ratio >= 1:
        st.warning(f"⚡ نسبة مقبولة، لكن الأفضل أن تكون 3x على الأقل.")
    else:
        st.error("🚨 تخسر في التسويق! LTV أقل من CAC.")


# ==========================================
# 19. حاسبة العمر
# ==========================================
elif tool_choice == "⏳ حاسبة العمر":
    page_header("⏳", "حاسبة العمر الدقيقة", "احسب عمرك بالسنوات والأيام")

    today = datetime.date.today()
    dob = st.date_input(
        "تاريخ الميلاد:",
        value=datetime.date(2000, 1, 1),
        min_value=datetime.date(1900, 1, 1),
        max_value=today,
    )

    if dob > today:
        st.error("⚠️ تاريخ الميلاد في المستقبل.")
    else:
        total_days = (today - dob).days
        total_weeks = total_days // 7

        if HAS_DATEUTIL:
            diff = relativedelta(today, dob)
            years = diff.years
            months = diff.months
            days = diff.days
        else:
            years = today.year - dob.year
            months = today.month - dob.month
            days = today.day - dob.day
            if days < 0:
                months -= 1
                prev_month = today.month - 1 if today.month > 1 else 12
                prev_year = today.year if today.month > 1 else today.year - 1
                days_in_prev = (
                    datetime.date(prev_year, prev_month + 1, 1)
                    - datetime.date(prev_year, prev_month, 1)
                ).days
                days += days_in_prev
            if months < 0:
                years -= 1
                months += 12

        total_months = years * 12 + months
        next_birthday = datetime.date(today.year, dob.month, dob.day)
        if next_birthday < today:
            next_birthday = datetime.date(today.year + 1, dob.month, dob.day)
        days_to_birthday = (next_birthday - today).days

        c1, c2, c3 = st.columns(3)
        c1.metric("سنة", years)
        c2.metric("شهر", months)
        c3.metric("يوم", days)

        st.divider()
        st.subheader("📊 تفاصيل إضافية")

        c4, c5, c6 = st.columns(3)
        c4.metric("إجمالي الأيام", f"{total_days:,}")
        c5.metric("إجمالي الأسابيع", f"{total_weeks:,}")
        c6.metric("إجمالي الأشهر", f"{total_months:,}")

        if days_to_birthday == 0:
            st.balloons()
            st.success("🎉 عيد ميلاد سعيد!")
        else:
            st.info(f"🎂 متبقي **{days_to_birthday}** يوماً لعيد ميلادك.")


# ==========================================
# 20. نقطة التعادل
# ==========================================
elif tool_choice == "📉 حاسبة نقطة التعادل":
    page_header("📉", "حاسبة نقطة التعادل", "اعرف عدد القطع لتغطية التكاليف")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    fixed_costs = st.number_input(f"المصاريف الثابتة ({currency})", min_value=0.0, value=1000.0, step=100.0)
    variable_cost = st.number_input(f"تكلفة القطعة ({currency})", min_value=0.0, value=50.0, step=5.0)
    sell_price = st.number_input(f"سعر البيع ({currency})", min_value=0.0, value=100.0, step=5.0)

    if sell_price <= variable_cost:
        st.error("⚠️ سعر البيع يجب أن يكون أعلى من التكلفة.")
    else:
        contribution_margin = sell_price - variable_cost
        break_even_units = fixed_costs / contribution_margin
        break_even_revenue = break_even_units * sell_price

        c1, c2, c3 = st.columns(3)
        c1.metric("القطع للتعادل", f"{break_even_units:,.0f}")
        c2.metric("إيراد التعادل", f"{fmt(break_even_revenue)} {currency}")
        c3.metric("هامش المساهمة", f"{fmt(contribution_margin)} {currency}")


# ==========================================
# 21. الضريبة VAT
# ==========================================
elif tool_choice == "🧾 حاسبة الضريبة VAT":
    page_header("🧾", "حاسبة ضريبة القيمة المضافة", "أضف أو استخرج الضريبة")

    currency = st.selectbox("العملة", CURRENCIES, index=0)
    calc_mode = st.radio("طريقة الحساب:", ["إضافة الضريبة", "استخراج الضريبة"], horizontal=True)
    price = st.number_input(f"المبلغ ({currency})", min_value=0.0, value=1000.0, step=100.0)
    vat_rate = st.number_input("نسبة الضريبة (%)", min_value=0.0, value=15.0, step=1.0)

    st.divider()

    if calc_mode == "إضافة الضريبة":
        vat_amount = price * (vat_rate / 100)
        total = price + vat_amount
        c1, c2 = st.columns(2)
        c1.metric("الضريبة", f"{fmt(vat_amount)} {currency}")
        c2.metric("السعر مع الضريبة", f"{fmt(total)} {currency}")
    else:
        base_price = price / (1 + vat_rate / 100)
        vat_amount = price - base_price
        c1, c2 = st.columns(2)
        c1.metric("قبل الضريبة", f"{fmt(base_price)} {currency}")
        c2.metric("الضريبة", f"{fmt(vat_amount)} {currency}")


# ==========================================
# 22. أرباح الكريبتو
# ==========================================
elif tool_choice == "📈 حاسبة أرباح الكريبتو":
    page_header("📈", "حاسبة أرباح الكريبتو", "احسب صافي ربحك بعد الرسوم")

    entry_price = st.number_input("سعر الدخول ($)", min_value=0.0, value=60000.0, step=100.0)
    amount = st.number_input("الكمية", min_value=0.0, value=0.1, step=0.01, format="%.4f")
    exit_price = st.number_input("سعر الخروج ($)", min_value=0.0, value=62000.0, step=100.0)
    fee = st.number_input("رسوم المنصة (%)", min_value=0.0, value=0.1, step=0.05)

    entry_value = entry_price * amount
    exit_value = exit_price * amount
    gross_profit = exit_value - entry_value
    fees_total = (entry_value + exit_value) * (fee / 100)
    net_profit = gross_profit - fees_total

    if entry_value > 0:
        roi = (net_profit / entry_value) * 100
    else:
        roi = 0

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("الربح الإجمالي", f"${fmt(gross_profit)}")
    c2.metric("الرسوم", f"${fmt(fees_total)}")
    c3.metric("الربح الصافي", f"${fmt(net_profit)}", delta=f"{roi:.2f}%" if net_profit != 0 else None)


# ==========================================
# 23. إدارة المخاطر
# ==========================================
elif tool_choice == "🛡️ حاسبة إدارة المخاطر":
    page_header("🛡️", "حاسبة إدارة المخاطر", "حدد حجم الصفقة المناسب")

    capital = st.number_input("حجم المحفظة (USDT)", min_value=0.0, value=1000.0, step=100.0)
    risk_percent = st.number_input("المخاطرة (%)", min_value=0.0, value=2.0, step=0.5)

    col_x, col_y = st.columns(2)
    with col_x:
        entry_p = st.number_input("سعر الدخول", min_value=0.0, value=50000.0, step=100.0)
    with col_y:
        stop_loss = st.number_input("وقف الخسارة", min_value=0.0, value=48000.0, step=100.0)

    risk_amount = capital * (risk_percent / 100)

    if entry_p <= 0 or stop_loss <= 0:
        st.warning("⚠️ أدخل أسعاراً صحيحة.")
    elif entry_p == stop_loss:
        st.error("⚠️ سعر الدخول = وقف الخسارة!")
    else:
        price_diff = abs(entry_p - stop_loss)
        position_size = risk_amount / price_diff
        position_value = position_size * entry_p

        p1, p2, p3 = st.columns(3)
        p1.metric("المبلغ المخاطر به", f"{fmt(risk_amount)} USDT")
        p2.metric("الكمية", f"{position_size:.6f}")
        p3.metric("حجم الصفقة", f"{fmt(position_value)} USDT")


# ==========================================
# 24. محول العملات
# ==========================================
elif tool_choice == "💱 محول العملات":
    page_header("💱", "محول العملات", "أسعار تقريبية - راجع البنك للأسعار المحدثة")

    # أسعار تقريبية مقابل 1 دولار أمريكي
    rates = {
        "USD ($)": 1.0,
        "SAR (ر.س)": 3.75,
        "AED (د.إ)": 3.67,
        "KWD (د.ك)": 0.31,
        "OMR (ر.ع)": 0.385,
        "EGP (ج.م)": 48.5,
        "EUR (€)": 0.92,
        "GBP (£)": 0.79,
        "QAR (ر.ق)": 3.64,
        "BHD (د.ب)": 0.376,
    }

    col1, col2 = st.columns(2)
    with col1:
        from_cur = st.selectbox("من", list(rates.keys()), index=1)
    with col2:
        to_cur = st.selectbox("إلى", list(rates.keys()), index=0)

    amount = st.number_input("المبلغ", min_value=0.0, value=100.0, step=10.0)

    usd_amount = amount / rates[from_cur]
    result = usd_amount * rates[to_cur]

    st.divider()
    st.metric("النتيجة", f"{fmt(result, 4)}", delta=f"{from_cur.split()[0]} → {to_cur.split()[0]}")

    st.info(f"💡 1 {from_cur.split()[0]} = {fmt(rates[to_cur] / rates[from_cur], 4)} {to_cur.split()[0]}")
    st.caption("⚠️ الأسعار تقريبية وقد تختلف عن أسعار البنوك. حدّثها يدوياً إذا لزم.")


# ==========================================
# 25. حاسبة أيام العمل
# ==========================================
elif tool_choice == "🗓️ حاسبة أيام العمل":
    page_header("🗓️", "حاسبة أيام العمل", "احسب أيام العمل الفعلية بين تاريخين")

    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("من تاريخ:", value=datetime.date.today())
    with col2:
        end = st.date_input("إلى تاريخ:", value=datetime.date.today() + datetime.timedelta(days=30))

    exclude_friday = st.checkbox("استبعاد أيام الجمعة", value=True)
    exclude_saturday = st.checkbox("استبعاد أيام السبت", value=False)
    exclude_sunday = st.checkbox("استبعاد أيام الأحد", value=False)

    official_holidays = st.number_input("أيام العطل الرسمية", min_value=0, value=0, step=1)

    if start <= end:
        total_days = (end - start).days + 1
        work_days = 0
        current = start

        while current <= end:
            weekday = current.weekday()  # 0=Mon ... 4=Fri, 5=Sat, 6=Sun
            skip = False
            if exclude_friday and weekday == 4:
                skip = True
            if exclude_saturday and weekday == 5:
                skip = True
            if exclude_sunday and weekday == 6:
                skip = True
            if not skip:
                work_days += 1
            current += datetime.timedelta(days=1)

        work_days = max(work_days - official_holidays, 0)

        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي الأيام", total_days)
        c2.metric("أيام العمل", work_days)
        c3.metric("أيام الراحة", total_days - work_days)

        st.info(f"📅 من **{start}** إلى **{end}**")
    else:
        st.error("⚠️ تاريخ النهاية يجب أن يكون بعد البداية.")


# ==========================================
# 26. مولد أرقام الفواتير
# ==========================================
elif tool_choice == "📅 مولد أرقام الفواتير":
    page_header("📅", "مولد أرقام الفواتير", "أنشئ أرقام فواتير تلقائية متسلسلة")

    prefix = st.text_input("البادئة (Prefix):", value="INV")
    year = st.number_input("السنة:", min_value=2000, max_value=2100, value=datetime.date.today().year, step=1)
    separator = st.selectbox("الفاصل:", ["-", "/", "_", "."], index=0)

    col1, col2 = st.columns(2)
    with col1:
        start_num = st.number_input("ابدأ من الرقم:", min_value=1, value=1, step=1)
    with col2:
        padding = st.number_input("عدد الخانات", min_value=1, max_value=10, value=4, step=1)

    count = st.number_input("عدد الفواتير المطلوب توليدها:", min_value=1, max_value=500, value=10, step=1)

    if st.button("🔢 توليد الأرقام"):
        numbers = []
        for i in range(count):
            num = start_num + i
            formatted = f"{prefix}{separator}{year}{separator}{num:0{padding}d}"
            numbers.append(formatted)

        df = pd.DataFrame({"رقم الفاتورة": numbers})
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 تحميل (CSV)", data=csv, file_name="invoice_numbers.csv", mime="text/csv")


# ==========================================
# 27. مولد QR Code
# ==========================================
elif tool_choice == "🔲 مولد QR Code":
    page_header("🔲", "مولد QR Code", "أنشئ رمز QR لأي رابط أو نص")

    content = st.text_area(
        "المحتوى (رابط، رقم، نص):",
        placeholder="https://example.com أو 966500000000",
    )

    col1, col2 = st.columns(2)
    with col1:
        size = st.number_input("الحجم (بكسل):", min_value=100, max_value=1000, value=300, step=50)
    with col2:
        fill_color = st.color_picker("لون الرمز:", "#1e3c72")

    if st.button("✨ توليد QR"):
        if not content.strip():
            st.warning("⚠️ أدخل محتوى أولاً.")
        elif not HAS_QR:
            st.error("⚠️ مكتبة qrcode غير مثبتة. أضف `qrcode[pil]` إلى requirements.txt")
        else:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=2,
            )
            qr.add_data(content.strip())
            qr.make(fit=True)

            img = qr.make_image(fill_color=fill_color, back_color="white")

            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)

            st.image(buf, caption="رمز QR", width=size)

            st.download_button(
                "📥 تحميل QR (PNG)",
                data=buf.getvalue(),
                file_name="qrcode.png",
                mime="image/png",
            )


# ==========================================
# 28. لوحة التقارير
# ==========================================
elif tool_choice == "📊 لوحة التقارير الموحدة":
    page_header("📊", "لوحة التقارير الموحدة", "جميع النتائج المحفوظة في مكان واحد")

    if len(st.session_state.all_results) == 0:
        st.info("ℹ️ لا توجد نتائج محفوظة بعد.")
    else:
        df_all = pd.DataFrame(st.session_state.all_results)
        st.dataframe(df_all, use_container_width=True)
        csv_all = df_all.to_csv(index=False).encode("utf-8-sig")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 تحميل التقرير (CSV)", data=csv_all, file_name="Full_Report.csv", mime="text/csv")
        with col2:
            if st.button("🗑️ مسح الكل"):
                st.session_state.all_results = []
                st.session_state.ecommerce_history = []
                st.rerun()


# ==========================================
# 29. القوالب الجاهزة
# ==========================================
elif tool_choice == "📄 القوالب الجاهزة":
    page_header("📄", "قوالب محاسبية وتجارية", "قوالب CSV جاهزة للفتح في Excel")

    with st.expander("📒 دفتر أستاذ الموردين", expanded=True):
        suppliers_csv = (
            "التاريخ,المورد,الفاتورة,البيان,مدين,دائن,الرصيد\n"
            "2025-01-01,مورد أ,INV-001,شراء,1000.00,,1000.00\n"
            "2025-01-05,مورد أ,PAY-001,سداد,,500.00,500.00\n"
            "2025-01-10,مورد ب,INV-002,شراء,750.00,,1250.00\n"
            ",,الإجمالي,,1750.00,500.00,1250.00\n"
        ).encode("utf-8-sig")
        st.download_button("📥 تحميل القالب", data=suppliers_csv, file_name="suppliers_ledger.csv", mime="text/csv", key="dl_suppliers")

    with st.expander("📦 جرد المخزون"):
        inventory_csv = (
            "الكود,الصنف,الوحدة,دفتر,فعلي,الفرق,التكلفة,القيمة\n"
            "SKU-001,سماعة,قطعة,100,98,-2,50.00,4900.00\n"
            "SKU-002,شاحن,قطعة,200,200,0,25.00,5000.00\n"
            "SKU-003,كابل,قطعة,500,495,-5,8.00,3960.00\n"
            ",,الإجمالي,,,,-,13860.00\n"
        ).encode("utf-8-sig")
        st.download_button("📥 تحميل القالب", data=inventory_csv, file_name="inventory_template.csv", mime="text/csv", key="dl_inventory")

    with st.expander("🧾 فاتورة مبيعات"):
        invoice_csv = (
            "بند,الوصف,الكمية,السعر,الإجمالي,الضريبة,الإجمالي مع الضريبة\n"
            "1,منتج أ,2,100.00,200.00,30.00,230.00\n"
            "2,منتج ب,1,150.00,150.00,22.50,172.50\n"
            "3,تركيب,1,50.00,50.00,7.50,57.50\n"
            ",الإجمالي,,,400.00,60.00,460.00\n"
        ).encode("utf-8-sig")
        st.download_button("📥 تحميل القالب", data=invoice_csv, file_name="sales_invoice.csv", mime="text/csv", key="dl_invoice")

    with st.expander("💸 سجل المصروفات"):
        expenses_csv = (
            "التاريخ,البند,الوصف,المبلغ,الدفع\n"
            "2025-01-01,إيجار,المكتب,3000.00,تحويل\n"
            "2025-01-03,رواتب,الفريق,15000.00,تحويل\n"
            "2025-01-05,شحن,عملاء,450.00,بطاقة\n"
            "2025-01-10,تسويق,إعلانات,1200.00,بطاقة\n"
            ",الإجمالي,,19650.00,\n"
        ).encode("utf-8-sig")
        st.download_button("📥 تحميل القالب", data=expenses_csv, file_name="expenses_log.csv", mime="text/csv", key="dl_expenses")

    with st.expander("💰 تسعير المنتجات"):
        pricing_csv = (
            "المنتج,التكلفة,الشحن,الرسوم,هامش %,السعر,الربح\n"
            "سماعة,50.00,15.00,4.30,40,140.00,70.70\n"
            "شاحن,25.00,10.00,2.50,50,90.00,52.50\n"
            "كابل,8.00,5.00,1.20,60,40.00,25.80\n"
        ).encode("utf-8-sig")
        st.download_button("📥 تحميل القالب", data=pricing_csv, file_name="pricing_template.csv", mime="text/csv", key="dl_pricing")

    with st.expander("📝 عرض سعر"):
        quote_csv = (
            "البند,الوصف,الكمية,السعر,الإجمالي\n"
            "1,منتج أ,5,100.00,500.00\n"
            "2,منتج ب,3,150.00,450.00\n"
            "3,خصم خاص,,,-50.00\n"
            ",الإجمالي قبل الضريبة,,,900.00\n"
            ",ضريبة 15%,,,135.00\n"
            ",الإجمالي النهائي,,,1035.00\n"
        ).encode("utf-8-sig")
        st.download_button("📥 تحميل القالب", data=quote_csv, file_name="quotation.csv", mime="text/csv", key="dl_quote")

    st.divider()
    st.info("💡 افتح ملفات CSV في Excel مباشرة.")


# ==========================================
# 30. الخصوصية
# ==========================================
elif tool_choice == "📜 سياسة الخصوصية":
    page_header("📜", "سياسة الخصوصية", "التزاماتنا تجاهك")

    st.info("🔒 جميع العمليات تُحسب محلياً في متصفحك.")

    st.subheader("📋 التزاماتنا:")
    st.markdown(
        "- ✅ لا نجمع بيانات شخصية.\n"
        "- ✅ لا نستخدم تتبع أو إعلانات.\n"
        "- ✅ البيانات مؤقتة وتُمسح بإغلاق الصفحة.\n"
        "- ✅ الأداة للأغراض التعليمية.\n"
    )

    st.subheader("⚠️ إخلاء المسؤولية:")
    st.warning("النتائج إرشادية فقط. راجع مختصاً مالياً للقرارات المهمة.")

    st.divider()
    st.write("**📧 للتواصل:** admin@smart-merchant-tools.com")
