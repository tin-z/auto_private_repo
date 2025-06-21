## auto_private_repo

The following Python script creates a private repository and replicates the commit history of a public repository.

 - install
```
rm -rf .venv && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt 

```

 - modify config.py by inserting your github apikey:
```
github_access_token = "ghp_AAA"

```

 - usage:
```
usage: main.py [-h] [--clean] [--force] repo_url

Clone a GitHub repo and create a new private repo with the same content.

positional arguments:
  repo_url    The URL of the GitHub repository to clone.

options:
  -h, --help  show this help message and exit
  --clean     Delete the local folder after cloning and pushing.
  --force     Delete the existing private repo if it exists and recreate it.

```

 - example:
```
python main.py https://github.com/jekyll/jekyllbot

# as a result, a private repository named 'jekyllbot__jekyll' will be created on your github

```

