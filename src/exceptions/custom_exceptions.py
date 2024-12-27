class MediaProcessingError(Exception):
    """Base exception for media processing errors."""
    pass


class InvalidFileError(MediaProcessingError):
    """Exception raised for invalid file operations."""
    pass


class CommandExecutionError(MediaProcessingError):
    """Exception raised when external command execution fails."""
    pass
