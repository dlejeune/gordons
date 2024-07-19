import json

import typer
import pandas as pd
import random
# from rich import print
from datetime import datetime
from rich.progress import track
import numpy as np

# random.seed(42)

class Document:
    def __init__(self, name, base_id, amount, is_printed, size, colour, laminated, double_sided, notes):
        self.name = name
        self.base_id = base_id
        self.amount = amount
        self.is_printed = is_printed
        self.size = size
        self.colour = colour
        self.laminated = laminated
        self.double_sided = double_sided
        self.notes = notes


    def as_dict(self):
        return {"name": self.name,
                "base_id": self.base_id,
                "amount": self.amount,
                "is_printed": self.is_printed,
                "size": self.size,
                "colour": self.colour,
                "laminated": self.laminated,
                "double_sided": self.double_sided,
                "notes": self.notes}
class Equipment:
    def __init__(self, base_id, name, amount, e_type, have, notes):
        self.base_id = base_id
        self.name = name
        self.amount = amount
        self.e_type = e_type
        self.have = have
        self.notes = notes

    def as_dict(self):
        return {"name": self.name,
                "amount": self.amount,
                "e_type": self.e_type,
                "have": self.have,
                "base_id": self.base_id,
                "notes": self.notes}



class Base:
    def __init__(self,
                 internal_base_id, 
                 external_base_id,
                 start_time, 
                 end_time, 
                 num_judges, 
                 base_name="", 
                 base_staff_description ="", 
                 base_scout_description="", 
                 base_location="", 
                 base_type="", 
                 marks="", 
                 test_id=None,
                 print_staff_doc=True):
        # self.base_id = base_id
        self.internal_id = internal_base_id
        self.external_id = external_base_id
        self.base_name = base_name
        self.start_time: datetime = start_time
        self.base_staff_description = base_staff_description
        self.base_scout_description = base_scout_description
        self.base_location = base_location
        self.base_type = base_type
        self.end_time = end_time
        self.marks = marks
        self.required_judges = num_judges
        self.judges = []
        self.equipment = []
        self.documents = []
        self.test_id = test_id
        self.print_staff_doc = print_staff_doc


    def convert_all_times(self):
        self.start_time = datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
        self.end_time = datetime.strptime(self.end_time, "%Y-%m-%d %H:%M:%S")

    def get_other_judges(self, judge):
        return_judges = []

        for base_judge in self.judges:
            if judge.judge_id != base_judge.judge_id:
                return_judges.append(base_judge)

        return return_judges

    def get_equipment(self, e_type="ALL"):
        if e_type == "ALL":
            return self.equipment
        else:
            return [e for e in self.equipment if e.e_type == e_type]

    def get_documents(self):
        return self.documents

    def is_full(self):
        return len(self.judges) == self.required_judges-100

    def get_judge_code(self):
        return self.required_judges


    def as_dict(self):
        return {"internal_base_id": self.internal_id,
                "external_base_id": self.external_id,
                "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": self.end_time.strftime("%Y-%m-%d %H:%M:%S"),

                "base_name": self.base_name,

                "base_staff_description": self.base_staff_description,
                "base_scout_description": self.base_scout_description,
                "base_location": self.base_location,
                "base_type": self.base_type,
                "marks": self.marks,
                "test_id":self.test_id,
                "print_staff_doc":self.print_staff_doc,
                "num_judges": self.required_judges,
                "judges": [judge.judge_id for judge in sorted(self.judges)],
                "equipment": [e.as_dict() for e in self.equipment],
                "documents": [d.as_dict() for d in self.documents]
                }


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def add_judges(self, judges):
        for judge in judges:
            self.add_judge(judge)

    def add_judge(self, judge):
        self.judges.append(judge)

    def add_document(self, document):
        self.documents.append(document)
    def __repr__(self):
        return f"Base {self.internal_id} from {self.start_time} to {self.end_time}"

    def __lt__(self, other):
        return self.start_time < other.start_time

    def __eq__(self, other):
        return self.internal_id == other.internal_id

    def __hash__(self):
        return hash(self.internal_id)

    def __gt__(self, other):
        return self.start_time > other.start_time

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class Judge:
    day1 = datetime(2023, 9, 16)
    day2 = datetime(2023, 9, 17)
    def __init__(self, judge_id, name, competence, is_special=False, abbreviation="", judge_type=None):
        self.judge_id = judge_id
        self.name = name
        self.competence = competence
        self.is_special = is_special
        self.abbreviation = abbreviation
        self.judge_type = judge_type
        self.bases: list[Base] = []
        self.abbreviation = abbreviation

    def add_base(self, base):
        self.bases.append(base)
    def is_judge_busy_at_time(self, time):
        for base in self.bases:
            if base.start_time <= time < base.end_time:
                return True
        return False

    def get_day_bases(self, day):
        return_bases = []
        for base in self.bases:
            if day == 1 and base.start_time.date() == self.day1:
                return_bases.append(base)
            elif day == 2 and  base.start_time.date() == self.day2:
                return_bases.append(base)

        return return_bases

    def printable_bases_iter(self):
        for base in self.bases:
            if base.print_staff_doc:
                yield base
            else:
                continue

    def as_dict(self):
        return {"judge_id": self.judge_id,
                "name": self.name,
                "competence": self.competence,
                "is_special": self.is_special,
                "abbreviation": self.abbreviation,
                "judge_type": self.judge_type,
                "bases": [base.internal_id for base in self.bases]}

    def __gt__(self, other):
        return self.name > other.name

    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return f"Judge {self.name} with ID {self.judge_id}"


