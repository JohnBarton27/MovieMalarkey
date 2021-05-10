import argparse
import os
import subprocess
from os.path import expanduser

parser = argparse.ArgumentParser(description="Runs SonarQube analysis for Movie Malarkey")
parser.add_argument("branch_name", help="Git branch being analyzed")

args = parser.parse_args()
branch = args.branch_name

if branch.startswith("origin/"):
    branch = branch.split("origin/")[-1]

coverage_location = os.path.join(expanduser("~"), ".local/bin/coverage")

# Run Tests (for Coverage report)
coverage_cmd = "{} run --source=. scripts/run_tests.py".format(coverage_location)
coverage_proc = subprocess.Popen(coverage_cmd.split(" "), shell=False)
coverage_proc.communicate()

coverage_xml_cmd = "{} xml".format(coverage_location)
coverage_xml_proc = subprocess.Popen(coverage_xml_cmd.split(" "), shell=False)
coverage_xml_proc.communicate()

options = {
    "sonar.projectKey": "MovieMalarkey",
    "sonar.organization": "johnbarton27",
    "sonar.host.url": "https://sonarcloud.io",
    "sonar.branch.name": branch,
    "sonar.tests": "test",
    "sonar.sources": ['src'],
    "sonar.exclusions": ["scripts/"],
    "sonar.python.coverage.reportPaths": "coverage.xml"
}

sonar_scanner_location = "/opt/sonar-scanner/current/bin/sonar-scanner"
command = "{} ".format(sonar_scanner_location)

for option in options:
    if isinstance(options[option], list):
        options[option] = ",".join(options[option])
    command += "-D{0}={1} ".format(option, options[option])

command = command.strip()
print(command)
proc = subprocess.Popen(command, shell=True)
proc.communicate()
