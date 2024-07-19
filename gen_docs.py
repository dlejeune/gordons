import subprocess

from main import Base, Judge, Competition, load_full_schedule_from_json
import typer
import json
from jinja2 import Template
import jinja2
import os

app = typer.Typer()

def load_judges(file):
    with open(file) as fh:
        judges = json.load(fh)


    judge_objs = []

    for judge in judges:
        judge_objs.append(Judge(judge["judge_id"], judge["name"], judge["competence"]))

    return judge_objs


def latex_sanitize(text):
    return text.replace("&", "\\&").replace("#", "num")

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

    template = latex_jinja_env.get_template('bse_template_2.tex')
    latex_jinja_env.globals.update(sanitize=latex_sanitize)

    with open("base_docs.tex", "w", encoding="utf-8") as fh:
        fh.write(template.render(bases=bases))

    subprocess.run(["xelatex", "base_docs.tex", "--output-directory", "tmp/"], shell=True)


def generate_judge_docs(judges):
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

    template = latex_jinja_env.get_template('judge_template.tex')
    latex_jinja_env.globals.update(sanitize=latex_sanitize)

    specific_judges = [i for i in range(1, 25)]

    for judge in judges:

        if judge.judge_id in specific_judges:
            filename = f"judge_{judge.name}.tex"

            new_judges = [judge,]

            with open(filename, "w") as fh:
                fh.write(template.render(judges=new_judges))

            subprocess.run(["xelatex", filename, "--output-directory", "tmp/", "-interaction=nonstopmode"], shell=True)

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

    comp = load_full_schedule_from_json("temp_ds_sched.json", "temp_ds_judges.json")
    #generate_base_docs(comp.bases)

    generate_judge_docs(comp.judges)
    pass


if __name__ == "__main__":
    typer.run(main)