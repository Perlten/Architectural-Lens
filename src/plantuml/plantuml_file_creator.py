import os
from src.core.bt_module import BTModule
from pathlib import Path


# list of subdomains is a set of strings, could be:
# "test_project/tp_src/api"
# "test_project/tp_src/tp_core/tp_sub_core"
# this would give the 2 sub-systems starting at api and tp_sub_core and how/if they relate in a drawing
def plantuml_diagram_creator_sub_domains(
    root_node,
    diagram_name,
    list_of_subdomains,
    ignore_modules,
    compare_graph_root,
    root_folder,
    save_location="./",
):
    create_directory_if_not_exist(save_location)

    diagram_type = "package "
    diagram_name = diagram_name.replace(" ", "_")
    diagram_name_txt = save_location + diagram_name + ".txt"

    que: Queue[BTModule] = Queue()
    que.enqueue(root_node)

    # tracks paths of nodes, so we dont enter the same node twice, path is needed so we dont hit duplicates
    node_tracker = {}

    # keeps track of names so we dont duplicate name modules in the graph
    name_tracker = {}

    if os.path.exists(diagram_name_txt):
        os.remove(diagram_name_txt)

    # adding root to the drawing IF its meant to be in there

    if check_if_module_should_be_in_filtered_graph(root_node.path, list_of_subdomains):
        f = open(diagram_name_txt, "a")
        f.write("@startuml \n")
        f.write("title " + diagram_name + "\n")
        f.write(diagram_type + root_node.name + "\n")
        f.close()
    else:
        f = open(diagram_name_txt, "a")
        f.write("@startuml \n")
        f.write("title " + diagram_name + "\n")
        f.close()

    while not que.isEmpty():
        curr_node: BTModule = que.dequeue()

        # adds all modules we want in our subgraph
        for child in curr_node.child_module:
            if child.path not in node_tracker and not ignore_modules_check(
                ignore_modules, child.name
            ):
                duplicate_name_check(name_tracker, child, node_tracker)
                if check_if_module_should_be_in_filtered_graph(
                    child.path, list_of_subdomains
                ):
                    f = open(diagram_name_txt, "a")
                    f.write(
                        diagram_type
                        + '"'
                        + get_name_for_module_duplicate_checker(child)
                        + '"'
                        + "\n"
                    )
                    f.close()

                que.enqueue(child)
                node_tracker[child.path] = child
                # reference the child, so we can add it to the graph in green later if its a new module
                name_tracker[child.name] = child

    # adding all dependencies
    que.enqueue(root_node)
    node_tracker_dependencies = {}
    dependencies_map = {}
    while not que.isEmpty():
        curr_node: BTModule = que.dequeue()

        for child in curr_node.child_module:
            if (
                child.path not in node_tracker_dependencies
                and not ignore_modules_check(ignore_modules, child.name)
            ):
                que.enqueue(child)
                node_tracker_dependencies[child.path] = True

        dependencies: set[BTModule] = curr_node.get_module_dependencies()
        name_curr_node = get_name_for_module_duplicate_checker(curr_node)

        for dependency in dependencies:
            if not ignore_modules_check(ignore_modules, dependency.name):
                name_dependency = get_name_for_module_duplicate_checker(dependency)
                if check_if_module_should_be_in_filtered_graph(
                    dependency.path, list_of_subdomains
                ) and check_if_module_should_be_in_filtered_graph(
                    curr_node.path, list_of_subdomains
                ):
                    # this if statement is made so that we dont point to ourselves
                    if name_curr_node != name_dependency:
                        # used to detect dependency changes
                        dep_str = name_curr_node + "-->" + name_dependency
                        if name_curr_node in dependencies_map:
                            dependency_list: list = dependencies_map[name_curr_node]
                            dependency_list.append(name_dependency)
                            dependencies_map[name_curr_node] = dependency_list
                        else:
                            dependency_list = []
                            dependency_list.append(name_dependency)
                            dependencies_map[name_curr_node] = dependency_list

                        ##
                        f = open(diagram_name_txt, "a")
                        f.write(
                            '"'
                            + name_curr_node
                            + '"'
                            + "-->"
                            + '"'
                            + name_dependency
                            + '"'
                            + "\n"
                        )
                        f.close()

    ##################################### TO BE REFACTORED #########################################
    # this section finds modules and colors them green or red depending on if theyre old or new

    que.enqueue(compare_graph_root)
    bfs_node_tracker = {}
    main_nodes = {}
    while not que.isEmpty():
        curr_node: BTModule = que.dequeue()
        for child in curr_node.child_module:
            if child.path not in bfs_node_tracker and not ignore_modules_check(
                ignore_modules, child.name
            ):
                duplicate_name_check(name_tracker, child, node_tracker, root_folder)
                if check_if_module_should_be_in_filtered_graph(
                    child.path, list_of_subdomains
                ):
                    que.enqueue(child)
                    bfs_node_tracker[child.path] = True
                    main_nodes[child.name] = child

                    # this will be true, if the package has been deleted
                    if child.name not in name_tracker and not ignore_modules_check(
                        ignore_modules, child.name
                    ):
                        f = open(diagram_name_txt, "a")
                        f.write(
                            diagram_type
                            + '"'
                            + get_name_for_module_duplicate_checker(child)
                            + '" #red'
                            + "\n"
                        )
                        f.close()

    for child in name_tracker.values():
        # children from original graph
        node: BTModule = child
        name = node.name
        if name not in main_nodes:
            f = open(diagram_name_txt, "a")
            f.write(
                diagram_type
                + '"'
                + get_name_for_module_duplicate_checker(node)
                + '" #green'
                + "\n"
            )
            f.close()
    ########################################################################################################

    ##################################### TO BE REFACTORED #########################################
    # this section finds Dependencies and colors them green or red depending on if theyre old or new

    que.enqueue(compare_graph_root)

    dependencies_map_main_graph = {}

    node_tracker_dependencies = {}
    while not que.isEmpty():
        curr_node: BTModule = que.dequeue()

        for child in curr_node.child_module:
            if (
                child.path not in node_tracker_dependencies
                and not ignore_modules_check(ignore_modules, child.name)
            ):
                que.enqueue(child)
                node_tracker_dependencies[child.path] = True

        name_curr_node = get_name_for_module_duplicate_checker(curr_node)
        dependencies: set[BTModule] = curr_node.get_module_dependencies()

        print("yo222")
        print(dependencies)

        list_of_red_dependencies = find_red_dependencies(
            dependencies_map, name_curr_node, dependencies
        )
        x = 4
    #     for dependency in dependencies:
    #         if not ignore_modules_check(ignore_modules, dependency.name):
    #             name_dependency = get_name_for_module_duplicate_checker(dependency)
    #             if check_if_module_should_be_in_filtered_graph(
    #                 dependency.path, list_of_subdomains
    #             ) and check_if_module_should_be_in_filtered_graph(
    #                 curr_node.path, list_of_subdomains
    #             ):
    #                 # this if statement is made so that we dont point to ourselves
    #                 if name_curr_node != name_dependency:
    #                     # used to detect dependency changes
    #                     dep_str = name_curr_node + "-->" + name_dependency
    #                     dependencies_map_main_graph[dep_str] = (curr_node, dependency)
    #                     ##
    #                     if dep_str not in dependencies_map:
    #                         f = open(diagram_name_txt, "a")
    #                         f.write(
    #                             '"'
    #                             + name_curr_node
    #                             + '"'
    #                             + "-->"
    #                             + '"'
    #                             + name_dependency
    #                             + '" #red'
    #                             + "\n"
    #                         )
    #                         f.close()

    # for dependency in dependencies_map.keys():
    #     if dependency not in dependencies_map_main_graph.keys():

    #         dependency_split = dependency.split("-->")

    #         f = open(diagram_name_txt, "a")
    #         f.write(
    #             '"'
    #             + dependency_split[0]
    #             + '"'
    #             + "-->"
    #             + '"'
    #             + dependency_split[1]
    #             + '" #green'
    #             + "\n"
    #         )
    #         f.close()

    #########################################################################################################
    # ends the uml
    f = open(diagram_name_txt, "a")
    f.write("@enduml")
    f.close()

    create_file(diagram_name_txt)
    # comment in when done, but leaving it in atm for developing purposes
    # os.remove(diagram_name_txt)


