from main import Judge, Base, load_judges, Competition
import csv
from datetime import datetime
import pandas as pd
import tabulate
import json

class Judges:

    def __init__(self, judges: list = []):
        self.judge_array: list[Judge] = judges
        self.judge_id_lookup = {}
        self.judge_abbrv_lookup = {}

        self.update_lookups()
    
    def as_array(self):
        return self.judge_array
    
    def update_lookups(self):
        self.judge_id_lookup = {judge.judge_id: judge for judge in self.judge_array}
        self.judge_abbrv_lookup = {judge.abbreviation: judge for judge in self.judge_array}

    
    def get_judge_by_id(self, judge_id):
        return self.judge_id_lookup.get(judge_id)
    
    def get_judge_by_abbrv(self, abbrv):
        return self.judge_abbrv_lookup.get(abbrv)

    def add(self, judge: Judge):
        self.judge_array.append(judge)

    
    def to_list(self):
        return self.judge_array

    def __iter__(self):
        return iter(self.judge_array)

    @classmethod
    def from_csv(cls, file):
        with open(file) as judge_fh:
            judge_reader = csv.DictReader(judge_fh)
            judges = Judges()

            for row in judge_reader:
                judge = Judge(
                    judge_id=int(row["judge_id"]), 
                    name = row["name"].strip(),
                     competence= 0, 
                     is_special=False,
                     abbreviation=row["abbrv"].strip(), 
                     judge_type=row["type"].strip())
                judges.add(judge)

            judges.update_lookups()
        return judges
    
    
    def to_markdown(self):
        table = []
        for judge in self.judge_array:
            table.append([judge.judge_id, judge.name, judge.competence, judge.abbrv, judge.judge_type])
        
        return tabulate.tabulate(table, headers=["ID", "Name", "Competence", "Abbreviation", "Type"], tablefmt="pipe")


def load_ds_schedule(file, judges=None):
    # File is a csv file with some columns including a base ID, a start time and an end time
    output = []
    day_lookup = {
        0: datetime(2024, 7, 19),
        1: datetime(2024, 7, 20),
        2: datetime(2024, 7, 21)
    }    

    with open(file, "r") as schedule_fh:
        sched_reader = csv.DictReader(schedule_fh, delimiter="\t")

        for row in sched_reader:
            current_day = day_lookup[int(row["day"])]
            start_time = current_day.combine(current_day, datetime.strptime(row["start_time"], "%H:%M").time())
            end_time = current_day.combine(current_day, datetime.strptime(row["end_time"], "%H:%M").time())

            print_base = row["print_staff_doc"].strip().lower() == "true"

            new_base = Base(
                            internal_base_id=int(row["event_id"]),
                            external_base_id=int(row["test_id"]),
                            start_time=start_time,
                           end_time=end_time,
                           num_judges=0,
                           base_staff_description=row["description"],
                           base_name=row["name"],
                           base_location=row["location"],
                           print_staff_doc=print_base,
                           marks = 0,
                           test_id = int(row["test_id"]) if int(row["test_id"]) > 0 else None)
            
            if judges:
                this_base_judge_list = []

                if len(row["judges"]) > 0 and "/" not in row["judges"]:
                    for judge_abbrv in row["judges"].split(","):
                        if judge_abbrv.strip() == "All":
                            for judge in judges:
                                this_base_judge_list.append(judge)
                                judge.bases.append(new_base)
                        else:
                            judge = judges.get_judge_by_abbrv(judge_abbrv.strip())
                            if judge:
                                this_base_judge_list.append(judge)
                                judge.bases.append(new_base)
                            else:
                                print(f"No judge definition for {judge_abbrv} found in judges file. Skipping.")
                
                    new_base.judges = this_base_judge_list                
                

            output.append(new_base)

    return output


if __name__ == "__main__":
    judges = Judges.from_csv("ds_judges.csv")

    # print(judges.to_markdown())

    bases = load_ds_schedule("ds_sched.tsv", judges=judges)

    base_output = []

    for base in bases:
        base_output.append(base.as_dict())

    with open("temp_ds_sched.json", "w") as f:
        json.dump(base_output, f, indent=4)

    doc_shield: Competition = Competition(bases=bases, judges=judges.to_list())

    doc_shield.bases_to_json("temp_ds_sched.json")
    doc_shield.judges_to_json("temp_ds_judges.json")


    with open("nigel_bases.csv", "w") as nfh:
        for base in bases:
            for judge in base.judges:
                if not base.test_id:
                    print(f"Base {base.internal_id} has no test ID. Skipping.")
                else:
                    sanitized_base_id = str(base.test_id).rjust(2, "0")
                    nfh.write(f"{sanitized_base_id},{judge.judge_id}\n")

    daniel = judges.get_judge_by_abbrv("DL")
    tabl_output = []

    for base in daniel.printable_bases_iter():
        tabl_output.append([base.internal_id, base.start_time, base.end_time, base.base_location, base.base_name, base.test_id])
    print(tabulate.tabulate(tabl_output, headers=["ID", "Start Time", "End Time", "Location", "Name", "Test ID"], tablefmt="pipe"))
    # table_output = []
    # for base in bases:
    #     table_output.append([base.base_id, base.start_time, base.end_time, base.base_location, base.base_name, base.test_id])
    
    # print(tabulate.tabulate(table_output, headers=["ID", "Start Time", "End Time", "Location", "Name", "Test ID"], tablefmt="pipe"))



