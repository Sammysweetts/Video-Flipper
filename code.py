import os
import tempfile
import streamlit as st
import subprocess
import shutil

# --- Page Configuration ---
st.set_page_config(
    page_title="Video Flipper 🎬",
    page_icon="🔄",
    layout="centered"
)

# --- Custom CSS ---
st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #555;
        margin-bottom: 25px;
    }
    .section-header {
        font-size: 22px;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 10px;
        color: #3366cc;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown('<div class="title">🔄 Video Flipper</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload a video and flip it horizontally and/or vertically</div>', unsafe_allow_html=True)

# --- Initialize Session State ---
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'video_bytes' not in st.session_state:
    st.session_state.video_bytes = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = ""

# --- Reset State on New Upload ---
def reset_state():
    st.session_state.processed = False
    st.session_state.video_bytes = None
    st.session_state.file_name = ""

# ==============================
# 🚀 1. Upload Section (Top)
# ==============================
st.markdown('<div class="section-header">📤 Upload Video</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a video file (MP4, MOV, AVI, MKV)",
    type=["mp4", "mov", "avi", "mkv"],
    on_change=reset_state,
    label_visibility="collapsed"
)

# ==============================
# 🔃 2. Flip Options (Below Upload)
# ==============================
st.markdown('<div class="section-header">⚙️ Flip Options</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    flip_horizontal = st.checkbox("🔁 Flip Horizontal", value=True)
with col2:
    flip_vertical = st.checkbox("🔃 Flip Vertical", value=False)

# ==============================
# ▶️ 3. Process Button (Below Options)
# ==============================
st.markdown('<div class="section-header">🛠️ Process Video</div>', unsafe_allow_html=True)

if uploaded_file:
    if st.button("✨ Flip Video", type="primary", use_container_width=True):
        if not flip_horizontal and not flip_vertical:
            st.error("⚠️ Please select at least one flip direction.")
        else:
            temp_dir = None
            try:
                temp_dir = tempfile.mkdtemp()
                input_path = os.path.join(temp_dir, uploaded_file.name)
                output_filename = os.path.splitext(uploaded_file.name)[0] + "_flipped.mp4"
                output_path = os.path.join(temp_dir, output_filename)

                with open(input_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text("🔄 Starting video processing...")

                flip_filters = []
                if flip_horizontal:
                    flip_filters.append('hflip')
                if flip_vertical:
                    flip_filters.append('vflip')
                flip_filter_str = ",".join(flip_filters)

                cmd = [
                    'ffmpeg', '-y',
                    '-i', input_path,
                    '-vf', flip_filter_str,
                    '-c:v', 'libx264',
                    '-crf', '18',
                    '-preset', 'slow',
                    '-c:a', 'copy',
                    '-movflags', '+faststart',
                    output_path
                ]

                status_text.text("⚙️ Processing video...")
                progress_bar.progress(40)
                result = subprocess.run(cmd, capture_output=True, text=True)
                progress_bar.progress(100)
                status_text.text("✅ Done!")

                if result.returncode != 0:
                    st.error("❌ FFmpeg Error:")
                    st.code(result.stderr)
                else:
                    st.success("🎉 Video flipped successfully!")
                    with open(output_path, "rb") as f:
                        video_bytes = f.read()
                    st.session_state.processed = True
                    st.session_state.video_bytes = video_bytes
                    st.session_state.file_name = output_filename

            except Exception as e:
                st.error(f"💥 Unexpected error: {str(e)}")
            finally:
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

# ==============================
# 🎬 4. Preview Section (Below Process)
# ==============================
if st.session_state.processed and st.session_state.video_bytes:
    st.markdown('<div class="section-header">🎬 Preview Your Flipped Video</div>', unsafe_allow_html=True)
    st.video(st.session_state.video_bytes)

    st.download_button(
        label="📥 Download Flipped Video",
        data=st.session_state.video_bytes,
        file_name=st.session_state.file_name,
        mime="video/mp4",
        use_container_width=True
    )
