import os
import git

def list_files_on_branch(branch_name):
    repo_path = os.getcwd()
    repo = git.Repo(repo_path)

    # Check out the desired branch
    repo.git.checkout(branch_name)

    # List the files in the current directory
    files = os.listdir()
    for file in files:
        print(file)
        
list_files_on_branch("master")