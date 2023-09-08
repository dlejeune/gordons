import json

import typer
import pandas as pd
import random
# from rich import print
from datetime import datetime
from rich.progress import track
import numpy as np

random.seed(42)

class Competition:

    def __init__(self, bases=[], judges=[]):
        self.bases = bases
        self.judges = judges

    def set_bases(self, bases):
        self.bases = bases

    def set_judges(self, judges):
        self.judges = judges


    def get_base(self, id):
        for base in self.bases:
            if base.base_id == id:
                return base
        return None

    def get_judge(self, id):
        for judge in self.judges:
            if judge.judge_id == id:
                return judge
        return None

    def add_base(self, base):
        self.bases.append(base)

    def add_judge(self, judge):
        self.judges.append(judge)

    def bases_to_json(self, output_file):
        base_output = []

        for base in self.bases:
            base_output.append(base.as_dict())
        with open(output_file, "w") as f:
            json.dump(base_output, f, indent=4)

    def judges_to_json(self, output_file):
        judge_output = []

        for judge in self.judges:
            judge_output.append(judge.as_dict())

        with open(output_file, "w") as f:
            json.dump(judge_output, f, indent=4)


class Base:
    def __init__(self, base_id,
                 start_time, end_time, num_judges, base_name="", base_description = "", base_location="", base_type="", marks=""):
        self.base_id = base_id
        self.base_name = base_name
        self.start_time = start_time
        self.base_description = base_description
        self.base_location = base_location
        self.base_type = base_type
        self.end_time = end_time
        self.marks = marks
        self.required_judges = num_judges
        self.judges = []
        self.equipment = []


    def convert_all_times(self):
        self.start_time = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
        self.end_time = datetime.strptime(self.end_time, "%Y-%m-%d %H:%M:%S")

    def is_full(self):
        return len(self.judges) == self.required_judges


    def as_dict(self):
        return {"base_id": self.base_id,
                "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": self.end_time.strftime("%Y-%m-%d %H:%M:%S"),

                "base_name": self.base_name,

                "base_description": self.base_description,
                "base_location": self.base_location,
                "base_type": self.base_type,
                "marks": self.marks,


                "num_judges": self.required_judges,
                "judges": [judge.judge_id for judge in self.judges]}


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def add_judges(self, judges):
        for judge in judges:
            self.add_judge(judge)

    def add_judge(self, judge):
        self.judges.append(judge)

    def __repr__(self):
        return f"Base {self.base_id} from {self.start_time} to {self.end_time}"

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Judge:
    def __init__(self, judge_id, name, competence):
        self.judge_id = judge_id
        self.name = name
        self.competence = competence
        self.bases = []

    def is_judge_busy_at_time(self, time):
        for base in self.bases:
            if base.start_time <= time < base.end_time:
                return True
        return False


    def as_dict(self):
        return {"judge_id": self.judge_id,
                "name": self.name,
                "competence": self.competence,
                "bases": [base.base_id for base in self.bases]}

    def __gt__(self, other):
        return self.judge_id > other.judge_id

    def __lt__(self, other):
        return self.judge_id < other.judge_id

    def __repr__(self):
        return f"Judge {self.name} with ID {self.judge_id}"

def load_schedule(file):
    # File is a csv file with some columns including a base ID, a start time and an end time
    output = []
    day1 = datetime(2023, 9, 16)
    day2 = datetime(2023, 9, 17)

    base_df = pd.read_csv(file)

    for i, row in base_df.iterrows():
        if row["Day"] == 1:
            start_time = day1.combine(day1, datetime.strptime(row["Start Time"], "%H:%M").time())

            end_time = day1.combine(day1, datetime.strptime(row["End Time"], "%H:%M").time())

        else:
            start_time = day1.combine(day2, datetime.strptime(row["Start Time"], "%H:%M").time())

            end_time = day1.combine(day2, datetime.strptime(row["End Time"], "%H:%M").time())

        output.append(Base(row["Test ID"],
                           start_time,
                           end_time,
                           int(row["Staff Required"]),
                           row["Short Description"],
                           row["Long Description"],
                           row["Location"],
                           row["Type"],
                           row["Marks"]))

    return output




def get_random_id():
    return random.randint(1000, 9999)

def load_judges(file):
    judges = []
    with open(file) as f:

        for line in f:
            split_line = line.strip().split(",")
            if split_line[0] == "Name":
                pass
            else:
                judges.append(Judge(int(split_line[6]), split_line[0], int(split_line[5])))

    return judges

    pass


def get_judges_with_competence(judges, competency):
    subset = []

    for judge in judges:

        if judge.competence == competency:
            subset.append(judge)

    return subset

