import logging
from pathlib import Path
from typing import List, Dict, Any

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class VideoHandler:
    """Handles video processing operations including scene detection."""

    def __init__(self):
        self.supported_formats = {'.mp4', '.mkv', '.avi', '.mov'}

    def detect_scene_changes(self, video_path: str, threshold: float = 30.0,
                             min_scene_length: float = 2.0) -> List[float]:
        """
        Detect major scene changes in video that might indicate commercial breaks.

        Args:
            video_path: Path to video file
            threshold: Threshold for scene change detection
            min_scene_length: Minimum length between scenes in seconds

        Returns:
            List of timestamps where scene changes occur
        """
        scene_changes = []
        cap = cv2.VideoCapture(str(Path(video_path).absolute()))

        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        min_frames = int(min_scene_length * fps)

        ret, prev_frame = cap.read()
        if not ret:
            cap.release()
            return scene_changes

        prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        frame_count = 0
        last_scene_frame = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert to grayscale for comparison
            curr_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Calculate frame difference
            diff = cv2.absdiff(curr_frame, prev_frame)
            mean_diff = np.mean(diff)

            # Check for scene change
            if mean_diff > threshold and (frame_count - last_scene_frame) >= min_frames:
                timestamp = frame_count / fps
                scene_changes.append(timestamp)
                last_scene_frame = frame_count
                logger.debug(f"Scene change detected at {timestamp:.2f}s")

            prev_frame = curr_frame
            frame_count += 1

        cap.release()
        logger.info(f"Detected {len(scene_changes)} scene changes")
        return scene_changes

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video file information."""
        cap = cv2.VideoCapture(str(Path(video_path).absolute()))

        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        info = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        }

        cap.release()
        return info

    def calculate_scene_metrics(self, video_path: str, window_size: int = 30) -> Dict[str, Any]:
        """Calculate metrics for scene detection tuning."""
        cap = cv2.VideoCapture(str(Path(video_path).absolute()))
        differences = []

        ret, prev_frame = cap.read()
        prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            curr_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(curr_frame, prev_frame)
            differences.append(np.mean(diff))
            prev_frame = curr_frame

        cap.release()

        if not differences:
            return {}

        differences = np.array(differences)
        metrics = {
            'mean_difference': float(np.mean(differences)),
            'std_difference': float(np.std(differences)),
            'median_difference': float(np.median(differences)),
            'suggested_threshold': float(np.mean(differences) + 2 * np.std(differences)),
            'max_difference': float(np.max(differences)),
            'min_difference': float(np.min(differences))
        }

        return metrics
