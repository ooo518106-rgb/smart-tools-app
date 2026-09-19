import streamlit as st
import pandas as pd
import datetime
import urllib.parse
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
