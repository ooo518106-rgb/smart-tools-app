import streamlit as st
import datetime
import pandas as pd
import urllib.parse

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="أدوات التاجر الذكي", page_icon="💰", layout="centered")

# ==========================================
# CSS آمن: تحسين الخطوط والأزرار بدون كسر تخطيط الشاشة
# ==========================================
st.markdown("""
<style>
    /* تحسين الخطوط */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif !important;
    }

    /* إخفاء العلامات والزر الأحمر بأمان */
    #MainMenu, footer, header {visibility: hidden !important;}
    [data-testid="stAppDeployButton"] {display: none !important;}

    /* تلوين الأزرار الأساسية بالأخضر */
    .stButton>button {
        background-color: #27ae60 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        border: none !important;
    }
    .stButton>button:hover {
        background-color: #219a52 !important;
    }
    
    /* ضبط اتجاه النصوص الرئيسية لليمين */
    .stMarkdown, .stText, label {
        direction: rtl !important;
        text-align: right !important;
    }
</style>
""", unsafe_allow_html=True)

# --- تهيئة ذاكرة الحفظ ---
if 'ecommerce_history' not in st.session_state:
    st.session_state.ecommerce_history = []

# القائمة الجانبية
st.sidebar.title("🛠️ قائمة الأدوات")
tool_choice = st.sidebar.radio("اختر الأداة", [
    "📦 حاسبة التجارة الإلكترونية",
    "💳 رسوم تابي وتمارا",
    "💬 صانع روابط واتساب",
    "🏦 حاسبة القروض والأقساط",
    "🕋 حاسبة زكاة المال",
    "💸 حاسبة الرواتب",
    "📅 حاسبة الدوام الدقيقة",
    "⚖️ توزيع مصاريف الشحن",
    "🏷️ حاسبة الخصومات",
    "⏳ حاسبة العمر",
    "📉 حاسبة نقطة التعادل",
    "🧾 حاسبة الضريبة VAT",
    "📈 حاسبة أرباح الكريبتو",
    "🛡️ حاسبة إدارة المخاطر",
    "📄 القوالب الجاهزة",
    "📜 سياسة الخصوصية"
])

# ==========================================
# 1. حاسبة التجارة الإلكترونية
# ==========================================
if tool_choice == "📦 حاسبة التجارة الإلكترونية":
    st.title("📦 حاسبة أرباح التجارة الإلكترونية")
    st.write("احسب هوامش الربح الصافية بعد خصم تكاليف الشحن ورسوم بوابات الدفع")
    
    col1, col2 = st.columns(2)
    with col1:
        cost_price = st.number_input("تكلفة المنتج من المورد", min_value=0.0, value=50.0)
        shipping_cost = st.number_input("تكلفة الشحن والتغليف", min_value=0.0, value=15.0)
    with col2:
        selling_price = st.number_input("سعر البيع للعميل", min_value=0.0, value=150.0)
        gateway_fee_percent = st.number_input("رسوم بوابة الدفع (%)", min_value=0.0, value=2.2)
        
    fixed_fee = st.number_input("الرسوم الثابتة للعملية", min_value=0.0, value=1.0)
    
    total_item_cost = cost_price + shipping_cost
    payment_gateway_fees = (selling_price * (gateway_fee_percent / 100)) + fixed_fee
    net_profit = selling_price - total_item_cost - payment_gateway_fees
    
    st.divider()
    st.subheader("📊 ملخص الأرباح")
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("التكلفة الإجمالية", f"{total_item_cost:.2f}")
    res_col2.metric("رسوم الدفع", f"{payment_gateway_fees:.2f}")
    res_col3.metric("الربح الصافي", f"{net_profit:.2f}", delta="ربح" if net_profit > 0 else "خسارة")

    st.divider()
    st.subheader("💾 سجل الحسابات (ميزة الذاكرة)")
    product_name = st.text_input("اسم المنتج (اختياري لحفظ النتيجة):")
    
    if st.button("➕ حفظ النتيجة في السجل"):
        record = {
            "المنتج": product_name if product_name else "بدون اسم",
            "التكلفة": round(total_item_cost, 2),
            "البيع": round(selling_price, 2),
            "الرسوم": round(payment_gateway_fees, 2),
            "الربح": round(net_profit, 2)
        }
        st.session_state.ecommerce_history.append(record)
        st.success(f"تم الحفظ بنجاح!")
        
    if len(st.session_state.ecommerce_history) > 0:
        df_history = pd.DataFrame(st.session_state.ecommerce_history)
        st.dataframe(df_history, use_container_width=True)
        csv_data = df_history.to_csv(index=False).encode('utf-8-sig') 
        
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            st.download_button("📥 تحميل السجل", csv_data, "Ecommerce.csv", "text/csv")
        with c_btn2:
            if st.button("🗑️ مسح السجل"):
                st.session_state.ecommerce_history = []
                st.rerun()

