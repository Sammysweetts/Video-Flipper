import os
import tempfile
import streamlit as st
import subprocess
import shutil # Import shutil for robust directory cleanup

# --- Page Configuration ---
st.set_page_config(
    page_title="Video Flipper",
    page_icon="🔄",
    layout="wide"
)

# --- App Title and Description ---
st.title("🔄 Video Flipper")
st.markdown("A simple app to flip your videos horizontally or vertically.")

# --- Initialize Session State ---
# This helps to keep the app state persistent across reruns
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'video_bytes' not in st.session_state:
    st.session_state.video_bytes = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = ""

# --- Callback to reset state when a new file is uploaded ---
def reset_state():
    st.session_state.processed = False
    st.session_state.video_bytes = None
    st.session_state.file_name = ""

st.write("---")

# --- Unified Control Panel (Options and Uploader) ---
col1, col2 = st.columns([1, 2]) # Give uploader more space

with col1:
    st.subheader("Flip Options")
    flip_horizontal = st.checkbox("Flip Horizontal", value=True)
    flip_vertical = st.checkbox("Flip Vertical", value=False)

with col2:
    st.subheader("Upload Video")
    uploaded_file = st.file_uploader(
        "Choose a video file to process...",
        type=["mp4", "mov", "avi", "mkv"],
        on_change=reset_state,
        label_visibility="collapsed" # Hides the default label for a cleaner look
    )

# --- Processing Logic and Button ---
# This section only appears after a file is uploaded
if uploaded_file is not None:
    if st.button("Flip Video", type="primary", use_container_width=True):
        # Ensure at least one flip direction is selected
        if not flip_horizontal and not flip_vertical:
            st.error("Please select at least one flip direction.")
        else:
            temp_dir = None # Initialize to ensure it's available in the finally block
            try:
                # Create a temporary directory to store files
                temp_dir = tempfile.mkdtemp()
                input_path = os.path.join(temp_dir, uploaded_file.name)
                # Ensure output is always .mp4 for browser compatibility
                output_filename = os.path.splitext(uploaded_file.name)[0] + "_flipped.mp4"
                output_path = os.path.join(temp_dir, output_filename)

                # Save uploaded file to the temporary directory
                with open(input_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                progress_bar = st.progress(0, text="Processing video, please wait...")
                
                # Build the FFmpeg filter string
                flip_filters = []
                if flip_horizontal:
                    flip_filters.append('hflip')
                if flip_vertical:
                    flip_filters.append('vflip')
                flip_filter_str = ",".join(flip_filters)

                # FFmpeg command with high-quality settings
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

                # Run FFmpeg command
                result = subprocess.run(cmd, capture_output=True, text=True)
                progress_bar.progress(100) # Mark as complete

                if result.returncode != 0:
                    st.error("FFmpeg Error:")
                    st.code(result.stderr)
                else:
                    st.success("Video processed successfully!")
                    
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

# --- Display Results from Session State ---
if st.session_state.processed and st.session_state.video_bytes:
    st.write("---")
    st.subheader("Your Flipped Video")
    st.video(st.session_state.video_bytes)
    
    st.download_button(
        label="Download Flipped Video",
        data=st.session_state.video_bytes,
        file_name=st.session_state.file_name,
        mime="video/mp4",
        use_container_width=True
    )
