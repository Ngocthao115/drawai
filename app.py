import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Drawing → Video Prompt",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── API Key: ưu tiên Secrets, fallback sidebar ────────────────────────────────
def get_api_key():
    # 1. Thao đã cài sẵn trong Streamlit Secrets → giáo viên không cần nhập
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key and len(key) > 10:
            return key, True          # (key, is_from_secrets)
    except Exception:
        pass
    # 2. Không có Secrets → hiện ô nhập cho người dùng tự nhập
    return None, False

SECRET_KEY, KEY_FROM_SECRETS = get_api_key()

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2rem; font-weight: 700;
        background: linear-gradient(135deg, #6C63FF, #48CAE4);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center; color: #888; font-size: 0.95rem; margin-bottom: 1.5rem;
    }
    .prompt-box {
        background: #f8f9ff;
        border: 1.5px solid #6C63FF33;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        font-family: monospace;
        font-size: 0.88rem;
        line-height: 1.7;
        white-space: pre-wrap;
        color: #222;
    }
    .badge {
        display: inline-block;
        background: #EEF0FF; color: #6C63FF;
        border-radius: 99px; padding: 3px 12px;
        font-size: 0.78rem; font-weight: 600; margin-bottom: 1rem;
    }
    .step-box {
        background: #fff; border: 1px solid #eee;
        border-radius: 10px; padding: 0.9rem 1rem; margin-bottom: 0.5rem;
    }
    .ready-badge {
        background: #e6f9f0; color: #1a7a4a;
        border-radius: 8px; padding: 8px 12px;
        font-size: 0.85rem; margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
VIDEO_STYLES = {
    "🎬 Điện ảnh (Cinematic)":     "cinematic, slow motion, warm golden lighting, film grain",
    "🖍️ Hoạt hình 2D vui nhộn":    "2D animation, colorful, playful, cartoon style, smooth frame motion",
    "✨ 3D Pixar Style":             "3D animation, Pixar-inspired, vibrant colors, expressive characters",
    "🎨 Màu nước chuyển động":      "watercolor animation, soft dreamy motion, pastel tones, gentle flow",
    "🌟 Stop Motion phép thuật":    "stop motion, handcrafted feel, magical sparkle effects, tactile texture",
    "🌿 Tài liệu thiên nhiên":      "nature documentary style, realistic lighting, calm pacing, 4K detail",
}

PLATFORMS = {
    "Sora (OpenAI)":       "Sora by OpenAI",
    "Runway Gen-3":        "Runway Gen-3 Alpha",
    "Kling AI":            "Kling AI",
    "Pika Labs":           "Pika 1.5",
    "Google Veo":          "Google Veo 2",
    "Luma Dream Machine":  "Luma Dream Machine",
}

LANGUAGES = {"🇬🇧 English": "English", "🇻🇳 Tiếng Việt": "Vietnamese"}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Cài đặt")

    # Nếu admin đã cài key → ẩn ô nhập, hiện thông báo sẵn sàng
    if KEY_FROM_SECRETS:
        st.markdown('<div class="ready-badge">✅ Hệ thống đã sẵn sàng<br><small>Không cần nhập API key</small></div>',
                    unsafe_allow_html=True)
        manual_key = ""
    else:
        st.info("Nhập Gemini API Key để sử dụng.\n\n[Lấy key miễn phí →](https://aistudio.google.com/app/apikey)")
        manual_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIza...",
            help="Lấy miễn phí tại aistudio.google.com",
        )

    st.markdown("---")
    style_label    = st.selectbox("🎞️ Phong cách video", list(VIDEO_STYLES.keys()))
    platform_label = st.selectbox("📱 Nền tảng", list(PLATFORMS.keys()))
    output_lang    = st.selectbox("🌐 Ngôn ngữ output", list(LANGUAGES.keys()))
    temperature    = st.slider("🌡️ Độ sáng tạo", 0.1, 1.0, 0.7, 0.1)

    st.markdown("---")
    st.markdown("""
**Hướng dẫn nhanh**
1. Tải hình vẽ lên
2. Chọn phong cách & nền tảng
3. Nhấn **Tạo Prompt**
4. Copy → dán vào Sora / Runway / Kling...
""")

