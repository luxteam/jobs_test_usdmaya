import csv
from argparse import ArgumentParser
import json
import os
from string import Template

parser = ArgumentParser()
parser.add_argument("-f", "--file",
                    help="Filename in CSV format", required=True)
parser.add_argument("-t", "--timeout",
                    help="Group timeout", default=3600)
parser.add_argument("-sf", "--scenes_folder",
                    help="Scenes location", required=True)
args = parser.parse_args()

test_cases_file = os.path.join(os.getcwd(), "..", "Tests", args.file.split('.')[0], "test_cases.json")
config_file = os.path.join(os.getcwd(), "..", "Tests", args.file.split('.')[0], "test.job-manifest.xml")
config_template_file = os.path.join(os.getcwd(), "templates", "test.job-manifest.xml")

os.makedirs(os.path.dirname(test_cases_file), exist_ok=True)
os.makedirs(os.path.dirname(config_file), exist_ok=True)

with open(config_file, "w") as f1, open(test_cases_file, "w") as f2, \
            open(config_template_file, "r") as temp_file, open(args.file, newline='', encoding="utf8") as csvfile:
    template = Template(temp_file.read())
    template_parameters = {
        "timeout" : "\"" + str(args.timeout) + "\"",
        "group" : args.file.split('.')[0],
        "scenes_folder" : str(args.scenes_folder)
    }
    f1.write(template.substitute(template_parameters))

    reader = csv.DictReader(csvfile)
    test_cases = []
    for row in reader:
        test_cases.append({
            "case" : row["Test Case ID"],
            "status" : "active",
            "functions" : ["rpr_render(case)"],
            "script_info" : [row["Case Description"]],
            "scene" : row["Scene Name"]
        })
    json.dump(test_cases, f2, ensure_ascii=False, indent=4)
