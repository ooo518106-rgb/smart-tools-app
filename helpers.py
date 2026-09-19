import streamlit as st
import pandas as pd
import datetime
import urllib.parse
from io import BytesIO


CURRENCY_NAMES_AR = {
    "USD": "دولار أمريكي",
    "SAR": "ريال سعودي",
    "AED": "درهم إماراتي",
    "KWD": "دينار كويتي",
    "OMR": "ريال عماني",
    "QAR": "ريال قطري",
    "BHD": "دينار بحريني",
    "EGP": "جنيه مصري",
    "JOD": "دينار أردني",
    "LBP": "ليرة لبنانية",
    "SYP": "ليرة سورية",
    "IQD": "دينار عراقي",
    "YER": "ريال يمني",
    "MAD": "درهم مغربي",
    "DZD": "دينار جزائري",
    "TND": "دينار تونسي",
    "LYD": "دينار ليبي",
    "SDG": "جنيه سوداني",
    "MRU": "أوقية موريتانية",
    "SOS": "شلن صومالي",
    "DJF": "فرنك جيبوتي",
    "KMF": "فرنك قمري",
    "EUR": "يورو",
    "GBP": "جنيه إسترليني",
    "CHF": "فرنك سويسري",
    "TRY": "ليرة تركية",
    "IRR": "ريال إيراني",
    "PKR": "روبية باكستانية",
    "INR": "روبية هندية",
    "BDT": "تاكا بنغلاديشية",
    "LKR": "روبية سريلانكية",
    "NPR": "روبية نيبالية",
    "AFN": "أفغاني",
    "IDR": "روبية إندونيسية",
    "MYR": "رينغيت ماليزي",
    "SGD": "دولار سنغافوري",
    "THB": "بات تايلندي",
    "PHP": "بيزو فلبيني",
    "VND": "دونغ فيتنامي",
    "CNY": "يوان صيني",
    "JPY": "ين ياباني",
    "KRW": "وون كوري",
    "HKD": "دولار هونغ كونغ",
    "TWD": "دولار تايواني",
    "MOP": "باتاكا ماكاوية",
    "AUD": "دولار أسترالي",
    "NZD": "دولار نيوزيلندي",
    "CAD": "دولار كندي",
    "MXN": "بيزو مكسيكي",
    "BRL": "ريال برازيلي",
    "ARS": "بيزو أرجنتيني",
    "CLP": "بيزو تشيلي",
    "COP": "بيزو كولومبي",
    "PEN": "سول بيروفي",
    "UYU": "بيزو أوروغوياني",
    "VES": "بوليفار فنزويلي",
    "SEK": "كرونة سويدية",
    "NOK": "كرونة نرويجية",
    "DKK": "كرونة دنماركية",
    "ISK": "كرونة آيسلندية",
    "PLN": "زلوتي بولندي",
    "CZK": "كرونة تشيكية",
    "HUF": "فورنت مجري",
    "RON": "ليو روماني",
    "BGN": "ليف بلغاري",
    "RSD": "دينار صربي",
    "MKD": "دينار مقدوني",
    "ALL": "ليك ألباني",
    "RUB": "روبل روسي",
    "UAH": "هريفنيا أوكرانية",
    "BYN": "روبل بيلاروسي",
    "GEL": "لاري جورجي",
    "AMD": "درام أرميني",
    "AZN": "مانات أذربيجاني",
    "KZT": "تينغي كازاخستاني",
    "UZS": "سوم أوزبكي",
    "TJS": "سوموني طاجيكي",
    "TMT": "مانات تركمانستاني",
    "KGS": "سوم قيرغيزستاني",
    "MNT": "توغروغ منغولي",
    "ILS": "شيكل إسرائيلي",
    "ZAR": "راند جنوب أفريقي",
    "NGN": "نايرا نيجيري",
    "KES": "شلن كيني",
    "GHS": "سيدي غاني",
    "ETB": "بير إثيوبي",
    "TZS": "شلن تنزاني",
    "UGX": "شلن أوغندي",
    "RWF": "فرنك رواندي",
    "BIF": "فرنك بوروندي",
    "XOF": "فرنك غرب أفريقي",
    "XAF": "فرنك وسط أفريقي",
    "XPF": "فرنك المحيط الهادئ",
    "MUR": "روبية موريشيوسية",
    "SCR": "روبية سيشيلية",
    "MGA": "أرياري ملغاشي",
    "MWK": "كواشا مالاوية",
    "ZMW": "كواشا زامبي",
    "BWP": "بولا بوتسواني",
    "NAD": "دولار ناميبي",
    "SZL": "ليلانغيني سوازي",
    "LSL": "لوتي ليسوتو",
    "MZN": "متكال موزمبيقي",
    "AOA": "كوانزا أنغولي",
    "CDF": "فرنك كونغولي",
    "GMD": "دالاسي غامبي",
    "GNF": "فرنك غيني",
    "LRD": "دولار ليبيري",
    "SLE": "ليون سيراليوني",
    "CVE": "إسكودو كابو فيردي",
    "STN": "دوبرا ساوتومية",
    "JMD": "دولار جامايكي",
    "TTD": "دولار ترينيداد",
    "BBD": "دولار بربادوسي",
    "BSD": "دولار باهامي",
    "BZD": "دولار بليزي",
    "XCD": "دولار شرق كاريبي",
    "KYD": "دولار كايماني",
    "BMD": "دولار برمودي",
    "ANG": "غيلدر أنتيلي",
    "AWG": "فلورين أروبي",
    "HTG": "غورد هايتي",
    "DOP": "بيزو دومينيكي",
    "CUP": "بيزو كوبي",
    "GTQ": "كتزال غواتيمالي",
    "HNL": "لمبيرة هندسية",
    "NIO": "كوردبا نيكاراغوية",
    "CRC": "كولون كوستاريكي",
    "PAB": "بالبوا بنمية",
    "SVC": "كولون سلفادوري",
    "BOB": "بوليفيانو بوليفي",
    "PYG": "غواراني باراغواي",
    "GYD": "دولار غياني",
    "SRD": "دولار سورينامي",
    "FJD": "دولار فيجي",
    "PGK": "كينا بابوا غينيا",
    "SBD": "دولار جزر سليمان",
    "VUV": "فاتو فانواتو",
    "WST": "تالا ساموا",
    "TOP": "بانغا تونغا",
    "BND": "دولار بروناي",
    "KHR": "رييل كمبودي",
    "LAK": "كيب لاوسي",
    "MMK": "كيات ميانماري",
    "MVR": "روفيا مالديفية",
    "BTN": "نغولترم بوتاني",
    "GIP": "جنيه جبل طارق",
    "FKP": "جنيه جزر فوكلاند",
    "SHP": "جنيه سانت هيلينا",
    "SSP": "جنيه جنوب السودان",
    "ERN": "ناكفا إريتري",
    "KPW": "وون كوري شمالي",
    "ZWL": "دولار زيمبابوي",
    "BAM": "مارك بوسني",
    "MDL": "ليو مولدوفي",
    "HRK": "كونا كرواتية",
}


