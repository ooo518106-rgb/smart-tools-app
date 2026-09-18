st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

html, body {
    font-family: 'Cairo', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf5 100%);
    direction: rtl;
}

footer {visibility: hidden;}

/* العناوين */
.main-title {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 50%, #00b4db 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 1.9rem;
    font-weight: 900;
    text-align: center;
    margin-bottom: 0.3rem;
    line-height: 1.4;
}

.sub-title {
    text-align: center;
    color: #5a6c8a;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

/* البطاقات */
[data-testid="stMetric"] {
    background: #ffffff;
    padding: 14px 12px;
    border-radius: 12px;
    border-right: 4px solid #2a5298;
    box-shadow: 0 2px 10px rgba(30, 60, 114, 0.08);
}

[data-testid="stMetricLabel"] {
    color: #5a6c8a !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: #1e3c72 !important;
    font-weight: 700 !important;
}

/* القائمة الجانبية */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] .stRadio label {
    background: rgba(255, 255, 255, 0.08);
    padding: 8px 12px;
    border-radius: 10px;
    margin-bottom: 6px;
    cursor: pointer;
    display: block;
}

section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255, 255, 255, 0.18);
}

/* الأزرار */
.stButton > button {
    background: linear-gradient(90deg, #2a5298 0%, #00b4db 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
    font-family: 'Cairo', sans-serif;
    width: 100%;
}

.stButton > button:hover {
    color: white;
    box-shadow: 0 6px 16px rgba(42, 82, 152, 0.3);
}

.stDownloadButton > button {
    background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    font-family: 'Cairo', sans-serif;
    width: 100%;
}

/* الحقول */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    border-radius: 10px !important;
    border: 2px solid #e0e6f0 !important;
    font-family: 'Cairo', sans-serif !important;
    direction: rtl !important;
    text-align: right !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: #2a5298 !important;
}

/* التنبيهات */
.stAlert {
    border-radius: 12px !important;
    font-family: 'Cairo', sans-serif !important;
}

/* العناوين الرئيسية */
h1, h2, h3 {
    font-family: 'Cairo', sans-serif !important;
    color: #1e3c72 !important;
}

/* الجداول */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* إخفاء الشعار العائم على الجوال */
[data-testid="stHeader"] {
    background: transparent !important;
}

#MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
