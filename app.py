import streamlit as st
from moviepy.editor import ImageClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx.all import fadein, fadeout, resize
import tempfile
import os

def create_image_sequence_with_transitions(image_files, duration_per_image=2, zoom_scale=1.2, transition_duration=1):
    """
    Creates a video from images with zoom and fade transitions.
    """
    clips = []

    for img_path in image_files:
        # Create an ImageClip
        clip = ImageClip(img_path).set_duration(duration_per_image)

        # Apply zoom (scale up slightly)
        def zoom_effect(get_frame, t):
            frame = get_frame(t)
            # Calculate scale factor
            scale = 1 + (zoom_scale - 1) * (t / duration_per_image)
            return resize(resize(clip, lambda c: scale))(get_frame=lambda t: frame)

        # Alternatively, use resize fx
        clip = clip.fx(resize, lambda t: 1 + (zoom_scale - 1) * (t / duration_per_image))
        # Apply fade in and fade out
        clip = fadein(clip, transition_duration).fx(fadeout, transition_duration)
        clips.append(clip)

    # Concatenate all clips with crossfade transitions
    final = concatenate_videoclips(clips, method="compose")
    return final

# Streamlit UI
st.title("Image to Video with Transitions (Streamlit)")

uploaded_images = st.file_uploader("Upload Images (multiple)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_images:
    duration_per_image = st.slider("Duration per image (seconds)", 1, 5, 2)
    zoom_scale = st.slider("Zoom scale (e.g., 1.2)", 1.0, 2.0, 1.2, 0.1)
    transition_duration = st.slider("Transition duration (seconds)", 0.5, 2, 1, 0.1)

    if st.button("Create Video"):
        with st.spinner("Processing images..."):
            # Save uploaded images to temp files
            image_paths = []
            for uploaded_file in uploaded_images:
                temp_file = tempfile.NamedTemporaryFile(suffix=os.path.splitext(uploaded_file.name)[1], delete=False)
                temp_file.write(uploaded_file.read())
                temp_file.close()
                image_paths.append(temp_file.name)

            # Generate video
            final_clip = create_image_sequence_with_transitions(
                image_paths,
                duration_per_image=duration_per_image,
                zoom_scale=zoom_scale,
                transition_duration=transition_duration
            )

            # Save to a temporary file
            output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
            final_clip.write_videofile(output_path, fps=24, codec='libx264', audio=False, verbose=False, logger=None)

            # Cleanup temp images
            for img_path in image_paths:
                os.remove(img_path)

            # Provide download
            with open(output_path, "rb") as f:
                st.download_button("Download Video", data=f, file_name="video_with_transitions.mp4", mime="video/mp4")

            # Show video preview
            st.video(output_path)