# ==========================================
# 2. رسوم تابي وتمارا
# ==========================================
elif tool_choice == "💳 رسوم تابي وتمارا":
    st.title("💳 حاسبة رسوم الدفع الآجل")
    price = st.number_input("سعر المنتج للعميل:", min_value=0.0, value=100.0)
    col1, col2, col3 = st.columns(3)
    with col1:
        fee_percent = st.number_input("العمولة (%):", min_value=0.0, value=7.0)
    with col2:
        fixed_fee = st.number_input("رسوم ثابتة:", min_value=0.0, value=1.5)
    with col3:
        vat_on_fee = st.number_input("الضريبة (%):", min_value=0.0, value=15.0)
        
    fee_amount = (price * (fee_percent / 100)) + fixed_fee
    vat_amount = fee_amount * (vat_on_fee / 100)
    total_deduction = fee_amount + vat_amount
    net_to_merchant = price - total_deduction
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("رسوم الشركة", f"{fee_amount:.2f}")
    c2.metric("الضريبة", f"{vat_amount:.2f}")
    c3.metric("الخصم الكلي", f"{total_deduction:.2f}")
    st.success(f"💰 الصافي للتاجر: **{net_to_merchant:.2f}**")

# ==========================================
# 3. صانع روابط واتساب
# ==========================================
elif tool_choice == "💬 صانع روابط واتساب":
    st.title("💬 صانع روابط واتساب")
    phone = st.text_input("رقم الجوال (بدون +):", placeholder="966500000000")
    msg = st.text_area("الرسالة الترحيبية:")
    
    if st.button("🔗 توليد الرابط"):
        if phone:
            encoded_msg = urllib.parse.quote(msg)
            wa_link = f"https://wa.me/{phone}?text={encoded_msg}"
            st.success("تم الإنشاء!")
            st.code(wa_link, language="")
            st.markdown(f"[📲 اضغط هنا لتجربة الرابط]({wa_link})")
        else:
            st.error("أدخل رقم الجوال أولاً.")

# ==========================================
# 4. القروض والأقساط
# ==========================================
elif tool_choice == "🏦 حاسبة القروض والأقساط":
    st.title("🏦 حاسبة القروض والأقساط")
    loan_amount = st.number_input("مبلغ التمويل:", min_value=0.0, value=10000.0)
    col1, col2 = st.columns(2)
    with col1:
        interest_rate = st.number_input("الفائدة السنوية (%):", min_value=0.0, value=5.0)
    with col2:
        months = st.number_input("مدة السداد (أشهر):", min_value=1, value=60)
        
    if interest_rate > 0:
        monthly_rate = (interest_rate / 100) / 12
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    else:
        monthly_payment = loan_amount / months
        
    total_paid = monthly_payment * months
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("القسط الشهري", f"{monthly_payment:.2f}")
    c2.metric("إجمالي الفوائد", f"{(total_paid - loan_amount):.2f}")

# ==========================================
# 5. زكاة المال
# ==========================================
elif tool_choice == "🕋 حاسبة زكاة المال":
    st.title("🕋 حاسبة زكاة المال")
    wealth = st.number_input("إجمالي المبلغ:", min_value=0.0, value=10000.0)
    st.metric("الزكاة الواجبة (2.5%)", f"{(wealth * 0.025):.2f}")

# ==========================================
# 6. الرواتب
# ==========================================
elif tool_choice == "💸 حاسبة الرواتب":
    st.title("💸 حاسبة الرواتب")
    basic = st.number_input("الراتب الأساسي:", value=500.0)
    allow = st.number_input("البدلات:", value=0.0)
    deduct = st.number_input("الخصومات:", value=0.0)
    st.metric("الراتب الصافي", f"{(basic + allow - deduct):.2f}")

