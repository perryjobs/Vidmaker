import streamlit as st
from moviepy.editor import ImageClip, concatenate_videoclips
import tempfile
import os

st.title("Image to Video with Transitions and Zoom Effects")

# Upload images: enforce exactly 4 images
uploaded_files = st.file_uploader(
    "Upload 4 Images (jpg, jpeg, png)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# Check if 4 images are uploaded
if uploaded_files and len(uploaded_files) == 4:
    # Parameters with explicit steps for float sliders
    clip_duration = st.slider(
        "Duration of each clip (seconds)",
        min_value=1,
        max_value=10,
        value=3,
        step=1
    )
    transition_duration = st.slider(
        "Transition duration (seconds)",
        min_value=0.5,
        max_value=3.0,
        value=1.0,
        step=0.1
    )
    zoom_factor = st.slider(
        "Maximum Zoom Level (e.g., 1.2 means 20% zoom)",
        min_value=1.0,
        max_value=2.0,
        value=1.2,
        step=0.1
    )

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

        # Define zoom function
        def zoom(t):
            # t in seconds, normalize to 0-1
            progress = t / clip_duration
            return 1 + (zoom_factor - 1) * progress

        # Apply zoom-in effect
        zoomed_clip = clip.resize(lambda t: zoom(t))
        clips.append(zoomed_clip)

    # Concatenate clips with crossfade transitions
    final_clip = concatenate_videoclips(
        clips,
        method="compose",
        padding=-transition_duration
    )

    # Save the output video
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    final_clip.write_videofile(output_path, fps=24)

    st.success("Video created successfully!")

    # Display the generated video
    st.video(output_path)

    # Cleanup temporary image files
    for file_path in temp_files:
        os.remove(file_path)

else:
    st.info("Please upload exactly 4 images to proceed.")
