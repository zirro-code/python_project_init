import csv
import pathlib
from typing import Any

import src.core.misc


class FileManager:
    def __init__(self, base_directory: pathlib.Path | None = None) -> None:
        base_directory = base_directory or pathlib.Path()

        self.cache_dir = base_directory / pathlib.Path("cache")
        self.input_dir = base_directory / pathlib.Path("input")
        self.output_dir = base_directory / pathlib.Path("output")
        self.backup_dir = base_directory / pathlib.Path("backup")

    @staticmethod
    def set_up_directory(path: str | pathlib.Path) -> None:
        path_to_check = (
            "/".join(f"{path}".split("/")[:-1]) if "." in str(path) else str(path)
        )
        if not pathlib.Path(path_to_check).exists():
            pathlib.Path(path_to_check).mkdir(parents=True)

    def dump_csv(self, data: list[dict[str, Any]], output_file_name: str) -> None:
        flattened_data: list[dict[Any, Any]] = [
            src.core.misc.flatten_json(record) for record in data
        ]
        fieldnames: list[str] = sorted(
            {key for d in flattened_data for key in d.keys()}
        )

        output_file_path: str = (
            f"{self.output_dir}/{'.'.join(output_file_name.split('.')[:-1])}.csv"
        )
        FileManager.set_up_directory(output_file_name)

        with pathlib.Path(output_file_path).open("w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_data)
