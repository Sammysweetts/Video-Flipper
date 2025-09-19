import streamlit as st
import os
import subprocess
from tempfile import NamedTemporaryFile
from pathlib import Path
import ffmpeg

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
This app uses pure Python implementation for video processing.
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
    """Flip video using ffmpeg-python"""
    try:
        stream = ffmpeg.input(input_path)
        
        if flip_horizontal and flip_vertical:
            stream = stream.hflip().vflip()
        elif flip_horizontal:
            stream = stream.hflip()
        elif flip_vertical:
            stream = stream.vflip()
        
        stream = stream.output(
            output_path,
            vcodec='libx264',
            crf=17,
            preset='fast',
            acodec='aac',
            audio_bitrate='192k'
        )
        
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        return True
    except ffmpeg.Error as e:
        st.error(f"Video processing failed: {e.stderr.decode('utf-8')}")
        return False
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return False

if uploaded_file and process_btn:
    with st.spinner("Processing your video..."):
        # Save uploaded file to temp file
        with NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_input:
            tmp_input.write(uploaded_file.read())
            input_path = tmp_input.name
        
        # Create output file path
        output_filename = f"flipped_{Path(uploaded_file.name).stem}.mp4"
        output_path = os.path.join("/tmp", output_filename)
        
        # Process video
        success = flip_video(
            input_path=input_path,
            output_path=output_path,
            flip_horizontal=flip_h,
            flip_vertical=flip_v
        )
        
        # Clean up input file
        try:
            os.unlink(input_path)
        except:
            pass
        
        if success:
            st.success("✅ Video processed successfully!")
            
            # Display the video
            st.video(output_path)
            
            # Download button
            with open(output_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download Flipped Video",
                    data=f,
                    file_name=output_filename,
                    mime="video/mp4"
                )
            
            # Clean up output file
            try:
                os.unlink(output_path)
            except:
                pass
        else:
            st.error("❌ Failed to process video. Please try again.")
