import streamlit as st

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="أدوات التاجر الذكي", page_icon="💰", layout="centered")

# إنشاء القائمة الجانبية للتنقل بين الأدوات
st.sidebar.title("🛠️ قائمة الأدوات")
tool_choice = st.sidebar.radio("اختر الأداة:", ["حاسبة التجارة الإلكترونية", "حاسبة أرباح التداول"])

# ==========================================
# الأداة الأولى: حاسبة التجارة الإلكترونية
# ==========================================
if tool_choice == "حاسبة التجارة الإلكترونية":
    st.title("📦 حاسبة أرباح التجارة الإلكترونية")
    st.write("أداة سريعة لحساب هوامش الربح الصافية بعد خصم تكاليف الشحن ورسوم بوابات الدفع الإلكتروني.")
    
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
        
    # العمليات الحسابية للتداول
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
