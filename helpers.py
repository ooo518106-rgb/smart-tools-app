import streamlit as st
import pandas as pd
import datetime
import urllib.parse
import json
import os
from io import BytesIO

CURRENCY_NAMES_AR = {
    "USD": "دولار أمريكي", "SAR": "ريال سعودي", "AED": "درهم إماراتي",
    "KWD": "دينار كويتي", "OMR": "ريال عماني", "QAR": "ريال قطري",
    "BHD": "دينار بحريني", "EGP": "جنيه مصري", "JOD": "دينار أردني",
    "LBP": "ليرة لبنانية", "SYP": "ليرة سورية", "IQD": "دينار عراقي",
    "YER": "ريال يمني", "MAD": "درهم مغربي", "DZD": "دينار جزائري",
    "TND": "دينار تونسي", "LYD": "دينار ليبي", "SDG": "جنيه سوداني",
    "EUR": "يورو", "GBP": "جنيه إسترليني", "CHF": "فرنك سويسري",
    "TRY": "ليرة تركية", "IRR": "ريال إيراني", "PKR": "روبية باكستانية",
    "INR": "روبية هندية", "BDT": "تاكا بنغلاديشية", "IDR": "روبية إندونيسية",
    "MYR": "رينغيت ماليزي", "SGD": "دولار سنغافوري", "THB": "بات تايلندي",
    "PHP": "بيزو فلبيني", "VND": "دونغ فيتنامي", "CNY": "يوان صيني",
    "JPY": "ين ياباني", "KRW": "وون كوري", "HKD": "دولار هونغ كونغ",
    "TWD": "دولار تايواني", "AUD": "دولار أسترالي", "NZD": "دولار نيوزيلندي",
    "CAD": "دولار كندي", "MXN": "بيزو مكسيكي", "BRL": "ريال برازيلي",
    "ARS": "بيزو أرجنتيني", "CLP": "بيزو تشيلي", "COP": "بيزو كولومبي",
    "PEN": "سول بيروفي", "SEK": "كرونة سويدية", "NOK": "كرونة نرويجية",
    "DKK": "كرونة دنماركية", "PLN": "زلوتي بولندي", "CZK": "كرونة تشيكية",
    "HUF": "فورنت مجري", "RON": "ليو روماني", "BGN": "ليف بلغاري",
    "RUB": "روبل روسي", "UAH": "هريفنيا أوكرانية", "GEL": "لاري جورجي",
    "KZT": "تينغي كازاخستاني", "ILS": "شيكل إسرائيلي", "ZAR": "راند جنوب أفريقي",
    "NGN": "نايرا نيجيري", "KES": "شلن كيني", "GHS": "سيدي غاني",
    "MUR": "روبية موريشيوسية",
}


def currency_label(code):
    name = CURRENCY_NAMES_AR.get(code, "")
    if name:
        return f"{code} - {name}"
    return code


def money(v, cur="", decimals=2):
    if v is None:
        return "0.00"
    try:
        s = f"{v:,.{decimals}f}"
    except (ValueError, TypeError):
        s = str(v)
    return f"{s} {cur}".strip() if cur else s


def save_result(tool_name, **data):
    if "all_results" not in st.session_state:
        st.session_state.all_results = []
    record = {
        "الأداة": tool_name,
        "التاريخ": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        **data,
    }
    st.session_state.all_results.append(record)
    st.toast("تم الحفظ", icon="💾")


def quick_save_button(key, tool_name, data_dict):
    if st.button("💾 حفظ النتيجة", key=f"qsave_{key}", use_container_width=True):
        save_result(tool_name, **data_dict)
        st.rerun()


def copy_box(text, label="📋 نسخ النتيجة"):
    with st.expander(label):
        st.code(text, language="")


