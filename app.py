import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import tempfile

# --- 網頁設定 (Page Config) ---
st.set_page_config(
    page_title="StockFlow AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 自定義 CSS (強制暗黑風格與專業按鈕) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stButton>button {
        width: 100%;
        background-color: #2E8B57;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #3CB371;
        border-color: #3CB371;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1E1E1E;
        border-radius: 4px;
        padding: 10px 20px;
        color: #B0B0B0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- 側邊欄：商業邏輯 (BYOK 模式) ---
with st.sidebar:
    st.title("🔐 StockFlow AI")
    st.caption("Professional Edition")
    st.markdown("---")
    
    # 1. 產品訪問密碼 (你賣給客戶的通行證)
    password = st.text_input("輸入產品授權碼 (Access Code)", type="password")
    
    # 【注意】這裡設定你要在 Gumroad 賣的密碼，目前預設為 123456
    if password != "Money2026":
        st.warning("🔒 請輸入授權碼以解鎖功能")
        st.info("💡 還沒購買？[點此前往 Gumroad 購買](https://gumroad.com/)") # 記得換成你的連結
        st.stop()
    
    st.success("✅ 授權驗證成功")
    st.markdown("---")
    
    # 2. API Key (客戶自備)
    st.markdown("### 🔑 設定 AI 引擎")
    api_key = st.text_input("輸入您的 Google API Key", type="password")
    
    st.caption("🚀 本工具使用 BYOK 模式 (Bring Your Own Key)。請使用您自己的 Key 以確保隱私與最快速度。")
    st.markdown("[👉 點此免費獲取 Google API Key](https://aistudio.google.com/app/apikey)")
    
    if not api_key:
        st.warning("⚠️ 請輸入 Google API Key 以開始使用")
        st.stop()
    
    # 設定 Gemini
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        st.error("API Key 格式錯誤，請重新檢查")
        st.stop()
    
    # 模型選擇 (已升級為 Pro)
    model_name = "gemini-1.5-pro" 
    st.success(f"🤖 AI 引擎已啟動: {model_name}")

# --- 主程式邏輯 ---

# 系統指令 (System Prompt)
SYSTEM_PROMPT = """
你現在是「StockSensei X」，全球頂尖的圖庫市場策略顧問與 AI 影像導演。
你的核心任務是協助使用者分析影像、生成高品質的 AI 繪圖/影片提示詞 (Prompt)，並提供符合 Adobe Stock、Shutterstock 標準的專業 SEO 元數據。

工作流程：
當使用者上傳圖片或影片時，請依據以下步驟思考並輸出：
1. 視覺分析：分析主體、環境、光影、攝影機運鏡。
2. 市場對接：思考這張圖的商業用途。
3. 內容生成：依照格式回覆。

語言規則：
- 分析與建議：全部使用「繁體中文」。
- SEO 內容 (Titles, Keywords, Prompt)：全部使用「英文」。

標準輸出格式：
A. 作品視覺與商業分析（中文）
B. AI 生成 Prompt（英文 - 包含 Main Prompt 與 Negative Prompt）
C. SEO 輸出（英文 - 包含 5 個 Titles, Best Title, Description, 50 個 Keywords）
"""

# 初始化模型
model = genai.GenerativeModel(
    model_name=model_name,
    system_instruction=SYSTEM_PROMPT
)

# --- 介面標題 ---
st.title("📈 StockFlow AI")
st.markdown("**Analyze. Prompt. Rank. Sell.** | 專業圖庫市場策略顧問")

# --- 分頁切換 ---
tab1, tab2 = st.tabs(["🧬 DeCode AI (視覺解碼)", "🚀 StockSensei X (SEO 專家)"])

# --- TAB 1: DeCode AI (反推 Prompt) ---
with tab1:
    st.header("DeCode AI - 影像反推工程")
    st.info("上傳參考圖/影片，反推它的 Prompt 與製作配方。")
    
    uploaded_file = st.file_uploader("上傳參考素材 (支援 JPG, PNG, MP4)", type=["jpg", "png", "jpeg", "mp4"])
    
    if uploaded_file:
        # 顯示預覽
        if uploaded_file.type.startswith('image'):
            image = Image.open(uploaded_file)
            st.image(image, caption="Reference Image", use_column_width=True)
            user_content = image
        elif uploaded_file.type.startswith('video'):
            st.video(uploaded_file)
            # 影片處理
            with st.spinner("正在處理影片檔案..."):
                tfile = tempfile.NamedTemporaryFile(delete=False) 
                tfile.write(uploaded_file.read())
                video_path = tfile.name
                video_file = genai.upload_file(video_path)
                
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                user_content = video_file

        if st.button("✨ 開始解碼 (Generate Prompt)", key="btn_decode"):
            with st.spinner("StockSensei 正在分析影像結構 (使用 Pro 模型)..."):
                try:
                    # 發送請求
                    response = model.generate_content([
                        "請分析這個素材，給我詳細的 AI 生成 Prompt 和商業分析。", 
                        user_content
                    ])
                    st.markdown("### 📊 分析報告")
                    st.write(response.text)
                    st.success("分析完成！")
                except Exception as e:
                    st.error(f"發生錯誤：{str(e)}")

# --- TAB 2: StockSensei X (SEO 生成) ---
with tab2:
    st.header("StockSensei X - SEO 策略專家")
    st.info("上傳你的成品，生成 Adobe Stock 專用標題與關鍵字。")
    
    uploaded_file_seo = st.file_uploader("上傳你的作品 (支援 JPG, PNG, MP4)", type=["jpg", "png", "jpeg", "mp4"], key="seo_uploader")
    
    if uploaded_file_seo:
        # 顯示預覽
        if uploaded_file_seo.type.startswith('image'):
            image_seo = Image.open(uploaded_file_seo)
            st.image(image_seo, caption="Your Work", use_column_width=True)
            seo_content = image_seo
        elif uploaded_file_seo.type.startswith('video'):
            st.video(uploaded_file_seo)
            # 影片處理
            with st.spinner("正在處理影片檔案..."):
                tfile = tempfile.NamedTemporaryFile(delete=False) 
                tfile.write(uploaded_file_seo.read())
                video_path = tfile.name
                video_file_seo = genai.upload_file(video_path)
                
                while video_file_seo.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file_seo = genai.get_file(video_file_seo.name)
                
                seo_content = video_file_seo

        if st.button("🚀 生成 SEO 套件 (Generate SEO)", key="btn_seo"):
            with st.spinner("StockSensei 正在撰寫 SEO 關鍵字 (使用 Pro 模型)..."):
                try:
                    prompt_text = """
                    請針對這個作品，產出 SEO 套件。
                    請嚴格遵守以下格式輸出英文內容：
                    
                    【SEO Titles (5 options)】
                    1.
                    2...
                    
                    【Best Title】
                    
                    【Description】
                    
                    【Keywords (50 words)】
                    (請列出50個英文關鍵字，用逗號分隔)
                    """
                    response = model.generate_content([prompt_text, seo_content])
                    st.markdown("### 📝 SEO 輸出結果")
                    st.code(response.text, language="markdown") 
                    st.success("生成完畢！請點擊右上角複製內容。")
                except Exception as e:
                    st.error(f"發生錯誤：{str(e)}")

# --- 頁尾 ---
st.markdown("---")
st.markdown("© 2025 StockFlow AI | Powered by Google Gemini 1.5 Pro")
