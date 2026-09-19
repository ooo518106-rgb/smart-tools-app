import streamlit as st
import pandas as pd
import datetime
import urllib.parse
from io import BytesIO


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
        "QAR": 3.64, "BHD": 0.376,
    }
    try:
        import requests
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        data = r.json()
        if data.get("result") == "success":
            rates = data.get("rates", {})
            return {k: rates.get(k, v) for k, v in fallback.items()}
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
