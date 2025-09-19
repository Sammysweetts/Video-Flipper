import streamlit as st
import os
import subprocess
from base64 import b64encode
import time
from io import BytesIO
import tempfile

# Define flip function (horizontal/vertical/both)
def flip_video(input_file, output_file, flip_horizontal=False, flip_vertical=False):
    flip_filters = []
    if flip_horizontal:
        flip_filters.append('hflip')
    if flip_vertical:
        flip_filters.append('vflip')

    if not flip_filters:
        raise ValueError("You must enable at least one flip direction.")
    
    flip_filter_str = ",".join(flip_filters)

    # Visually lossless, browser-compatible encoding
    cmd = [
        'ffmpeg', '-y',
        '-i', input_file,
        '-vf', flip_filter_str,
        '-c:v', 'libx264',
        '-crf', '17',
        '-preset', 'fast',
        '-c:a', 'aac',
        '-b:a', '192k',
        output_file
    ]

    print("Running FFmpeg command:")
    print(" ".join(cmd))

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print("⚠️ FFmpeg Error:")
        print(result.stderr)
    else:
        print("✅ Video processed successfully.")

# Streamlit UI
st.title("Video Flipper")
st.write("Upload a video and choose the flip direction (horizontal/vertical) to process.")

# Upload video
uploaded_file = st.file_uploader("Choose a video file", type=["mp4"])

# Flip options
flip_horizontal = st.checkbox("Flip horizontally")
flip_vertical = st.checkbox("Flip vertically")

if uploaded_file is not None:
    # Create a temporary file for the uploaded video
    temp_input_file = tempfile.NamedTemporaryFile(delete=False)
    temp_input_file.write(uploaded_file.read())
    temp_input_file.close()
    
    # Generate output filename
    temp_output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_output_file.close()

    if st.button("Flip Video"):
        try:
            # Process the video
            flip_video(temp_input_file.name, temp_output_file.name, flip_horizontal, flip_vertical)

            # Provide download link
            st.success("✅ Video processed successfully.")
            
            # Display the video
            with open(temp_output_file.name, 'rb') as f:
                video_bytes = f.read()

            video_data_url = "data:video/mp4;base64," + b64encode(video_bytes).decode()

            st.video(video_data_url)

            # Trigger download of the flipped video
            st.download_button(
                label="Download Flipped Video",
                data=video_bytes,
                file_name="flipped_output.mp4",
                mime="video/mp4"
            )
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
else:
    st.info("Please upload a video file to get started.")
