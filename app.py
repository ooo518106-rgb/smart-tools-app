import streamlit as st

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="أدوات التاجر الذكي", page_icon="💰", layout="centered")

# القائمة الجانبية
st.sidebar.title("🛠️ قائمة الأدوات")
tool_choice = st.sidebar.radio("اختر الأداة:", [
    "📦 حاسبة التجارة الإلكترونية",
    "📉 حاسبة نقطة التعادل (جديد)",
    "🧾 حاسبة الضريبة VAT (جديد)",
    "📈 حاسبة أرباح الكريبتو",
    "🛡️ حاسبة إدارة المخاطر (جديد)",
    "📄 القوالب الجاهزة (مجاناً)",
    "📜 سياسة الخصوصية"
])

# ==========================================
# 1. حاسبة التجارة الإلكترونية (الدروبشيبينغ)
# ==========================================
if tool_choice == "📦 حاسبة التجارة الإلكترونية":
    st.title("📦 حاسبة أرباح التجارة الإلكترونية")
    st.write("احسب هوامش الربح الصافية بعد خصم تكاليف الشحن ورسوم بوابات الدفع.")
    col1, col2 = st.columns(2)
    with col1:
        cost_price = st.number_input("تكلفة المنتج من المورد:", min_value=0.0, value=50.0)
        shipping_cost = st.number_input("تكلفة الشحن والتغليف:", min_value=0.0, value=15.0)
    with col2:
        selling_price = st.number_input("سعر البيع للعميل:", min_value=0.0, value=150.0)
        gateway_fee_percent = st.number_input("رسوم بوابة الدفع (%):", min_value=0.0, value=2.2)
    fixed_fee = st.number_input("الرسوم الثابتة للعملية:", min_value=0.0, value=1.0)
    
    total_item_cost = cost_price + shipping_cost
    payment_gateway_fees = (selling_price * (gateway_fee_percent / 100)) + fixed_fee
    net_profit = selling_price - total_item_cost - payment_gateway_fees
    
    st.divider()
    st.subheader("📊 ملخص الأرباح")
    st.write(f"إجمالي تكلفة المنتج الواصل: **{total_item_cost:.2f}**")
    st.write(f"إجمالي الرسوم المخصومة: **{payment_gateway_fees:.2f}**")
    if net_profit > 0:
        st.success(f"الربح الصافي: {net_profit:.2f}")
    elif net_profit < 0:
        st.error(f"خسارة بقيمة: {net_profit:.2f}")

# ==========================================
# 2. حاسبة نقطة التعادل (للتجار والمحاسبين)
# ==========================================
elif tool_choice == "📉 حاسبة نقطة التعادل (جديد)":
    st.title("📉 حاسبة نقطة التعادل (Break-Even)")
    st.write("اعرف كم قطعة تحتاج أن تبيع لتغطية مصاريفك الثابتة (مثل الإيجار والاشتراكات) والبدء في تحقيق الأرباح، مما يسهل عليك بناء خطة المبيعات وتوجيه قيودك في النظام المحاسبي.")
    
    fixed_costs = st.number_input("إجمالي المصاريف الثابتة (شهرياً):", min_value=0.0, value=1000.0)
    col1, col2 = st.columns(2)
    with col1:
        variable_cost = st.number_input("تكلفة القطعة الواحدة (عليك):", min_value=0.0, value=50.0)
    with col2:
        sell_price = st.number_input("سعر بيع القطعة للعميل:", min_value=0.0, value=100.0)
        
    st.divider()
    if sell_price > variable_cost:
        break_even_units = fixed_costs / (sell_price - variable_cost)
        break_even_revenue = break_even_units * sell_price
        st.success(f"📌 تحتاج لبيع: **{break_even_units:.0f} قطعة** لتغطية تكاليفك.")
        st.info(f"💰 إجمالي المبيعات المطلوبة لنقطة التعادل: **{break_even_revenue:.2f}**")
    else:
        st.error("سعر البيع يجب أن يكون أعلى من تكلفة القطعة لكي يكون هناك نقطة تعادل!")

# ==========================================
# 3. حاسبة ضريبة القيمة المضافة (VAT)
# ==========================================
elif tool_choice == "🧾 حاسبة الضريبة VAT (جديد)":
    st.title("🧾 حاسبة ضريبة القيمة المضافة (VAT)")
    st.write("أداة سريعة لحساب الضريبة للسوق الخليجي (إضافة الضريبة أو استخراجها).")
    
    price = st.number_input("المبلغ:", min_value=0.0, value=1000.0)
    vat_rate = st.number_input("نسبة الضريبة (%):", min_value=0.0, value=15.0)
    vat_type = st.radio("نوع الحسبة:", ["إضافة الضريبة على المبلغ (المبلغ غير شامل)", "استخراج الضريبة من المبلغ (المبلغ شامل الضريبة)"])
    
    st.divider()
    if vat_type == "إضافة الضريبة على المبلغ (المبلغ غير شامل)":
        vat_amount = price * (vat_rate / 100)
        total_price = price + vat_amount
        st.success(f"قيمة الضريبة: **{vat_amount:.2f}**")
        st.info(f"المبلغ الإجمالي (بعد الضريبة): **{total_price:.2f}**")
    else:
        base_price = price / (1 + (vat_rate / 100))
        vat_amount = price - base_price
        st.success(f"المبلغ الأساسي (قبل الضريبة): **{base_price:.2f}**")
        st.info(f"قيمة الضريبة المستقطعة: **{vat_amount:.2f}**")

