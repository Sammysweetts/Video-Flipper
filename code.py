import os
import tempfile
import streamlit as st
import subprocess
import shutil

# --- Page Configuration ---
st.set_page_config(
    page_title="🔄 Video Flipper",
    page_icon="📼",
    layout="wide"
)

# --- CSS Styling for a Better UI ---
st.markdown("""
<style>
    .main {
        background-color: #f9fafc;
    }
    .stButton>button {
        color: white;
        background: linear-gradient(90deg, #0066ff, #00ccff);
        border: none;
        border-radius: 8px;
        padding: 0.5em 1em;
    }
    .stDownloadButton>button {
        background-color: #10b981;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    .stProgress div div div {
        background-color: #10b981 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- App Title and Description ---
st.markdown("<h1 style='text-align:center;'>🔄 Video Flipper</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Flip your videos <b>Horizontally</b> and/or <b>Vertically</b> with ease!</p>", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExc3MwZDFxcmg3a2htZ3ZmMjl5aTFlZ2w5ZTdrbDlmeDdwbHFndXBuNyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/IfyLZHq14PjUzKhG3p/giphy.gif", use_column_width=True)
    st.markdown("## 💡 How it works")
    with st.expander("See explanation"):
        st.info("""
        1. Upload a video.
        2. Choose flip direction(s).
        3. Click 'Flip Video.'
        4. Download or preview it right here.
        """)

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

# --- UI Divider ---
st.markdown("---")

# --- Control Panel ---
st.markdown("### ⚙️ Flip Settings & Upload")
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("#### 🎛️ Flip Options")
    flip_horizontal = st.checkbox("🔁 Flip Horizontal", value=True)
    flip_vertical = st.checkbox("🔃 Flip Vertical", value=False)

with col2:
    st.markdown("#### 📤 Upload your Video")
    uploaded_file = st.file_uploader(
        "Choose a video file to process",
        type=["mp4", "mov", "avi", "mkv"],
        on_change=reset_state,
        label_visibility="collapsed"
    )

# --- Video Processing Section ---
if uploaded_file is not None:
    st.markdown("### ▶️ Ready to Process?")
    st.markdown("✅ Click the button below to flip your video based on the selected direction(s).")

    if st.button("🚀 Flip Video", type="primary", use_container_width=True):
        if not flip_horizontal and not flip_vertical:
            st.error("❗ Please select at least one flip direction.")
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
                    st.error("⚠️ FFmpeg Error:")
                    st.code(result.stderr)
                else:
                    st.success("🎉 Video processed successfully!")

                    with open(output_path, "rb") as f:
                        video_bytes = f.read()

                    st.session_state.processed = True
                    st.session_state.video_bytes = video_bytes
                    st.session_state.file_name = output_filename

            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")
            finally:
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

# --- Display Processed Video ---
if st.session_state.processed and st.session_state.video_bytes:
    st.markdown("---")
    st.markdown("## 🎞️ Your Flipped Video")
    
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
st.markdown("<div style='text-align:center;'>Made with ❤️ using FFmpeg & Streamlit</div>", unsafe_allow_html=True)
