# Media Timeline Sync

A specialized command-line tool for synchronizing audio and video files, particularly designed for dubbing workflows. This tool can automatically detect scene changes, handle commercial breaks, and ensure perfect synchronization between original video and dubbed audio tracks.

## Key Features

- **Smart Synchronization**: Automatically detects scene changes and commercial breaks
- **Audio Fingerprinting**: Uses advanced audio analysis for precise sync point detection
- **Flexible Timing**: Supports both automatic and manual offset adjustments
- **Quality Preservation**: Maintains original video quality through stream copying
- **Multiple Format Support**: Handles various video and audio formats

## Prerequisites

- Python 3.13 or higher
- FFmpeg installed and in system PATH
- Required Python packages (installed via pip)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/akl773/media-timeline-sync
   cd media-timeline-sync
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify FFmpeg installation:
   ```bash
   ffmpeg -version
   ```

## Usage Instructions

Basic usage with automatic synchronization:
```bash
python media_sync_cli.py --input video.mp4 --audio dub.mp3 --output final.mp4 --smart-sync
```

Manual offset adjustment:
```bash
python media_sync_cli.py --input video.mp4 --audio dub.mp3 --output final.mp4 --offset 2.5
```

Preview mode (generate a 30-second preview):
```bash
python media_sync_cli.py --input video.mp4 --audio dub.mp3 --output final.mp4 --smart-sync --preview
```
This will create a file named `final_preview.mp4` containing the first 30 seconds of the synchronized output, so you can quickly check sync quality before processing the full file.

### Command-Line Options

- `--input`, `-i`: Input video file path (required)
- `--audio`, `-a`: Input audio file (dub track) path (required)
- `--output`, `-o`: Output file path (required)
- `--smart-sync`: Enable smart synchronization
- `--offset`: Manual audio offset in seconds (default: 0.0)
- `--track-number`: Audio track number in output (default: 1)
- `--overwrite`: Overwrite output file if it exists
- `--verbose`, `-v`: Enable detailed logging

## Supported Formats

Video:
- MP4 (.mp4)
- MKV (.mkv)
- AVI (.avi)
- MOV (.mov)

Audio:
- MP3 (.mp3)
- WAV (.wav)
- AAC (.aac)
- M4A (.m4a)

## How It Works

1. Scene Detection:
   - Analyzes video for major scene changes
   - Identifies potential commercial break points

2. Audio Analysis:
   - Creates audio fingerprints using mel-scale spectrograms
   - Finds matching segments between original and dub

3. Smart Sync:
   - Automatically aligns audio segments
   - Handles varying commercial break patterns
   - Maintains sync across scene changes

## Example Workflow

Here is a typical workflow for synchronizing dubbed audio with a video:

1. Prepare your original video and dubbed audio files.
2. Run the tool with smart sync enabled:
   ```bash
   python media_sync_cli.py --input original.mp4 --audio dub.mp3 --output synced.mp4 --smart-sync
   ```
3. Review the output. If further adjustment is needed, use the manual offset option:
   ```bash
   python media_sync_cli.py --input original.mp4 --audio dub.mp3 --output synced.mp4 --offset 1.5
   ```
4. Use the `--dry-run` option to validate your setup before processing large files.

## Smart Sync vs Manual Offset

- **Smart Sync**: Automatically analyzes scene changes and audio fingerprints to align dubbed audio with the original video, even if there are commercial breaks or edits.
- **Manual Offset**: Applies a fixed time shift to the audio track. Useful for simple cases or as a fallback if smart sync is not accurate enough.

## Troubleshooting Q&A

**Q: The output video is out of sync. What should I do?**
A: Try running with `--smart-sync` for automatic alignment. If still out of sync, use the `--offset` option to manually adjust the timing.

**Q: FFmpeg is not found.**
A: Make sure FFmpeg is installed and available in your system PATH. See the Troubleshooting section above for installation commands.

**Q: The tool is slow on large files.**
A: Smart sync performs detailed analysis and may take longer. For faster processing, use manual offset or process shorter segments.

## Extending the Tool

- **Add New Formats**: Update the `supported_formats` sets in `AudioHandler` and `VideoHandler` classes.
- **Custom Processing Steps**: Extend the `MediaProcessor` class or add new modules in `src/core/`.
- **Configuration**: Add new options to `config/config.yaml` and access them via the `ConfigLoader` utility.