import streamlit as st
import os
import time
import subprocess
from base64 import b64encode # For displaying video in web browser
from moviepy.editor import VideoFileClip # For getting video duration
import tempfile # For handling temporary files safely

# --- Configuration ---
FFMPEG_BINARY = "ffmpeg" # Assumes ffmpeg is available in the environment (e.g., via apt install in Docker/Streamlit sharing)

# --- Streamlit Page Setup ---
st.set_page_config(
    page_title="Video Flipper",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Video Flipper")
st.write("Upload a video, choose your flip options, and download the flipped result!")

# --- Helper Function: Flip Video ---
def flip_video_processor(input_filepath, output_filepath, flip_horizontal, flip_vertical):
    flip_filters = []
    if flip_horizontal:
        flip_filters.append('hflip')
    if flip_vertical:
        flip_filters.append('vflip')

    if not flip_filters:
        st.error("You must enable at least one flip direction.")
        return False # Indicate failure

    flip_filter_str = ",".join(flip_filters)

    # Visually lossless, browser-compatible encoding
    cmd = [
        FFMPEG_BINARY, '-y',
        '-i', input_filepath,
        '-vf', flip_filter_str,
        '-c:v', 'libx264',
        '-crf', '17', # Constant Rate Factor (0-51, lower is better quality)
        '-preset', 'fast', # Encoding speed vs. compression efficiency
        '-c:a', 'aac',
        '-b:a', '192k', # Audio bitrate
        output_filepath
    ]

    st.info(f"Processing video with FFmpeg...")
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Use subprocess.Popen for real-time output parsing to update progress
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Get video duration for progress calculation (using moviepy)
    try:
        clip = VideoFileClip(input_filepath)
        total_duration = clip.duration
        clip.close()
    except Exception as e:
        st.warning(f"Could not determine video duration for progress: {e}. Progress bar will not be precise.")
        total_duration = None

    stderr_output = []
    for line in iter(process.stderr.readline, ''):
        stderr_output.append(line)
        # Attempt to parse time from FFmpeg's stderr for progress
        if total_duration and "time=" in line:
            try:
                # Example: time=00:00:15.23
                time_str = line.split("time=")[1].split(" ")[0]
                h, m, s = map(float, time_str.split(':'))
                current_time = h * 3600 + m * 60 + s
                progress = min(1.0, current_time / total_duration)
                progress_bar.progress(progress)
                status_text.text(f"Processing... {int(progress*100)}%")
            except Exception:
                pass # Ignore parsing errors

    # Ensure progress bar reaches 100% at the end
    progress_bar.progress(1.0)
    status_text.text("Processing complete.")

    process.wait() # Wait for the process to finish

    if process.returncode != 0:
        st.error("⚠️ FFmpeg Error:")
        st.code("".join(stderr_output)) # Display full stderr for debugging
        return False
    else:
        st.success("✅ Video processed successfully.")
        return True

# --- File Uploader ---
uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file is not None:
    st.video(uploaded_file, format='video/mp4', start_time=0)

    # --- Flip Options ---
    col1, col2 = st.columns(2)
    with col1:
        flip_horizontal = st.checkbox("Flip Horizontally (Left-Right)", value=True)
    with col2:
        flip_vertical = st.checkbox("Flip Vertically (Up-Down)", value=False)

    if not flip_horizontal and not flip_vertical:
        st.warning("Please select at least one flip direction.")
    else:
        # --- Process Button ---
        if st.button("Flip Video"):
            with st.spinner("Uploading and processing your video... This might take a moment."):
                # Create temporary files for input and output
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as input_temp_file:
                    input_temp_file.write(uploaded_file.getvalue())
                    input_filepath = input_temp_file.name

                output_filepath = os.path.join(tempfile.gettempdir(), "flipped_output.mp4")

                try:
                    if flip_video_processor(input_filepath, output_filepath, flip_horizontal, flip_vertical):
                        st.subheader("Flipped Video")

                        # Display video inline
                        # This works well for small/medium videos. For very large videos, Streamlit's st.video()
                        # with a file path (once it supports local paths better) or direct download is preferred.
                        try:
                            # Read the processed video file
                            with open(output_filepath, 'rb') as f:
                                processed_video_bytes = f.read()

                            # Encode to base64 for embedding in HTML (for browser display)
                            video_base64 = b64encode(processed_video_bytes).decode()
                            video_html = f"""
                            <video width=640 controls autoplay loop>
                                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                                Your browser does not support the video tag.
                            </video>
                            """
                            st.components.v1.html(video_html, height=480) # Adjust height as needed
                        except Exception as e:
                            st.error(f"Error displaying video inline: {e}. You can still download it.")

                        # Provide download link
                        with open(output_filepath, "rb") as file:
                            st.download_button(
                                label="Download Flipped Video",
                                data=file,
                                file_name="flipped_video.mp4",
                                mime="video/mp4"
                            )
                finally:
                    # Clean up temporary files
                    if os.path.exists(input_filepath):
                        os.remove(input_filepath)
                    if os.path.exists(output_filepath):
                        os.remove(output_filepath)
