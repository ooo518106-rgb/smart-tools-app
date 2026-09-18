import streamlit as st
import datetime

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="أدوات التاجر الذكي", page_icon="💰", layout="centered")

# CSS آمن: يخفي الفوتر النصي فقط ويحافظ على شريط القائمة الجانبية ليعمل على الجوال
st.markdown("""
<style>
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# القائمة الجانبية
st.sidebar.title("🛠️ قائمة الأدوات")
tool_choice = st.sidebar.radio("اختر الأداة", [
    "📦 حاسبة التجارة الإلكترونية",
    "💸 حاسبة الرواتب",
    "📅 حاسبة الدوام الدقيقة (مُحدث)",
    "⚖️ توزيع مصاريف الشحن",
    "🏷️ حاسبة الخصومات",
    "⏳ حاسبة العمر",
    "📉 حاسبة نقطة التعادل",
    "🧾 حاسبة الضريبة VAT",
    "📈 حاسبة أرباح الكريبتو",
    "🛡️ حاسبة إدارة المخاطر",
    "📄 القوالب الجاهزة (مجاناً)",
    "📜 سياسة الخصوصية"
])

# ==========================================
# 1. حاسبة التجارة الإلكترونية (الدروبشيبينغ)
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

# ==========================================
# 2. حاسبة الرواتب السريعة
# ==========================================
elif tool_choice == "💸 حاسبة الرواتب":
    st.title("💸 حاسبة الرواتب السريعة")
    st.write("احسب الراتب الصافي للموظف بعد إضافة البدلات وخصم الغيابات أو السلف بثانية واحدة.")
    
    basic_salary = st.number_input("الراتب الأساسي المتفق عليه:", min_value=0.0, value=500.0)
    
    col1, col2 = st.columns(2)
    with col1:
        allowances = st.number_input("إجمالي البدلات (مكافآت، مواصلات):", min_value=0.0, value=0.0)
    with col2:
        deductions = st.number_input("إجمالي الخصومات (غياب، سلف، تأخير):", min_value=0.0, value=0.0)
        
    net_salary = basic_salary + allowances - deductions
    
    st.divider()
    st.metric(label="💰 الراتب المستحق الدفع (الصافي)", value=f"{net_salary:.2f}")

# ==========================================
# 3. حاسبة أيام الدوام والراتب بدقة متناهية (محدثة)
# ==========================================
elif tool_choice == "📅 حاسبة الدوام الدقيقة (مُحدث)":
    st.title("📅 حاسبة الدوام والراتب الدقيقة")
    st.write("احسب المدة الفعلية للدوام (بالأيام، الساعات، الدقائق، والثواني) والراتب المستحق عليها بدقة متناهية.")
    
    monthly_salary = st.number_input("الراتب الشهري الكامل للموظف:", min_value=0.0, value=500.0)
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.write("🟢 **بداية الدوام:**")
        start_date = st.date_input("تاريخ البداية:", value=datetime.date.today().replace(day=1))
        start_time = st.time_input("وقت البداية (ساعة:دقيقة):", value=datetime.time(8, 0, 0), step=60)
    with col2:
        st.write("🔴 **نهاية الدوام:**")
        end_date = st.date_input("تاريخ النهاية:", value=datetime.date.today())
        end_time = st.time_input("وقت النهاية (ساعة:دقيقة):", value=datetime.time(16, 0, 0), step=60)
        
    start_datetime = datetime.datetime.combine(start_date, start_time)
    end_datetime = datetime.datetime.combine(end_date, end_time)
    
    st.divider()
    if start_datetime < end_datetime:
        time_diff = end_datetime - start_datetime
        total_seconds = time_diff.total_seconds()
        
        # استخراج الأيام والساعات والدقائق والثواني
        days = time_diff.days
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # حساب الراتب بناءً على الثواني (الشهر 30 يوم = 2,592,000 ثانية)
        total_month_seconds = 30 * 24 * 3600
        earned_salary = (total_seconds / total_month_seconds) * monthly_salary
        
        st.subheader("⏱️ المدة الفعلية المقضية:")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(label="أيام", value=days)
        c2.metric(label="ساعات", value=hours)
        c3.metric(label="دقائق", value=minutes)
        c4.metric(label="ثواني", value=seconds)
        
        st.success(f"💰 الراتب المستحق لهذه المدة بدقة: **{earned_salary:.2f}**")
    else:
        st.error("تأكد أن تاريخ ووقت النهاية يجب أن يكون بعد البداية!")

# ==========================================
# 4. حاسبة توزيع مصاريف الشحن
# ==========================================
elif tool_choice == "⚖️ توزيع مصاريف الشحن":
    st.title("⚖️ حاسبة توزيع مصاريف الشحن والجمارك")
    st.write("أداة لتوزيع المصاريف الإضافية على الأصناف لمعرفة التكلفة الحقيقية للقطعة الواحدة")
    
    total_invoice = st.number_input("إجمالي قيمة الفاتورة (لجميع البضائع):", min_value=1.0, value=1000.0)
    total_expenses = st.number_input("إجمالي مصاريف الشحن والجمارك:", min_value=0.0, value=200.0)
    item_price = st.number_input("سعر شراء الصنف الواحد (من المورد):", min_value=0.0, value=50.0)
    
    st.divider()
    if total_invoice > 0:
        expense_ratio = total_expenses / total_invoice
        item_expense = item_price * expense_ratio
        final_item_cost = item_price + item_expense
        
        c1, c2 = st.columns(2)
        c1.metric(label="نصيب القطعة من المصاريف", value=f"{item_expense:.2f}")
        c2.metric(label="التكلفة النهائية للقطعة", value=f"{final_item_cost:.2f}")

# ==========================================
# 5. حاسبة الخصومات
# ==========================================
elif tool_choice == "🏷️ حاسبة الخصومات":
    st.title("🏷️ حاسبة الخصومات والعروض")
    st.write("احسب السعر النهائي للمنتج بعد تطبيق الخصم التجاري")
    
    price_before = st.number_input("السعر الأساسي:", min_value=0.0, value=100.0)
    discount_type = st.radio("نوع الخصم:", ["نسبة مئوية (%)", "مبلغ ثابت"])
    
    if discount_type == "نسبة مئوية (%)":
        disc_percent = st.number_input("نسبة الخصم (%):", min_value=0.0, max_value=100.0, value=20.0)
        disc_amount = price_before * (disc_percent / 100)
    else:
        disc_amount = st.number_input("مبلغ الخصم:", min_value=0.0, max_value=price_before, value=20.0)
        
    price_after = price_before - disc_amount
    
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric(label="قيمة التوفير (الخصم)", value=f"{disc_amount:.2f}")
    c2.metric(label="السعر النهائي للعميل", value=f"{price_after:.2f}")

# ==========================================
# 6. حاسبة العمر
# ==========================================
elif tool_choice == "⏳ حاسبة العمر":
    st.title("⏳ حاسبة العمر الدقيقة")
    st.write("أدخل تاريخ ميلادك لمعرفة عمرك بالتفصيل")
    
    today = datetime.date.today()
    dob = st.date_input("تاريخ الميلاد:", min_value=datetime.date(1900, 1, 1), max_value=today, value=datetime.date(2000, 1, 1))
    
    years = today.year - dob.year
    months = today.month - dob.month
    days = today.day - dob.day
    
    if days < 0:
        months -= 1
        days += 30
    if months < 0:
        years -= 1
        months += 12
        
    st.divider()
    st.subheader("عمرك الآن هو:")
    
    c1, c2, c3 = st.columns(3)
    c1.metric(label="سنة", value=years)
    c2.metric(label="شهر", value=months)
    c3.metric(label="يوم", value=days)

# ==========================================
# 7. حاسبة نقطة التعادل
# ==========================================
elif tool_choice == "📉 حاسبة نقطة التعادل":
    st.title("📉 حاسبة نقطة التعادل (Break-Even)")
    st.write("اعرف كم قطعة تحتاج أن تبيع لتغطية مصاريفك الثابتة والبدء في تحقيق الأرباح")
    
    fixed_costs = st.number_input("إجمالي المصاريف الثابتة (شهرياً)", min_value=0.0, value=1000.0)
    col1, col2 = st.columns(2)
    with col1:
        variable_cost = st.number_input("تكلفة القطعة الواحدة (عليك)", min_value=0.0, value=50.0)
    with col2:
        sell_price = st.number_input("سعر بيع القطعة للعميل", min_value=0.0, value=100.0)
        
    st.divider()
    if sell_price > variable_cost:
        break_even_units = fixed_costs / (sell_price - variable_cost)
        break_even_revenue = break_even_units * sell_price
        
        c1, c2 = st.columns(2)
        c1.metric(label="القطع المطلوبة للتعادل", value=f"{break_even_units:.0f} قطعة")
        c2.metric(label="المبيعات المطلوبة", value=f"{break_even_revenue:.2f}")
    else:
        st.error("سعر البيع يجب أن يكون أعلى من تكلفة القطعة لكي يكون هناك نقطة تعادل")

# ==========================================
# 8. حاسبة ضريبة القيمة المضافة (VAT)
# ==========================================
elif tool_choice == "🧾 حاسبة الضريبة VAT":
    st.title("🧾 حاسبة ضريبة القيمة المضافة (VAT)")
    st.write("أداة سريعة لحساب الضريبة للسوق الخليجي (إضافة الضريبة أو استخراجها)")
    
    price = st.number_input("المبلغ", min_value=0.0, value=1000.0)
    vat_rate = st.number_input("نسبة الضريبة (%)", min_value=0.0, value=15.0)
    vat_type = st.radio("نوع الحسبة", ["إضافة الضريبة (المبلغ غير شامل)", "استخراج الضريبة (المبلغ شامل)"])
    
    st.divider()
    res1, res2 = st.columns(2)
    
    if vat_type == "إضافة الضريبة (المبلغ غير شامل)":
        vat_amount = price * (vat_rate / 100)
        total_price = price + vat_amount
        res1.metric(label="قيمة الضريبة", value=f"{vat_amount:.2f}")
        res2.metric(label="المبلغ الإجمالي", value=f"{total_price:.2f}")
    else:
        base_price = price / (1 + (vat_rate / 100))
        vat_amount = price - base_price
        res1.metric(label="المبلغ الأساسي", value=f"{base_price:.2f}")
        res2.metric(label="الضريبة المستقطعة", value=f"{vat_amount:.2f}")

# ==========================================
# 9. حاسبة أرباح الكريبتو
# ==========================================
elif tool_choice == "📈 حاسبة أرباح الكريبتو":
    st.title("📈 حاسبة أرباح التداول والعملات الرقمية")
    st.write("احسب أرباحك الصافية بعد خصم عمولات منصات التداول")
    
    col_a, col_b = st.columns(2)
    with col_a:
        entry_price = st.number_input("سعر الدخول (الشراء)", min_value=0.0, value=60000.0)
        amount = st.number_input("الكمية (عدد الحبات)", min_value=0.0, value=0.1, step=0.01)
    with col_b:
        exit_price = st.number_input("سعر الخروج (البيع)", min_value=0.0, value=62000.0)
        trading_fee = st.number_input("رسوم المنصة (%)", min_value=0.0, value=0.1)
        
    total_buy = entry_price * amount
    total_sell = exit_price * amount
    fee_buy = total_buy * (trading_fee / 100)
    fee_sell = total_sell * (trading_fee / 100)
    total_fees = fee_buy + fee_sell
    net_crypto_profit = (total_sell - total_buy) - total_fees
    
    st.divider()
    st.subheader("📊 ملخص صفقة التداول")
    
    cr1, cr2, cr3 = st.columns(3)
    cr1.metric(label="رأس المال المستثمر", value=f"{total_buy:.2f}")
    cr2.metric(label="إجمالي الرسوم", value=f"{total_fees:.2f}")
    cr3.metric(label="الربح الصافي", value=f"{net_crypto_profit:.2f}", delta="ربح" if net_crypto_profit > 0 else "خسارة")

# ==========================================
# 10. حاسبة إدارة المخاطر للكريبتو
# ==========================================
elif tool_choice == "🛡️ حاسبة إدارة المخاطر":
    st.title("🛡️ حاسبة إدارة المخاطر (Position Sizing)")
    st.write("اعرف حجم الكمية المناسبة للشراء بناءً على نسبة المخاطرة التي تتحملها في محفظتك")
    
    capital = st.number_input("حجم المحفظة الإجمالي (USDT)", min_value=0.0, value=1000.0)
    risk_percent = st.number_input("المخاطرة المسموحة للصفقة (%)", min_value=0.0, value=2.0)
    col_x, col_y = st.columns(2)
    with col_x:
        entry_p = st.number_input("سعر الدخول المستهدف", min_value=0.0, value=50000.0)
    with col_y:
        stop_loss = st.number_input("سعر وقف الخسارة (Stop Loss)", min_value=0.0, value=48000.0)
        
    st.divider()
    risk_amount = capital * (risk_percent / 100)
    
    if entry_p > 0 and stop_loss > 0 and entry_p != stop_loss:
        position_size = risk_amount / abs(entry_p - stop_loss)
        position_value = position_size * entry_p
        
        st.info(f"المبلغ المعرض للمخاطرة (في حال ضرب الوقف): **{risk_amount:.2f} USDT**")
        p1, p2 = st.columns(2)
        p1.metric(label="الكمية المسموح شراؤها", value=f"{position_size:.4f}")
        p2.metric(label="حجم الصفقة", value=f"{position_value:.2f} USDT")
    else:
        st.warning("يرجى إدخال أسعار دخول ووقف خسارة صحيحة ومختلفة")

# ==========================================
# 11. القوالب الجاهزة
# ==========================================
elif tool_choice == "📄 القوالب الجاهزة (مجاناً)":
    st.title("📄 قوالب محاسبية وتجارية جاهزة")
    st.write("نماذج مصممة لتسهيل ترحيل أرصدتك وتكاليفك إلى نظامك المحاسبي")
    
    st.info("💡 حمل القوالب مجاناً وافتحها باستخدام Excel أو Word")
    
    with st.expander("1. قالب دفتر أستاذ الموردين (Excel)", expanded=True):
        st.write("ملف لتسجيل فواتير المشتريات وحساب تكلفة الوحدة للمنتجات المستوردة")
        st.download_button("📥 تحميل القالب الان", "عينة", "suppliers.csv")
        
    with st.expander("2. نموذج جرد المخزون الدوري (PDF)"):
        st.write("جدول مبسط لمتابعة حركة الأصناف وتسجيل النواقص")
        st.download_button("📥 تحميل نموذج الجرد", "عينة", "inventory.txt")

# ==========================================
# 12. سياسة الخصوصية
# ==========================================
elif tool_choice == "📜 سياسة الخصوصية":
    st.title("📜 سياسة الخصوصية وإخلاء المسؤولية")
    st.info("نحن في أدوات التاجر الذكي نولي خصوصيتك أهمية قصوى")
    st.write("العمليات الحسابية تتم محلياً على متصفحك. نحن **لا نقوم بجمع أو حفظ** بياناتك المالية")
    st.write("الموقع يستخدم خدمات أطراف ثالثة (Google AdSense) لعرض الإعلانات")
    st.divider()
    st.write("**للتواصل والدعم:** admin@smart-merchant-tools.com")