# ==========================================
# 7. الدوام الدقيقة
# ==========================================
elif tool_choice == "📅 حاسبة الدوام الدقيقة":
    st.title("📅 حاسبة الدوام والراتب")
    monthly_salary = st.number_input("الراتب الشهري:", value=500.0)
    c1, c2 = st.columns(2)
    with c1:
        sd = st.date_input("بداية (تاريخ):", datetime.date.today().replace(day=1))
        st_t = st.time_input("بداية (وقت):", datetime.time(8, 0))
    with c2:
        ed = st.date_input("نهاية (تاريخ):", datetime.date.today())
        et_t = st.time_input("نهاية (وقت):", datetime.time(16, 0))
        
    start_dt = datetime.datetime.combine(sd, st_t)
    end_dt = datetime.datetime.combine(ed, et_t)
    if start_dt < end_dt:
        diff = end_dt - start_dt
        secs = diff.total_seconds()
        earned = (secs / (30*24*3600)) * monthly_salary
        st.success(f"الراتب المستحق: {earned:.2f}")
    else:
        st.error("التاريخ غير صالح")

# ==========================================
# 8. توزيع الشحن
# ==========================================
elif tool_choice == "⚖️ توزيع مصاريف الشحن":
    st.title("⚖️ توزيع مصاريف الشحن")
    inv = st.number_input("إجمالي الفاتورة:", value=1000.0)
    exp = st.number_input("إجمالي المصاريف:", value=200.0)
    price = st.number_input("سعر الصنف:", value=50.0)
    if inv > 0:
        c1, c2 = st.columns(2)
        c1.metric("النصيب من المصاريف", f"{(price * (exp/inv)):.2f}")
        c2.metric("التكلفة النهائية", f"{(price + (price * (exp/inv))):.2f}")

# ==========================================
# 9. الخصومات
# ==========================================
elif tool_choice == "🏷️ حاسبة الخصومات":
    st.title("🏷️ حاسبة الخصومات")
    p = st.number_input("السعر الأساسي:", value=100.0)
    d = st.number_input("نسبة الخصم (%):", value=20.0)
    st.metric("السعر النهائي", f"{(p - (p * (d/100))):.2f}")

# ==========================================
# 10. العمر
# ==========================================
elif tool_choice == "⏳ حاسبة العمر":
    st.title("⏳ حاسبة العمر")
    dob = st.date_input("تاريخ الميلاد:", datetime.date(2000,1,1))
    today = datetime.date.today()
    st.metric("العمر بالسنوات", today.year - dob.year)

# ==========================================
# 11. نقطة التعادل
# ==========================================
elif tool_choice == "📉 حاسبة نقطة التعادل":
    st.title("📉 نقطة التعادل")
    fix = st.number_input("المصاريف الثابتة:", value=1000.0)
    var = st.number_input("تكلفة القطعة:", value=50.0)
    sell = st.number_input("سعر البيع:", value=100.0)
    if sell > var:
        st.metric("القطع المطلوبة", f"{(fix / (sell - var)):.0f}")

# ==========================================
# 12. الضريبة VAT
# ==========================================
elif tool_choice == "🧾 حاسبة الضريبة VAT":
    st.title("🧾 حاسبة الضريبة")
    p = st.number_input("المبلغ:", value=1000.0)
    st.metric("قيمة الضريبة (15%)", f"{(p * 0.15):.2f}")

# ==========================================
# 13. أرباح الكريبتو
# ==========================================
elif tool_choice == "📈 حاسبة أرباح الكريبتو":
    st.title("📈 أرباح الكريبتو")
    buy = st.number_input("دخول", value=60000.0)
    sell = st.number_input("خروج", value=62000.0)
    st.metric("الفرق", f"{(sell - buy):.2f}")

# ==========================================
# 14. المخاطر
# ==========================================
elif tool_choice == "🛡️ حاسبة إدارة المخاطر":
    st.title("🛡️ إدارة المخاطر")
    st.write("أداة قيد التطوير...")

# ==========================================
# 15. القوالب
# ==========================================
elif tool_choice == "📄 القوالب الجاهزة":
    st.title("📄 القوالب")
    st.write("حمل القوالب من هنا...")

# ==========================================
# 16. الخصوصية
# ==========================================
elif tool_choice == "📜 سياسة الخصوصية":
    st.title("📜 الخصوصية")
    st.write("بياناتك آمنة ولن يتم حفظها.")
