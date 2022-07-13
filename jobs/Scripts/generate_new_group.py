import csv
from argparse import ArgumentParser
from argparse import BooleanOptionalAction
import json
import os
from string import Template

parser = ArgumentParser()
parser.add_argument("-f", "--file",
                    help="Filename in CSV format", required=True)
parser.add_argument("-t", "--timeout",
                    help="Group timeout", default=3600)
parser.add_argument("-u", "--update", action=BooleanOptionalAction,
                    help="Scenes location")
args = parser.parse_args()

test_cases_file = os.path.join(os.getcwd(), "..", "Tests", args.file.split('.')[0], "test_cases.json")
config_file = os.path.join(os.getcwd(), "..", "Tests", args.file.split('.')[0], "test.job-manifest.xml")
config_template_file = os.path.join(os.getcwd(), "templates", "test.job-manifest.xml")

existing_cases = []
existing_cases_ids = []

if (args.update and os.path.exists(test_cases_file) and os.path.exists(config_file)):
    with open(test_cases_file, "r", encoding="utf8") as existing_cases:
        existing_cases = json.load(existing_cases)
        existing_cases_ids = list(map(lambda case: case["case"], existing_cases))
else:
    os.makedirs(os.path.dirname(test_cases_file), exist_ok=True)
    os.makedirs(os.path.dirname(config_file), exist_ok=True)

with open(config_file, "w", encoding="utf8") as f1, open(test_cases_file, "w", encoding="utf8") as f2, \
            open(config_template_file, "r", encoding="utf8") as temp_file, open(args.file, newline='', encoding="utf8") as csvfile:
    template = Template(temp_file.read())
    template_parameters = {
        "timeout" : "\"" + str(args.timeout) + "\"",
        "group" : args.file.split('.')[0]
    }
    f1.write(template.substitute(template_parameters))

    reader = csv.DictReader(csvfile)
    test_cases = []
    for row in reader:
        if not (args.update and row["Test Case ID"] in existing_cases_ids):
            test_cases.append({
                "case" : row["Test Case ID"],
                "status" : "active",
                "functions" : ["rpr_render(case)"],
                "script_info" : [row["Case Description"]],
                "scene" : row["Scene Name"]
            })
    if args.update:
        existing_cases.extend(test_cases)
        json.dump(existing_cases, f2, ensure_ascii=False, indent=4)
    else:
        json.dump(test_cases, f2, ensure_ascii=False, indent=4)
