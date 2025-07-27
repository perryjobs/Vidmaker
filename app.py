import streamlit as st
from moviepy.editor import ImageClip, concatenate_videoclips
from moviepy.video.fx.all import resize, fadein, fadeout
import tempfile
import os

def create_video(images, duration=2, zoom=1.2, trans_duration=1):
    clips = []
    for img_path in images:
        clip = ImageClip(img_path).set_duration(duration)
        clip = resize(clip, lambda t: 1 + (zoom - 1) * (t / duration))
        clip = fadein(clip, trans_duration).fx(fadeout, trans_duration)
        clips.append(clip)
    return concatenate_videoclips(clips, method="compose")

st.title("Test Image to Video")

uploaded_files = st.file_uploader("Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    try:
        temp_files = []
        for f in uploaded_files:
            tf = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(f.name)[1])
            tf.write(f.read())
            tf.close()
            temp_files.append(tf.name)

        video_clip = create_video(temp_files)

        output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
        video_clip.write_videofile(output_path, fps=24, codec='libx264', audio=False, verbose=False, logger=None)

        # Clean up temp images
        for file in temp_files:
            os.remove(file)

        with open(output_path, "rb") as f:
            st.download_button("Download Video", f, file_name="output.mp4", mime="video/mp4")

        st.video(output_path)
    except Exception as e:
        st.error(f"Error: {e}")
