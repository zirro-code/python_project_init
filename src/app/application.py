import os
import pathlib
from subprocess import run
from venv import create

import click


class Application:
    ASSETS_FOLDER_PATH = [
        file
        for file in pathlib.Path(__file__).parent.parent.parent.resolve().iterdir()
        if file.name == "assets"
    ][0]
    CURRENT_DIRECTORY = pathlib.Path(os.getcwd()).resolve()

    @staticmethod
    @click.command()
    @click.option(
        "--mongo",
        help="Include MongoDB connector.",
        is_flag=True,
    )
    @click.option(
        "--docker",
        help="Make project docker native.",
        is_flag=True,
    )
    def command(**kwargs: list[dict[str, bool]]) -> None:
        for filename in [
            ".gitignore",
            ".env",
            ".env.example",
            "LICENSE",
            "README.md",
            "requirements.txt",
            "restart.sh",
            "ci.sh",
            "mypy.ini",
            "pytest.ini",
            "ruff.toml",
            ".vscode",
            "tests",
            "src/__main__.py",
            "src/__init__.py",
            "src/core/log.py",
            "src/core/file_manager.py",
            "src/core/http_clients/http_client.py",
            "src/app/application.py",
            "src/app/config.py",
        ]:
            Application.__copy_fileobj(
                pathlib.Path(str(Application.ASSETS_FOLDER_PATH) + "/" + filename)
            )

        for key, value in kwargs.items():
            if value:
                getattr(Application, f"_handle_{key}")()

        Application.__create_venv()

    @staticmethod
    def _handle_mongo() -> None:
        for filename in [
            "src/core/mongo",
        ]:
            Application.__copy_fileobj(
                pathlib.Path(str(Application.ASSETS_FOLDER_PATH) + "/" + filename)
            )

            Application.__add_module_to_requirements("pymongo")

            Application.__add_var_to_env("MONGO_URI", "mongodb://localhost:27017/")
            Application.__add_var_to_env("MONGO_DATABASE_NAME", "")

    @staticmethod
    def _handle_postgres() -> None:
        for filename in [
            "src/core/postgres",
            "alembic.ini",
        ]:
            Application.__copy_fileobj(
                pathlib.Path(str(Application.ASSETS_FOLDER_PATH) + "/" + filename)
            )

            Application.__add_module_to_requirements("sqlalchemy[asyncio]")
            Application.__add_module_to_requirements("asyncpg")
            Application.__add_module_to_requirements("alembic")

            Application.__add_var_to_env(
                "POSTGRES_URI",
                "postgresql+asyncpg://pguser:pgpass@localhost:5432/",
            )
            Application.__add_var_to_env("POSTGRES_DATABASE_NAME", "")

            Application.__add_var_to_env(
                "ALEMBIC_POSTGRES_URI",
                "POSTGRES_URI=postgresql+psycopg://postgres:superadmin@localhost:5432/",
            )
            Application.__add_var_to_env("ALEMBIC_POSTGRES_DATABASE_NAME", "")

    @staticmethod
    def _handle_docker() -> None:
        for filename in [
            ".dockerignore",
            "app.dockerfile",
            "docker-compose.yml",
            ".github/workflows/build_docker_image.yml",
        ]:
            Application.__copy_fileobj(
                pathlib.Path(str(Application.ASSETS_FOLDER_PATH) + "/" + filename)
            )

    @staticmethod
    def __create_venv() -> None:
        env_dir = f"{str(Application.CURRENT_DIRECTORY)}/venv"
        create(env_dir, with_pip=True)
        run(
            [
                "bin/pip",
                "install",
                "-r",
                f"{str(Application.CURRENT_DIRECTORY)}/requirements.txt",
            ],
            cwd=env_dir,
        )

    @staticmethod
    def __copy_fileobj(copy_path: pathlib.Path) -> None:
        for file in copy_path.glob("**/*") if copy_path.is_dir() else [copy_path]:
            if file.is_dir():
                continue
            source_dir = pathlib.Path("/".join(str(file.resolve()).split("/")[:-1]))
            relative_file_path = str(source_dir)[
                len(str(Application.ASSETS_FOLDER_PATH)) :
            ]
            target_dir = pathlib.Path(
                f"{Application.CURRENT_DIRECTORY}/{relative_file_path}"
            )
            target_file = pathlib.Path(f"{str(target_dir)}/{file.name}")

            if not target_dir.exists():
                target_dir.mkdir(parents=True)
            target_file.write_text(file.read_text())

    @staticmethod
    def __add_module_to_requirements(module_name: str) -> None:
        with pathlib.Path(f"{Application.ASSETS_FOLDER_PATH}/requirements.txt").open(
            "a"
        ) as file:
            file.write(f"{module_name}\n")

    @staticmethod
    def __add_var_to_env(key: str, value: str) -> None:
        for env_file in [".env", ".env.example"]:
            with pathlib.Path(f"{Application.ASSETS_FOLDER_PATH}/{env_file}").open(
                "a"
            ) as file:
                file.write(f'{key}="{value}"\n')

    def __init__(self) -> None:
        pass

    async def ainit(self) -> "Application":
        return self

    async def run(self) -> None:
        self.command()
