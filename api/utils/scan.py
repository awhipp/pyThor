"""Scanning class which scans a directory and returns a list of files and metadata."""

import mimetypes
import os

from models.file import FileMetadata
from pydantic import BaseModel
from utils.logger import get_logger

logger = get_logger(__name__)


def is_file_a_video(file_path: str) -> bool:
    """Check if the file is a video file."""
    mime_type, _ = mimetypes.guess_type(file_path)
    logger.debug(f"Checking file: {file_path} => {mime_type}")
    return mime_type and mime_type.startswith("video")


class ScanDirectory(BaseModel):
    """Given a directory this class scans the directory and
    returns a list of files and metadata.

    Args:
        root_dir (str): The directory to scan.
        valid_extensions (list[str]): List of valid extensions to scan for.
    """

    root_dir: str
    files: dict[str, FileMetadata] = {}

    def __init__(self, root_dir: str = os.getenv("ROOT_DIR", ".")):
        """Post-initialization to set up additional attributes."""
        super().__init__(root_dir=root_dir)
        self.scan_directory()

    def get_files(self) -> list[FileMetadata]:
        """Return the list of files."""
        return list(self.files.values())

    def scan_directory(self):
        """Scans the directory and returns a list of files and metadata."""
        logger.info(f"Scanning directory: {self.root_dir}")
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_name = os.path.basename(file_path)

                if not is_file_a_video(file_path):
                    continue

                file_size = os.path.getsize(file_path)
                file_metadata = FileMetadata(
                    file_name=file_name,
                    file_path=file_path,
                    initial_size=file_size,
                )

                if file_metadata.file_id in self.files:
                    logger.debug(f"File already exists: {file_path} -- Updating...")

                self.files[file_metadata.file_id] = file_metadata

                logger.debug(f"Found file: {file_path}")