def share_buttons(text, title="نتيجتي"):
    encoded = urllib.parse.quote(text)
    wa = f"https://wa.me/?text={encoded}"
    tw = f"https://twitter.com/intent/tweet?text={encoded}"
    tg = f"https://t.me/share/url?url=&text={encoded}"

    st.markdown(
        '<p style="font-weight:700; margin-top:16px; color:#64748b;">📤 مشاركة النتيجة</p>',
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<a href="' + wa + '" target="_blank" class="share-btn" '
            'style="background:#25D366;">واتساب</a>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            '<a href="' + tw + '" target="_blank" class="share-btn" '
            'style="background:#1DA1F2;">تويتر</a>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<a href="' + tg + '" target="_blank" class="share-btn" '
            'style="background:#0088cc;">تيليجرام</a>',
            unsafe_allow_html=True,
        )


@st.cache_data(ttl=3600)
def fetch_currency_rates():
    fallback = {
        "USD": 1.0, "SAR": 3.75, "AED": 3.67, "KWD": 0.31,
        "OMR": 0.385, "EGP": 48.5, "EUR": 0.92, "GBP": 0.79,
        "QAR": 3.64, "BHD": 0.376, "JOD": 0.71, "TRY": 34.5,
        "CNY": 7.25, "JPY": 155.0, "INR": 84.0, "PKR": 278.0,
    }
    try:
        import requests
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=8)
        data = r.json()
        if data.get("result") == "success":
            rates = data.get("rates", {})
            if rates:
                return rates
    except Exception:
        pass
    return fallback


def export_to_excel(df_dict, filename="report.xlsx"):
    try:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            for sheet_name, df in df_dict.items():
                safe_name = str(sheet_name)
                for ch in ["/", "\\", "?", "*", "[", "]", ":"]:
                    safe_name = safe_name.replace(ch, "-")
                safe_name = safe_name.strip()[:31]
                if not safe_name:
                    safe_name = "Sheet"
                df.to_excel(writer, sheet_name=safe_name, index=False)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"خطأ في التصدير: {e}")
        return None


def page_header(icon, title, subtitle=""):
    html = (
        '<div class="page-hero">'
        '<div class="page-hero-icon">' + icon + '</div>'
        '<h1 class="page-title">' + title + '</h1>'
    )
    if subtitle:
        html += '<p class="page-subtitle">' + subtitle + '</p>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def check_pin():
    correct = ""
    try:
        correct = st.secrets.get("APP_PIN", "")
    except Exception:
        correct = ""

    if not correct:
        return True

    if st.session_state.get("pin_ok"):
        return True

    st.markdown("### 🔐 التطبيق محمي")
    pin = st.text_input("أدخل الرمز:", type="password", key="pin_input")
    if st.button("🚀 دخول", use_container_width=True):
        if pin == correct:
            st.session_state.pin_ok = True
            st.rerun()
        else:
            st.error("❌ رمز خاطئ")
    return False


def render_reminders():
    reminders = st.session_state.get("reminders", [])
    today = datetime.date.today()

    st.subheader("🔔 التنبيهات")

    with st.expander("➕ إضافة تنبيه جديد", expanded=False):
        rtext = st.text_input("نص التنبيه:", key="rtext")
        rdate = st.date_input(
            "التاريخ:",
            value=today + datetime.timedelta(days=7),
            key="rdate",
        )
        if st.button("➕ إضافة", key="add_rem_btn", use_container_width=True):
            if rtext.strip():
                reminders.append({"text": rtext.strip(), "date": str(rdate)})
                st.session_state.reminders = reminders
                st.rerun()

    if not reminders:
        st.info("لا توجد تنبيهات حالياً")
        return

    for r in sorted(reminders, key=lambda x: x["date"]):
        try:
            r_date = datetime.date.fromisoformat(r["date"])
        except Exception:
            continue
        delta = (r_date - today).days
        if delta < 0:
            st.error(f"⚠️ متأخر! {r['text']} ({r['date']})")
        elif delta == 0:
            st.warning(f"⏰ اليوم! {r['text']}")
        elif delta <= 7:
            st.info(f"📅 {r['text']} — بعد {delta} يوم")


