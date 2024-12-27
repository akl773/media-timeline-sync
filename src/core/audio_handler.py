import numpy as np
from pathlib import Path
import soundfile as sf
from scipy import signal
from typing import List, Tuple, Optional
import subprocess
import logging

logger = logging.getLogger(__name__)


class AudioHandler:
    """Handles all audio processing operations including fingerprinting and analysis."""

    def __init__(self):
        self.supported_formats = {'.mp3', '.wav', '.aac', '.m4a'}

    def _mel_filterbank(self, frequencies: np.ndarray, n_mels: int = 20,
                        fmin: float = 0.0, fmax: Optional[float] = None) -> np.ndarray:
        """Create a Mel filter bank matrix to convert frequencies to mel scale."""
        fmax = fmax or frequencies[-1]
        mel_max = 2595 * np.log10(1 + fmax / 700.0)
        mel_min = 2595 * np.log10(1 + fmin / 700.0)
        mel_points = np.linspace(mel_min, mel_max, n_mels + 2)
        hz_points = 700 * (10 ** (mel_points / 2595.0) - 1)

        bin_hz = frequencies[1] - frequencies[0]
        bin_idx = np.floor(hz_points / bin_hz)

        filters = np.zeros((n_mels, len(frequencies)))

        for i in range(n_mels):
            filters[i, int(bin_idx[i]):int(bin_idx[i + 2])] = \
                np.concatenate([
                    np.linspace(0, 1, int(bin_idx[i + 1] - bin_idx[i])),
                    np.linspace(1, 0, int(bin_idx[i + 2] - bin_idx[i + 1]))
                ])

        return filters

    def extract_fingerprint(self, audio_path: str, start_time: float = 0,
                            duration: float = 60) -> np.ndarray:
        """Extract audio fingerprint using scipy and soundfile."""
        audio_path = str(Path(audio_path).absolute())

        # Read audio file
        data, sample_rate = sf.read(audio_path)

        # Convert start_time and duration to samples
        start_sample = int(start_time * sample_rate)
        duration_samples = int(duration * sample_rate)

        # Extract segment
        if len(data.shape) > 1:  # If stereo, convert to mono
            data = data.mean(axis=1)

        segment = data[start_sample:start_sample + duration_samples]

        # Create spectrogram
        frequencies, times, spectrogram = signal.spectrogram(
            segment,
            fs=sample_rate,
            nperseg=2048,
            noverlap=1024
        )

        # Get mel-scale features
        mel_basis = self._mel_filterbank(frequencies, n_mels=20)
        mel_spectrogram = np.dot(mel_basis, spectrogram)

        # Log-scale the features
        mel_spectrogram = np.log(mel_spectrogram + 1e-9)

        return mel_spectrogram

    def find_sync_points(self, original_audio: str, dub_audio: str,
                         scene_changes: List[float]) -> List[Tuple[float, float]]:
        """Find synchronization points between original and dub audio."""
        sync_points = []
        window_size = 30  # Seconds around scene changes to analyze

        for scene_time in scene_changes:
            # Extract fingerprints around scene change
            orig_fp = self.extract_fingerprint(
                original_audio,
                start_time=max(0, scene_time - window_size / 2),
                duration=window_size
            )

            # Search for matching segment in dub
            best_offset = 0
            best_correlation = -float('inf')

            for offset in np.arange(-60, 60, 0.5):  # ±60 seconds search window
                dub_fp = self.extract_fingerprint(
                    dub_audio,
                    start_time=max(0, scene_time + offset - window_size / 2),
                    duration=window_size
                )

                correlation = np.corrcoef(orig_fp.flatten(), dub_fp.flatten())[0, 1]

                if correlation > best_correlation:
                    best_correlation = correlation
                    best_offset = offset

            if best_correlation > 0.7:  # Confidence threshold
                sync_points.append((scene_time, scene_time + best_offset))
                logger.debug(f"Found sync point at {scene_time:.2f}s with offset {best_offset:.2f}s")

        return sync_points

    def extract_audio_from_video(self, video_path: str, output_path: str) -> str:
        """Extract audio track from video file."""
        try:
            cmd = [
                'ffmpeg', '-i', str(Path(video_path).absolute()),
                '-vn', '-acodec', 'pcm_s16le',
                str(Path(output_path).absolute())
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to extract audio: {e.stderr}")
            raise

    def create_sync_filter(self, sync_points: List[Tuple[float, float]],
                           manual_offset: float = 0.0) -> str:
        """Create FFmpeg filter complex string for audio synchronization."""
        if not sync_points:
            return f'[1:a]adelay={int(manual_offset * 1000)}|{int(manual_offset * 1000)}[merged_audio]'

        segments = []
        for i, (orig_time, dub_time) in enumerate(sync_points):
            offset = dub_time - orig_time
            next_time = sync_points[i + 1][0] if i + 1 < len(sync_points) else ''
            segments.append(
                f"[1:a]atrim={dub_time}:{next_time},"
                f"adelay={int(offset * 1000)}|{int(offset * 1000)}[seg{i}];"
            )

        return ''.join(segments) + ''.join(f'[seg{i}]' for i in range(len(segments))) + \
            f'concat=n={len(segments)}:v=0:a=1[merged_audio]'
