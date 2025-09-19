import os
import tempfile
import streamlit as st
import subprocess
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
Upload a video (up to 200MB) to flip it horizontally or vertically. The processed video will maintain high quality.
""")

# Sidebar controls
with st.sidebar:
    st.header("Flip Options")
    flip_horizontal = st.checkbox("Flip Horizontal", value=True)
    flip_vertical = st.checkbox("Flip Vertical", value=False)
    st.markdown("---")
    st.info("Note: Large files may take longer to process")

# File uploader with size limit
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"], 
                                accept_multiple_files=False)

if uploaded_file is not None:
    # Check file size (200MB limit)
    if uploaded_file.size > 200 * 1024 * 1024:
        st.error("File too large! Please upload files under 200MB")
        st.stop()
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, uploaded_file.name)
    output_path = os.path.join(temp_dir, f"flipped_{uploaded_file.name}")
    
    # Save uploaded file to temp
    try:
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    except Exception as e:
        st.error(f"Failed to save file: {str(e)}")
        st.stop()
    
    # Process video
    if st.button("Flip Video"):
        with st.spinner("Processing video..."):
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
                    '-c:v', 'libx264',
                    '-crf', '18',
                    '-preset', 'slow',
                    '-tune', 'film',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-movflags', '+faststart',
                    output_path
                ]

                # Run FFmpeg with timeout
                try:
                    result = subprocess.run(cmd, timeout=300,  # 5 minute timeout
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE, 
                                         text=True)
                except subprocess.TimeoutExpired:
                    st.error("Processing took too long. Try a smaller file.")
                    st.stop()

                if result.returncode != 0:
                    st.error("FFmpeg Error:")
                    st.code(result.stderr)
                    st.stop()
                
                # Verify output file exists
                if not Path(output_path).exists():
                    st.error("Output file not created")
                    st.stop()

                # Display the processed video
                try:
                    with open(output_path, "rb") as f:
                        video_bytes = f.read()
                    
                    st.success("Processing complete!")
                    st.video(video_bytes)
                    
                    # Download button
                    st.download_button(
                        label="Download Flipped Video",
                        data=video_bytes,
                        file_name=f"flipped_{uploaded_file.name}",
                        mime="video/mp4"
                    )
                except Exception as e:
                    st.error(f"Failed to display video: {str(e)}")
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                # Clean up temp files
                for f in [input_path, output_path]:
                    try:
                        if os.path.exists(f):
                            os.remove(f)
                    except:
                        pass
