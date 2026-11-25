import yaml
import pandas as pd
import json


class Validate():
    def __init__(self):
        self.config = "./config.yaml"
        self.colleges = "./colleges.json"
        try:
            with open(self.config) as file:
                self.config_data = yaml.safe_load(file)
            self.gpa = float(self.config_data["applicant"]["gpa"])
            self.sat = float(self.config_data["applicant"]["sat"])
            self.essay = float(self.config_data["applicant"]["essay"])
            self.ecs = float(self.config_data["applicant"]["ecs"])
            self.rec = float(self.config_data["applicant"]["rec"])
            self.awards = float(self.config_data["applicant"]["awards"])
        except TypeError as error:
            raise(error, "This is an issue with your data, fix config.yaml")
        try:
            self.college_df = pd.read_json(self.colleges).T.reset_index(names="name")
        except:
            raise SyntaxError("Make Sure JSON File exists and Syntax is correct")
              
    def run(self):
        self.convert()
        print("All data seems fine now")
        return self.gpa, self.sat, self.essay, self.ecs, self.rec, self.awards, self.college_df

    def convert(self):
        if self.gpa > 1:
            print("Converting GPA to 1.0 Scale")
            self.gpa = (self.gpa - 2.5 )/ 1.5
        if self.sat > 1:
            print("Converting SAT to 1.0 Scale")
            self.sat = (self.sat - 1000) / 600
        verification = (self.essay, self.rec, self.awards, self.ecs) 
        if any(v > 1 for v in verification):
            raise ValueError("Your config.yaml applicant infromation is wrong, everything except gpa and SAT must be out of 1")
        # DF Converting
        if (self.college_df["min_gpa"] > 1).any():
            self.college_df["min_gpa"] =  self.college_df["min_gpa"] / 4 
            print("Converting MIN GPA to 1.0 Scale")

        print("Converting MIN SAT to 1.0 Scale")
        i = 0
        for row in self.college_df["min_sat"]:
            if row > 1:
                self.college_df.loc[i, "min_sat"] = (row - 400) / 1200
            i+=1


def main():
    _Validate = Validate()
    _Validate.run()


if __name__ == "__main__":
    main()
