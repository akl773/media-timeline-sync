import argparse
import logging
import sys
from pathlib import Path

from src.core.media_processor import MediaProcessor
from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader

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
        '--config',
        default='config/config.yaml',
        help='Path to configuration YAML file (default: config/config.yaml)'
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

    parser.add_argument(
        '--list-formats',
        action='store_true',
        help='List supported video and audio formats and exit'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate inputs and config, but do not process media'
    )

    parser.add_argument(
        '--preview',
        action='store_true',
        help='Generate a short preview (first 30 seconds) of the synchronized output.'
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


def print_supported_formats():
    video_formats = [
        ('.mp4', 'MPEG-4 Video'),
        ('.mkv', 'Matroska Video'),
        ('.avi', 'Audio Video Interleave'),
        ('.mov', 'QuickTime Movie'),
    ]
    audio_formats = [
        ('.mp3', 'MPEG Audio Layer III'),
        ('.wav', 'Waveform Audio'),
        ('.aac', 'Advanced Audio Coding'),
        ('.m4a', 'MPEG-4 Audio'),
    ]
    print("\nSupported Video Formats:")
    print("  Extension   Description")
    print("  ---------   ----------------------")
    for ext, desc in video_formats:
        print(f"  {ext:<10} {desc}")
    print("\nSupported Audio Formats:")
    print("  Extension   Description")
    print("  ---------   ----------------------")
    for ext, desc in audio_formats:
        print(f"  {ext:<10} {desc}")
    print()


def main():
    """Main CLI entry point"""
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Load config
    config_loader = ConfigLoader(args.config)

    if args.list_formats:
        print_supported_formats()
        return 0

    try:
        # Validate paths
        validate_paths(args.input, args.audio, args.output)
        # Validate config (example: check ffmpeg.audio_codec)
        audio_codec = config_loader.get('ffmpeg.audio_codec', 'aac')
        video_codec = config_loader.get('ffmpeg.video_codec', 'copy')
        logger.info(f"Config: audio_codec={audio_codec}, video_codec={video_codec}")

        if args.dry_run:
            print("Dry run successful. Inputs and config are valid.")
            return 0

        # Initialize processor
        processor = MediaProcessor()

        # Handle preview mode
        if args.preview:
            preview_output = str(Path(args.output).with_name(Path(args.output).stem + '_preview' + Path(args.output).suffix))
            # Use ffmpeg to trim both video and audio to first 30 seconds, then run merge
            import subprocess
            from tempfile import NamedTemporaryFile
            # Trim video
            with NamedTemporaryFile(suffix=Path(args.input).suffix, delete=False) as temp_vid:
                subprocess.run([
                    'ffmpeg', '-y', '-i', args.input, '-t', '30', '-c', 'copy', temp_vid.name
                ], check=True)
                # Trim audio
                with NamedTemporaryFile(suffix=Path(args.audio).suffix, delete=False) as temp_aud:
                    subprocess.run([
                        'ffmpeg', '-y', '-i', args.audio, '-t', '30', '-c', 'copy', temp_aud.name
                    ], check=True)
                    # Merge preview
                    output_path = processor.merge_audio_video(
                        video_path=temp_vid.name,
                        audio_path=temp_aud.name,
                        output_path=preview_output,
                        smart_sync=args.smart_sync,
                        manual_offset=args.offset,
                        audio_track_number=args.track_number,
                        overwrite=True
                    )
            print(f"Preview created: {output_path}")
            return 0

        logger.info("Starting media synchronization...")
        logger.info(f"Input video: {args.input}")
        logger.info(f"Input audio: {args.audio}")
        logger.info(f"Output path: {args.output}")
        logger.info(f"Smart sync: {'enabled' if args.smart_sync else 'disabled'}")

        # Process media
        output_path = processor.merge_audio_video(
            video_path=args.input,
            audio_path=args.audio,
            output_path=args.output,
            smart_sync=args.smart_sync,
            manual_offset=args.offset,
            audio_track_number=args.track_number,
            overwrite=args.overwrite
        )

        logger.info(f"Successfully created: {output_path}")
        return 0

    except FileNotFoundError as e:
        logger.error(f"File error: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
