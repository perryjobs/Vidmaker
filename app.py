import streamlit as st
import warnings
from moviepy.editor import ImageClip, concatenate_videoclips
from moviepy.video.fx.all import resize, fadein, fadeout
import tempfile
import os
import gc

# Suppress specific warnings to keep logs clean
warnings.filterwarnings("ignore", category=SyntaxWarning)

st.title("Image to Video Converter with MoviePy")

# Configuration options
st.sidebar.header("Video Settings")
duration = st.sidebar.slider("Duration per image (seconds)", 1, 5, 2)
zoom = st.sidebar.slider("Zoom level", 1.0, 1.5, 1.2)
trans_duration = st.sidebar.slider("Transition duration (seconds)", 0.5, 2.0, 1.0)
fps = st.sidebar.selectbox("Frame rate (FPS)", [15, 24, 30], index=1)

# Upload multiple images
uploaded_files = st.file_uploader(
    "Upload images", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True,
    help="Upload 2-10 images for best performance on Streamlit Cloud"
)

if uploaded_files:
    # Limit number of images to prevent crashes
    if len(uploaded_files) > 10:
        st.warning("⚠️ Too many images! Please upload 10 or fewer images for optimal performance.")
        uploaded_files = uploaded_files[:10]
    
    st.info(f"Processing {len(uploaded_files)} images...")
    
    try:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process images one at a time and create clips
        clips = []
        temp_files = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing image {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
            
            # Save current image to temporary file
            ext = os.path.splitext(uploaded_file.name)[1]
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
            temp_file.write(uploaded_file.read())
            temp_file.close()
            temp_files.append(temp_file.name)
            
            # Create clip from current image
            try:
                clip = ImageClip(temp_file.name).set_duration(duration)
                
                # Apply zoom effect (more conservative for memory)
                if zoom > 1.0:
                    clip = resize(clip, lambda t: 1 + (zoom - 1) * (t / duration))
                
                # Apply fade effects
                if trans_duration > 0:
                    clip = fadein(clip, min(trans_duration, duration/3))
                    clip = fadeout(clip, min(trans_duration, duration/3))
                
                clips.append(clip)
                
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                continue
            
            # Update progress
            progress_bar.progress((i + 1) / len(uploaded_files))
            
            # Force garbage collection after each image
            gc.collect()
        
        if not clips:
            st.error("No valid clips were created. Please check your images.")
        else:
            status_text.text("Combining clips into video...")
            
            # Combine clips with conservative settings
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Save to temporary file with conservative settings
            output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
            
            status_text.text("Rendering video... This may take a moment.")
            
            # Use more conservative encoding settings for Streamlit Cloud
            final_video.write_videofile(
                output_path, 
                fps=fps, 
                codec='libx264',
                audio=False,
                verbose=False,
                logger=None,
                remove_temp=True,
                preset='ultrafast',  # Faster encoding
                ffmpeg_params=['-crf', '28']  # Lower quality but smaller file
            )
            
            # Clean up clips from memory
            final_video.close()
            for clip in clips:
                clip.close()
            
            # Clean up temporary image files
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            # Force garbage collection
            gc.collect()
            
            status_text.text("Video created successfully!")
            progress_bar.progress(1.0)
            
            # Get file size for display
            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            st.success(f"✅ Video created! File size: {file_size:.1f} MB")
            
            # Provide download button
            with open(output_path, "rb") as f:
                st.download_button(
                    "📥 Download Video", 
                    f.read(), 
                    file_name="slideshow_video.mp4", 
                    mime="video/mp4"
                )
            
            # Display the video (but warn about potential loading time)
            if file_size < 50:  # Only auto-display if less than 50MB
                st.video(output_path)
            else:
                st.info("Video is large - use the download button above to save it.")
            
            # Clean up output file
            try:
                os.remove(output_path)
            except:
                pass

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Try uploading fewer or smaller images, or reducing the duration/effects.")

else:
    st.info("👆 Please upload 2-10 images to create a video slideshow.")
    
    # Add some helpful information
    with st.expander("💡 Tips for best results"):
        st.write("""
        - **Upload 2-10 images** for optimal performance
        - **Use smaller image files** (under 5MB each) to prevent timeouts
        - **Lower settings** (shorter duration, less zoom) use less memory
        - **Be patient** - video processing takes time on shared servers
        - **Download immediately** - files are temporary and will be deleted
        """)