def get_hijri_date():
    try:
        from hijri_converter import Gregorian
        today = datetime.date.today()
        h = Gregorian(today.year, today.month, today.day).to_hijri()
        months_ar = [
            "محرم", "صفر", "ربيع الأول", "ربيع الثاني",
            "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان",
            "رمضان", "شوال", "ذو القعدة", "ذو الحجة",
        ]
        return f"{h.day} {months_ar[h.month - 1]} {h.year} هـ"
    except Exception:
        return ""


def print_button(text_to_print, label="🖨️ طباعة"):
    import streamlit.components.v1 as components
    text_json = json.dumps(text_to_print)
    html = (
        '<button onclick="printContent()" '
        'style="background:linear-gradient(135deg,#6366f1,#ec4899);'
        'color:white;border:none;border-radius:14px;padding:12px 20px;'
        'font-weight:700;width:100%;cursor:pointer;font-family:Cairo;'
        'font-size:0.95rem;">' + label + '</button>'
        '<script>'
        'function printContent() {'
        '  var text = ' + text_json + ';'
        '  var w = window.open("", "", "width=800,height=600");'
        '  w.document.write("<html dir=\'rtl\'><head><title>طباعة</title>");'
        '  w.document.write("<style>body{font-family:Cairo,Arial;padding:40px;line-height:2;}pre{white-space:pre-wrap;font-size:16px;}</style>");'
        '  w.document.write("</head><body><h2>أدوات التاجر الذكي</h2><pre>");'
        '  w.document.write(text);'
        '  w.document.write("</pre></body></html>");'
        '  w.document.close();'
        '  setTimeout(function(){w.print();}, 300);'
        '}'
        '</script>'
    )
    components.html(html, height=70)


def _download_font_ar():
    font_path = "/tmp/Amiri-Regular.ttf"
    if os.path.exists(font_path):
        return font_path
    try:
        import urllib.request
        url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
        urllib.request.urlretrieve(url, font_path)
        return font_path
    except Exception:
        return None


def export_to_pdf_ar(title, rows, filename="report.pdf"):
    font_path = _download_font_ar()
    if not font_path:
        return None
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.add_font("Amiri", "", font_path)
        pdf.set_font("Amiri", size=18)
        pdf.cell(0, 12, "أدوات التاجر الذكي", ln=True, align="C")

        pdf.set_font("Amiri", size=12)
        pdf.cell(0, 8, "تقرير حسابي", ln=True, align="C")
        pdf.ln(6)

        pdf.set_font("Amiri", size=14)
        pdf.cell(0, 10, title, ln=True, align="R")
        pdf.ln(3)

        pdf.set_font("Amiri", size=11)
        for label, value in rows:
            pdf.cell(80, 9, str(label), border=1, align="R")
            pdf.cell(0, 9, str(value), border=1, ln=True, align="R")

        pdf.ln(5)
        pdf.set_font("Amiri", size=9)
        pdf.cell(0, 8, "صادر من تطبيق أدوات التاجر الذكي", ln=True, align="C")

        return bytes(pdf.output())
    except Exception:
        return None


def pdf_download_button(title, rows, filename="report.pdf", key_suffix=""):
    pdf_bytes = export_to_pdf_ar(title, rows, filename)
    if pdf_bytes:
        st.download_button(
            "📤 تحميل PDF",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
            key=f"pdf_{filename}_{key_suffix}",
        )
    else:
        st.caption("⚠️ PDF غير متاح حالياً")


