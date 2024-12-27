import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from src.core.audio_handler import AudioHandler
from src.core.video_handler import VideoHandler
from src.exceptions.custom_exceptions import MediaProcessingError, CommandExecutionError
from src.utils.logger import setup_logger
from src.utils.validators import validate_file_exists, validate_media_format

logger = setup_logger(__name__)


class MediaProcessor:
    """
    Core class for processing and synchronizing media files.
    Handles video and audio merging operations with intelligent synchronization.
    Accounts for commercial breaks and editing differences between sources.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the MediaProcessor with optional configuration."""
        self.config = config or {}
        self.audio_handler = AudioHandler()
        self.video_handler = VideoHandler()
        self.supported_video_formats = self.video_handler.supported_formats
        self.supported_audio_formats = self.audio_handler.supported_formats

    def merge_audio_video(
            self,
            video_path: str,
            audio_path: str,
            output_path: str,
            smart_sync: bool = True,
            manual_offset: float = 0.0,
            audio_track_number: int = 1,
            overwrite: bool = False
    ) -> str:
        """
        Merge audio with video file while maintaining synchronization.

        Args:
            video_path (str): Path to input video file
            audio_path (str): Path to input audio file
            output_path (str): Path for the output file
            smart_sync (bool): Whether to use smart sync detection
            manual_offset (float): Manual time offset for audio in seconds
            audio_track_number (int): Track number for the new audio
            overwrite (bool): Whether to overwrite existing output file

        Returns:
            str: Path to the output file
        """
        try:
            # Convert to absolute paths
            video_path = str(Path(video_path).absolute())
            audio_path = str(Path(audio_path).absolute())
            output_path = str(Path(output_path).absolute())

            # Validate input files
            for path in [video_path, audio_path]:
                validate_file_exists(path)

            video_path = Path(video_path)
            audio_path = Path(audio_path)
            output_path = Path(output_path)

            validate_media_format(video_path, self.supported_video_formats)
            validate_media_format(audio_path, self.supported_audio_formats)

            # Handle smart synchronization
            if smart_sync:
                logger.info("Starting smart synchronization analysis...")

                # Extract original audio from video
                temp_audio = str(Path(output_path).parent / "temp_original_audio.wav")
                self.audio_handler.extract_audio_from_video(str(video_path), temp_audio)

                # Detect scene changes that might indicate commercial breaks
                scene_changes = self.video_handler.detect_scene_changes(str(video_path))
                logger.info(f"Detected {len(scene_changes)} potential scene changes")

                # Find sync points between original and dub audio
                sync_points = self.audio_handler.find_sync_points(temp_audio, str(audio_path), scene_changes)
                logger.info(f"Found {len(sync_points)} sync points")

                # Create filter complex based on sync points
                filter_complex = self.audio_handler.create_sync_filter(sync_points, manual_offset)

                Path(temp_audio).unlink()  # Clean up temp file
            else:
                # Use simple manual offset
                filter_complex = self.audio_handler.create_sync_filter([], manual_offset)

            # Prepare FFmpeg command
            command = [
                'ffmpeg',
                '-y' if overwrite else '-n',
                '-i', str(video_path),
                '-i', str(audio_path),
                '-filter_complex', filter_complex,
                '-map', '0:v',  # map video from first input
                '-map', '[merged_audio]',  # map processed audio
                '-map', '0:a',  # map original audio
                '-c:v', 'copy',  # copy video codec
                '-c:a', 'aac',  # encode audio to AAC
                '-b:a', '192k',  # audio bitrate
                '-metadata:s:a:0', f'title=Audio Track {audio_track_number}',
                str(output_path)
            ]

            logger.info(f"Starting media merge process with command: {' '.join(command)}")

            # Execute FFmpeg command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )

            if result.returncode != 0:
                raise CommandExecutionError(
                    f"FFmpeg command failed with error: {result.stderr}"
                )

            logger.info(f"Successfully merged audio and video to: {output_path}")
            return str(output_path)

        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg processing failed: {e.stderr}"
            logger.error(error_msg)
            raise MediaProcessingError(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error during media processing: {str(e)}"
            logger.error(error_msg)
            raise MediaProcessingError(error_msg)
