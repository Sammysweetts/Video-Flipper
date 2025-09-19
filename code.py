import os
import tempfile
import streamlit as st
import subprocess
from pathlib import Path

# Configuration
MAX_FILE_SIZE = 1024  # MB
FFMPEG_TIMEOUT = 1800  # 30 minutes
TEMP_DIR = "/tmp"  # Using system temp directory which has more space

# Set page config
st.set_page_config(
    page_title="Video Flipper Pro",
    page_icon="🔄",
    layout="wide"
)

# App title and description
st.title("🔄 Video Flipper Pro")
st.markdown(f"""
Upload a video (up to {MAX_FILE_SIZE}MB) to flip it horizontally or vertically. 
The processed video will maintain high quality.
""")

# Sidebar controls
with st.sidebar:
    st.header("Flip Options")
    flip_horizontal = st.checkbox("Flip Horizontal", value=True)
    flip_vertical = st.checkbox("Flip Vertical", value=False)
    st.markdown("---")
    st.warning(f"Note: Processing large files (>{MAX_FILE_SIZE//2}MB) may take several minutes")

# Custom file uploader with chunked processing
def save_uploadedfile(uploadedfile, destination):
    try:
        with open(destination, "wb") as f:
            for chunk in uploadedfile.iter_bytes(chunk_size=1024*1024):  # 1MB chunks
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        st.error(f"File upload failed: {str(e)}")
        return False

# File uploader with size limit
uploaded_file = st.file_uploader(
    f"Upload a video file (max {MAX_FILE_SIZE}MB)", 
    type=["mp4", "mov", "avi", "mkv"],
    accept_multiple_files=False
)

if uploaded_file is not None:
    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE:
        st.error(f"File too large! Maximum allowed is {MAX_FILE_SIZE}MB")
        st.stop()
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(dir=TEMP_DIR)
    input_path = os.path.join(temp_dir, uploaded_file.name)
    output_path = os.path.join(temp_dir, f"flipped_{uploaded_file.name}")
    
    # Save uploaded file in chunks
    upload_progress = st.progress(0, text="Uploading file...")
    if not save_uploadedfile(uploaded_file, input_path):
        st.stop()
    upload_progress.progress(100, text="Upload complete!")
    time.sleep(1)
    upload_progress.empty()
    
    # Process video
    if st.button("Flip Video"):
        processing = st.progress(0, text="Initializing processing...")
        
        try:
            # Build flip filters
            flip_filters = []
            if flip_horizontal:
                flip_filters.append('hflip')
            if flip_vertical:
                flip_filters.append('vflip')

            if not flip_filters:
                st.error("Please select at least one flip direction.")
                st.stop()
            
            flip_filter_str = ",".join(flip_filters)

            # FFmpeg command with optimal quality settings
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-vf', flip_filter_str,
                '-c:v', 'libx264',
                '-crf', '18',          # High quality
                '-preset', 'medium',   # Balanced speed/quality
                '-tune', 'film',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-movflags', '+faststart',
                output_path
            ]

            # Run FFmpeg with progress tracking
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # Monitor progress
            duration = None
            while True:
                output = process.stderr.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Parse duration if available
                    if "Duration:" in output:
                        try:
                            time_str = output.split("Duration:")[1].split(",")[0].strip()
                            h, m, s = time_str.split(':')
                            duration = int(h) * 3600 + int(m) * 60 + float(s)
                        except:
                            pass
                    # Update progress if we have duration
                    if duration and "time=" in output:
                        time_str = output.split("time=")[1].split(" ")[0]
                        h, m, s = time_str.split(':')
                        current_time = int(h) * 3600 + int(m) * 60 + float(s)
                        progress = min(100, int((current_time / duration) * 100))
                        processing.progress(progress, text=f"Processing... {progress}%")
            
            if process.returncode != 0:
                st.error("FFmpeg processing failed")
                st.stop()

            # Verify output
            if not Path(output_path).exists():
                st.error("Output file not created")
                st.stop()
            
            # Display results
            processing.progress(100, text="Processing complete!")
            time.sleep(1)
            processing.empty()
            
            st.success("Video processed successfully!")
            
            # Display video preview (first 30 seconds)
            preview_path = os.path.join(temp_dir, "preview.mp4")
            preview_cmd = [
                'ffmpeg', '-y',
                '-i', output_path,
                '-ss', '00:00:00',
                '-t', '30',  # 30 second preview
                '-c', 'copy',  # Stream copy (no re-encoding)
                preview_path
            ]
            subprocess.run(preview_cmd, check=True)
            
            with open(preview_path, "rb") as f:
                st.video(f.read())
            
            # Download section
            st.markdown("---")
            st.markdown("### Download Options")
            
            # Full download
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            st.download_button(
                label=f"Download Full Video ({file_size:.1f}MB)",
                data=open(output_path, "rb"),
                file_name=f"flipped_{uploaded_file.name}",
                mime="video/mp4"
            )
            
            # Clean preview
            if os.path.exists(preview_path):
                os.remove(preview_path)
                
        except Exception as e:
            st.error(f"Processing error: {str(e)}")
        finally:
            # Clean up
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
            except:
                pass
