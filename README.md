# OldGitRepos
A small tool to list and archive old git repositories associated with an organisation.

Usage: python main.py [arguments]

## Arguments: 

`--token`: A git access token to log in to git. You can create one via "Settings > Developer Settings > Personal Access Tokens"
           
`--org_id`: The name of the organisation to get repositories for (e.g. ICRAR)
           
`--older_than`: Only look at repositories that have not had commits or modifies this long ago. (e.g. 2 years)

`--csv`: Specify a CSV file to save the repo list to. (e.g. repos.csv)

`--archive`: Specify a file name to archive the repos to. This will create a .tar.gz file containing the repos. (e.g. repos.tar.gz)

Example command line to save CSV: ```python main.py --token (token here) --org_id ICRAR --older_than "2 years" --csv repos.csv```

Example command line to archvie repos: ```python main.py --token (token here) --org_id ICRAR --older_than "2 years" --archive repos.tar.gz```
