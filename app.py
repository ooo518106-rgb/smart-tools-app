import streamlit as st
import pandas as pd
import datetime
from io import BytesIO


def money(v, cur="", decimals=2):
    """تنسيق الأرقام بفواصل الآلاف مع العملة"""
    if v is None:
        return "0.00"
    try:
        s = f"{v:,.{decimals}f}"
    except (ValueError, TypeError):
        s = str(v)
    return f"{s} {cur}".strip() if cur else s


def save_result(tool_name, **data):
    """حفظ نتيجة في التقارير الموحدة"""
    if "all_results" not in st.session_state:
        st.session_state.all_results = []
    record = {"الأداة": tool_name, "التاريخ": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), **data}
    st.session_state.all_results.append(record)
    st.toast("✅ تم الحفظ في التقارير", icon="💾")


def quick_save_button(key, tool_name, data_dict):
    """زر حفظ سريع يظهر في كل حاسبة"""
    if st.button("💾 حفظ في التقارير", key=f"qsave_{key}", use_container_width=True):
        save_result(tool_name, **data_dict)
        st.rerun()


def copy_box(text, label="📋 نسخ النتيجة"):
    """عرض النتيجة في صندوق فيه زر نسخ تلقائي"""
    with st.expander(label):
        st.code(text, language="")


def export_to_excel(df_dict, filename="report.xlsx"):
    """تصدير قاموس من DataFrames إلى ملف Excel متعدد الأوراق"""
    try:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            for sheet_name, df in df_dict.items():
                safe_name = sheet_name[:31]
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
