تمام، فهمت. سأعطيك الملف كاملاً جاهزاً للنسخ — انسخه كاملاً واحذف القديم واستبدله. لا تعدل أي سطر يدوياً.

طريقة الاستبدال من الجوال:

1. افتح ملف app.py في GitHub (على المتصفح)
2. اضغط أيقونة قلم التعديل ✏️
3. حدد كل المحتوى (اضغط مطولاً → تحديد الكل)
4. احذفه والصق الكود الجديد كاملاً
5. اضغط Commit changes

---

```python
import streamlit as st
import datetime
import pandas as pd
import urllib.parse

try:
    from dateutil.relativedelta import relativedelta
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False

st.set_page_config(
    page_title="أدوات التاجر الذكي",
    page_icon="💰",
    layout="centered"
)

st.markdown(
    "<style>footer {visibility: hidden;}</style>",
    unsafe_allow_html=True
)


def fmt(n, decimals=2):
    if n is None:
        return "0.00"
    return f"{n:,.{decimals}f}"


if "ecommerce_history" not in st.session_state:
    st.session_state.ecommerce_history = []

if "all_results" not in st.session_state:
    st.session_state.all_results = []


st.sidebar.title("🛠️ قائمة الأدوات")

tool_choice = st.sidebar.radio(
    "اختر الأداة",
    [
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
        "📊 لوحة التقارير الموحدة",
        "📄 القوالب الجاهزة",
        "📜 سياسة الخصوصية",
    ],
)


# ==========================================
# 1. حاسبة التجارة الإلكترونية
# ==========================================
if tool_choice == "📦 حاسبة التجارة الإلكترونية":
    st.title("📦 حاسبة أرباح التجارة الإلكترونية")
    st.write("احسب هوامش الربح الصافية بعد خصم الشحن ورسوم الدفع")

    currency = st.selectbox(
        "العملة",
        ["ر.س", "د.إ", "د.ك", "ر.ع", "ج.م", "$"],
        index=0,
    )

    col1, col2 = st.columns(2)

    with col1:
        cost_price = st.number_input(
            f"تكلفة المنتج ({currency})",
            min_value=0.0, value=50.0, step=1.0,
        )
        shipping_cost = st.number_input(
            f"تكلفة الشحن ({currency})",
            min_value=0.0, value=15.0, step=1.0,
        )

    with col2:
        selling_price = st.number_input(
            f"سعر البيع ({currency})",
            min_value=0.0, value=150.0, step=1.0,
        )
        gateway_fee_percent = st.number_input(
            "رسوم بوابة الدفع (%)",
            min_value=0.0, value=2.2, step=0.1,
        )

    fixed_fee = st.number_input(
        f"الرسوم الثابتة ({currency})",
        min_value=0.0, value=1.0, step=0.5,
    )

    total_item_cost = cost_price + shipping_cost
    payment_gateway_fees = (
        selling_price * (gateway_fee_percent / 100)
    ) + fixed_fee
    net_profit = selling_price - total_item_cost - payment_gateway_fees

    if selling_price > 0:
        margin = (net_profit / selling_price) * 100
    else:
        margin = 0

    st.divider()
    st.subheader("📊 ملخص الأرباح")

    res_col1, res_col2, res_col3, res_col4 = st.columns(4)

    res_col1.metric(
        "التكلفة الإجمالية",
        f"{fmt(total_item_cost)} {currency}",
    )
    res_col2.metric(
        "رسوم الدفع",
        f"{fmt(payment_gateway_fees)} {currency}",
    )
    res_col3.metric(
        "الربح الصافي",
        f"{fmt(net_profit)} {currency}",
        delta="ربح" if net_profit > 0 else "خسارة",
    )
    res_col4.metric("هامش الربح", f"{margin:.1f}%")

    if net_profit <= 0:
        st.warning("⚠️ هذا المنتج لا يحقق ربحاً! راجع التسعير.")

    st.divider()
    st.subheader("💾 سجل الحسابات")
    st.write("احفظ النتيجة لمقارنتها مع منتجات أخرى.")

    product_name = st.text_input(
        "اسم المنتج:",
        placeholder="مثال: سماعة بلوتوث",
    )

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

            result_entry = {
                "الأداة": "التجارة الإلكترونية",
                **record,
            }
            st.session_state.all_results.append(result_entry)

            st.toast(f"✅ تم حفظ '{product_name}'", icon="💾")
            st.rerun()

    if len(st.session_state.ecommerce_history) > 0:
        df_history = pd.DataFrame(st.session_state.ecommerce_history)
        st.dataframe(df_history, use_container_width=True)

        csv_data = df_history.to_csv(index=False).encode("utf-8-sig")

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            st.download_button(
                label="📥 تحميل السجل (CSV)",
                data=csv_data,
                file_name="Ecommerce_Calculations.csv",
                mime="text/csv",
            )

        with col_btn2:
            if st.button("🗑️ مسح السجل"):
                st.session_state.ecommerce_history = []
                st.rerun()


# ==========================================
# 2. حاسبة رسوم تابي وتمارا
# ==========================================
elif tool_choice == "💳 رسوم تابي وتمارا":
    st.title("💳 حاسبة رسوم الدفع الآجل")
    st.write("احسب المبلغ الصافي بعد خصم رسوم التقسيط والضريبة.")

    currency = st.selectbox(
        "العملة",
        ["ر.س", "د.إ", "د.ك", "ر.ع", "ج.م", "$"],
        index=0,
    )

    price = st.number_input(
        f"سعر المنتج ({currency})",
        min_value=0.0, value=100.0, step=1.0,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        fee_percent = st.number_input(
            "عمولة الشركة (%)",
            min_value=0.0, value=7.0, step=0.1,
        )

    with col2:
        fixed_fee = st.number_input(
            f"رسوم ثابتة ({currency})",
            min_value=0.0, value=1.5, step=0.5,
        )

    with col3:
        vat_on_fee = st.number_input(
            "ضريبة القيمة المضافة (%)",
            min_value=0.0, value=15.0, step=1.0,
        )

    fee_amount = (price * (fee_percent / 100)) + fixed_fee
    vat_amount = fee_amount * (vat_on_fee / 100)
    total_deduction = fee_amount + vat_amount
    net_to_merchant = price - total_deduction

    st.divider()

    c1, c2, c3 = st.columns(3)
    c1.metric("رسوم الشركة", f"{fmt(fee_amount)} {currency}")
    c2.metric("الضريبة", f"{fmt(vat_amount)} {currency}")
    c3.metric("إجمالي الخصم", f"{fmt(total_deduction)} {currency}")

    st.success(
        f"💰 الصافي للتاجر: **{fmt(net_to_merchant)} {currency}**"
    )


# ==========================================
# 3. صانع روابط واتساب
# ==========================================
elif tool_choice == "💬 صانع روابط واتساب":
    st.title("💬 صانع روابط واتساب")

    phone = st.text_input(
        "رقم الجوال (مع رمز الدولة):",
        placeholder="مثال: 966500000000",
    )
    msg = st.text_area(
        "الرسالة (اختياري):",
        placeholder="مرحباً، أود الاستفسار...",
    )

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
# 4. حاسبة القروض والأقساط
# ==========================================
elif tool_choice == "🏦 حاسبة القروض والأقساط":
    st.title("🏦 حاسبة القروض والأقساط")

    currency = st.selectbox(
        "العملة",
        ["ر.س", "د.إ", "د.ك", "ر.ع", "ج.م", "$"],
        index=0,
    )

    loan_amount = st.number_input(
        f"مبلغ القرض ({currency})",
        min_value=0.0, value=10000.0, step=100.0,
    )

    col1, col2 = st.columns(2)

    with col1:
        interest_rate = st.number_input(
            "الفائدة السنوية (%)",
            min_value=0.0, value=5.0, step=0.1,
        )

    with col2:
        months = st.number_input(
            "المدة (أشهر)",
            min_value=1, value=60, step=1,
        )

    st.divider()

    if loan_amount <= 0:
        st.warning("⚠️ أدخل مبلغ قرض صحيح.")
    elif months <= 0:
        st.warning("⚠️ عدد الأشهر يجب أن يكون > صفر.")
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

        st.info(f"💡 إجمالي المسدد: **{fmt(total_paid)} {currency}**")


# ==========================================
# 5. حاسبة زكاة المال
# ==========================================
elif tool_choice == "🕋 حاسبة زكاة المال":
    st.title("🕋 حاسبة زكاة المال")
    st.write("احسب مقدار الزكاة (2.5%).")

    nisab = st.number_input(
        "قيمة النصاب (اختياري):",
        min_value=0.0, value=0.0, step=100.0,
    )
    wealth = st.number_input(
        "إجمالي المال:",
        min_value=0.0, value=10000.0, step=100.0,
    )

    zakat_amount = wealth * 0.025

    st.divider()

    if nisab > 0 and wealth < nisab:
        st.warning(f"⚠️ مالك أقل من النصاب، لا زكاة.")
    else:
        st.metric("مقدار الزكاة", f"{fmt(zakat_amount)}")


# ==========================================
# 6. حاسبة الرواتب
# ==========================================
elif tool_choice == "💸 حاسبة الرواتب":
    st.title("💸 حاسبة الرواتب")

    currency = st.selectbox(
        "العملة",
        ["ر.س", "د.إ", "د.ك", "ر.ع", "ج.م", "$"],
        index=0,
    )

    basic_salary = st.number_input(
        f"الراتب الأساسي ({currency})",
        min_value=0.0, value=500.0, step=50.0,
    )

    col1, col2 = st.columns(2)

    with col1:
        allowances = st.number_input(
            f"البدلات ({currency})",
            min_value=0.0, value=0.0, step=50.0,
        )

    with col2:
        deductions = st.number_input(
            f"الخصومات ({currency})",
            min_value=0.0, value=0.0, step=50.0,
        )

    net_salary = basic_salary + allowances - deductions

    st.divider()

    if net_salary < 0:
        st.error("⚠️ الخصومات تتجاوز الراتب!")
    else:
        st.metric("💰 الراتب المستحق", f"{fmt(net_salary)} {currency}")


# ==========================================
# 7. حاسبة الدوام الدقيقة
# ==========================================
elif tool_choice == "📅 حاسبة الدوام الدقيقة":
    st.title("📅 حاسبة الدوام والراتب الدقيقة")

    currency = st.selectbox(
        "العملة",
        ["ر.س", "د.إ", "د.ك", "ر.ع", "ج.م", "$"],
        index=0,
    )

    monthly_salary = st.number_input(
        f"الراتب الشهري ({currency})",
        min_value=0.0, value=500.0, step=50.0,
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "تاريخ البداية:",
            value=datetime.date.today().replace(day=1),
        )
        start_time = st.time_input(
            "وقت البداية:",
            value=datetime.time(8, 0, 0),
        )

    with col2:
        end_date = st.date_input(
            "تاريخ النهاية:",
            value=datetime.date.today(),
        )
        end_time = st.time_input(
            "وقت النهاية:",
            value=datetime.time(16, 0, 0),
        )

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
# 8. توزيع مصاريف الشحن
# ==========================================
elif tool_choice == "⚖️ توزيع مصاريف الشحن":
    st.title("⚖️ توزيع مصاريف الشحن والجمارك")

    currency = st.selectbox(
        "العملة",
        ["ر.س", "د.إ", "د.ك", "ر.ع", "ج.م", "$"],
        index=0,
    )

    total_invoice = st.number_input(
        f"إجمالي الفاتورة ({currency})",
        min_value=0.01, value=1000.0, step=100.0,
    )
    total_expenses = st.number_input(
        f"إجمالي الشحن ({currency})",
        min_value=0.0, value=200.0, step=10.0,
    )
    item_price = st.number_input(
        f"سعر الصنف ({currency})",
        min_value=0.0, value=50.0, step=10.0,
    )

    if total_invoice > 0:
        expense_ratio = total_expenses / total_invoice
        item_expense = item_price * expense_ratio

        c1, c2, c3 = st.columns(3)
        c1.metric("نسبة المصاريف", f"{expense_ratio * 100:.2f}%")
        c2.metric("نصيب القطعة", f"{fmt(item_expense)} {currency}")
        c3.metric("التكلفة النهائية", f"{fmt(item_price + item_expense)} {currency}")


# ==========================================
# 9. حاسبة الخصومات
# ==========================================
elif tool_choice == "🏷️ حاسبة الخصومات":
    st.title("🏷️ حاسبة الخصومات")

    currency = st.selectbox(
        "العملة",
        ["ر.س", "د.إ", "د.ك", "ر.ع", "ج.م", "$"],
        index=0,
    )

    price_before = st.number_input(
        f"السعر الأساسي ({currency})",
        min_value=0.0, value=100.0, step=10.0,
    )

    discount_type = st.radio(
        "نوع الخصم:",
        ["نسبة مئوية (%)", "مبلغ ثابت"],
        horizontal=True,
    )

    if discount_type == "نسبة مئوية (%)":
        disc_percent = st.number_input(
            "نسبة الخصم (%)",
            min_value=0.0, max_value=100.0, value=20.0, step=1.0,
        )
        disc_amount = price_before * (disc_percent / 100)
    else:
        disc_amount = st.number_input(
            f"مبلغ الخصم ({currency})",
            min_value=0.0, max_value=price_before, value=20.0, step=5.0,
        )

    c1, c2 = st.columns(2)
    c1.metric("التوفير", f"{fmt(disc_amount)} {currency}")
    c2.metric("السعر النهائي", f"{fmt(price_before - disc_amount)} {currency}")


# ==========================================
# 10. حاسبة العمر
# ==========================================
elif tool_choice == "⏳ حاسبة العمر":
    st.title("⏳ حاسبة العمر الدقيقة")

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
# 11. نقطة التعادل
# ==========================================
elif tool_choice == "📉 حاسبة نقطة التعادل":
    st.title("📉 حاسبة نقطة التعادل")

    currency = st.selectbox(
        "العملة",
        ["ر.س", "د.إ", "د.ك", "ر.ع", "ج.م", "$"],
        index=0,
    )

    fixed_costs = st.number_input(
        f"المصاريف الثابتة ({currency})",
        min_value=0.0, value=1000.0, step=100.0,
    )
    variable_cost = st.number_input(
        f"تكلفة القطعة ({currency})",
        min_value=0.0, value=50.0, step=5.0,
    )
    sell_price = st.number_input(
        f"سعر البيع ({currency})",
        min_value=0.0, value=100.0, step=5.0,
    )

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
# 12. الضريبة VAT
# ==========================================
elif tool_choice == "🧾 حاسبة الضريبة VAT":
    st.title("🧾 حاسبة ضريبة القيمة المضافة")

    currency = st.selectbox(
        "العملة",
        ["ر.س", "د.إ", "د.ك", "ر.ع", "ج.م", "$"],
        index=0,
    )

    calc_mode = st.radio(
        "طريقة الحساب:",
        ["إضافة الضريبة", "استخراج الضريبة"],
        horizontal=True,
    )

    price = st.number_input(
        f"المبلغ ({currency})",
        min_value=0.0, value=1000.0, step=100.0,
    )
    vat_rate = st.number_input(
        "نسبة الضريبة (%)",
        min_value=0.0, value=15.0, step=1.0,
    )

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
# 13. أرباح الكريبتو
# ==========================================
elif tool_choice == "📈 حاسبة أرباح الكريبتو":
    st.title("📈 حاسبة أرباح الكريبتو")

    entry_price = st.number_input(
        "سعر الدخول ($)",
        min_value=0.0, value=60000.0, step=100.0,
    )
    amount = st.number_input(
        "الكمية",
        min_value=0.0, value=0.1, step=0.01, format="%.4f",
    )
    exit_price = st.number_input(
        "سعر الخروج ($)",
        min_value=0.0, value=62000.0, step=100.0,
    )
    fee = st.number_input(
        "رسوم المنصة (%)",
        min_value=0.0, value=0.1, step=0.05,
    )

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
    c3.metric(
        "الربح الصافي",
        f"${fmt(net_profit)}",
        delta=f"{roi:.2f}%" if net_profit != 0 else None,
    )


# ==========================================
# 14. إدارة المخاطر
# ==========================================
elif tool_choice == "🛡️ حاسبة إدارة المخاطر":
    st.title("🛡️ حاسبة إدارة المخاطر")

    capital = st.number_input(
        "حجم المحفظة (USDT)",
        min_value=0.0, value=1000.0, step=100.0,
    )
    risk_percent = st.number_input(
        "المخاطرة (%)",
        min_value=0.0, value=2.0, step=0.5,
    )

    col_x, col_y = st.columns(2)

    with col_x:
        entry_p = st.number_input(
            "سعر الدخول",
            min_value=0.0, value=50000.0, step=100.0,
        )

    with col_y:
        stop_loss = st.number_input(
            "وقف الخسارة",
            min_value=0.0, value=48000.0, step=100.0,
        )

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
# 15. لوحة التقارير
# ==========================================
elif tool_choice == "📊 لوحة التقارير الموحدة":
    st.title("📊 لوحة التقارير الموحدة")
    st.write("جميع النتائج المحفوظة في مكان واحد.")

    if len(st.session_state.all_results) == 0:
        st.info("ℹ️ لا توجد نتائج محفوظة بعد.")
    else:
        df_all = pd.DataFrame(st.session_state.all_results)
        st.dataframe(df_all, use_container_width=True)

        csv_all = df_all.to_csv(index=False).encode("utf-8-sig")

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "📥 تحميل التقرير (CSV)",
                data=csv_all,
                file_name="Full_Report.csv",
                mime="text/csv",
            )

        with col2:
            if st.button("🗑️ مسح الكل"):
                st.session_state.all_results = []
                st.session_state.ecommerce_history = []
                st.rerun()


# ==========================================
# 16. القوالب الجاهزة
# ==========================================
elif tool_choice == "📄 القوالب الجاهزة":
    st.title("📄 قوالب محاسبية وتجارية")
    st.write("قوالب CSV جاهزة للفتح في Excel.")

    with st.expander("📒 دفتر أستاذ الموردين", expanded=True):
        suppliers_csv = (
            "التاريخ,المورد,الفاتورة,البيان,مدين,دائن,الرصيد\n"
            "2025-01-01,مورد أ,INV-001,شراء,1000.00,,1000.00\n"
            "2025-01-05,مورد أ,PAY-001,سداد,,500.00,500.00\n"
            "2025-01-10,مورد ب,INV-002,شراء,750.00,,1250.00\n"
            ",,الإجمالي,,1750.00,500.00,1250.00\n"
        ).encode("utf-8-sig")

        st.download_button(
            "📥 تحميل القالب",
            data=suppliers_csv,
            file_name="suppliers_ledger.csv",
            mime="text/csv",
            key="dl_suppliers",
        )

    with st.expander("📦 جرد المخزون"):
        inventory_csv = (
            "الكود,الصنف,الوحدة,دفتر,فعلي,الفرق,التكلفة,القيمة\n"
            "SKU-001,سماعة,قطعة,100,98,-2,50.00,4900.00\n"
            "SKU-002,شاحن,قطعة,200,200,0,25.00,5000.00\n"
            "SKU-003,كابل,قطعة,500,495,-5,8.00,3960.00\n"
            ",,الإجمالي,,,,-,13860.00\n"
        ).encode("utf-8-sig")

        st.download_button(
            "📥 تحميل القالب",
            data=inventory_csv,
            file_name="inventory_template.csv",
            mime="text/csv",
            key="dl_inventory",
        )

    with st.expander("🧾 فاتورة مبيعات"):
        invoice_csv = (
            "بند,الوصف,الكمية,السعر,الإجمالي,الضريبة,الإجمالي مع الضريبة\n"
            "1,منتج أ,2,100.00,200.00,30.00,230.00\n"
            "2,منتج ب,1,150.00,150.00,22.50,172.50\n"
            "3,تركيب,1,50.00,50.00,7.50,57.50\n"
            ",الإجمالي,,,400.00,60.00,460.00\n"
        ).encode("utf-8-sig")

        st.download_button(
            "📥 تحميل القالب",
            data=invoice_csv,
            file_name="sales_invoice.csv",
            mime="text/csv",
            key="dl_invoice",
        )

    with st.expander("💸 سجل المصروفات"):
        expenses_csv = (
            "التاريخ,البند,الوصف,المبلغ,الدفع\n"
            "2025-01-01,إيجار,المكتب,3000.00,تحويل\n"
            "2025-01-03,رواتب,الفريق,15000.00,تحويل\n"
            "2025-01-05,شحن,عملاء,450.00,بطاقة\n"
            "2025-01-10,تسويق,إعلانات,1200.00,بطاقة\n"
            ",الإجمالي,,19650.00,\n"
        ).encode("utf-8-sig")

        st.download_button(
            "📥 تحميل القالب",
            data=expenses_csv,
            file_name="expenses_log.csv",
            mime="text/csv",
            key="dl_expenses",
        )

    with st.expander("💰 تسعير المنتجات"):
        pricing_csv = (
            "المنتج,التكلفة,الشحن,الرسوم,هامش %,السعر,الربح\n"
            "سماعة,50.00,15.00,4.30,40,140.00,70.70\n"
            "شاحن,25.00,10.00,2.50,50,90.00,52.50\n"
            "كابل,8.00,5.00,1.20,60,40.00,25.80\n"
        ).encode("utf-8-sig")

        st.download_button(
            "📥 تحميل القالب",
            data=pricing_csv,
            file_name="pricing_template.csv",
            mime="text/csv",
            key="dl_pricing",
        )

    st.divider()
    st.info("💡 افتح ملفات CSV في Excel مباشرة.")


# ==========================================
# 17. الخصوصية
# ==========================================
elif tool_choice == "📜 سياسة الخصوصية":
    st.title("📜 سياسة الخصوصية")

    st.info("🔒 جميع العمليات تُحسب محلياً في متصفحك.")

    st.subheader("📋 التزاماتنا:")
    st.markdown(
        "- ✅ لا نجمع بيانات شخصية.\n"
        "- ✅ لا نستخدم تتبع أو إعلانات.\n"
        "- ✅ البيانات مؤقتة وتُمسح بإغلاق الصفحة.\n"
        "- ✅ الأداة للأغراض التعليمية.\n"
    )

    st.subheader("⚠️ إخلاء المسؤولية:")
    st.warning(
        "النتائج إرشادية فقط. راجع مختصاً مالياً للقرارات المهمة."
    )

    st.divider()
    st.write("**📧 للتواصل:** admin@smart-merchant-tools.com")
```

---

✅ ملاحظات مهمة لتنجح من الجوال

1. الخطأ السابق أُصلح تماماً — لم يعد هناك سطر يبدأ بـ )}#.
2. تحسين إضافي: أضفت try/except لمكتبة dateutil — فلو لم تكن مثبتة على Streamlit Cloud، الكود سيعمل تلقائياً بحساب بديل. (لكن الأفضل أن تضيفها).
3. لتثبيت مكتبة dateutil (لمزيد دقة في حاسبة العمر):
   · اذهب لملف requirements.txt في مستودعك على GitHub
   · أضف سطراً جديداً فيه:
   ```
   python-dateutil
   ```
   · احفظ الملف (Commit)
4. بعد اللصق، اضغط Commit changes وسيُعيد Streamlit Cloud تشغيل التطبيق تلقائياً خلال دقيقة.

هل تريد أيضاً أن أرسل لك محتوى ملف requirements.txt كاملاً جاهزاً؟
