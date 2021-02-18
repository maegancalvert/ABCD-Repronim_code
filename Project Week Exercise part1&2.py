import pandas as pd # to read/manipulate/write data from files
import numpy as np # to manipulate data/generate random numbers
# import plotly.express as px # interactive visualizations
# import seaborn as sns # static visualizations
import matplotlib.pyplot as plt # fine tune control over visualizations

from pathlib import Path # represent and interact with directories/folders in the operating system
from collections import namedtuple # structure data in an easy to consume way

import requests # retrieve data from an online source

# save directory we downloaded the ABCD data to `data_path`
data_path = Path("/home/mcalvert/ABCD3")
# glob (match) all text files in the `data_path` directory
files = sorted(data_path.glob("*.txt"))

data_elements = []
data_structures = {}
event_names = set()
StructureInfo = namedtuple("StructureInfo", field_names=["description", "eventnames"])

for text_file in files:
    # Extract data structure from filename
    data_structure = Path(text_file).name.split('.txt')[0]

    # Read the data structure and capture all the elements from the file
    # Note this could have been done using the data returned from the NDA API
    # We are using pandas to read both the first and second rows of the file as the header
    # Note: by convention dataframe variables contain `df` in the name.
    data_structure_df = pd.read_csv(text_file, header=[0, 1], nrows=0)
    for data_element, metadata in data_structure_df.columns.values.tolist():
        data_elements.append([data_element, metadata, data_structure])

    # (Optional) Retrieve the eventnames in each structure. Some structures were only collected
    # at baseline while others were collected at specific or multiple timepoints
    events_in_structure = None
    if any(['eventname' == data_element for data_element in data_structure_df.columns.levels[0]]):
        # Here we are skipping the 2nd row of the file containing description using skiprows
        possible_event_names_df = pd.read_csv(text_file, skiprows=[1], usecols=['eventname'])
        events_in_structure = possible_event_names_df.eventname.unique().tolist()
        event_names.update(events_in_structure)

    # (Optional) Retrieve the title for the structure using the NDA API
    rinfo = requests.get(f"https://nda.nih.gov/api/datadictionary/datastructure/{data_structure}").json()
    data_structures[data_structure] = StructureInfo(description=rinfo["title"] if "title" in rinfo else None,
                                                    eventnames=events_in_structure)

# Convert to a Pandas dataframe
data_elements_df = pd.DataFrame(data_elements, columns=["element", "description", "structure"])
#print(data_elements_df.head())
data_elements_df.to_csv("data_elements.tsv", sep="\t", index=None)
# print(data_elements_df.shape)
# print(len(data_structures))
# print(event_names)
# print(data_elements_df.element.unique().shape)
# print(data_elements_df.query("element == 'smri_vol_scs_amygdalalh'"))

structure = 'abcd_mri01'  # 'abcd_psb01'
example_structure_df = pd.read_csv(data_path / f"{structure}.txt", header=[0, 1], nrows=0)
#print(example_structure_df.columns.tolist())

NOEVENTS = {}
for data_structure, info in data_structures.items():
    if info.eventnames:
        if 'baseline_year_1_arm_1' in info.eventnames:
            print(f"{data_structure}: {info.description}")
    else:
        NOEVENTS[data_structure] = info

# for data_structure, info in NOEVENTS.items():
    # print(f"{data_structure}: {info.description}")

common = ["subjectkey", "interview_date", "interview_age", "eventname", "sex"]
demographic = ["site_id_l", "anthroheightcalc", "anthroweightcalc", "ehi_y_ss_scoreb", 'neighborhood_crime_y', 'snellen_aid_y']
clinical = ['ksads_1_2_t', 'ksads_8_29_t', 'ksads_25_33_t', 'ksads_13_929_t', 'pps_y_ss_severity_score']
behavioral = ['prosocial_q2_y', 'prosocial_q3_y'] # 'fit_ss_sleepperiod_minutes', 'fit_ss_avg_hr_deep',
cognitive = []
imaging = ["smri_vol_cdk_total", "smri_vol_scs_amygdalalh", 'mri_info_manufacturer',]

data_elements_of_interest = demographic + clinical + behavioral + cognitive + imaging
#print(data_elements_of_interest)

# structures2read = {}
# for element in data_elements_of_interest:
#     # print(element)
#     item = data_elements_df.query(f"element == '{element}'").structure.values
#     # print(item)
#     if item not in structures2read:
#         structures2read[item] = []
#     structures2read[item].append(element)
# print(structures2read)
#
# all_df = None
# for structure, elements in structures2read.items():
#     data_structure_filtered_df = pd.read_table(data_path / f"{structure}.txt", skiprows=[1], low_memory=False, usecols=common + elements)
#     data_structure_filtered_df = data_structure_filtered_df.query("eventname == 'baseline_year_1_arm_1'")
#     if all_df is None:
#         all_df =  data_structure_filtered_df[["subjectkey", "interview_date", "interview_age", "sex"] + elements]
#     else:
#         all_df = all_df.merge( data_structure_filtered_df[['subjectkey'] + elements], how='outer')
#
# all_df.head()