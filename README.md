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

## Troubleshooting

Common issues and solutions:

1. FFmpeg not found:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # On macOS with Homebrew
   brew install ffmpeg
   ```

2. Audio sync issues:
   - Try enabling smart sync with `--smart-sync`
   - Use `--verbose` for detailed analysis
   - Adjust manual offset if needed

3. Performance issues:
   - Smart sync requires more processing time
   - Use manual offset for faster processing

## Configuration Management

You can now specify a custom configuration file and override config values with environment variables.

- Use `--config` to specify a custom YAML config file:
  ```bash
  python media_sync_cli.py --config path/to/your_config.yaml ...
  ```
- Use `--list-formats` to print supported video and audio formats:
  ```bash
  python media_sync_cli.py --list-formats
  ```
- Use `--dry-run` to validate your inputs and config without processing media:
  ```bash
  python media_sync_cli.py --input video.mp4 --audio dub.mp3 --output final.mp4 --dry-run
  ```

### Sample config.yaml
```yaml
ffmpeg:
  video_codec: copy
  audio_codec: aac
  audio_bitrate: 192k
  max_offset: 300
logging:
  level: INFO
  file: logs/media_sync.log
processing:
  max_concurrent_jobs: 4
  temp_directory: /tmp/media_sync
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.