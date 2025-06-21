import os
import shutil
import subprocess
import argparse
import sys

from github import Github
from github import Auth

from config import github_access_token


auth = None
git = None
user = None


def init_git():
    global git, auth, user
    if auth == None:
        try:
            auth = Auth.Token(github_access_token)
            git = Github(auth=auth)
            user = git.get_user()
        except Exception as ex:
            print(f"[x] Exception on github auth: '{ex}' ..quit")
            return False
    return True


def close_git():
    global git, auth, user
    if git != None:
        git.close()


def clone_and_create_private_repo(source_repo_url, clean, force):
    global user

    # Extract repo name from URL
    repo_url = source_repo_url.rstrip('/').split('/')
    repo_name_url = repo_url[-1]
    repo_user = repo_url[-2]

    repo_name = f"{repo_name_url}__{repo_user}"

    # Clone the source repository
    out_dir = "./out"
    # Ensure the output directory exists
    os.makedirs(out_dir, exist_ok=True)

    local_dir = os.path.join(out_dir, repo_name)
    #local_dir = f"./{repo_name}"

    if os.path.exists(local_dir): 
        print(f"Local directory '{local_dir}' already exists.")
    else:
        print(f"Cloning repository: {source_repo_url}")
        try:
            subprocess.run(["git", "clone", "--mirror", source_repo_url, local_dir], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            return

    # Initialize GitHub API and store a Github instance on 'user'
    if not init_git():
        return

    # check if private repo was already created before
    try:
        existing_repo = user.get_repo(repo_name)
        if force:
            print(f"Repository '{repo_name}' already exists. Deleting it as --force flag is set.")
            try:
                existing_repo.delete()
            except Exception as ex:
                print(f"[x] Can't delete private repo '{repo_name}': '{ex}' ..quit")
                return
            print(f"Repository '{repo_name}' deleted.")
        else:
            print(f"Repository '{repo_name}' already exists. Use --force to overwrite it.")
            return

    except Exception as ex:
        # If the repository does not exist, continue
        print(f"Repository '{repo_name}' does not exist. Proceeding to create it.")

    # Create a new private repository
    print(f"Creating private repository: {repo_name}")
    try:
        new_repo = user.create_repo(repo_name, private=True)
        print(f"New repository created: {new_repo.clone_url}")
    except Exception as e:
        print(f"Error creating private repository: {e}")
        return

    # Authenticate the push URL using the token
    token_auth_url = new_repo.clone_url.replace(
        "https://", f"https://{github_access_token}@"
    )

    # Push to the new repository
    try:
        print(f"Pushing to new private repository: {token_auth_url}")
        subprocess.run(["git", "--git-dir", local_dir, "push", "--mirror", token_auth_url], check=True)
        print("Push successful.")
    except subprocess.CalledProcessError as e:
        print(f"Error pushing to new repository: {e}")
    finally:
        if clean:
            shutil.rmtree(local_dir)
            print(f"Local clone directory {local_dir} cleaned up.")


def main():
    parser = argparse.ArgumentParser(description="Clone a GitHub repo and create a new private repo with the same content.")
    parser.add_argument("repo_url", help="The URL of the GitHub repository to clone.")
    parser.add_argument("--clean", action="store_true", help="Delete the local folder after cloning and pushing.")
    parser.add_argument("--force", action="store_true", help="Delete the existing private repo if it exists and recreate it.")

    args = parser.parse_args()

    clone_and_create_private_repo(args.repo_url, args.clean, args.force)
    close_git()


if __name__ == "__main__":
    main()