def quick_print(title, content):
    import streamlit.components.v1 as components
    content_json = json.dumps(content)
    title_json = json.dumps(title)
    html = (
        '<button onclick="doPrint()" style="background:linear-gradient(135deg,#6366f1,#ec4899);'
        'color:white;border:none;border-radius:14px;padding:12px 20px;font-weight:700;'
        'width:100%;cursor:pointer;font-family:Cairo;font-size:0.95rem;">'
        '🖨️ طباعة</button>'
        '<script>'
        'function doPrint() {'
        '  var title = ' + title_json + ';'
        '  var text = ' + content_json + ';'
        '  var w = window.open("", "", "width=800,height=600");'
        '  w.document.write("<html dir=\'rtl\'><head><meta charset=\'utf-8\'><title>" + title + "</title>");'
        '  w.document.write("<style>body{font-family:Cairo,Arial;padding:40px;line-height:2;direction:rtl;}");'
        '  w.document.write("pre{white-space:pre-wrap;font-size:16px;}h2{color:#4f46e5;border-bottom:3px solid #6366f1;padding-bottom:10px;}</style>");'
        '  w.document.write("</head><body><h2>" + title + "</h2><pre>" + text + "</pre>");'
        '  w.document.write("<p style=\'margin-top:40px;color:#94a3b8;font-size:12px;\'>Generated by Smart Merchant Tools</p>");'
        '  w.document.write("</body></html>");'
        '  w.document.close();'
        '  setTimeout(function(){w.print();}, 400);'
        '}'
        '</script>'
    )
    components.html(html, height=70)


