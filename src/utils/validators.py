from pathlib import Path
from typing import Set
from src.exceptions.custom_exceptions import InvalidFileError


def validate_file_exists(file_path: str) -> None:
    """
    Validate that a file exists at the given path.

    Args:
        file_path (str): Path to the file to validate

    Raises:
        InvalidFileError: If file doesn't exist
    """
    path = Path(file_path)
    if not path.is_file():
        raise InvalidFileError(f"File not found: {str(path.absolute())}")


def validate_media_format(file_path: Path, supported_formats: Set[str]) -> None:
    """
    Validate that a file has a supported format.

    Args:
        file_path (Path): Path to the media file
        supported_formats (Set[str]): Set of supported file extensions

    Raises:
        InvalidFileError: If file format is not supported
    """
    if file_path.suffix.lower() not in supported_formats:
        raise InvalidFileError(
            f"Unsupported format {file_path.suffix} for file: {str(file_path.absolute())}. "
            f"Supported formats: {', '.join(supported_formats)}"
        )


def validate_directory(dir_path: str) -> None:
    """
    Validate that a directory exists and is writable.

    Args:
        dir_path (str): Path to the directory to validate

    Raises:
        InvalidFileError: If directory doesn't exist or isn't writable
    """
    path = Path(dir_path)
    if not path.exists():
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise InvalidFileError(f"Cannot create directory {str(path.absolute())}: {str(e)}")
    elif not path.is_dir():
        raise InvalidFileError(f"Path exists but is not a directory: {str(path.absolute())}")

    # Check if the directory is writable
    try:
        test_file = path / '.write_test'
        test_file.touch()
        test_file.unlink()
    except Exception as e:
        raise InvalidFileError(f"Directory is not writable: {str(path.absolute())}: {str(e)}")
