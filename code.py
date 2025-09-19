import os
import tempfile
import streamlit as st
import subprocess
import shutil

# --- Page Setup ---
st.set_page_config(
    page_title="Video Flipper",
    page_icon="🔄",
    layout="centered"
)

# --- Basic Styles ---
st.markdown("""
    <style>
        .app-title {
            text-align: center;
            margin-top: 20px;
            font-size: 36px;
            color: #333;
        }
        .subtext {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .section-header {
            font-size: 22px;
            font-weight: 600;
            margin-top: 30px;
            color: #222;
        }
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            background-color: #2563eb;
            color: white;
            height: 48px;
            font-size: 18px;
        }
        .stDownloadButton>button {
            background-color: #10b981;
            color: white;
            font-weight: 600;
            border-radius: 8px;
            height: 44px;
        }
        .stProgress div > div {
            background-color: #10b981 !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<div class='app-title'>🔄 Video Flipper</div>", unsafe_allow_html=True)
st.markdown("<div class='subtext'>Flip your video horizontally or vertically in seconds!</div>", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'video_bytes' not in st.session_state:
    st.session_state.video_bytes = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = ""

# --- Reset State ---
def reset_state():
    st.session_state.processed = False
    st.session_state.video_bytes = None
    st.session_state.file_name = ""

# -------------------------
# 🔼 Step 1: Upload Section
# -------------------------
st.markdown("### 📤 Step 1: Upload Your Video")
uploaded_file = st.file_uploader(
    "Supported formats: MP4, MOV, AVI, MKV",
    type=["mp4", "mov", "avi", "mkv"],
    on_change=reset_state,
    label_visibility="visible"
)

# -----------------------------
# 🎛️ Step 2: Flip Direction
# -----------------------------
if uploaded_file:
    st.markdown("### 🎚 Step 2: Choose Flip Options")

    col1, col2 = st.columns(2)
    with col1:
        flip_horizontal = st.checkbox("🔁 Flip Horizontally", value=True)
    with col2:
        flip_vertical = st.checkbox("🔃 Flip Vertically", value=False)

    st.markdown("### 🚀 Step 3: Process Your Video")

    if st.button("✨ Flip Video"):
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

                progress_bar = st.progress(0, text="Processing your video...")

                # Create filter
                flip_filters = []
                if flip_horizontal:
                    flip_filters.append("hflip")
                if flip_vertical:
                    flip_filters.append("vflip")
                flip_filter_str = ",".join(flip_filters)

                cmd = [
                    "ffmpeg", "-y",
                    "-i", input_path,
                    "-vf", flip_filter_str,
                    "-c:v", "libx264",
                    "-crf", "18",
                    "-preset", "slow",
                    "-c:a", "copy",
                    "-movflags", "+faststart",
                    output_path
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)
                progress_bar.progress(100)

                if result.returncode != 0:
                    st.error("🚫 FFmpeg failed!")
                    st.code(result.stderr)
                else:
                    st.success("✅ Video processing complete!")

                    with open(output_path, "rb") as f:
                        video_bytes = f.read()

                    st.session_state.processed = True
                    st.session_state.video_bytes = video_bytes
                    st.session_state.file_name = output_filename

            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
            finally:
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

# ----------------------------------
# 🎞️ Step 4: Preview and Download
# ----------------------------------
if st.session_state.processed and st.session_state.video_bytes:
    st.markdown("### 🎞️ Step 4: Preview & Download")

    st.video(st.session_state.video_bytes)

    st.download_button(
        label="⬇️ Download Flipped Video",
        data=st.session_state.video_bytes,
        file_name=st.session_state.file_name,
        mime="video/mp4",
        use_container_width=True
    )

# --- Footer ---
st.markdown("---")
st.markdown("<div style='text-align:center; font-size:14px; color:gray;'>Built with ❤️ using FFmpeg and Streamlit</div>", unsafe_allow_html=True)
