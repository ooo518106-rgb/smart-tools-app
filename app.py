import streamlit as st

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="أدوات التاجر الذكي", page_icon="💰", layout="centered")

# إنشاء القائمة الجانبية
st.sidebar.title("🛠️ قائمة الأدوات")
tool_choice = st.sidebar.radio("اختر الصفحة:", [
    "حاسبة التجارة الإلكترونية", 
    "حاسبة أرباح التداول", 
    "القوالب الجاهزة (مجاناً)",
    "سياسة الخصوصية (Privacy Policy)"
])

# ==========================================
# الأداة الأولى: حاسبة التجارة الإلكترونية
# ==========================================
if tool_choice == "حاسبة التجارة الإلكترونية":
    st.title("📦 حاسبة أرباح التجارة الإلكترونية")
    st.write("أداة سريعة لحساب هوامش الربح الصافية للمتاجر الإلكترونية بعد خصم تكاليف الشحن ورسوم بوابات الدفع.")
    
    col1, col2 = st.columns(2)
    with col1:
        cost_price = st.number_input("تكلفة المنتج من المورد:", min_value=0.0, value=50.0)
        shipping_cost = st.number_input("تكلفة الشحن والتغليف:", min_value=0.0, value=15.0)
    with col2:
        selling_price = st.number_input("سعر البيع للعميل:", min_value=0.0, value=150.0)
        gateway_fee_percent = st.number_input("نسبة رسوم بوابة الدفع (%):", min_value=0.0, value=2.2)
    
    fixed_fee = st.number_input("الرسوم الثابتة للعملية:", min_value=0.0, value=1.0)
    
    total_item_cost = cost_price + shipping_cost
    payment_gateway_fees = (selling_price * (gateway_fee_percent / 100)) + fixed_fee
    net_profit = selling_price - total_item_cost - payment_gateway_fees
    
    st.divider()
    st.subheader("📊 ملخص الأرباح")
    st.write(f"إجمالي تكلفة المنتج الواصل: **{total_item_cost:.2f}**")
    st.write(f"إجمالي رسوم الدفع المخصومة: **{payment_gateway_fees:.2f}**")
    if net_profit > 0:
        st.success(f"الربح الصافي للقطعة الواحدة: {net_profit:.2f}")
    elif net_profit < 0:
        st.error(f"انتباه! هناك خسارة بقيمة: {net_profit:.2f}")

# ==========================================
# الأداة الثانية: حاسبة تداول العملات الرقمية
# ==========================================
elif tool_choice == "حاسبة أرباح التداول":
    st.title("📈 حاسبة أرباح التداول والعملات الرقمية")
    st.write("احسب أرباحك الصافية من الصفقات بعد خصم عمولات منصات التداول.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        entry_price = st.number_input("سعر الدخول (الشراء):", min_value=0.0, value=60000.0)
        amount = st.number_input("الكمية (عدد الحبات):", min_value=0.0, value=0.1, step=0.01)
    with col_b:
        exit_price = st.number_input("سعر الخروج (البيع):", min_value=0.0, value=62000.0)
        trading_fee = st.number_input("رسوم المنصة (%):", min_value=0.0, value=0.1, help="رسوم التداول المعتادة في منصة Binance هي 0.1%")
        
    total_buy = entry_price * amount
    total_sell = exit_price * amount
    
    fee_buy = total_buy * (trading_fee / 100)
    fee_sell = total_sell * (trading_fee / 100)
    total_fees = fee_buy + fee_sell
    
    net_crypto_profit = (total_sell - total_buy) - total_fees
    
    st.divider()
    st.subheader("📊 ملخص صفقة التداول")
    st.write(f"رأس المال المستثمر (قيمة الشراء): **{total_buy:.2f}**")
    st.write(f"إجمالي رسوم المنصة (بيع وشراء): **{total_fees:.2f}**")
    
    if net_crypto_profit > 0:
        st.success(f"الربح الصافي للصفقة: {net_crypto_profit:.2f}")
    elif net_crypto_profit < 0:
        st.error(f"خسارة الصفقة: {net_crypto_profit:.2f}")
    else:
        st.warning("الخروج على نقطة الدخول (نقطة التعادل).")

# ==========================================
# الأداة الثالثة: القوالب الجاهزة للتحميل
# ==========================================
elif tool_choice == "القوالب الجاهزة (مجاناً)":
    st.title("📄 قوالب محاسبية وتجارية جاهزة للتحميل")
    st.write("مجموعة من النماذج المصممة لضبط حسابات متجرك وتسهيل ترحيل الأرصدة وتكاليف المنتجات إلى نظامك المحاسبي.")
    st.divider()
    st.subheader("1. قالب دفتر أستاذ الموردين (Excel)")
    st.download_button(label="📥 تحميل قالب الموردين", data="عينة", file_name="suppliers_ledger_template.csv")
    st.subheader("2. نموذج جرد المخزون الدوري (PDF)")
    st.download_button(label="📥 تحميل نموذج الجرد", data="عينة", file_name="inventory_template.txt")
    st.subheader("3. كشف مطابقة رصيد (Word)")
    st.download_button(label="📥 تحميل كشف المطابقة", data="عينة", file_name="balance_statement.txt")

# ==========================================
# القسم الرابع: سياسة الخصوصية (أساسي لـ AdSense)
# ==========================================
elif tool_choice == "سياسة الخصوصية (Privacy Policy)":
    st.title("📜 سياسة الخصوصية وإخلاء المسؤولية")
    st.write("نحن في **أدوات التاجر الذكي** نولي خصوصيتك أهمية قصوى ونلتزم بحماية بياناتك.")
    
    st.subheader("1. جمع البيانات واستخدامها")
    st.write("جميع العمليات الحسابية التي تقوم بها على هذا الموقع (مثل حساب تكاليف الدروبشيبينغ أو صفقات الكريبتو) تتم محلياً على متصفحك. نحن **لا نقوم بجمع أو حفظ أو تخزين** أي أرقام، أسعار، أو بيانات مالية تدخلها في الحاسبات.")
    
    st.subheader("2. ملفات تعريف الارتباط (Cookies) والإعلانات")
    st.write("يستخدم هذا الموقع ملفات تعريف الارتباط (Cookies) وخدمات أطراف ثالثة مثل **Google AdSense** لعرض إعلانات مخصصة ومناسبة لاهتماماتك. يمكنك في أي وقت تعديل إعدادات الإعلانات من خلال حسابك في جوجل.")
    
    st.subheader("3. إخلاء المسؤولية المالية (Disclaimer)")
    st.write("الأدوات والنتائج المقدمة في هذا الموقع هي لأغراض تقديرية ومساعدة فقط لتسهيل عملياتك التجارية. يجب عليك دائماً مراجعة الأرقام ومطابقتها مع نظامك المحاسبي المعتمد (مثل نظام فينيكس المحاسبي أو غيره) لضمان دقة قيود المشتريات والمصروفات بالكامل.")
    
    st.subheader("📬 اتصل بنا")
    st.write("إذا كان لديك أي استفسار أو اقتراح لتطوير أدوات جديدة تخدم تجار السوق الخليجي، يسعدنا تواصلك معنا عبر البريد الإلكتروني:")
    st.write("**admin@smart-merchant-tools.com**")
