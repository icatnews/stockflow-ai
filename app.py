import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- 網頁設定 (Page Config) ---
st.set_page_config(
    page_title="StockFlow AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 自定義 CSS (讓介面更像你的截圖) ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #2E8B57;
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1E1E1E;
        border-radius: 4px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- 側邊欄：登入與設定 ---
with st.sidebar:
    st.title("🔐 StockFlow AI")
    st.markdown("---")
    
    # 1. 密碼保護
    password = st.text_input("輸入訪問密碼 (Access Password)", type="password")
    if password != "22Vbncsl":  # 【注意】這裡設定你的密碼，目前是 123456
        st.warning("請輸入正確密碼以解鎖功能")
        st.stop()  # 停止執行下面的程式碼
    
    st.success("✅ 登入成功")
    st.markdown("---")
    
    # 2. API Key 輸入
    api_key = st.text_input("輸入 Google API Key", type="password")
    if not api_key:
        st.info("請輸入你的 API Key (以 AIza 開頭)")
        st.stop()
    
    # 設定 Gemini
    genai.configure(api_key=api_key)
    
    # 模型選擇
    model_name = "gemini-1.5-flash"  # 使用 Flash 模型比較省錢且快速
    st.caption(f"目前使用模型: {model_name}")

# --- 主程式邏輯 ---

# 系統指令 (System Prompt) - 這是大腦的核心
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
            # 影片處理需要先上傳到 Google 臨時空間
            with st.spinner("正在處理影片檔案..."):
                # 儲存臨時檔案
                import tempfile
                tfile = tempfile.NamedTemporaryFile(delete=False) 
                tfile.write(uploaded_file.read())
                video_path = tfile.name
                # 上傳到 Gemini
                video_file = genai.upload_file(video_path)
                
                # 等待處理完成
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                user_content = video_file

        if st.button("✨ 開始解碼 (Generate Prompt)", key="btn_decode"):
            with st.spinner("StockSensei 正在分析影像結構..."):
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
                import tempfile
                tfile = tempfile.NamedTemporaryFile(delete=False) 
                tfile.write(uploaded_file_seo.read())
                video_path = tfile.name
                video_file_seo = genai.upload_file(video_path)
                
                while video_file_seo.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file_seo = genai.get_file(video_file_seo.name)
                
                seo_content = video_file_seo

        if st.button("🚀 生成 SEO 套件 (Generate SEO)", key="btn_seo"):
            with st.spinner("StockSensei 正在撰寫 SEO 關鍵字..."):
                try:
                    prompt_text = """
                    請針對這個作品，產出 SEO 套件。
                    請嚴格遵守以下格式輸出：
                    
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
                    st.code(response.text, language="markdown") # 使用代碼區塊方便複製
                    st.success("生成完畢！請點擊右上角複製內容。")
                except Exception as e:
                    st.error(f"發生錯誤：{str(e)}")

# --- 頁尾 ---
st.markdown("---")
st.markdown("© 2025 StockFlow AI | Powered by Google Gemini 1.5 Flash")
