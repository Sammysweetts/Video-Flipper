import streamlit as st
import subprocess
import os
import tempfile
from pathlib import Path

# Title
st.title("🎬 Video Flipper with FFmpeg")

# Instructions
st.markdown("Upload an MP4 video and choose the flip direction(s) to process it using FFmpeg!")

# File uploader
uploaded_file = st.file_uploader("📁 Upload your video (.mp4)", type=["mp4"])

# Flip direction options
flip_horizontal = st.checkbox("↔️ Flip Horizontally", value=True)
flip_vertical = st.checkbox("↕️ Flip Vertically")

# Function to run ffmpeg
def flip_video(input_path, output_path, flip_horizontal, flip_vertical):
    flip_filters = []
    if flip_horizontal:
        flip_filters.append("hflip")
    if flip_vertical:
        flip_filters.append("vflip")
    
    if not flip_filters:
        raise ValueError("You must select at least one flip direction.")

    filter_str = ",".join(flip_filters)

    cmd = [
        'ffmpeg', '-y',
        '-i', str(input_path),
        '-vf', filter_str,
        '-c:v', 'libx264',
        '-crf', '17',
        '-preset', 'fast',
        '-c:a', 'aac',
        '-b:a', '192k',
        str(output_path)
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        st.error("⚠️ FFmpeg error detected:")
        st.code(result.stderr)
        return False
    return True

# Main logic
if uploaded_file and (flip_horizontal or flip_vertical):
    with st.spinner("Processing video..."):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            input_path = tmpdir / "input.mp4"
            output_path = tmpdir / "output.mp4"

            with open(input_path, "wb") as f:
                f.write(uploaded_file.read())

            success = flip_video(input_path, output_path, flip_horizontal, flip_vertical)

            if success:
                st.success("✅ Video flipped successfully!")

                # Display video
                st.video(str(output_path))

                # Download button
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Flipped Video",
                        data=f,
                        file_name="flipped_video.mp4",
                        mime="video/mp4"
                    )
else:
    if uploaded_file:
        st.warning("⚠️ Please select at least one flip direction.")