# key thực sự dùng = từ secrets hoặc từ ô nhập tay
active_key = SECRET_KEY if KEY_FROM_SECRETS else manual_key

# ── Main UI ───────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🎨 Drawing → Video AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Biến hình vẽ của trẻ thành prompt video chuyên nghiệp · Dành cho giáo viên mầm non</div>',
            unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Tải lên hình vẽ",
    type=["png", "jpg", "jpeg", "webp", "gif"],
    help="Hình vẽ của trẻ, tranh màu nước, bất kỳ ảnh nào",
)

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption=f"📎 {uploaded_file.name}", use_container_width=True)

# ── Generate button ───────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    generate_btn = st.button(
        "✨ Tạo Prompt Video AI",
        disabled=(not active_key or not uploaded_file),
        use_container_width=True,
        type="primary",
    )
with col2:
    if st.button("🗑️ Xóa", use_container_width=True):
        st.session_state.pop("last_prompt", None)
        st.rerun()

# ── Helpers ───────────────────────────────────────────────────────────────────
def build_system_prompt(style: str, platform: str, lang: str) -> str:
    lang_instruction = (
        "Write the prompt in English only."
        if lang == "English"
        else "Write the prompt in Vietnamese only (no English)."
    )
    return f"""You are an expert AI video prompt engineer specializing in children's educational content and early childhood art.

Analyze the uploaded image thoroughly and create ONE professional, detailed prompt for AI video generation.

Your prompt MUST include:
1. Detailed description of every visual element in the image
2. Natural, age-appropriate movements (camera motion, character animation, environment effects, lighting)
3. Video style: {style}
4. Optimized specifically for: {platform}
5. Warm, joyful, safe atmosphere for preschool children

Rules:
- {lang_instruction}
- Output ONLY the prompt text — no labels, no explanations, no markdown
- Start directly with the scene description
- Be specific, vivid, and cinematic
- Keep it under 300 words"""

# ── Generate logic ────────────────────────────────────────────────────────────
if generate_btn and active_key and uploaded_file:
    style    = VIDEO_STYLES[style_label]
    platform = PLATFORMS[platform_label]
    lang     = LANGUAGES[output_lang]

    with st.spinner("🔍 Gemini Vision đang phân tích hình vẽ..."):
        try:
            genai.configure(api_key=active_key)
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=800,
                ),
            )
            img_obj = Image.open(uploaded_file)
            response = model.generate_content([img_obj, build_system_prompt(style, platform, lang)])
            st.session_state["last_prompt"]   = response.text.strip()
            st.session_state["last_platform"] = platform_label
        except Exception as e:
            st.error(f"❌ Lỗi: {e}\n\nVui lòng kiểm tra lại và thử lại.")

# ── Show result ───────────────────────────────────────────────────────────────
if "last_prompt" in st.session_state:
    st.markdown("---")
    st.markdown(f'<div class="badge">✅ Prompt cho {st.session_state.get("last_platform","AI Video")}</div>',
                unsafe_allow_html=True)

    prompt = st.session_state["last_prompt"]
    st.markdown(f'<div class="prompt-box">{prompt}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("💾 Tải prompt (.txt)", data=prompt,
                           file_name="video_prompt.txt", mime="text/plain",
                           use_container_width=True)
    with c2:
        st.code(prompt, language=None)

    st.markdown("---")
    st.markdown("### 📋 Dán prompt vào nền tảng nào?")
    for name, url, label in [
        ("Sora (OpenAI)",      "https://sora.com",                    "sora.com"),
        ("Runway Gen-3",       "https://runwayml.com",                "runwayml.com"),
        ("Kling AI",           "https://klingai.com",                 "klingai.com"),
        ("Pika Labs",          "https://pika.art",                    "pika.art"),
        ("Google Veo",         "https://labs.google/veo",             "labs.google"),
        ("Luma Dream Machine", "https://lumalabs.ai/dream-machine",   "lumalabs.ai"),
    ]:
        st.markdown(f'<div class="step-box">🔗 <b>{name}</b> — <a href="{url}" target="_blank">{label}</a></div>',
                    unsafe_allow_html=True)