class StaffTeam:
    def __init__(self, id, name, staff_ids = []):
        self.id = id
        self.name = name
        self.staff_ids = staff_ids






class Competition:
    JUDGE_TEAM_CODE = 800
    RANDOM_STAFF = 100
    SPECIFIC_STAFF = 900

    def __init__(self, bases=[], judges=[]):
        self.bases = bases
        self.judges = judges
        self.teams = []

    def set_bases(self, bases):
        self.bases = bases

    def set_judges(self, judges):
        self.judges = judges

    def get_num_special_judges(self):
        return len([judge for judge in self.judges if judge.is_special])

    def load_judge_teams(self, input_file):
        with open(input_file, "r") as fh:
            team_json = json.load(fh)

            for team in team_json:
                temp_team = StaffTeam(**team)
                self.teams.append(temp_team)

    def get_team_judges(self, team_id):
        team = None

        for team_i in self.teams:
            if team_i.id == team_id:
                team = team_i
                break
        judges = [self.get_judge(x) for x in team.staff_ids]

        return judges


    def get_base(self, id):
        for base in self.bases:
            if base.internal_id == id:
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

    def assign_equipment_to_bases(self, equipment_file):
        equip = pd.read_csv(equipment_file)

        for i, row in equip.iterrows():
            base = self.get_base(row["UID"])
            if base is not None:
                base.equipment.append(Equipment(row["UID"],row["Item"], row["Quantity"], row["Type"], row["Have"], row["Notes"]))

    def assign_documents_to_bases(self, documents_file):
        docs = pd.read_csv(documents_file)

        for i, row in docs.iterrows():
            base = self.get_base(row["UID"])
            if base is not None:
                base.documents.append(
                    Document(row["Document"], row["UID"], row["Quantity"], "", row["Size"], row["Colour"],
                             row["Laminated"], row["Double-Sided"], ""))


    def load_descriptions_from_csv(self, file):
        description_df = pd.read_csv(file)

        for i, row in description_df.iterrows():
            temp_base: Base = self.get_base(row["UID"])
            temp_base.base_scout_description = row["Scout Instructions"]
            temp_base.base_staff_description = row["Base Instructions"]

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

    def get_judges_with_competence(self, competency):
        subset = []

        for judge in self.judges:

            if judge.competence == competency and not judge.is_special:
                subset.append(judge)

        return subset


    def load_from_csv(self, bases_csv, judges_csv):


        # File is a csv file with some columns including a base ID, a start time and an end time
        bases = []
        day0 = datetime(2023, 9, 15)
        day1 = datetime(2023, 9, 16)
        day2 = datetime(2023, 9, 17)

        base_df = pd.read_csv(bases_csv)

        for i, row in base_df.iterrows():

            if row["Day"] == 1:
                start_time = day1.combine(day1, datetime.strptime(row["Start Time"], "%H:%M").time())

                end_time = day1.combine(day1, datetime.strptime(row["End Time"], "%H:%M").time())

            elif row["Day"] == 2:
                start_time = day1.combine(day2, datetime.strptime(row["Start Time"], "%H:%M").time())

                end_time = day1.combine(day2, datetime.strptime(row["End Time"], "%H:%M").time())
            elif row["Day"] == 0:
                start_time = day1.combine(day0, datetime.strptime(row["Start Time"], "%H:%M").time())

                end_time = day1.combine(day0, datetime.strptime(row["End Time"], "%H:%M").time())

            bases.append(Base(internal_base_id=row["UID"],
                              external_base_id=row["Event ID"],
                               start_time=start_time,
                               end_time=end_time,
                               num_judges=int(row["Staff Required"]),
                               base_name=row["Event"],
                               base_scout_description="",
                              base_staff_description="",
                               base_location=row["Location"],
                               base_type=row["Type"],
                               marks=row["Mark"]))

        self.bases = bases

        judges = []

        judges_df = pd.read_csv(judges_csv)

        for i, row in judges_df.iterrows():
            if row["Attending"]:
                judges.append(Judge(row["Judge ID"], row["Full Name"], row["Score"], row["Special Staff"], row["Abbriviation"]))

        self.judges = judges


    def judge_allocation_to_csv(self):
        with open("judge_allocation_generated.csv", "w") as fh:
            for base in self.bases:
                for judge in base.judges:
                    fh.write(f"{base.external_id},{judge.judge_id}\n")




    def assign_judges_to_bases(self):
        failures = 0
        for base in self.bases:

            competency = 1
            print(f"Working on base {base.internal_id}")
            total_attempts = []

            if base.get_judge_code() < 200:

                required_judges = base.get_judge_code() - 100

                while not (required_judges == len(base.judges)) and len(np.unique(total_attempts)) < len(self.judges)-self.get_num_special_judges():

                    judges_with_competence = self.get_judges_with_competence(competency)
                    random.shuffle(judges_with_competence)
                    judge = judges_with_competence[0]

                    # print(f"Trying to assign judge {judge.name} with competency {competency} to base {base.base_id}")
                    total_attempts.append(judge.judge_id)

                    while judge.is_judge_busy_at_time(base.start_time) and len(np.unique(total_attempts)) < len(
                            self.judges):

                        # print(f"Judge {judge.name} is busy at {base.start_time}")
                        judges_with_competence.remove(judge)
                        if len(judges_with_competence) == 0:
                            competency = competency + 1 if competency < 5 else 1

                            # print(f"No more judges with competency {competency} available. Changed competency to {competency}")

                            judges_with_competence = self.get_judges_with_competence(competency)
                            random.shuffle(judges_with_competence)

                        judge = judges_with_competence[0]
                        total_attempts.append(judge.judge_id)
                        # print(f"Trying to assign judge {judge.name} with competency {competency} to base {base.base_id}")

                    if len(np.unique(total_attempts)) < len(self.judges)-self.get_num_special_judges():
                        base.judges.append(judge)
                        judge.bases.append(base)
                        competency += 1
                        if competency > 5:
                            competency = 1
                    else:
                        print(f"Could not assign judge to base {base.internal_id}")
                        failures += 1
                        break


            elif base.get_judge_code() > self.JUDGE_TEAM_CODE and base.get_judge_code() < self.SPECIFIC_STAFF:
                for judge in self.get_team_judges(base.get_judge_code()):
                    base.add_judge(judge)
                    judge.add_base(base)

            elif base.get_judge_code() >= 900:
                judge = self.get_judge(base.get_judge_code() - self.SPECIFIC_STAFF)
                base.add_judge(judge)
                judge.add_base(base)

            elif  base.get_judge_code() == 800:
                for judge in self.judges:
                    base.add_judge(judge)
                    judge.add_base(base)


        print(failures)


