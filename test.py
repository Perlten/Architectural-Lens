import os
import git
import shutil
import tempfile


def print_files_on_branch(branch):
    # Clone the repository to a temporary directory
    # repo_path = os.getcwd()
    repo_path = "test_projects/test_project"
    temp_dir = tempfile.mkdtemp()
    git.Repo.clone_from(repo_path, temp_dir)

    # Switch to the branch and get the latest changes
    repo = git.Repo(temp_dir)
    repo.git.checkout(branch)
    repo.remotes.origin.pull()

    # Print the files
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            print(os.path.join(root, file))

    # Delete the temporary directory
    shutil.rmtree(temp_dir)
    
print_files_on_branch('lol')