def currency_label(code):
    name = CURRENCY_NAMES_AR.get(code, "")
    return f"{code} - {name}" if name else code


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
    st.toast("✅ تم الحفظ في التقارير", icon="💾")


def quick_save_button(key, tool_name, data_dict):
    if st.button("💾 حفظ في التقارير", key=f"qsave_{key}", use_container_width=True):
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

    st.markdown("**📤 مشاركة النتيجة:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<a href="{wa}" target="_blank" style="text-decoration:none;">'
            f'<div style="text-align:center; padding:10px; border-radius:8px; '
            f'background:#25D366; color:white; font-weight:600; cursor:pointer;">'
            f'واتساب 💬</div></a>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<a href="{tw}" target="_blank" style="text-decoration:none;">'
            f'<div style="text-align:center; padding:10px; border-radius:8px; '
            f'background:#1DA1F2; color:white; font-weight:600; cursor:pointer;">'
            f'تويتر 🐦</div></a>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<a href="{tg}" target="_blank" style="text-decoration:none;">'
            f'<div style="text-align:center; padding:10px; border-radius:8px; '
            f'background:#0088cc; color:white; font-weight:600; cursor:pointer;">'
            f'تيليجرام ✈️</div></a>',
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
    st.markdown(
        f'<div class="main-title">{icon} {title}</div>',
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(
            f'<div class="sub-title">{subtitle}</div>',
            unsafe_allow_html=True,
        )
