import zeeguu
from src.core.bt_node import BTNode


def setup():
    app_node = BTNode(code_path="zeeguu.api.app", label="encoding")
    config_node = BTNode(
        code_path="zeeguu.core.configuration.configuration", label="config"
    )

    app_node.whitelist(config_node)

    return [app_node, config_node]


def settings():
    return {
        "diagram_name": "Zeeguu Diagram",
        "project": zeeguu,
    }