def assign_judges_to_bases(judges, bases):
    failures = 0
    for base in track(bases, description="Assigning judges to bases"):

        competency = 1
        print(f"Working on base {base.base_id}")
        total_attempts = []

        while not base.is_full() and len(np.unique(total_attempts)) < len(judges):

            judges_with_competence = get_judges_with_competence(judges, competency)
            random.shuffle(judges_with_competence)
            judge = judges_with_competence[0]
            num_with_competency = len(judges_with_competence)

            counter = 1

            # print(f"Trying to assign judge {judge.name} with competency {competency} to base {base.base_id}")
            total_attempts.append(judge.judge_id)

            while judge.is_judge_busy_at_time(base.start_time) and len(np.unique(total_attempts)) < len(judges):

                # print(f"Judge {judge.name} is busy at {base.start_time}")
                judges_with_competence.remove(judge)
                if len(judges_with_competence) == 0:

                    competency = competency + 1 if competency < 5 else 1

                    #print(f"No more judges with competency {competency} available. Changed competency to {competency}")

                    judges_with_competence = get_judges_with_competence(judges, competency)
                    random.shuffle(judges_with_competence)

                judge = judges_with_competence[0]
                total_attempts.append(judge.judge_id)
                #print(f"Trying to assign judge {judge.name} with competency {competency} to base {base.base_id}")

            if len(np.unique(total_attempts)) < len(judges):
                base.judges.append(judge)
                judge.bases.append(base)
                competency +=1
                if competency > 5:
                    competency = 1
            else:
                print(f"Could not assign judge to base {base.base_id}")
                failures +=1
    print(failures)
    return bases, judges

def allocation_to_csv(bases):
    with open("output.csv", "w") as f:
        f.write("Base ID, Judges, Median Competency,AverageCompetency,Num\n")
        for base in bases:
            judge_string = "-".join([str(judge.judge_id) for judge in sorted(base.judges)])

            comps = [judge.competence for judge in base.judges]

            f.write(f"{base.base_id}, {judge_string}, {np.median(comps)}, {np.mean(comps)}, {len(base.judges)}\n")

def bases_to_json(bases, output_file):
    base_output = []

    for base in bases:
        base_output.append(base.as_dict())
    with open(output_file, "w") as f:
        json.dump(base_output, f, indent=4)


def judges_to_json(judges, output_file):
    judge_output = []

    for judge in judges:
        judge_output.append(judge.as_dict())

    with open(output_file, "w") as f:
        json.dump(judge_output, f, indent=4)


def load_full_schedule_from_json(base_file, judge_file):



    base_json = json.load(open(base_file))
    judge_json = json.load(open(judge_file))

    gordons = Competition()

    for judge in judge_json:
        gordons.add_judge(Judge(judge["judge_id"],
                            judge["name"],
                            judge["competence"]))


    for base in base_json:
        temp_base = Base(base["base_id"],
                          datetime.strptime(base["start_time"], "%Y-%m-%d %H:%M:%S"),
                          datetime.strptime(base["end_time"], "%Y-%m-%d %H:%M:%S"),
                          base["num_judges"],
                          base["base_name"],
                          base["base_description"],
                          base["base_location"],
                          base["base_type"],
                          base["marks"])

        for judge_id in base["judges"]:
            temp_base.add_judge(gordons.get_judge(judge_id))

        gordons.add_base(temp_base)



    return gordons


def export_all_info(bases, judges):
    base_json = [base.as_dict() for base in bases]

    judge_json = [judge.as_dict() for judge in judges]


    with open("bases.json", "w") as f:
        json.dump(base_json, f)

    with open("judges.json", "w") as f:
        json.dump(judge_json, f)


def main():
    # print(load_schedule("bases.csv"))
    # print(load_judges("judges.csv"))
    # print("")
    #
    # allocations = assign_judges_to_bases(load_judges("judges.csv"), load_schedule("bases.csv"))
    # allocation_to_csv(allocations[0])
    # export_all_info(allocations[0], allocations[1])

    # bases = load_schedule("bases.csv")
    # bases_to_json(bases, "bases.json")

    # judges = load_judges("judges.csv")
    # judges_to_json(judges, "judges.json")

    gordons = load_full_schedule_from_json("bases.json", "judges.json")

    gordons.set_bases(assign_judges_to_bases(gordons.judges, gordons.bases)[0])

    gordons.bases_to_json("bases_allocated.json")
    gordons.judges_to_json("judges_allocated.json")

if __name__ == "__main__":
    typer.run(main)