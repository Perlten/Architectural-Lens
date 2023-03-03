def verify_config_options(config: dict):
    views = config.get("views", {})
    for view_name, view_data in views.items():
        packages = view_data.get("packages")
        ignore_packages = view_data.get("ignorePackages")
        total_packages = set((packages + ignore_packages))
        print("dsad")