def find_red_dependencies(new_dependencies, node_name, old_dependencies: set[BTModule]):
    res = []

    if node_name not in new_dependencies:
        for dependency in old_dependencies:
            res.append(dependency.name)
    else:
        list_of_new_dep_graph = new_dependencies[node_name]
        for dependency in old_dependencies:
            for new_dependency in list_of_new_dep_graph:
                if dependency.name != new_dependency:
                    res.append(dependency.name)

    # if node_name in new_dependencies:
    #     list_of_new_dep_graph = new_dependencies[node_name]
    #     for new_dependency in list_of_new_dep_graph:
    #         for old_dependency in old_dependencies:
    #             if new_dependency != old_dependency.name:
    #                 res.append(old_dependency.name)
    return res


def create_file(name):
    os.system("python -m plantuml " + name + ".svg" + " " + name)


def get_name_for_module_duplicate_checker(module: BTModule):
    if module.name_if_duplicate_exists != None:
        return module.name_if_duplicate_exists
    return module.name


def duplicate_name_check(
    node_names, curr_node: BTModule, path_tracker, root_folder=None
):
    if was_node_in_original_graph(curr_node, path_tracker, root_folder):
        if not curr_node.name_if_duplicate_exists:
            if curr_node.name in node_names:
                curr_node_split = curr_node.path.split("/")
                curr_node_name = curr_node_split[-2] + "/" + curr_node_split[-1]
                curr_node.name_if_duplicate_exists = curr_node_name


def was_node_in_original_graph(node: BTModule, path_tracker, root_folder):
    if root_folder:
        for path in path_tracker.keys():
            path_split = path.split(root_folder)[-1]
            path_from_tracker = root_folder + path_split
            node_split = node.path.split(root_folder)[-1]
            path_from_node = root_folder + node_split
            if path_from_tracker == path_from_node:
                if len(path_from_tracker.split("/")) != 2:
                    return True
            return False


def ignore_modules_check(list_ignore, module):
    for word in list_ignore:
        if word in module:
            return True
    return False


def check_if_module_should_be_in_filtered_graph(module, allowed_modules):
    if len(allowed_modules) == 0:
        return True
    for module_curr in allowed_modules:
        if module_curr in module:
            return True
    return False


def create_directory_if_not_exist(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)


queue = Queue()
