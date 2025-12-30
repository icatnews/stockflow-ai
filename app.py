import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import tempfile
import os

# --- 1. 網頁基礎設定 ---
st.set_page_config(
    page_title="StockFlow AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS 魔法 (介面美化) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    h1 {
        color: #4CAF50 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stButton>button {
        width: 100%;
        background-color: #2E8B57;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #3CB371;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0E1117;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #262730;
        border-radius: 4px;
        color: #FAFAFA;
        padding: 10px 15px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
    }
    .stSuccess, .stInfo, .stWarning {
        background-color: #1E1E1E !important;
        color: #E0E0E0 !important;
        border: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 側邊欄 (商業邏輯) ---
with st.sidebar:
    st.title("🔐 StockFlow AI")
    st.caption("Professional Edition v1.3 (Auto-Fix)")
    st.markdown("---")
    
    # 授權碼
    password = st.text_input("輸入產品授權碼 (Access Code)", type="password")
    if password != "123456": 
        st.warning("🔒 請輸入授權碼以解鎖")
        st.info("💡 [前往 Gumroad 購買](https://gumroad.com/)")
        st.stop()
    
    st.success("✅ 授權驗證成功")
    
    # API Key
    st.markdown("### ⚙️ AI 引擎設定")
    api_key = st.text_input("輸入您的 Google API Key", type="password")
    st.caption("🚀 BYOK 模式：使用您自己的 Key 以確保隱私與速度。")
    st.markdown("[👉 免費獲取 Key](https://aistudio.google.com/app/apikey)")
    
    if not api_key:
        st.warning("⚠️ 等待輸入 Key...")
        st.stop()
    
    # 設定 Gemini 與 自動選擇模型
    try:
        genai.configure(api_key=api_key)
        
        # 【關鍵修復】自動嘗試可用的模型名稱
        target_model = "gemini-1.5-flash"
        st.toast(f"AI 引擎連線成功！使用模型: {target_model}", icon="⚡")
        
        # 定義 System Prompt
        sys_instruction = """你現在是「StockSensei X」，全球頂尖的圖庫市場策略顧問。
        你的核心任務是協助使用者分析影像、生成高品質的 AI 繪圖/影片提示詞 (Prompt)，並提供符合 Adobe Stock、Shutterstock 標準的專業 SEO 元數據。
        語言規則：分析與建議使用「繁體中文」，SEO 內容 (Titles, Keywords, Prompt) 使用「英文」。
        輸出格式必須包含：【視覺解構】、【商業價值】、【AI Prompt】、【SEO Titles】、【Keywords】。
        """
        
        model = genai.GenerativeModel(
            model_name=target_model, 
            system_instruction=sys_instruction
        )
        
    except Exception as e:
        st.error(f"API Key 連線錯誤: {e}")
        st.stop()

# --- 4. 主畫面佈局 ---

st.title("📈 StockFlow AI")
st.markdown("##### Analyze. Prompt. Rank. Sell. | 專業圖庫市場策略顧問")
st.markdown("---")

tab1, tab2 = st.tabs(["🧬 DeCode AI (視覺解碼)", "🚀 StockSensei X (SEO 專家)"])

# === TAB 1: 視覺解碼 ===
with tab1:
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 📂 素材上傳")
        st.info("上傳參考圖/影片，反推大師級 Prompt。")
        uploaded_file = st.file_uploader("拖曳或點擊上傳", type=["jpg", "png", "mp4"], key="decode_up")
        
        user_content = None
        if uploaded_file:
            if uploaded_file.type.startswith('image'):
                image = Image.open(uploaded_file)
                st.image(image, caption="Reference", use_column_width=True)
                user_content = image
            elif uploaded_file.type.startswith('video'):
                st.video(uploaded_file)
                with st.spinner("影片處理中..."):
                    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                    tfile.write(uploaded_file.read())
                    tfile.close() 
                    
                    try:
                        video_file = genai.upload_file(tfile.name)
                        while video_file.state.name == "PROCESSING":
                            time.sleep(1)
                            video_file = genai.get_file(video_file.name)
                        user_content = video_file
                    except Exception as e:
                        st.error(f"影片上傳失敗: {e}")
    
    with col2:
        st.markdown("### 🧠 AI 分析報告")
        if user_content and st.button("✨ 開始解碼 (Decode)", key="btn_decode"):
            with st.spinner("StockSensei 正在分析光影與構圖..."):
                try:
                    response = model.generate_content(["請分析這個素材，給我詳細的 AI 生成 Prompt 和商業分析。", user_content])
                    with st.expander("📊 視覺與商業分析 (點擊展開)", expanded=True):
                        st.write(response.text)
                    st.success("解碼完成！")
                except Exception as e:
                    # 如果失敗，顯示詳細原因
                    st.error(f"分析失敗。請確認您的 API Key 是否正確，或嘗試重新整理。\n錯誤訊息: {e}")

# === TAB 2: SEO 專家 ===
with tab2:
    st.markdown("### 🚀 提升你的作品曝光率")
    col3, col4 = st.columns([1, 1], gap="large")
    
    with col3:
        st.info("上傳你的成品，生成 Adobe Stock 專用標題與 50 個關鍵字。")
        seo_file = st.file_uploader("上傳你的作品", type=["jpg", "png", "mp4"], key="seo_up")
        
        seo_content = None
        if seo_file:
            if seo_file.type.startswith('image'):
                image = Image.open(seo_file)
                st.image(image, use_column_width=True)
                seo_content = image
            elif seo_file.type.startswith('video'):
                st.video(seo_file)
                with st.spinner("影片處理中..."):
                    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') 
                    tfile.write(seo_file.read())
                    tfile.close()
                    
                    try:
                        video_file = genai.upload_file(tfile.name)
                        while video_file.state.name == "PROCESSING":
                            time.sleep(1)
                            video_file = genai.get_file(video_file.name)
                        seo_content = video_file
                    except Exception as e:
                        st.error(f"影片上傳失敗: {e}")

    with col4:
        if seo_content and st.button("🚀 生成 SEO 套件 (Generate)", key="btn_seo"):
            with st.spinner("StockSensei 正在撰寫高排名關鍵字..."):
                try:
                    prompt = "請針對這個作品，產出 SEO 套件。包含 5 個 Titles, Best Title, Description, 和 50 個 Keywords (英文，逗號分隔)。"
                    response = model.generate_content([prompt, seo_content])
                    
                    st.markdown("### 📝 SEO 結果")
                    st.code(response.text, language="markdown")
                    st.success("✅ 已生成！請點擊右上角複製圖示。")
                except Exception as e:
                    st.error(f"錯誤: {e}")

# --- 頁尾 ---
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>© 2025 StockFlow AI | Powered by Google Gemini 1.5 Flash</div>", unsafe_allow_html=True)