# ==========================================
# 4. حاسبة أرباح الكريبتو
# ==========================================
elif tool_choice == "📈 حاسبة أرباح الكريبتو":
    st.title("📈 حاسبة أرباح التداول والعملات الرقمية")
    st.write("احسب أرباحك الصافية بعد خصم عمولات منصات التداول (مثل Binance).")
    col_a, col_b = st.columns(2)
    with col_a:
        entry_price = st.number_input("سعر الدخول (الشراء):", min_value=0.0, value=60000.0)
        amount = st.number_input("الكمية (عدد الحبات):", min_value=0.0, value=0.1, step=0.01)
    with col_b:
        exit_price = st.number_input("سعر الخروج (البيع):", min_value=0.0, value=62000.0)
        trading_fee = st.number_input("رسوم المنصة (%):", min_value=0.0, value=0.1)
        
    total_buy = entry_price * amount
    total_sell = exit_price * amount
    fee_buy = total_buy * (trading_fee / 100)
    fee_sell = total_sell * (trading_fee / 100)
    total_fees = fee_buy + fee_sell
    net_crypto_profit = (total_sell - total_buy) - total_fees
    
    st.divider()
    st.subheader("📊 ملخص صفقة التداول")
    st.write(f"رأس المال المستثمر: **{total_buy:.2f}** | إجمالي الرسوم: **{total_fees:.2f}**")
    if net_crypto_profit > 0:
        st.success(f"الربح الصافي للصفقة: {net_crypto_profit:.2f}")
    elif net_crypto_profit < 0:
        st.error(f"خسارة الصفقة: {net_crypto_profit:.2f}")

# ==========================================
# 5. حاسبة إدارة المخاطر للكريبتو
# ==========================================
elif tool_choice == "🛡️ حاسبة إدارة المخاطر (جديد)":
    st.title("🛡️ حاسبة إدارة المخاطر (Position Sizing)")
    st.write("اعرف حجم الكمية المناسبة للشراء بناءً على نسبة المخاطرة التي تتحملها في محفظتك (لتجنب تصفية الحساب).")
    
    capital = st.number_input("حجم المحفظة الإجمالي (USDT):", min_value=0.0, value=1000.0)
    risk_percent = st.number_input("المخاطرة المسموحة للصفقة (%):", min_value=0.0, value=2.0)
    col_x, col_y = st.columns(2)
    with col_x:
        entry_p = st.number_input("سعر الدخول المستهدف:", min_value=0.0, value=50000.0)
    with col_y:
        stop_loss = st.number_input("سعر وقف الخسارة (Stop Loss):", min_value=0.0, value=48000.0)
        
    st.divider()
    risk_amount = capital * (risk_percent / 100)
    st.write(f"المبلغ المعرض للمخاطرة (في حال ضرب الوقف): **{risk_amount:.2f} USDT**")
    
    if entry_p > 0 and stop_loss > 0 and entry_p != stop_loss:
        position_size = risk_amount / abs(entry_p - stop_loss)
        position_value = position_size * entry_p
        st.success(f"الكمية المسموح شراؤها: **{position_size:.4f} حبة**")
        st.info(f"حجم الصفقة بالدولار: **{position_value:.2f} USDT**")
    else:
        st.warning("يرجى إدخال أسعار دخول ووقف خسارة صحيحة ومختلفة.")

# ==========================================
# 6. القوالب الجاهزة
# ==========================================
elif tool_choice == "📄 القوالب الجاهزة (مجاناً)":
    st.title("📄 قوالب محاسبية وتجارية جاهزة")
    st.write("نماذج مصممة لتسهيل ترحيل أرصدتك وتكاليفك إلى نظامك المحاسبي.")
    st.subheader("1. قالب دفتر أستاذ الموردين (Excel)")
    st.download_button("📥 تحميل قالب الموردين", "عينة", "suppliers.csv")
    st.subheader("2. نموذج جرد المخزون الدوري (PDF)")
    st.download_button("📥 تحميل نموذج الجرد", "عينة", "inventory.txt")

# ==========================================
# 7. سياسة الخصوصية
# ==========================================
elif tool_choice == "📜 سياسة الخصوصية":
    st.title("📜 سياسة الخصوصية وإخلاء المسؤولية")
    st.write("العمليات الحسابية تتم محلياً على متصفحك. نحن لا نقوم بجمع أو حفظ بياناتك المالية.")
    st.write("الموقع يستخدم خدمات أطراف ثالثة (Google AdSense) لعرض الإعلانات.")
    st.write("**للتواصل:** admin@smart-merchant-tools.com")
