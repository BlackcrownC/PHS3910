import numpy as np
import cv2

def video_to_3d_array(video_path):
    """
    Reads an AVI video file and converts it to a 3D NumPy array.
    
    Args:
        video_path (str): Path to the AVI video file.
    
    Returns:
        np.ndarray: A 4D array with shape (frames, height, width, channels).
    """
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise FileNotFoundError(f"Unable to open video: {video_path}")
    
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Stop when there are no more frames
        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame)
    
    cap.release()
    # Convert the list of frames to a NumPy array
    video_array = np.array(frames, dtype=np.uint8)
    return video_array[:,:,:,0]

# Example usage
video_path = "video_to_start_coding_early.avi"  # Replace with your video file path
video_array = video_to_3d_array(video_path)
print("Video shape:", video_array.shape)  # Output: (frames, height, width, channels)