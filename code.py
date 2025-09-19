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
st.markdown("""
Upload a video, choose your flip options, and click the button to process. 
The processed video will maintain high quality and be available for download.
""")

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

# --- File Uploader ---
st.info("Note: Uploading a new file will reset the state.")
uploaded_file = st.file_uploader(
    "Upload a video file",
    type=["mp4", "mov", "avi", "mkv"],
    on_change=reset_state
)

# --- Main Logic ---
if uploaded_file is not None:
    
    # --- Flip Options (now in the main interface) ---
    st.subheader("Flip Options")
    col1, col2, col3 = st.columns([1, 1, 3]) # Create columns for layout
    with col1:
        flip_horizontal = st.checkbox("Flip Horizontal", value=True)
    with col2:
        flip_vertical = st.checkbox("Flip Vertical", value=False)
    
    st.write("---") # Visual separator

    # --- Process Button ---
    if st.button("Flip Video", type="primary"):
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

                with st.spinner("Processing video (this may take a while for large files)..."):
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
                        '-c:v', 'libx264',       # H.264 codec
                        '-crf', '18',            # High quality (range is 0-51, lower is better)
                        '-preset', 'slow',       # Better compression (slower encoding)
                        '-c:a', 'copy',          # Copy audio stream without re-encoding (preserves quality)
                        '-movflags', '+faststart', # Optimize for web streaming
                        output_path
                    ]

                    # Run FFmpeg command
                    result = subprocess.run(cmd, capture_output=True, text=True)

                    if result.returncode != 0:
                        st.error("FFmpeg Error:")
                        st.code(result.stderr) # Use capture_output=True to get stderr
                    else:
                        st.success("Video processed successfully!")
                        
                        # Read the processed video file into memory
                        with open(output_path, "rb") as f:
                            video_bytes = f.read()
                        
                        # Store results in session state to persist them
                        st.session_state.processed = True
                        st.session_state.video_bytes = video_bytes
                        st.session_state.file_name = output_filename

            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
            finally:
                # **Crucial Cleanup Step**
                # Remove the temporary directory and all its contents
                if temp_dir and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

# --- Display Results from Session State ---
# This block runs if processing was successful in a previous run,
# ensuring the result stays on screen until a new file is uploaded.
if st.session_state.processed and st.session_state.video_bytes:
    st.subheader("Flipped Video")
    st.video(st.session_state.video_bytes)
    
    st.download_button(
        label="Download Flipped Video",
        data=st.session_state.video_bytes,
        file_name=st.session_state.file_name,
        mime="video/mp4"
    )
