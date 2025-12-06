import csv
import pathlib
from collections.abc import Generator
from typing import Any, Literal

import src.core.misc


class FileManager:
    def __init__(self, base_directory: pathlib.Path | None = None) -> None:
        self.base_directory = base_directory or pathlib.Path()

        self.cache_dir = self.base_directory / pathlib.Path("cache")
        self.input_dir = self.base_directory / pathlib.Path("input")
        self.output_dir = self.base_directory / pathlib.Path("output")
        self.backup_dir = self.base_directory / pathlib.Path("backup")

    @staticmethod
    def set_up_directory(path: str | pathlib.Path) -> None:
        path_to_check = (
            "/".join(f"{path}".split("/")[:-1]) if "." in str(path) else str(path)
        )
        if not pathlib.Path(path_to_check).exists():
            pathlib.Path(path_to_check).mkdir(parents=True)

    def get_env_variable_names(
        self, space: Literal[".env", ".env.example"]
    ) -> Generator[str, Any, None]:
        env_namespace: str = f"./{space}"
        path = self.base_directory / pathlib.Path(env_namespace)
        with path.open("r") as file:
            for line in file:
                yield line.split("=")[0].upper()

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
