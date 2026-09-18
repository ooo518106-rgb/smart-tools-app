import streamlit as st
import datetime
import pandas as pd

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="أدوات التاجر الذكي", page_icon="💰", layout="centered")

# CSS آمن: يخفي الفوتر النصي فقط ويحافظ على شريط القائمة الجانبية
st.markdown("""
<style>
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- تهيئة ذاكرة الحفظ (Session State) ---
if 'ecommerce_history' not in st.session_state:
    st.session_state.ecommerce_history = []

# القائمة الجانبية
st.sidebar.title("🛠️ قائمة الأدوات")
tool_choice = st.sidebar.radio("اختر الأداة", [
    "📦 حاسبة التجارة الإلكترونية (مع الذاكرة)",
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
if tool_choice == "📦 حاسبة التجارة الإلكترونية (مع الذاكرة)":
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

    # --- قسم الذاكرة والحفظ ---
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
        
    # عرض السجل إذا كان يحتوي على بيانات
    if len(st.session_state.ecommerce_history) > 0:
        df_history = pd.DataFrame(st.session_state.ecommerce_history)
        st.dataframe(df_history, use_container_width=True)
        
        # زر التحميل كملف CSV (يفتح في Excel)
        csv_data = df_history.to_csv(index=False).encode('utf-8-sig') # utf-8-sig لدعم اللغة العربية في إكسل
        
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
# 2. حاسبة الرواتب السريعة
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
# 3. حاسبة أيام الدوام والراتب بدقة متناهية
# ==========================================
elif tool_choice == "📅 حاسبة الدوام الدقيقة":
    st.title("📅 حاسبة الدوام والراتب الدقيقة")
    
    monthly_salary = st.number_input("الراتب الشهري الكامل:", min_value=0.0, value=500.0)
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.write("🟢 **بداية الدوام:**")
        start_date = st.date_input("تاريخ البداية:", value=datetime.date.today().replace(day=1))
        start_time = st.time_input("وقت البداية:", value=datetime.time(8, 0, 0), step=60)
    with col2:
        st.write("🔴 **نهاية الدوام:**")
        end_date = st.date_input("تاريخ النهاية:", value=datetime.date.today())
        end_time = st.time_input("وقت النهاية:", value=datetime.time(16, 0, 0), step=60)
        
    start_datetime = datetime.datetime.combine(start_date, start_time)
    end_datetime = datetime.datetime.combine(end_date, end_time)
    
    st.divider()
    if start_datetime < end_datetime:
        time_diff = end_datetime - start_datetime
        total_seconds = time_diff.total_seconds()
        days = time_diff.days
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        total_month_seconds = 30 * 24 * 3600
        earned_salary = (total_seconds / total_month_seconds) * monthly_salary
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(label="أيام", value=days)
        c2.metric(label="ساعات", value=hours)
        c3.metric(label="دقائق", value=minutes)
        c4.metric(label="ثواني", value=seconds)
        st.success(f"💰 الراتب المستحق: **{earned_salary:.2f}**")
    else:
        st.error("تاريخ النهاية يجب أن يكون بعد تاريخ البداية!")

# ==========================================
# باقي الأدوات (تم اختصار الكود هنا للحفاظ على المساحة، يرجى إبقاء باقي الأقسام كما هي في الكود السابق)
# 4. توزيع الشحن، 5. الخصومات، 6. العمر، 7. التعادل، 8. الضريبة، 9. الكريبتو، 10. المخاطر، 11. القوالب، 12. الخصوصية
# ==========================================

# ==========================================
# 4. حاسبة توزيع مصاريف الشحن
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
        c1.metric(label="نصيب القطعة من المصاريف", value=f"{item_expense:.2f}")
        c2.metric(label="التكلفة النهائية للقطعة", value=f"{(item_price + item_expense):.2f}")

# ==========================================
# 5. حاسبة الخصومات
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
    c1.metric(label="قيمة التوفير", value=f"{disc_amount:.2f}")
    c2.metric(label="السعر النهائي", value=f"{(price_before - disc_amount):.2f}")

# ==========================================
# 6. حاسبة العمر
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
    c1.metric(label="سنة", value=years)
    c2.metric(label="شهر", value=months)
    c3.metric(label="يوم", value=days)

# ==========================================
# 7. حاسبة نقطة التعادل
# ==========================================
elif tool_choice == "📉 حاسبة نقطة التعادل":
    st.title("📉 حاسبة نقطة التعادل")
    fixed_costs = st.number_input("إجمالي المصاريف الثابتة:", min_value=0.0, value=1000.0)
    variable_cost = st.number_input("تكلفة القطعة الواحدة:", min_value=0.0, value=50.0)
    sell_price = st.number_input("سعر بيع القطعة:", min_value=0.0, value=100.0)
    
    if sell_price > variable_cost:
        break_even_units = fixed_costs / (sell_price - variable_cost)
        st.metric(label="القطع المطلوبة للتعادل", value=f"{break_even_units:.0f} قطعة")
    else:
        st.error("سعر البيع يجب أن يكون أعلى من تكلفة القطعة")

# ==========================================
# 8. حاسبة الضريبة VAT
# ==========================================
elif tool_choice == "🧾 حاسبة الضريبة VAT":
    st.title("🧾 حاسبة ضريبة القيمة المضافة")
    price = st.number_input("المبلغ", min_value=0.0, value=1000.0)
    vat_rate = st.number_input("نسبة الضريبة (%)", min_value=0.0, value=15.0)
    vat_amount = price * (vat_rate / 100)
    st.metric(label="قيمة الضريبة", value=f"{vat_amount:.2f}")

# ==========================================
# 9. حاسبة الكريبتو
# ==========================================
elif tool_choice == "📈 حاسبة أرباح الكريبتو":
    st.title("📈 حاسبة أرباح الكريبتو")
    entry_price = st.number_input("سعر الدخول", value=60000.0)
    amount = st.number_input("الكمية", value=0.1)
    exit_price = st.number_input("سعر الخروج", value=62000.0)
    fee = st.number_input("رسوم المنصة (%)", value=0.1)
    
    net_profit = (exit_price * amount) - (entry_price * amount) - (((entry_price*amount)+(exit_price*amount))*(fee/100))
    st.metric(label="الربح الصافي", value=f"{net_profit:.2f}")

# ==========================================
# 10. المخاطر، 11. القوالب، 12. الخصوصية
# ==========================================
elif tool_choice == "🛡️ حاسبة إدارة المخاطر":
    st.title("🛡️ إدارة المخاطر")
    st.write("أداة قيد التطوير...")
elif tool_choice == "📄 القوالب الجاهزة":
    st.title("📄 القوالب")
    st.write("حمل القوالب من هنا...")
elif tool_choice == "📜 سياسة الخصوصية":
    st.title("📜 الخصوصية")
    st.write("بياناتك آمنة ولن يتم حفظها في خوادمنا.")