def get_all_data_json():
    data = {
        "all_results": st.session_state.get("all_results", []),
        "ecommerce_history": st.session_state.get("ecommerce_history", []),
        "reminders": st.session_state.get("reminders", []),
        "customers": st.session_state.get("customers", []),
        "theme": st.session_state.get("theme", "تلقائي"),
        "exported_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "version": "1.0",
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def load_all_data_json(text):
    try:
        data = json.loads(text)
        keys = ["all_results", "ecommerce_history", "reminders", "customers"]
        for k in keys:
            if k in data and isinstance(data[k], list):
                st.session_state[k] = data[k]
        return True
    except Exception:
        return False


def backup_restore_ui():
    st.markdown('<h2 class="section-title">💾 النسخ الاحتياطي</h2>', unsafe_allow_html=True)

    st.markdown("**📥 حفظ البيانات:**")
    json_data = get_all_data_json()
    st.download_button(
        "📥 تنزيل نسخة احتياطية (JSON)",
        data=json_data.encode("utf-8"),
        file_name=f"backup_{datetime.date.today()}.json",
        mime="application/json",
        use_container_width=True,
    )

    st.markdown("**📤 استعادة البيانات:**")
    uploaded = st.file_uploader("اختر ملف النسخة الاحتياطية", type=["json"], key="restore_uploader")
    if uploaded is not None:
        try:
            text = uploaded.read().decode("utf-8")
            if load_all_data_json(text):
                st.success("✅ تم استعادة البيانات!")
                st.rerun()
            else:
                st.error("❌ ملف غير صالح")
        except Exception as e:
            st.error(f"خطأ: {e}")


def inject_local_storage_saver():
    """يحفظ البيانات تلقائياً في localStorage المتصفح"""
    import streamlit.components.v1 as components
    data = {
        "all_results": st.session_state.get("all_results", []),
        "ecommerce_history": st.session_state.get("ecommerce_history", []),
        "reminders": st.session_state.get("reminders", []),
        "customers": st.session_state.get("customers", []),
        "theme": st.session_state.get("theme", "تلقائي"),
        "saved_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    data_json = json.dumps(data, ensure_ascii=False)
    html = (
        '<script>'
        'try {'
        '  localStorage.setItem("smart_merchant_data", ' + json.dumps(data_json) + ');'
        '  console.log("✅ تم الحفظ التلقائي");'
        '} catch(e) { console.log("localStorage error:", e); }'
        '</script>'
    )
    components.html(html, height=0)


def localStorage_load_button():
    """زر استعادة البيانات من localStorage"""
    import streamlit.components.v1 as components
    html = (
        '<button id="load_ls_btn" onclick="loadLocalStorage()" '
        'style="background:linear-gradient(135deg,#10b981,#059669);'
        'color:white;border:none;border-radius:14px;padding:12px 20px;'
        'font-weight:700;width:100%;cursor:pointer;font-family:Cairo;'
        'font-size:0.95rem;">'
        '📂 استعادة من المتصفح</button>'
        '<div id="ls_status" style="margin-top:8px; text-align:center; color:#64748b; font-size:0.85rem;"></div>'
        '<script>'
        'function loadLocalStorage() {'
        '  try {'
        '    var data = localStorage.getItem("smart_merchant_data");'
        '    var status = document.getElementById("ls_status");'
        '    if (!data) {'
        '      status.innerText = "⚠️ لا توجد بيانات محفوظة في المتصفح";'
        '      status.style.color = "#f59e0b";'
        '      return;'
        '    }'
        '    var parsed = JSON.parse(data);'
        '    var content = JSON.stringify(parsed, null, 2);'
        '    var blob = new Blob([content], {type: "application/json"});'
        '    var url = URL.createObjectURL(blob);'
        '    var a = document.createElement("a");'
        '    a.href = url;'
        '    a.download = "local_backup_" + new Date().toISOString().slice(0,10) + ".json";'
        '    a.click();'
        '    status.innerText = "✅ تم تنزيل البيانات - ارفعها من قسم الاستعادة";'
        '    status.style.color = "#10b981";'
        '  } catch(e) {'
        '    document.getElementById("ls_status").innerText = "❌ خطأ: " + e.message;'
        '  }'
        '}'
        '</script>'
    )
    components.html(html, height=130)


def get_smart_alerts():
    """توليد تنبيهات ذكية بناءً على البيانات"""
    alerts = []
    now = datetime.datetime.now()
    today = datetime.date.today()

    reminders = st.session_state.get("reminders", [])
    for r in reminders:
        try:
            r_date = datetime.date.fromisoformat(r["date"])
            delta = (r_date - today).days
            if delta < 0:
                alerts.append(("error", f"⚠️ تنبيه متأخر: {r['text']}"))
            elif delta == 0:
                alerts.append(("warning", f"⏰ اليوم: {r['text']}"))
            elif delta <= 3:
                alerts.append(("info", f"📅 بعد {delta} أيام: {r['text']}"))
        except Exception:
            pass

    customers = st.session_state.get("customers", [])
    if customers:
        top_customer = max(customers, key=lambda c: c.get("إجمالي المشتريات", 0))
        if top_customer.get("إجمالي المشتريات", 0) > 1000:
            alerts.append(
                ("success", f"⭐ عميل VIP: {top_customer.get('الاسم', '')} — {money(top_customer.get('إجمالي المشتريات', 0))}")
            )

    results = st.session_state.get("all_results", [])
    if len(results) > 0:
        today_str = today.strftime("%Y-%m-%d")
        today_ops = [r for r in results if r.get("التاريخ", "").startswith(today_str)]
        if len(today_ops) >= 5:
            alerts.append(("success", f"🎉 أنجزت {len(today_ops)} عملية اليوم!"))

    theme = st.session_state.get("theme", "تلقائي")
    hour = now.hour
    if theme == "تلقائي":
        if hour >= 22:
            alerts.append(("info", "🌙 وقت متأخر - لا تنسَ أخذ قسط من الراحة"))
        elif 6 <= hour < 9:
            alerts.append(("success", "☀️ صباح الخير! يوم موفق"))

    return alerts


def render_smart_alerts():
    """عرض التنبيهات الذكية"""
    alerts = get_smart_alerts()
    if not alerts:
        return
    for kind, msg in alerts:
        if kind == "success":
            st.success(msg)
        elif kind == "warning":
            st.warning(msg)
        elif kind == "error":
            st.error(msg)
        else:
            st.info(msg)


def render_analytics_dashboard():
    """لوحة تحليلات متقدمة"""
    results = st.session_state.get("all_results", [])
    customers = st.session_state.get("customers", [])
    ecom = st.session_state.get("ecommerce_history", [])

    total_ops = len(results)
    total_customers = len(customers)
    total_products = len(ecom)

    st.markdown(
        '<div class="stat-grid">'
        '<div class="stat-card">'
        '<div class="stat-icon">📊</div>'
        '<div class="stat-value">' + str(total_ops) + '</div>'
        '<div class="stat-label">إجمالي العمليات</div>'
        '</div>'
        '<div class="stat-card">'
        '<div class="stat-icon">👥</div>'
        '<div class="stat-value">' + str(total_customers) + '</div>'
        '<div class="stat-label">عملاء مسجلون</div>'
        '</div>'
        '<div class="stat-card">'
        '<div class="stat-icon">📦</div>'
        '<div class="stat-value">' + str(total_products) + '</div>'
        '<div class="stat-label">منتجات محللة</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    if not results and not customers:
        st.info("📭 لا توجد بيانات كافية للتحليل. ابدأ باستخدام الحاسبات وأضف عملاء.")
        return

    try:
        import plotly.express as px
        HAS_PLOTLY = True
    except ImportError:
        HAS_PLOTLY = False

    st.markdown('<h2 class="section-title">📅 نشاط آخر 7 أيام</h2>', unsafe_allow_html=True)

    today = datetime.date.today()
    last_7 = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        count = len([r for r in results if r.get("التاريخ", "").startswith(day_str)])
        last_7.append({"اليوم": day.strftime("%m-%d"), "العدد": count})

    df_week = pd.DataFrame(last_7)

    if HAS_PLOTLY:
        fig = px.bar(
            df_week, x="اليوم", y="العدد",
            labels={"اليوم": "التاريخ", "العدد": "عدد العمليات"},
            color="العدد", color_continuous_scale="Purples",
        )
        fig.update_layout(height=300, showlegend=False, font=dict(family="Cairo"),
                          margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart(df_week.set_index("اليوم"))

    if customers:
        st.markdown('<h2 class="section-title">👑 أفضل 5 عملاء</h2>', unsafe_allow_html=True)
        top5 = sorted(customers, key=lambda c: c.get("إجمالي المشتريات", 0), reverse=True)[:5]
        for i, c in enumerate(top5, 1):
            medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i - 1]
            st.markdown(
                f"**{medal} {c.get('الاسم', '')}** — {money(c.get('إجمالي المشتريات', 0))} "
                f"({c.get('عدد الطلبات', 0)} طلب)"
            )

    if ecom:
        st.markdown('<h2 class="section-title">💰 أعلى المنتجات ربحاً</h2>', unsafe_allow_html=True)
        top_products = sorted(ecom, key=lambda p: p.get("الربح الصافي", 0), reverse=True)[:5]
        for i, p in enumerate(top_products, 1):
            medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i - 1]
            st.markdown(
                f"**{medal} {p.get('اسم المنتج', '')}** — ربح: {money(p.get('الربح الصافي', 0))} "
                f"(هامش {p.get('هامش %', 0)}%)"
            )

    if results:
        st.markdown('<h2 class="section-title">🏆 أكثر الأدوات استخداماً</h2>', unsafe_allow_html=True)
        tool_counts = {}
        for r in results:
            tool = r.get("الأداة", "")
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        top_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for i, (tool, count) in enumerate(top_tools, 1):
            medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i - 1]
            st.markdown(f"**{medal} {tool}** — {count} مرة")

    st.markdown('<h2 class="section-title">📈 ملخص عام</h2>', unsafe_allow_html=True)

    if customers:
        total_revenue = sum(c.get("إجمالي المشتريات", 0) for c in customers)
        st.metric("💰 إجمالي المشتريات", money(total_revenue))

        if results:
            first_date_str = results[0].get("التاريخ", "").split(" ")[0]
            try:
                first_date = datetime.date.fromisoformat(first_date_str)
                days_active = (today - first_date).days + 1
                avg_per_day = total_revenue / days_active if days_active > 0 else 0
                st.metric("📅 متوسط يومي", money(avg_per_day))
            except Exception:
                pass
