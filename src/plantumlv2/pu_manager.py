from src.core.bt_graph import BTGraph
from src.plantumlv2.pu_entities import PuPackage
from src.plantumlv2.utils import get_pu_package_name_from_bt_package


def render_pu(graph: BTGraph, config: dict):
    bt_packages = graph.get_all_bt_modules_map()

    for view_name, view in config["views"].items():
        pu_package_map: dict[str, PuPackage] = {}
        for bt_package in bt_packages.values():
            pu_package = PuPackage(bt_package)
            pu_package_map[pu_package.name] = pu_package

        for pu_package in pu_package_map.values():
            pu_package.setup_dependencies(pu_package_map)

        pu_package_list = filter_packages(pu_package_map, view)

        pu_package_string = "\n".join(
            [pu_package.render_package() for pu_package in pu_package_list]
        )
        pu_dependency_string = "\n".join(
            [pu_package.render_dependency() for pu_package in pu_package_list]
        )
        uml_str = f"""
@startuml
title {view_name}
{pu_package_string}
{pu_dependency_string}
@enduml
        """
        print(uml_str)
        print("Program Complete")


def find_packages_with_depth(
    package: PuPackage, depth: int, pu_package_map: dict[PuPackage]
):
    bt_sub_packages = package.bt_package.get_submodules_recursive()
    filtered_sub_packages = [
        get_pu_package_name_from_bt_package(sub_package)
        for sub_package in bt_sub_packages
        if (sub_package.depth - package.bt_package.depth) <= depth
    ]
    return [pu_package_map[p] for p in filtered_sub_packages]


def filter_packages(
    packages_map: dict[PuPackage], view: dict
) -> list[PuPackage]:
    packages = packages_map.values()
    filtered_packages_set: set[PuPackage] = set()
    # packages
    for package_view in view["packages"]:
        for package in packages:
            filter_path = package_view

            if isinstance(package_view, str):
                if package.path.startswith(filter_path):
                    filtered_packages_set.add(package)

            if isinstance(package_view, dict):
                filter_path = package_view["packagePath"]
                view_depth = package_view["depth"]
                if package.path == filter_path:
                    filtered_packages_set.add(package)
                    depth_filter_packages = find_packages_with_depth(
                        package, view_depth, packages_map
                    )
                    filtered_packages_set.update(depth_filter_packages)

    if len(view["packages"]) == 0:
        filtered_packages_set = set(packages_map.values())

    # ignorePackages
    updated_filtered_packages_set: set = set()
    for ignore_packages in view["ignorePackages"]:
        for package in filtered_packages_set:
            should_filter = False
            ignore_packages: str = ignore_packages
            if ignore_packages.startswith("*") and ignore_packages.endswith(
                "*"
            ):
                if ignore_packages[1:-1] in package.path:
                    should_filter = True
            else:
                if package.path.startswith(ignore_packages):
                    should_filter = True

            if not should_filter:
                updated_filtered_packages_set.add(package)

    if len(view["ignorePackages"]) == 0:
        updated_filtered_packages_set = filtered_packages_set

    filtered_packages_set = updated_filtered_packages_set

    for package in packages:
        package.filter_excess_packages(filtered_packages_set)
    return list(filtered_packages_set)
