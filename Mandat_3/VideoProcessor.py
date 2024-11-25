import cv2
import numpy as np


class VideoProcessor:
    def __init__(self, vid_ext="avi"):
        self.vid_ext = vid_ext

    def get_video_matrix(self, filename: str = "test"):
        # Open the video file
        video = cv2.VideoCapture(f"{filename}.{self.vid_ext}")

        # print the shape
        print(video.get(cv2.CAP_PROP_FRAME_WIDTH))

        if not video.isOpened():
            raise FileNotFoundError(f"Could not open video file: {filename}.{self.vid_ext}")

        frames = []
        while True:
            ret, frame = video.read()
            if not ret:
                break
            # Convert frame to grayscale if needed
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frames.append(frame)

        video.release()

        # Convert to a 3D numpy array
        video_matrix = np.stack(frames, axis=0)  # Shape: (num_frames, height, width, channels)

        # Get min and max values
        min_val = np.min(video_matrix)
        max_val = np.max(video_matrix)

        return video_matrix, min_val, max_val

    def write_normalized_video(self, video_matrix, min_val, max_val, output_filename="output"):
        # Normalize the video matrix
        normalized_video = ((video_matrix - min_val) / (max_val - min_val) * 255).astype(np.uint8)

        # Extract video dimensions
        num_frames, height, width, channels = normalized_video.shape
        is_color = channels == 3  # Check if video is color or grayscale

        # Define the output video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use MP4 codec
        output_video = cv2.VideoWriter(f"{output_filename}.{self.vid_ext}", fourcc, 30, (width, height), is_color)

        for frame in normalized_video:
            output_video.write(frame)

        output_video.release()
        print(f"Video saved as {output_filename}.{self.vid_ext}")


# Example usage
processor = VideoProcessor()
video_matrix, min_val, max_val = processor.get_video_matrix("test")
processor.write_normalized_video(video_matrix, min_val, max_val, "normalized_output")
