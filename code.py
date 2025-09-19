import streamlit as st
import tempfile
import os
import ffmpeg

st.set_page_config(page_title="🎬 Free Video Flipper", layout="centered")

# App Title and Description
st.title("🎬 Free Video Flipper")
st.markdown("Upload a video, choose the flip direction, and download the flipped version.")

# Upload a video file
uploaded_file = st.file_uploader("📁 Upload a video file", type=["mp4", "mov", "avi", "mkv", "mpeg4"])

# Flip direction selection
flip_option = st.radio("🔁 Choose flip direction:", ["Horizontal", "Vertical", "Both"], index=0)

# Process button is only available if a file is uploaded
if uploaded_file:
    # Create temporary input & output files
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
        temp_input.write(uploaded_file.read())
        input_path = temp_input.name

    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

    # Define the flip filter based on user selection
    if flip_option == "Horizontal":
        vf_filter = "hflip"
    elif flip_option == "Vertical":
        vf_filter = "vflip"
    elif flip_option == "Both":
        vf_filter = "hflip,vflip"

    # Flip the video when the button is clicked
    if st.button("⚙️ Flip Video"):
        with st.spinner("Processing... Please wait."):
            try:
                (
                    ffmpeg
                    .input(input_path)
                    .output(
                        output_path,
                        vf=vf_filter,
                        vcodec="libx264",
                        crf=17,
                        preset="fast",
                        acodec="aac",
                        audio_bitrate="192k"
                    )
                    .overwrite_output()
                    .run(quiet=True)
                )
                st.success("✅ Processing complete!")
                
                # Display flipped video
                with open(output_path, "rb") as vid:
                    video_bytes = vid.read()
                    st.video(video_bytes)
                
                # Download button
                st.download_button("⬇️ Download Flipped Video", data=video_bytes, file_name="flipped_video.mp4", mime="video/mp4")

            except ffmpeg.Error as e:
                st.error("❌ FFmpeg processing failed.")
                st.text(e.stderr.decode())
