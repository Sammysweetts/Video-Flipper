import os
import streamlit as st
import subprocess
from base64 import b64encode

# Ensure FFmpeg is available
if not os.path.exists('/usr/bin/ffmpeg'):
    os.system('apt-get update && apt-get install -y ffmpeg')

# ✅ Set paths (to be stored in Streamlit’s temporary directories)
TEMP_INPUT_FILE = "/tmp/input_video.mp4"
TEMP_OUTPUT_FILE = "/tmp/flipped_output.mp4"

# ✅ Define flip function (horizontal/vertical/both)
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

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        st.error(f"FFmpeg Error: {result.stderr}")
    else:
        st.success("✅ Video processed successfully.")

# ✅ Streamlit interface
st.title("Video Flipper")

st.write("Upload a video file and select the flip direction:")

# Upload video
uploaded_file = st.file_uploader("Choose a video...", type=["mp4"])

# Select flip direction
flip_horizontal = st.checkbox("Flip Horizontally")
flip_vertical = st.checkbox("Flip Vertically")

if uploaded_file is not None:
    # Save the uploaded file to the temp directory
    with open(TEMP_INPUT_FILE, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.video(uploaded_file)  # Display the uploaded video

    # Button to process the video
    if st.button("Flip Video"):
        flip_video(TEMP_INPUT_FILE, TEMP_OUTPUT_FILE, flip_horizontal, flip_vertical)
        
        # Display the flipped video
        with open(TEMP_OUTPUT_FILE, 'rb') as f:
            flipped_video = f.read()
            data_url = "data:video/mp4;base64," + b64encode(flipped_video).decode()
            st.video(data_url)  # Display the flipped video
        
        # Trigger download link
        st.download_button(
            label="Download Flipped Video",
            data=flipped_video,
            file_name="flipped_output.mp4",
            mime="video/mp4"
        )
