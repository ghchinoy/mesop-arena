# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from pathlib import Path
from typing import Dict, List, Union, Optional
import logging
from google.cloud import storage
from google.cloud.storage import transfer_manager
from alive_progress import alive_bar
import fire

from config.default import Default

config = Default()

class GCSUploader:
    """Singleton class for uploading directories to Google Cloud Storage."""

    _instances = {}  # Store instances per project/bucket

    def __new__(cls, bucket_name: str, project_id: Optional[str] = None):
        key = (bucket_name, project_id)
        if key not in cls._instances:
            cls._instances[key] = super(GCSUploader, cls).__new__(cls)
            cls._instances[key].storage_client = storage.Client(project=project_id)
            cls._instances[key].bucket = cls._instances[key].storage_client.bucket(bucket_name)
            cls._instances[key]._setup_logging()
        return cls._instances[key]

    def __init__(self, bucket_name: str, project_id: Optional[str] = None):
        # This init will run every time, but only the first time sets the bucket.
        # This avoids reinitializing the bucket on subsequent calls.
        if not hasattr(self, 'bucket'):
            self.bucket = self.storage_client.bucket(bucket_name)

    def _setup_logging(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def upload_dir_to_gcs(
        self,
        src_dir: str,
        gcs_dest_dir: str,
        workers: int = os.cpu_count(),
        verbose: bool = False,
        skip_if_exists: bool = False,
        extensions: Optional[List[str]] = None,
    ) -> Dict[str, Union[None, Exception]]:
        """Upload every file in a directory, including all files in subdirectories."""

        if not os.path.exists(src_dir):
            raise ValueError(f"Directory {src_dir} is not found.")

        dir_as_path_objs = Path(src_dir)
        paths = [
            str(path.relative_to(src_dir))
            for path in dir_as_path_objs.rglob("*")
            if path.is_file() and (extensions is None or path.suffix[1:].lower() in extensions)
        ]

        if verbose:
            self._log(f"Found {len(paths)} files in directory: {src_dir}")
            self._log("Starting upload...")

        upload_results: Dict[str, Union[None, Exception]] = {}
        try:
            with alive_bar(len(paths), title='Uploading...', force_tty=True) as bar:
                def progress_callback(blob):
                    bar()
                    if verbose:
                        self._log(f"Uploaded {blob.name} to {self.bucket.name}.")

                results = transfer_manager.upload_many_from_filenames(
                    self.bucket,
                    paths,
                    source_directory=src_dir,
                    blob_name_prefix=f"{gcs_dest_dir}/",
                    max_workers=workers,
                    skip_if_exists=skip_if_exists,
                    progress_callback=progress_callback,
                )

            for name, result in zip(paths, results):
                upload_results[name] = result
                if isinstance(result, Exception):
                    self._log(f"Failed to upload {name} due to exception: {result}", level=logging.ERROR)
                elif verbose:
                    self._log(f"Uploaded {name} to {self.bucket.name}.")
        except Exception as e:
            self._log(f"Error during upload: {e}", level=logging.ERROR)
            return {"error": e}

        return upload_results

    def _log(self, message: str, level: int = logging.INFO):
        """Internal logging function."""
        self.logger.log(level, message)

def main(
    bucket_name: str,
    source_directory: str,
    destination_prefix: str = "",
    verbose: bool = False,
    skip_if_exists: bool = False,
    extensions: Optional[str] = ".json,png",
    project_id: Optional[str] = config.DEMO_PROJECT_ID,
):
    """
    Uploads files from a local directory to a GCS bucket.

    Args:
        bucket_name: The GCS bucket name.
        source_directory: The local directory path.
        destination_prefix: Optional GCS destination prefix.
        verbose: Enable verbose output.
        skip_if_exists: Skip existing files.
        extensions: Optional comma-separated file extensions (e.g., "png,json").
        project_id: Optional Google Cloud Project ID.
    """

    if extensions:
        extensions_list = [ext.strip().lower() for ext in extensions.split(',')]
    else:
        extensions_list = None

    uploader = GCSUploader(bucket_name, project_id)

    try:
        results = uploader.upload_dir_to_gcs(
            source_directory,
            destination_prefix,
            verbose=verbose,
            skip_if_exists=skip_if_exists,
            extensions=extensions_list,
        )

        if "error" in results:
            print("Upload failed. See logs for details.")
        else:
            print("Upload completed.")
            if verbose:
                for filename, result in results.items():
                    if isinstance(result, Exception):
                        print(f"Failed: {filename}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    fire.Fire(main)