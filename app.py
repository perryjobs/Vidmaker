import streamlit as st
import warnings
from moviepy.editor import ImageClip, concatenate_videoclips
from moviepy.video.fx.all import resize, fadein, fadeout
import tempfile
import os

# Suppress specific warnings to keep logs clean
warnings.filterwarnings("ignore", category=SyntaxWarning)

st.title("Image to Video Converter with MoviePy")

# Upload multiple images
uploaded_files = st.file_uploader("Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    try:
        # Save uploaded images temporarily
        temp_files = []
        for f in uploaded_files:
            ext = os.path.splitext(f.name)[1]
            tf = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
            tf.write(f.read())
            tf.close()
            temp_files.append(tf.name)

        # Function to create a video clip from images
        def create_video(images, duration=2, zoom=1.2, trans_duration=1):
            clips = []
            for img_path in images:
                clip = ImageClip(img_path).set_duration(duration)
                # Apply zoom effect
                clip = resize(clip, lambda t: 1 + (zoom - 1) * (t / duration))
                # Apply fade in and out for smooth transitions
                clip = fadein(clip, trans_duration).fx(fadeout, trans_duration)
                clips.append(clip)
            return concatenate_videoclips(clips, method="compose")

        # Generate the video clip
        video_clip = create_video(temp_files)

        # Save to temporary file
        output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
        video_clip.write_videofile(output_path, fps=24, codec='libx264', audio=False, verbose=False, logger=None)

        # Clean up temporary image files
        for file in temp_files:
            os.remove(file)

        # Provide download button for the generated video
        with open(output_path, "rb") as f:
            st.download_button("Download Video", f, file_name="output.mp4", mime="video/mp4")

        # Display the generated video
        st.video(output_path)

    except Exception as e:
        st.error(f"An error occurred: {e}")

else:
    st.info("Please upload images to create a video.")
