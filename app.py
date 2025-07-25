import streamlit as st
from moviepy.editor import ImageClip, concatenate_videoclips
import tempfile
import os

st.title("Image to Video with Transitions and Zoom Effects")

# Upload images
uploaded_files = st.file_uploader("Upload 4 Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Ensure 4 images are uploaded
if uploaded_files and len(uploaded_files) == 4:
    # Parameters
    clip_duration = st.slider("Duration of each clip (seconds)", 1, 10, 3)
    transition_duration = st.slider("Transition duration (seconds)", 0.5, 3, 1)
    zoom_factor = st.slider("Maximum Zoom Level (e.g., 1.2 means 20% zoom)", 1.0, 2.0, 1.2)

    # Save uploaded images temporarily
    temp_files = []
    for uploaded_file in uploaded_files:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
        temp_file.write(uploaded_file.read())
        temp_files.append(temp_file.name)

    clips = []

    # Create clips with zoom effect
    for file_path in temp_files:
        clip = ImageClip(file_path).set_duration(clip_duration)

        # Apply zoom-in effect
        def zoom(t):
            return 1 + (zoom_factor - 1) * (t / clip_duration)

        zoomed_clip = clip.resize(lambda t: zoom(t))
        clips.append(zoomed_clip)

    # Concatenate clips with crossfade transitions
    final_clip = concatenate_videoclips(
        clips,
        method="compose",
        padding=-transition_duration
    )

    # Save the video to a temporary file
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    final_clip.write_videofile(output_path, fps=24)

    st.success("Video created successfully!")

    # Display the video
    st.video(output_path)

    # Clean up temporary files after
    for file_path in temp_files:
        os.remove(file_path)
else:
    st.info("Please upload exactly 4 images to proceed.")
