import streamlit as st
import datetime
import pandas as pd
import urllib.parse

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="أدوات التاجر الذكي", page_icon="💰", layout="centered")

# CSS آمن جداً: يخفي الفوتر فقط دون لمس رأس الصفحة أو القائمة الجانبية
st.markdown("""
<style>
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- تهيئة ذاكرة الحفظ (Session State) لحاسبة التجارة ---
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
# 1. حاسبة التجارة الإلكترونية (مع ميزة الذاكرة)
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
    res_col1.metric(label="التكلفة الإجمالية", value=f"{total_item_cost:.2f}")
    res_col2.metric(label="رسوم الدفع", value=f"{payment_gateway_fees:.2f}")
    res_col3.metric(label="الربح الصافي", value=f"{net_profit:.2f}", delta="ربح" if net_profit > 0 else "خسارة")

    st.divider()
    st.subheader("💾 سجل الحسابات (ميزة الذاكرة)")
    st.write("يمكنك حفظ نتيجة هذا المنتج لمقارنتها مع منتجات أخرى، ثم تحميل السجل كملف.")
    
    product_name = st.text_input("اسم المنتج (اختياري لحفظ النتيجة):", placeholder="مثال: سماعة بلوتوث")
    
    if st.button("➕ حفظ النتيجة في السجل"):
        record = {
            "اسم المنتج": product_name if product_name else "منتج غير مسمى",
            "التكلفة الواصلة": round(total_item_cost, 2),
            "سعر البيع": round(selling_price, 2),
            "رسوم الدفع": round(payment_gateway_fees, 2),
            "الربح الصافي": round(net_profit, 2)
        }
        st.session_state.ecommerce_history.append(record)
        st.success(f"تم حفظ '{record['اسم المنتج']}' في السجل بنجاح!")
        
    if len(st.session_state.ecommerce_history) > 0:
        df_history = pd.DataFrame(st.session_state.ecommerce_history)
        st.dataframe(df_history, use_container_width=True)
        
        csv_data = df_history.to_csv(index=False).encode('utf-8-sig') 
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.download_button(
                label="📥 تحميل السجل (Excel)",
                data=csv_data,
                file_name="Ecommerce_Calculations.csv",
                mime="text/csv"
            )
        with col_btn2:
            if st.button("🗑️ مسح السجل"):
                st.session_state.ecommerce_history = []
                st.rerun()

# ==========================================
# 2. حاسبة رسوم تابي وتمارا
# ==========================================
elif tool_choice == "💳 رسوم تابي وتمارا":
    st.title("💳 حاسبة رسوم الدفع الآجل (تابي/تمارا)")
    st.write("احسب المبلغ الصافي الذي سيصلك كتاجر بعد خصم رسوم شركات التقسيط والضريبة عليها.")
    
    price = st.number_input("سعر المنتج للعميل:", min_value=0.0, value=100.0)
    col1, col2, col3 = st.columns(3)
    with col1:
        fee_percent = st.number_input("نسبة عمولة الشركة (%):", min_value=0.0, value=7.0)
    with col2:
        fixed_fee = st.number_input("الرسوم الثابتة للعملية:", min_value=0.0, value=1.5)
    with col3:
        vat_on_fee = st.number_input("ضريبة القيمة المضافة (%):", min_value=0.0, value=15.0)
        
    fee_amount = (price * (fee_percent / 100)) + fixed_fee
    vat_amount = fee_amount * (vat_on_fee / 100)
    total_deduction = fee_amount + vat_amount
    net_to_merchant = price - total_deduction
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي رسوم الشركة", f"{fee_amount:.2f}")
    c2.metric("الضريبة على الرسوم", f"{vat_amount:.2f}")
    c3.metric("إجمالي الخصم من التاجر", f"{total_deduction:.2f}")
    
    st.success(f"💰 المبلغ الصافي الذي سيصل للتاجر: **{net_to_merchant:.2f}**")

# ==========================================
# 3. صانع روابط واتساب
# ==========================================
elif tool_choice == "💬 صانع روابط واتساب":
    st.title("💬 صانع روابط واتساب المباشرة")
    st.write("اصنع رابطاً مباشراً لبدء محادثة واتساب معك بضغطة زر.")
    
    phone = st.text_input("رقم الجوال (مع رمز الدولة بدون +):", placeholder="مثال: 966500000000")
    msg = st.text_area("الرسالة الترحيبية (اختياري):", placeholder="مرحباً، أود الاستفسار عن منتجاتكم...")
    
    if st.button("🔗 توليد الرابط"):
        if phone:
            encoded_msg = urllib.parse.quote(msg)
            wa_link = f"https://wa.me/{phone}?text={encoded_msg}"
            st.success("تم إنشاء الرابط بنجاح!")
            st.code(wa_link, language="")
            st.markdown(f"[📲 اضغط هنا لتجربة الرابط]({wa_link})")
        else:
            st.error("يرجى إدخال رقم الجوال أولاً.")

# ==========================================
# 4. حاسبة القروض والأقساط
# ==========================================
elif tool_choice == "🏦 حاسبة القروض والأقساط":
    st.title("🏦 حاسبة القروض والأقساط")
    st.write("احسب القسط الشهري الدقيق لقرضك أو مشترياتك بالتقسيط.")
    
    loan_amount = st.number_input("مبلغ القرض (التمويل):", min_value=0.0, value=10000.0)
    col1, col2 = st.columns(2)
    with col1:
        interest_rate = st.number_input("نسبة الفائدة السنوية (%):", min_value=0.0, value=5.0)
    with col2:
        months = st.number_input("مدة السداد (بالأشهر):", min_value=1, value=60)
        
    st.divider()
    if interest_rate > 0:
        monthly_rate = (interest_rate / 100) / 12
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    else:
        monthly_payment = loan_amount / months
        
    total_paid = monthly_payment * months
    total_interest = total_paid - loan_amount
    
    c1, c2 = st.columns(2)
    c1.metric("القسط الشهري المتوقع", f"{monthly_payment:.2f}")
    c2.metric("إجمالي الفوائد المضافة", f"{total_interest:.2f}")
    st.info(f"إجمالي المبلغ المسدد في نهاية المدة: **{total_paid:.2f}**")

# ==========================================
# 5. حاسبة زكاة المال
# ==========================================
elif tool_choice == "🕋 حاسبة زكاة المال":
    st.title("🕋 حاسبة زكاة المال")
    st.write("احسب مقدار الزكاة الواجب إخراجه عن أموالك (ربع العشر 2.5%).")
    
    wealth = st.number_input("إجمالي المبلغ أو المدخرات:", min_value=0.0, value=10000.0)
    zakat_rate = 0.025
    zakat_amount = wealth * zakat_rate
    
    st.divider()
    st.metric(label="مقدار الزكاة الواجب إخراجه", value=f"{zakat_amount:.2f}")

# ==========================================
# 6. حاسبة الرواتب السريعة
# ==========================================
elif tool_choice == "💸 حاسبة الرواتب":
    st.title("💸 حاسبة الرواتب السريعة")
    basic_salary = st.number_input("الراتب الأساسي المتفق عليه:", min_value=0.0, value=500.0)
    col1, col2 = st.columns(2)
    with col1:
        allowances = st.number_input("إجمالي البدلات:", min_value=0.0, value=0.0)
    with col2:
        deductions = st.number_input("إجمالي الخصومات:", min_value=0.0, value=0.0)
        
    net_salary = basic_salary + allowances - deductions
    st.divider()
    st.metric(label="💰 الراتب المستحق الدفع", value=f"{net_salary:.2f}")

# ==========================================
# 7. حاسبة الدوام الدقيقة
# ==========================================
elif tool_choice == "📅 حاسبة الدوام الدقيقة":
    st.title("📅 حاسبة الدوام والراتب الدقيقة")
    monthly_salary = st.number_input("الراتب الشهري الكامل:", min_value=0.0, value=500.0)
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("تاريخ البداية:", value=datetime.date.today().replace(day=1))
        start_time = st.time_input("وقت البداية:", value=datetime.time(8, 0, 0), step=60)
    with col2:
        end_date = st.date_input("تاريخ النهاية:", value=datetime.date.today())
        end_time = st.time_input("وقت النهاية:", value=datetime.time(16, 0, 0), step=60)
        
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
        st.success(f"💰 الراتب المستحق: **{earned_salary:.2f}**")
    else:
        st.error("تاريخ النهاية يجب أن يكون بعد البداية!")

# ==========================================
# 8. توزيع مصاريف الشحن
# ==========================================
elif tool_choice == "⚖️ توزيع مصاريف الشحن":
    st.title("⚖️ حاسبة توزيع مصاريف الشحن والجمارك")
    total_invoice = st.number_input("إجمالي قيمة الفاتورة:", min_value=1.0, value=1000.0)
    total_expenses = st.number_input("إجمالي مصاريف الشحن والجمارك:", min_value=0.0, value=200.0)
    item_price = st.number_input("سعر شراء الصنف الواحد:", min_value=0.0, value=50.0)
    
    if total_invoice > 0:
        expense_ratio = total_expenses / total_invoice
        item_expense = item_price * expense_ratio
        c1, c2 = st.columns(2)
        c1.metric("نصيب القطعة من المصاريف", f"{item_expense:.2f}")
        c2.metric("التكلفة النهائية للقطعة", f"{(item_price + item_expense):.2f}")

# ==========================================
# 9. حاسبة الخصومات
# ==========================================
elif tool_choice == "🏷️ حاسبة الخصومات":
    st.title("🏷️ حاسبة الخصومات والعروض")
    price_before = st.number_input("السعر الأساسي:", min_value=0.0, value=100.0)
    discount_type = st.radio("نوع الخصم:", ["نسبة مئوية (%)", "مبلغ ثابت"])
    
    if discount_type == "نسبة مئوية (%)":
        disc_percent = st.number_input("نسبة الخصم (%):", min_value=0.0, max_value=100.0, value=20.0)
        disc_amount = price_before * (disc_percent / 100)
    else:
        disc_amount = st.number_input("مبلغ الخصم:", min_value=0.0, max_value=price_before, value=20.0)
        
    c1, c2 = st.columns(2)
    c1.metric("قيمة التوفير", f"{disc_amount:.2f}")
    c2.metric("السعر النهائي", f"{(price_before - disc_amount):.2f}")

# ==========================================
# 10. حاسبة العمر
# ==========================================
elif tool_choice == "⏳ حاسبة العمر":
    st.title("⏳ حاسبة العمر الدقيقة")
    today = datetime.date.today()
    dob = st.date_input("تاريخ الميلاد:", value=datetime.date(2000, 1, 1))
    
    years = today.year - dob.year
    months = today.month - dob.month
    days = today.day - dob.day
    if days < 0:
        months -= 1; days += 30
    if months < 0:
        years -= 1; months += 12
        
    c1, c2, c3 = st.columns(3)
    c1.metric("سنة", years)
    c2.metric("شهر", months)
    c3.metric("يوم", days)

# ==========================================
# 11. نقطة التعادل
# ==========================================
elif tool_choice == "📉 حاسبة نقطة التعادل":
    st.title("📉 حاسبة نقطة التعادل")
    fixed_costs = st.number_input("إجمالي المصاريف الثابتة:", min_value=0.0, value=1000.0)
    variable_cost = st.number_input("تكلفة القطعة الواحدة:", min_value=0.0, value=50.0)
    sell_price = st.number_input("سعر بيع القطعة:", min_value=0.0, value=100.0)
    
    if sell_price > variable_cost:
        break_even_units = fixed_costs / (sell_price - variable_cost)
        st.metric("القطع المطلوبة للتعادل", f"{break_even_units:.0f} قطعة")
    else:
        st.error("سعر البيع يجب أن يكون أعلى من تكلفة القطعة")

# ==========================================
# 12. الضريبة VAT
# ==========================================
elif tool_choice == "🧾 حاسبة الضريبة VAT":
    st.title("🧾 حاسبة ضريبة القيمة المضافة")
    price = st.number_input("المبلغ", min_value=0.0, value=1000.0)
    vat_rate = st.number_input("نسبة الضريبة (%)", min_value=0.0, value=15.0)
    vat_amount = price * (vat_rate / 100)
    st.metric("قيمة الضريبة", f"{vat_amount:.2f}")

# ==========================================
# 13. أرباح الكريبتو
# ==========================================
elif tool_choice == "📈 حاسبة أرباح الكريبتو":
    st.title("📈 حاسبة أرباح الكريبتو")
    entry_price = st.number_input("سعر الدخول", value=60000.0)
    amount = st.number_input("الكمية", value=0.1)
    exit_price = st.number_input("سعر الخروج", value=62000.0)
    fee = st.number_input("رسوم المنصة (%)", value=0.1)
    
    net_profit = (exit_price * amount) - (entry_price * amount) - (((entry_price*amount)+(exit_price*amount))*(fee/100))
    st.metric("الربح الصافي", f"{net_profit:.2f}")

# ==========================================
# 14. المخاطر
# ==========================================
elif tool_choice == "🛡️ حاسبة إدارة المخاطر":
    st.title("🛡️ حاسبة إدارة المخاطر (Position Sizing)")
    capital = st.number_input("حجم المحفظة الإجمالي (USDT)", min_value=0.0, value=1000.0)
    risk_percent = st.number_input("المخاطرة المسموحة للصفقة (%)", min_value=0.0, value=2.0)
    col_x, col_y = st.columns(2)
    with col_x:
        entry_p = st.number_input("سعر الدخول المستهدف", min_value=0.0, value=50000.0)
    with col_y:
        stop_loss = st.number_input("سعر وقف الخسارة (Stop Loss)", min_value=0.0, value=48000.0)
        
    risk_amount = capital * (risk_percent / 100)
    if entry_p > 0 and stop_loss > 0 and entry_p != stop_loss:
        position_size = risk_amount / abs(entry_p - stop_loss)
        p1, p2 = st.columns(2)
        p1.metric("الكمية المسموح شراؤها", f"{position_size:.4f}")
        p2.metric("حجم الصفقة", f"{(position_size * entry_p):.2f} USDT")

# ==========================================
# 15. القوالب
# ==========================================
elif tool_choice == "📄 القوالب الجاهزة":
    st.title("📄 قوالب محاسبية وتجارية جاهزة")
    with st.expander("1. قالب دفتر أستاذ الموردين (Excel)", expanded=True):
        st.download_button("📥 تحميل القالب الان", "عينة", "suppliers.csv")
    with st.expander("2. نموذج جرد المخزون الدوري (PDF)"):
        st.download_button("📥 تحميل نموذج الجرد", "عينة", "inventory.txt")

# ==========================================
# 16. الخصوصية
# ==========================================
elif tool_choice == "📜 سياسة الخصوصية":
    st.title("📜 سياسة الخصوصية وإخلاء المسؤولية")
    st.info("العمليات الحسابية تتم محلياً على متصفحك. نحن لا نقوم بجمع أو حفظ بياناتك المالية.")
    st.write("**للتواصل:** admin@smart-merchant-tools.com")
