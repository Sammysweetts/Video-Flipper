import os
import tempfile
import streamlit as st
import subprocess
import shutil

# --- Page Configuration ---
st.set_page_config(
    page_title="🔄 Video Flipper",
    page_icon="🎬",
    layout="centered"
)

# --- CSS Styling for Stylish Layout ---
st.markdown("""
<style>
    .main {
        background-color: #f9fafc;
    }
    .stButton>button {
        color: white;
        background: linear-gradient(90deg, #0066ff, #00ccff);
        font-weight: 600;
        border: none;
        border-radius: 7px;
        padding: 0.5em 1.2em;
    }
    .stDownloadButton>button {
        background-color: #10b981;
        color: white;
        font-weight: bold;
        border-radius: 7px;
    }
    .stProgress div div div {
        background-color: #10b981 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'video_bytes' not in st.session_state:
    st.session_state.video_bytes = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = ""

# --- Callback to Reset Session State ---
def reset_state():
    st.session_state.processed = False
    st.session_state.video_bytes = None
    st.session_state.file_name = ""

# --- Title ---
st.markdown("<h1 style='text-align:center;'>🔄 Video Flipper</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>A simple tool to flip your videos horizontally or vertically!</p>", unsafe_allow_html=True)

# --- File Upload Section ---
st.markdown("## 📤 Step 1: Upload Video")
uploaded_file = st.file_uploader(
    "Choose a video file to flip (mp4, mov, avi, mkv):",
    type=["mp4", "mov", "avi", "mkv"],
    on_change=reset_state,
    label_visibility="visible"
)

# --- Flip Options Section ---
st.markdown("## 🎛️ Step 2: Select Flip Options")
col1, col2 = st.columns(2)
with col1:
    flip_horizontal = st.checkbox("🔁 Flip Horizontally", value=True)
with col2:
    flip_vertical = st.checkbox("🔃 Flip Vertically", value=False)

# --- Process Button ---
if uploaded_file:
    st.markdown("## 🚀 Step 3: Process Video")
    st.markdown("Click the button below to flip your video based on selections.")

    if st.button("🚩 Flip Video Now", type="primary", use_container_width=True):
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

                progress_bar = st.progress(0, text="Processing video, please wait...")

                # Build filter string
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
                    st.error("❌ FFmpeg processing failed!")
                    st.code(result.stderr)
                else:
                    st.success("✅ Video processed successfully!")

                    with open(output_path, "rb") as f:
                        video_bytes = f.read()

                    st.session_state.processed = True
                    st.session_state.video_bytes = video_bytes
                    st.session_state.file_name = output_filename

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
            finally:
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

# --- Preview and Download Section ---
if st.session_state.processed and st.session_state.video_bytes:
    st.markdown("## 🎞️ Step 4: Preview & Download")
    st.video(st.session_state.video_bytes)

    st.download_button(
        label="⬇️ Download Your Flipped Video",
        data=st.session_state.video_bytes,
        file_name=st.session_state.file_name,
        mime="video/mp4",
        use_container_width=True
    )

# --- Footer Credit ---
st.markdown("---")
st.markdown("<div style='text-align: center; font-size: 14px;'>✨ Made with Streamlit + FFmpeg ❤️</div>", unsafe_allow_html=True)
