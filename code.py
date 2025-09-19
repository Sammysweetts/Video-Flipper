import os
import tempfile
import streamlit as st
import subprocess
import shutil

# --- Page Configuration ---
st.set_page_config(
    page_title="Video Flipper 🎬",
    page_icon="🔄",
    layout="wide"
)

# --- Custom Styles ---
st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
    }
    .description {
        text-align: center;
        font-size: 18px;
        color: #4f4f4f;
    }
    .section-title {
        font-size: 22px;
        margin-top: 30px;
        font-weight: bold;
        color: #3366cc;
    }
    </style>
""", unsafe_allow_html=True)

# --- App Title and Description ---
st.markdown('<div class="title">🔄 Video Flipper</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Flip your videos horizontally or vertically with ease!</div>', unsafe_allow_html=True)

st.write("---")

# --- Initialize Session State ---
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'video_bytes' not in st.session_state:
    st.session_state.video_bytes = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = ""

def reset_state():
    st.session_state.processed = False
    st.session_state.video_bytes = None
    st.session_state.file_name = ""

# --- UI Layout ---
with st.expander("📁 Upload & Options", expanded=True):
    tab1, tab2 = st.tabs(["⚙️ Flip Options", "📤 Upload Video"])

    with tab1:
        st.markdown('<div class="section-title">Select Flip Direction</div>', unsafe_allow_html=True)
        flip_horizontal = st.checkbox("🔁 Flip Horizontal", value=True)
        flip_vertical = st.checkbox("🔃 Flip Vertical", value=False)

    with tab2:
        st.markdown('<div class="section-title">Upload Your Video File</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Choose a video file to flip",
            type=["mp4", "mov", "avi", "mkv"],
            on_change=reset_state
        )

st.write("---")

# --- Processing Logic ---
if uploaded_file is not None:
    st.markdown('<div class="section-title">🚀 Ready to Process</div>', unsafe_allow_html=True)

    if st.button("✨ Flip Video Now", type="primary", use_container_width=True):
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
                status_text.text("Initializing...")

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

                status_text.text("🔄 Flipping video, please wait...")
                progress_bar.progress(30)

                result = subprocess.run(cmd, capture_output=True, text=True)
                progress_bar.progress(100)
                status_text.text("✅ Done!")

                if result.returncode != 0:
                    st.error("❌ FFmpeg Error:")
                    st.code(result.stderr)
                else:
                    st.success("🎉 Video processed successfully!")

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

# --- Display Result ---
if st.session_state.processed and st.session_state.video_bytes:
    st.write("---")
    st.markdown('<div class="section-title">🎬 Your Flipped Video</div>', unsafe_allow_html=True)
    st.video(st.session_state.video_bytes)

    st.download_button(
        label="📥 Download Flipped Video",
        data=st.session_state.video_bytes,
        file_name=st.session_state.file_name,
        mime="video/mp4",
        use_container_width=True
    )
