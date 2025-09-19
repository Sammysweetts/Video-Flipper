import os
import tempfile
import streamlit as st
import subprocess
import shutil

# --- Page Configuration ---
st.set_page_config(
    page_title="Video Flipper Pro",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- App Title and Description ---
st.title("🔄 Video Flipper Pro")
st.markdown("A sleek and simple app to flip your videos horizontally or vertically with ease.")

# --- Initialize Session State ---
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'video_bytes' not in st.session_state:
    st.session_state.video_bytes = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = ""

# --- Callback to reset state when a new file is uploaded ---
def reset_state():
    """Resets the session state variables to their defaults."""
    st.session_state.processed = False
    st.session_state.video_bytes = None
    st.session_state.file_name = ""

# --- Sidebar for Options and Instructions ---
with st.sidebar:
    st.header("⚙️ Flip Controls")
    st.write("Configure how you want to flip your video.")
    
    flip_horizontal = st.checkbox("Flip Horizontal (Left/Right)", value=True)
    flip_vertical = st.checkbox("Flip Vertical (Up/Down)", value=False)
    
    st.divider()
    
    st.header("💡 How to Use")
    st.info(
        """
        1. **Upload** your video file in the main panel.
        2. **Configure** the flip options on this sidebar.
        3. **Click** the 'Flip My Video!' button.
        4. **Preview & Download** your processed video.
        """
    )
    
    st.divider()
    st.success("Powered by [Streamlit](https://streamlit.io/) & [FFmpeg](https://ffmpeg.org/)")


# --- Main Page Layout ---

# --- STEP 1: UPLOAD VIDEO ---
upload_container = st.container(border=True)
with upload_container:
    st.subheader("Step 1: Upload Your Video File")
    uploaded_file = st.file_uploader(
        "Choose a video file...",
        type=["mp4", "mov", "avi", "mkv"],
        on_change=reset_state,
        label_visibility="collapsed"
    )

# --- Processing Logic and Button ---
if uploaded_file is not None:
    # --- STEP 2: PREVIEW & PROCESS ---
    process_container = st.container(border=True)
    with process_container:
        st.subheader("Step 2: Preview & Process")
        
        # Show a preview of the original video
        st.write("Your original video:")
        st.video(uploaded_file)
        
        st.info("Adjust flip settings in the sidebar, then click the button below to start.")

        if st.button("🎬 Flip My Video!", type="primary", use_container_width=True):
            if not flip_horizontal and not flip_vertical:
                st.error("⚠️ Please select at least one flip direction in the sidebar.")
            else:
                temp_dir = None
                with st.spinner('Flipping your video... This might take a moment!'):
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
                            flip_filters.append('hflip')
                        if flip_vertical:
                            flip_filters.append('vflip')
                        flip_filter_str = ",".join(flip_filters)

                        cmd = [
                            'ffmpeg', '-y', '-i', input_path, '-vf', flip_filter_str,
                            '-c:v', 'libx264', '-crf', '18', '-preset', 'slow',
                            '-c:a', 'copy', '-movflags', '+faststart', output_path
                        ]
                        
                        progress_bar.progress(50, text="Running FFmpeg command...")
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        progress_bar.progress(100, text="Finalizing...")

                        if result.returncode != 0:
                            st.error("FFmpeg Error:")
                            st.code(result.stderr, language="bash")
                        else:
                            st.success("✅ Video processed successfully!")
                            with open(output_path, "rb") as f:
                                video_bytes = f.read()
                            
                            st.session_state.processed = True
                            st.session_state.video_bytes = video_bytes
                            st.session_state.file_name = output_filename

                    except Exception as e:
                        st.error(f"An unexpected error occurred: {str(e)}")
                    finally:
                        if temp_dir and os.path.exists(temp_dir):
                            shutil.rmtree(temp_dir)

# --- STEP 3: DISPLAY RESULTS (from Session State) ---
if st.session_state.processed and st.session_state.video_bytes:
    result_container = st.container(border=True)
    with result_container:
        st.header("✨ Your Flipped Video is Ready!")
        st.video(st.session_state.video_bytes)
        
        st.download_button(
            label="📥 Download Flipped Video",
            data=st.session_state.video_bytes,
            file_name=st.session_state.file_name,
            mime="video/mp4",
            use_container_width=True,
            type="primary"
        )
