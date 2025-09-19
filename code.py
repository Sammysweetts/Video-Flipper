import streamlit as st
import os
import subprocess
from tempfile import NamedTemporaryFile
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Video Flipper",
    page_icon="🔄",
    layout="wide"
)

# App title and description
st.title("🔄 Video Flipper")
st.markdown("""
Upload a video and flip it horizontally, vertically, or both!
""")

# File uploader
uploaded_file = st.file_uploader(
    "Choose a video file", 
    type=["mp4", "mov", "avi", "mkv"],
    accept_multiple_files=False
)

# Flip options
col1, col2 = st.columns(2)
with col1:
    flip_h = st.checkbox("Flip Horizontally", value=True)
with col2:
    flip_v = st.checkbox("Flip Vertically")

# Process button
process_btn = st.button("Flip Video!")

def flip_video(input_path, output_path, flip_horizontal, flip_vertical):
    """Flip video using FFmpeg"""
    flip_filters = []
    if flip_horizontal:
        flip_filters.append('hflip')
    if flip_vertical:
        flip_filters.append('vflip')

    if not flip_filters:
        raise ValueError("You must enable at least one flip direction.")
    
    flip_filter_str = ",".join(flip_filters)

    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-vf', flip_filter_str,
        '-c:v', 'libx264',
        '-crf', '17',
        '-preset', 'fast',
        '-c:a', 'aac',
        '-b:a', '192k',
        output_path
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        st.error("FFmpeg Error:")
        st.code(result.stderr)
        return False
    return True

if uploaded_file and process_btn:
    with st.spinner("Processing your video..."):
        # Save uploaded file to temp file
        with NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
            tmp.write(uploaded_file.read())
            input_path = tmp.name
        
        # Create output file path
        output_path = f"flipped_{uploaded_file.name}"
        
        # Process video
        success = flip_video(
            input_path=input_path,
            output_path=output_path,
            flip_horizontal=flip_h,
            flip_vertical=flip_v
        )
        
        # Clean up input file
        os.unlink(input_path)
        
        if success:
            st.success("Video processed successfully!")
            
            # Display the video
            st.video(output_path)
            
            # Download button
            with open(output_path, "rb") as f:
                st.download_button(
                    label="Download Flipped Video",
                    data=f,
                    file_name=output_path,
                    mime="video/mp4"
                )
            
            # Clean up output file
            os.unlink(output_path)
