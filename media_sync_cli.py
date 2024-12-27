import argparse
import logging
import sys
from pathlib import Path

from src.core.media_processor import MediaProcessor
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Media Timeline Synchronization Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    Basic usage:
    python media_sync_cli.py --input video.mp4 --audio hindi.mp3 --output final.mp4

    With smart sync:
    python media_sync_cli.py --input video.mp4 --audio hindi.mp3 --output final.mp4 --smart-sync

    Manual offset:
    python media_sync_cli.py --input video.mp4 --audio hindi.mp3 --output final.mp4 --offset 2.5
        """
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input video file path'
    )

    parser.add_argument(
        '--audio', '-a',
        required=True,
        help='Input audio file path (dub track)'
    )

    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output file path'
    )

    parser.add_argument(
        '--smart-sync',
        action='store_true',
        help='Enable smart synchronization (default: False)'
    )

    parser.add_argument(
        '--offset',
        type=float,
        default=0.0,
        help='Manual audio offset in seconds (used if smart-sync fails or is disabled)'
    )

    parser.add_argument(
        '--track-number',
        type=int,
        default=1,
        help='Audio track number in output (default: 1)'
    )

    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite output file if it exists'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()


def validate_paths(input_path: str, audio_path: str, output_path: str) -> None:
    """Validate input and output paths"""
    # Check input video exists
    if not Path(input_path).is_file():
        raise FileNotFoundError(f"Input video not found: {input_path}")

    # Check input audio exists
    if not Path(audio_path).is_file():
        raise FileNotFoundError(f"Input audio not found: {audio_path}")

    # Check output directory exists or can be created
    output_dir = Path(output_path).parent
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True)
        except Exception as e:
            raise RuntimeError(f"Cannot create output directory: {str(e)}")


if __name__ == "__main__":
    pass
