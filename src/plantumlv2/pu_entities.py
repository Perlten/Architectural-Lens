from src.core.bt_module import BTModule
from src.plantumlv2.utils import get_pu_package_name_from_bt_package
from src.utils.path_manager_singleton import PathManagerSingleton


class PuPackage:
    name = ""
    pu_dependency_list: list["PuDependency"] = None
    bt_package: BTModule = None

    def __init__(self, bt_package: BTModule) -> None:
        self.pu_dependency_list = []
        self.name = get_pu_package_name_from_bt_package(bt_package)
        self.bt_package = bt_package

    @property
    def path(self):
        path_manager = PathManagerSingleton()
        return path_manager.get_relative_path_from_project_root(
            self.bt_package.path, True
        )

    def setup_dependencies(self, pu_package_map: dict[str, "PuPackage"]):
        bt_dependencies = self.bt_package.get_module_dependencies()
        for bt_package_dependency in bt_dependencies:
            pu_name = get_pu_package_name_from_bt_package(
                bt_package_dependency
            )
            pu_package_dependency = pu_package_map[pu_name]
            self.pu_dependency_list.append(
                PuDependency(
                    self,
                    pu_package_dependency,
                    self.bt_package,
                    bt_package_dependency,
                )
            )

    def render_package(self) -> str:
        return f'package "{self.name}"'

    def render_dependency(self) -> str:
        return "\n".join(
            [
                pu_dependency.render()
                for pu_dependency in self.pu_dependency_list
            ]
        )

    def filter_excess_packages(self, used_packages: set["PuPackage"]):
        filtered_dependency_list: list[PuDependency] = []

        for dependency in self.pu_dependency_list:
            if dependency.to_package in used_packages:
                filtered_dependency_list.append(dependency)
        self.pu_dependency_list = filtered_dependency_list


class PuDependency:
    from_package: PuPackage = None
    to_package: PuPackage = None

    from_bt_package: BTModule = None
    to_bt_package: BTModule = None

    dependency_count = 0

    def __init__(
        self,
        from_package: PuPackage,
        to_package: PuPackage,
        from_bt_package: BTModule,
        to_bt_package: BTModule,
    ) -> None:
        self.from_package = from_package
        self.to_package = to_package
        self.from_bt_package = from_bt_package
        self.to_bt_package = to_bt_package
        self.dependency_count = self.from_bt_package.get_dependency_count(
            self.to_bt_package
        )

    def render(self) -> str:
        from_name = self.from_package.name
        to_name = self.to_package.name
        return f'"{from_name}"-->"{to_name}": {self.dependency_count}'
