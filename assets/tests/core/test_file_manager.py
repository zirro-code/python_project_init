import pathlib
from collections.abc import Generator
from typing import Any

import pytest

import src.core.file_manager


@pytest.mark.no_cover
def remove_dir_recursive(path: pathlib.Path):
    for child in path.iterdir():
        if child.is_file() or child.is_symlink():
            child.unlink()
        elif child.is_dir():
            remove_dir_recursive(child)
    path.rmdir()


@pytest.fixture(scope="session")
def base_directory() -> pathlib.Path:
    return pathlib.Path("./tmp/test/file_manager")


@pytest.fixture
def file_manager(base_directory: pathlib.Path) -> src.core.file_manager.FileManager:
    return src.core.file_manager.FileManager(base_directory)


@pytest.fixture(scope="session", autouse=True)
def set_up_test_folder(base_directory: pathlib.Path) -> Generator[None, Any, None]:
    if not base_directory.exists():
        base_directory.mkdir(parents=True)
    yield
    remove_dir_recursive(base_directory)


class TestFileManager:
    def test_set_up_directory(
        self,
        file_manager: src.core.file_manager.FileManager,
        base_directory: pathlib.Path,
    ) -> None:
        path = base_directory / pathlib.Path("./set_up_directory/dir")
        file_manager.set_up_directory(str(path))
        assert path.exists()
        file_manager.set_up_directory(str(path))
        path = base_directory / pathlib.Path("./set_up_single_directory")
        file_manager.set_up_directory(str(path))
        assert path.exists()

        path = base_directory / pathlib.Path("./set_up_single_one_directory/csv.csv")
        assert not path.exists()
        assert not (
            base_directory / pathlib.Path("./set_up_single_one_directory")
        ).exists()

        path = base_directory / pathlib.Path("./set_up_directory1/csv.csv")
        file_manager.set_up_directory(path)
        assert not path.exists()
        assert (base_directory / pathlib.Path("./set_up_directory1")).exists()

        path = base_directory / pathlib.Path("./set_up_directory2/csv2.csv")
        file_manager.set_up_directory(str(path))
        assert not path.exists()
        assert (base_directory / pathlib.Path("./set_up_directory2")).exists()

    def test_dump_csv(
        self,
        file_manager: src.core.file_manager.FileManager,
    ) -> None:
        data: list[dict[str, Any]] = [
            {"a": 1, "b": 2},
            {"b": 2, "c": 3, "d": {"d": 1, "e": [{"a": 1}, {"b": 2}]}},
        ]
        path = file_manager.output_dir
        file_name = pathlib.Path("./csv1.csv")

        file_manager.set_up_directory(str(path))
        assert path.exists()

        file_path = path / file_name
        file_manager.dump_csv(data, str(file_name))
        assert file_path.exists()

        with pathlib.Path(file_path).open() as file:
            assert (
                file.read()
                == """a,b,c,d.d,d.e.0.a,d.e.1.b
1,2,,,,
,2,3,1,1,2
"""
            )
