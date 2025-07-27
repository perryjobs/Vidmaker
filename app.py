import streamlit as st
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
import tempfile

def your_processing_function(clip):
    """
    Placeholder for your video processing logic.
    For example, applying filters, overlays, etc.
    Currently, it returns the original clip.
    """
    # Example: apply a simple effect (uncomment to activate)
    # import moviepy.video.fx.all as vfx
    # return clip.fx(vfx.colorx, 1.2)
    return clip

def process_video_in_chunks(uploaded_file, chunk_duration=10):
    """
    Processes uploaded video in chunks within Streamlit.
    Returns the path to the final processed video.
    """
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_input:
        temp_input.write(uploaded_file.read())
        input_path = temp_input.name

    try:
        original_clip = VideoFileClip(input_path)
        total_duration = original_clip.duration
        st.write(f"Loaded video: {uploaded_file.name}")
        st.write(f"Total duration: {total_duration:.2f} seconds")
    except Exception as e:
        st.error(f"Error loading video: {e}")
        return None

    clips = []
    temp_files = []
    start = 0

    # Process in chunks
    while start < total_duration:
        end = min(start + chunk_duration, total_duration)
        try:
            st.write(f"Processing segment: {start:.2f} to {end:.2f} seconds")
            # Extract subclip
            subclip = original_clip.subclip(start, end)
            # Apply processing
            processed_subclip = your_processing_function(subclip)
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_clip_file:
                processed_subclip.write_videofile(
                    temp_clip_file.name,
                    codec='libx264',
                    audio_codec='aac',
                    verbose=False,
                    logger=None
                )
                temp_files.append(temp_clip_file.name)
                clips.append(VideoFileClip(temp_clip_file.name))
        except Exception as e:
            st.error(f"Error processing segment {start}-{end}: {e}")
        start += chunk_duration

    # Concatenate all clips
    if clips:
        try:
            st.write("Concatenating segments...")
            final_clip = concatenate_videoclips(clips, method="compose")
            output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', verbose=False, logger=None)
            st.success("Processing complete!")
            return output_path
        except Exception as e:
            st.error(f"Error concatenating clips: {e}")
            return None
        finally:
            # Cleanup individual segment files
            for f in temp_files:
                try:
                    os.remove(f)
                except:
                    pass
    return None

# Streamlit UI
st.title("Video Processor in Chunks (Streamlit Cloud)")

uploaded_file = st.file_uploader("Upload your video", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    chunk_size = st.slider("Chunk duration (seconds)", min_value=5, max_value=60, value=10, step=5)
    process_button = st.button("Process Video")
    
    if process_button:
        with st.spinner("Processing..."):
            output_video_path = process_video_in_chunks(uploaded_file, chunk_duration=chunk_size)
            if output_video_path:
                with open(output_video_path, "rb") as f:
                    st.download_button(
                        label="Download Processed Video",
                        data=f,
                        file_name="processed_video.mp4",
                        mime="video/mp4"
                    )
                # Optionally, display the video
                st.video(output_video_path)
