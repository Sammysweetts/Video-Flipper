import streamlit as st
import subprocess
import tempfile
import os

# --- Core FFmpeg Function (adapted from your script) ---
def flip_video(input_path, output_path, flip_horizontal, flip_vertical):
    """
    Flips a video using FFmpeg.
    Returns the subprocess result object.
    """
    flip_filters = []
    if flip_horizontal:
        flip_filters.append('hflip')
    if flip_vertical:
        flip_filters.append('vflip')

    if not flip_filters:
        # This case is handled in the UI, but good to have for safety
        raise ValueError("At least one flip direction must be selected.")
    
    flip_filter_str = ",".join(flip_filters)

    # Command for FFmpeg
    # -y: overwrite output file if it exists
    # -i: input file
    # -vf: video filter graph
    # -c:v libx264: H.264 video codec (great compatibility)
    # -crf 17: Constant Rate Factor for quality (17 is visually lossless)
    # -preset fast: encoding speed vs. compression ratio
    # -c:a aac: AAC audio codec (great compatibility)
    # -b:a 192k: Audio bitrate
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

    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

# --- Streamlit User Interface ---

st.set_page_config(layout="centered", page_title="Video Flipper", page_icon="🔄")

st.title("🔄 Video Flipper")
st.markdown("Upload a video and choose how you want to flip it. Powered by `FFmpeg` and Streamlit.")

# Sidebar for options
with st.sidebar:
    st.header("⚙️ Flip Options")
    uploaded_file = st.file_uploader(
        "Choose a video file", 
        type=["mp4", "mov", "avi", "mkv"]
    )
    
    flip_horizontal = st.checkbox("Flip Horizontally (left-to-right)", value=True)
    flip_vertical = st.checkbox("Flip Vertically (upside-down)")

    process_button = st.button("Process Video", type="primary")

# Main content area
if process_button and uploaded_file is not None:
    if not flip_horizontal and not flip_vertical:
        st.warning("Please select at least one flip direction.")
    else:
        with st.spinner('Processing your video... This might take a moment.'):
            # Use a temporary directory to handle file I/O
            with tempfile.TemporaryDirectory() as temp_dir:
                input_path = os.path.join(temp_dir, uploaded_file.name)
                output_path = os.path.join(temp_dir, f"flipped_{uploaded_file.name}")

                # Save the uploaded file to the temporary directory
                with open(input_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                # Run the FFmpeg process
                result = flip_video(input_path, output_path, flip_horizontal, flip_vertical)

                # Check if FFmpeg ran successfully
                if result.returncode == 0:
                    st.success("✅ Video processed successfully!")

                    # Display the video
                    st.video(output_path)
                    
                    # Provide a download button
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 Download Flipped Video",
                            data=f,
                            file_name=f"flipped_{uploaded_file.name}",
                            mime="video/mp4"
                        )
                else:
                    st.error("⚠️ An error occurred during video processing.")
                    with st.expander("Click to see FFmpeg error log"):
                        st.code(result.stderr)
                        
elif process_button and uploaded_file is None:
    st.warning("Please upload a video file first.")
