import streamlit as st
import subprocess
import os
import uuid

# Function to flip the video using ffmpeg
def flip_video(input_path, output_path, flip_horizontal=False, flip_vertical=False):
    filters = []
    if flip_horizontal:
        filters.append("hflip")
    if flip_vertical:
        filters.append("vflip")

    if not filters:
        raise ValueError("At least one flip direction must be selected.")

    filter_str = ",".join(filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", filter_str,
        "-c:v", "libx264",
        "-crf", "17",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "192k",
        output_path
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr}")

# Streamlit UI
st.set_page_config(page_title="🎬 Video Flipper", layout="centered")
st.title("🎥 Video Flipper with FFmpeg")
st.markdown("Flip videos horizontally, vertically, or both — directly in your browser!")

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])

flip_horizontal = st.checkbox("Flip Horizontally")
flip_vertical = st.checkbox("Flip Vertically")

if uploaded_file and (flip_horizontal or flip_vertical):
    unique_id = str(uuid.uuid4())
    input_path = f"input_{unique_id}.mp4"
    output_path = f"output_{unique_id}.mp4"

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    try:
        with st.spinner("Flipping your video..."):
            flip_video(input_path, output_path, flip_horizontal, flip_vertical)

        st.success("✅ Video flipped successfully!")

        st.video(output_path)

        # Download button
        with open(output_path, "rb") as f:
            st.download_button("📥 Download Flipped Video", f, file_name="flipped_video.mp4", mime="video/mp4")

    except Exception as e:
        st.error(f"Error: {e}")

    # Clean up files after use (optional during streamlit session)
    try:
        os.remove(input_path)
        os.remove(output_path)
    except:
        pass

elif uploaded_file:
    st.warning("☝️ Please select at least one flip option.")
