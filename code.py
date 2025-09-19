# app.py

import streamlit as st
import subprocess
import os
import uuid  # Used to create unique filenames

# --- Core FFmpeg Logic (from your Colab notebook) ---
# This function is mostly unchanged, but we'll add some Streamlit feedback.
def flip_video(input_path, output_path, flip_horizontal, flip_vertical):
    """
    Flips a video using FFmpeg and provides progress updates.
    """
    flip_filters = []
    if flip_horizontal:
        flip_filters.append('hflip')
    if flip_vertical:
        flip_filters.append('vflip')

    if not flip_filters:
        raise ValueError("You must select at least one flip direction (horizontal or vertical).")

    flip_filter_str = ",".join(flip_filters)

    # FFmpeg command for web-compatible, visually lossless output
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

    # Run the command and capture output
    process = subprocess.run(cmd, capture_output=True, text=True)

    if process.returncode != 0:
        # If FFmpeg fails, show the error
        st.error(f"FFmpeg failed with return code {process.returncode}")
        st.code(process.stderr)
        return False
    
    return True

# --- Streamlit User Interface ---

st.set_page_config(page_title="Video Flipper", layout="centered")

st.title("🎬 Video Flipper")
st.markdown("Upload a video, choose how you want to flip it, and get your new video instantly!")

# Create a temporary directory to store uploaded and processed files
TEMP_DIR = "temp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# 1. File Uploader
uploaded_file = st.file_uploader(
    "Choose a video file", 
    type=['mp4', 'mov', 'avi', 'mkv']
)

if uploaded_file is not None:
    # 2. Flip options
    st.subheader("Flip Options")
    col1, col2 = st.columns(2)
    with col1:
        flip_h = st.checkbox("Flip Horizontally", value=True)
    with col2:
        flip_v = st.checkbox("Flip Vertically")

    # 3. Process Button
    if st.button("Process Video", type="primary"):
        if not flip_h and not flip_v:
            st.warning("Please select at least one flip direction.")
        else:
            # Generate unique file paths to avoid conflicts
            unique_id = uuid.uuid4().hex
            input_path = os.path.join(TEMP_DIR, f"{unique_id}_{uploaded_file.name}")
            output_path = os.path.join(TEMP_DIR, f"flipped_{unique_id}.mp4")

            # Save uploaded file to the temporary directory
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Process the video with a spinner
            with st.spinner("Flipping your video... This might take a moment."):
                success = flip_video(input_path, output_path, flip_h, flip_v)

            if success:
                st.success("✅ Video processed successfully!")

                # 4. Display the result
                st.subheader("Flipped Video")
                video_file = open(output_path, 'rb')
                video_bytes = video_file.read()
                st.video(video_bytes)

                # 5. Provide a download button
                st.download_button(
                    label="Download Flipped Video",
                    data=video_bytes,
                    file_name=f"flipped_{uploaded_file.name}.mp4",
                    mime="video/mp4"
                )

            # Clean up temporary files
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                # We can't delete it immediately if the download button needs it,
                # but in Streamlit's execution model, this is generally safe.
                # For more complex apps, you might manage cleanup differently.
                pass 
else:
    st.info("Upload a video file to get started.")