def load_schedule(file):
    # File is a csv file with some columns including a base ID, a start time and an end time
    output = []
    day0 = datetime(2023, 9, 15)
    day1 = datetime(2023, 9, 16)
    day2 = datetime(2023, 9, 17)

    base_df = pd.read_csv(file)

    for i, row in base_df.iterrows():
        if row["Day"] == 1:
            start_time = day1.combine(day1, datetime.strptime(row["Start Time"], "%H:%M").time())

            end_time = day1.combine(day1, datetime.strptime(row["End Time"], "%H:%M").time())

        elif row["Day"] == 2:
            start_time = day1.combine(day2, datetime.strptime(row["Start Time"], "%H:%M").time())

            end_time = day1.combine(day2, datetime.strptime(row["End Time"], "%H:%M").time())
        elif row["Day"] == 0:
            start_time = day1.combine(day0, datetime.strptime(row["Start Time"], "%H:%M").time())

            end_time = day1.combine(day0, datetime.strptime(row["End Time"], "%H:%M").time())

        output.append(Base(row["Event ID"],
                           start_time,
                           end_time,
                           int(row["Staff Required"]),
                           row["Event"],
                           "",
                           "",
                           row["Location"],
                           row["Type"],
                           row["Mark"]))

    return output




def get_random_id():
    return random.randint(1000, 9999)

