import streamlit as st
import tempfile
import os
import ffmpeg

# Title
st.title("🎬 Free Video Flipper")

# Instructions
st.markdown("""
Upload a video, choose the flip direction, and download the flipped version.
""")

# Upload video
uploaded_file = st.file_uploader("📁 Upload a video file", type=["mp4", "mov", "avi", "mkv"])

# Choose flip direction
flip_option = st.radio("🔁 Choose flip direction:", ["Horizontal", "Vertical", "Both"], index=0)

# Output filename (safe default)
output_filename = "flipped_output.mp4"

def process_video(input_path, output_path, flip_option):
    # Determine FFmpeg flip filter
    if flip_option == "Horizontal":
        flip_filter = "hflip"
    elif flip_option == "Vertical":
        flip_filter = "vflip"
    elif flip_option == "Both":
        flip_filter = "hflip,vflip"
    else:
        raise ValueError("Invalid flip option selected.")

    # FFmpeg pipeline
    try:
        (
            ffmpeg
            .input(input_path)
            .video.filter('transpose', 2) if flip_option == "Vertical" else None
        )
        (
            ffmpeg
            .input(input_path)
            .output(
                output_path,
                vf=flip_filter,
                vcodec='libx264',
                crf=17,
                preset='fast',
                acodec='aac',
                audio_bitrate='192k'
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return True
    except ffmpeg.Error as e:
        st.error("❌ FFmpeg error occurred:")
        st.text(e.stderr.decode())
        return False

if uploaded_file:
    # Save to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input_file:
        input_path = temp_input_file.name
        temp_input_file.write(uploaded_file.read())

    # Output temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output_file:
        output_path = temp_output_file.name

    if st.button("⚙️ Flip Video"):
        with st.spinner("Processing..."):
            success = process_video(input_path, output_path, flip_option)
            if success:
                st.success("✅ Done! Here's your flipped video:")
                # Display video
                st.video(output_path)
                # Download link
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Flipped Video",
                        data=f,
                        file_name="flipped_video.mp4",
                        mime="video/mp4"
                    )
