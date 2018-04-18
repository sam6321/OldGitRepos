#
#    (c) UWA, The University of Western Australia
#    M468/35 Stirling Hwy
#    Perth WA 6009
#    Australia
#
#    Copyright by UWA, 2018
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#

"""
Gathers information about git repositories
"""
import os
import re
import csv
import tarfile
import shutil
from subprocess import Popen
from argparse import ArgumentParser
from github import Github
from datetime import datetime, timedelta


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--token", required=True, help="Github Auth Token")
    parser.add_argument("--org_id", help="Specify an organisation to get repositories for")
    parser.add_argument("--older_than", default="", help="Specify a min age for the shown repositories")
    parser.add_argument("--archive", default=None, help="Archive the master branch of each repository to the specified archive file")
    parser.add_argument("--csv", default=None, help="Save a CSV of each matching repository to the specified CSV file")

    return vars(parser.parse_args())


def get_timedelta(line):
    timespaces = {"days": 0}
    for timeunit in "year month week day hour minute second".split():
        content = re.findall(r"([0-9]*?)\s*?" + timeunit, line)
        if content:
            timespaces[timeunit + "s"] = int(content[0])
    timespaces["days"] += 30 * timespaces.pop("months", 0) + 365 * timespaces.pop("years", 0)
    return timedelta(**timespaces)


def sort_key(repo):
    return max(repo.pushed_at, repo.updated_at)


def write_repo(repo, writer, now):
    writer.writerow({"Name": repo.full_name,
                     "Link": repo.html_url,
                     "Pushed At": repo.pushed_at,
                     "Days Since Push": (now - repo.pushed_at).days,
                     "Updated At": repo.updated_at,
                     "Days Since Update": (now - repo.updated_at).days})


def print_repo(repo, now):
    print("Name: {0}, Pushed: {1} days ago, Updated: {2} days ago".format(repo.full_name, (now - repo.pushed_at).days, (now - repo.updated_at).days))


def older_than(repos, now, period):
    for repo in repos:
        if now - sort_key(repo) > period:
            yield repo


def clone_repo(repo, path):
    # Clone the default branch from each repo into path
    full_path = os.path.join(path, repo.full_name)
    os.makedirs(full_path, exist_ok=True)
    return Popen('./clone.sh {0} {1}'.format(repo.html_url, full_path), shell=True)


def main():
    args = parse_args()

    github = Github(args["token"])
    user = github.get_user()

    org_id = args.get("org_id", None)
    if org_id is not None:
        repos = None
        for org in user.get_orgs():
            if org.login == org_id:
                repos = org.get_repos()
                break
        if repos is None:
            print("Organisation with ID {0} not found.".format(org_id))
            exit(1)
    else:
        repos = user.get_repos()

    period = get_timedelta(args["older_than"])
    now = datetime.now()
    repos = sorted(older_than(repos, now, period), key=sort_key)

    for repo in repos:
        print_repo(repo, now)

    csv_filename = args["csv"]
    if csv_filename is not None:
        with open(csv_filename, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["Name", "Link", "Pushed At", "Days Since Push", "Updated At", "Days Since Update"])
            writer.writeheader()
            for repo in repos:
                write_repo(repo, writer, now)

    archive = args["archive"]
    if archive is not None:
        tmp_dir = "/tmp/git_archive"
        try:
            os.makedirs(tmp_dir, exist_ok=True)
            # Clone all repos at concurrently
            for process in [clone_repo(repo, tmp_dir) for repo in repos]:
                process.wait()

            with tarfile.open(archive, "w:gz") as tf:
                tf.add(tmp_dir, arcname=os.path.basename(tmp_dir))
        finally:
            shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    main()