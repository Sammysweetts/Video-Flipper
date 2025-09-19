import os
import tempfile
import streamlit as st
import subprocess

# Set page config
st.set_page_config(
    page_title="Video Flipper",
    page_icon="🔄",
    layout="wide"
)

# App title and description
st.title("🔄 Video Flipper")
st.markdown("""
Upload a video and flip it horizontally or vertically. The processed video will maintain high quality and be available for download.
""")

# Sidebar controls (only flip options)
with st.sidebar:
    st.header("Flip Options")
    flip_horizontal = st.checkbox("Flip Horizontal", value=True)
    flip_vertical = st.checkbox("Flip Vertical", value=False)

# File uploader
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file is not None:
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, uploaded_file.name)
    output_path = os.path.join(temp_dir, "flipped_" + uploaded_file.name)
    
    # Save uploaded file to temp
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Process video
    if st.button("Flip Video"):
        with st.spinner("Processing video (this may take a while for large files)..."):
            try:
                # Build flip filters
                flip_filters = []
                if flip_horizontal:
                    flip_filters.append('hflip')
                if flip_vertical:
                    flip_filters.append('vflip')

                if not flip_filters:
                    st.error("Please select at least one flip direction.")
                    st.stop()
                
                flip_filter_str = ",".join(flip_filters)

                # FFmpeg command with optimal quality settings
                cmd = [
                    'ffmpeg', '-y',
                    '-i', input_path,
                    '-vf', flip_filter_str,
                    '-c:v', 'libx264',       # H.264 codec
                    '-crf', '18',            # High quality (range is 0-51, lower is better)
                    '-preset', 'slow',       # Better compression (slower encoding)
                    '-tune', 'film',         # Optimize for high quality video
                    '-c:a', 'aac',           # Audio codec
                    '-b:a', '192k',          # Audio bitrate
                    '-movflags', '+faststart', # Enable streaming
                    output_path
                ]

                # Run FFmpeg
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                if result.returncode != 0:
                    st.error("FFmpeg Error:")
                    st.code(result.stderr)
                else:
                    st.success("Video processed successfully with high quality settings!")
                    
                    # Display the processed video
                    with open(output_path, "rb") as f:
                        video_bytes = f.read()
                    
                    st.video(video_bytes)
                    
                    # Download button
                    st.download_button(
                        label="Download Flipped Video",
                        data=video_bytes,
                        file_name="flipped_" + uploaded_file.name,
                        mime="video/mp4"
                    )
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
