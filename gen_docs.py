import subprocess

from main import Base, Judge
import typer
import json
from jinja2 import Template
import jinja2
import os

def load_judges(file):
    with open(file) as fh:
        judges = json.load(fh)


    judge_objs = []

    for judge in judges:
        judge_objs.append(Judge(judge["judge_id"], judge["name"], judge["competence"]))

    return judge_objs


def latex_sanitize(text):
    return text.replace("&", "\\&")

def generate_base_docs(bases):
    latex_jinja_env = jinja2.Environment(
        block_start_string='\BLOCK{',
        block_end_string='}',
        variable_start_string='\VAR{',
        variable_end_string='}',
        comment_start_string='\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader("templates/")
    )

    template = latex_jinja_env.get_template('bse_template.tex')
    latex_jinja_env.globals.update(sanitize=latex_sanitize)

    with open("base_docs.tex", "w") as fh:
        fh.write(template.render(bases=bases))

    subprocess.run(["xelatex", "base_docs.tex", "--output-directory", "tmp/"], shell=True)



def load_bases(file):
    with open(file) as fh:
        bases = json.load(fh)

    base_objs = []

    for base in bases:
        temp_base = Base(base["base_id"], base["start_time"], base["end_time"], base["required_judges"])

        for judge in base["judges"]:
            temp_judge = Judge(judge["judge_id"], judge["name"], judge["competence"])

            for base in judge["bases"]:
                temp_judge.bases.append(int(base))

            temp_base.judges.append(temp_judge)

        base_objs.append(temp_base)


    [base.convert_all_times() for base in base_objs]

    return base_objs



def main():
    generate_base_docs(load_bases("bases.json"))
    pass


if __name__ == "__main__":
    typer.run(main)