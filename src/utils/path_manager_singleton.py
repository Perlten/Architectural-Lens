from pathlib import Path


class PathManagerSingleton:
    _instance = None
    _config_path = None
    _git_config_path = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def setup(self, config: dict, git_config=None, append_root_folder=False):
        self._config_path = self._get_path(config, append_root_folder)
        self._git_config_path = self._get_path(git_config, append_root_folder)

    def get_relative_path_from_project_root(self, path: str):
        if self._config_path is None:
            raise Exception(
                "Should call setup method before any other function"
            )
        try:
            return Path(path).relative_to(self._config_path).as_posix()
        except Exception:
            return Path(path).relative_to(self._git_config_path).as_posix()

    def _get_path(self, config, append_root_folder):
        if config is None:
            return None
        config_path = Path(config["_config_path"])
        if append_root_folder:
            config_path = config_path.joinpath(config["rootFolder"])
        config_path = config_path.as_posix()
        return config_path
