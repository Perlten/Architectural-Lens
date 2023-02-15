import git
import tempfile
import os
from src.core.bt_graph import BTGraph
import json
import requests
import jsonschema
import shutil


def create_git_graph():
    repo_path = "https://github.com/JesperRusbjerg/test_project"
    # repo_path = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    git.Repo.clone_from(repo_path, temp_dir)

    # Switch to the branch and get the latest changes
    repo = git.Repo(temp_dir)
    repo.git.checkout("main")
    repo.remotes.origin.pull()

    # Print the files
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            print(os.path.join(root, file))

    # Build a graph of the master branch
    config = read_config_file(temp_dir+"/bt_config.json")
    g = BTGraph()
    g.build_graph(config)

    # Switch back to the original branch
    # repo.git.checkout(original_branch)

    # Remove the temporary directory
    shutil.rmtree(temp_dir)

    return g



def read_config_file(config_path):
    schema_url = "https://raw.githubusercontent.com/Perlten/Master-thesis-rename/feature/json-config/config.schema.json"
    config = None
    with open(config_path, "r") as f:
        config = json.load(f)

    schema = requests.get(schema_url).json()

    jsonschema.validate(instance=config, schema=schema)

    config["_config_path"] = os.path.dirname(config_path)
    return config



if __name__ == '__main__':
    # print("yo")
    create_git_graph()



# 'test_projects/test_project/bt_config.json'