def load_judges(file):
    judges = []

    judges_df = pd.read_csv(file)

    for i, row in judges_df.iterrows():
        if row["Attending"]:
            judges.append(Judge(row["Judge ID"], row["Full Name"], row["Score"], row["Special Staff"]))

    return judges



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
                            judge["abbreviation"],
                            judge["competence"]))


    for base in base_json:
        temp_base = Base(base["internal_base_id"],
                         base["external_base_id"],
                          datetime.strptime(base["start_time"], "%Y-%m-%d %H:%M:%S"),
                          datetime.strptime(base["end_time"], "%Y-%m-%d %H:%M:%S"),
                          base["num_judges"],
                          base["base_name"],
                          base["base_staff_description"],
                         base["base_scout_description"],
                          base["base_location"],
                          base["base_type"],
                          base["marks"],
                          base["test_id"],
                          base["print_staff_doc"])

        if "equipment" in base.keys():
            for equipment in base["equipment"]:
                temp_base.equipment.append(Equipment(**equipment))

        if "documents" in base.keys():
            for document in base["documents"]:
                temp_base.documents.append(Document(**document))

        for judge_id in base["judges"]:
            temp_judge = gordons.get_judge(judge_id)
            temp_base.add_judge(temp_judge)
            temp_judge.bases.append(temp_base)




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

    gordons = Competition()
    gordons.load_from_csv("events.csv", "judges.csv")


    # gordons = load_full_schedule_from_json("test_bases.json", "test_judges.json")


    gordons.load_judge_teams("judging_teams.json")

    gordons.load_descriptions_from_csv("descriptions.csv")

    gordons.assign_documents_to_bases("documents.csv")
    gordons.assign_equipment_to_bases("equipment.csv")

    gordons.assign_judges_to_bases()

    gordons.judge_allocation_to_csv()


    #
    gordons.bases_to_json("final_bases.json")
    #
    gordons.judges_to_json("final_judges.json")


    #
    # gordons.bases_to_json("bases_allocated.json")
    #
    # gordons.judges_to_json("judges_allocated.json")

if __name__ == "__main__":
    typer.run(main)