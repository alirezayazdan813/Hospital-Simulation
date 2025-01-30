"""
Project Name: Hospital Simulation
File Name:
Description:
    This script establishes a simulation framework for modeling the operational 
    dynamics of a hospital system. It emphasizes the patient flow through various 
    departments, such as emergency, laboratory, operating rooms, and intensive care units (ICU/CCU). 
    The focus of this phase is to develop a structured model by identifying key components, 
    relationships, and statistical distributions relevant to hospital operations.

Key Objectives:
    1. Model the hospital's key sections and the movement of elective and non-elective patients.
    2. Identify statistical distributions for patient arrivals, service times, and transitions.
    3. Specify performance metrics for future evaluation.
    4. Document assumptions and limitations for realistic modeling.

Hospital Sections and Capacities:
    1. Pre-surgery Preparation: 25 beds
    2. Emergency Department: 10 beds
    3. Laboratory for Initial Tests: Capacity not limited by beds; depends on testing stations.
    4. Operating Rooms: 3 rooms
    5. General Recovery Wards: 40 beds
    6. Specialized Intensive Care Units (ICU): 10 beds
    7. Cardiac Intensive Care Units (CCU): 5 beds

Distributions Used:
    1. Patient Arrivals:
       - Elective patients: Poisson distribution, 1 patient/hour.
       - Non-elective patients: Poisson group arrivals, 4/hour; group size follows a discrete 
         uniform distribution [2, 5].
    2. Lab Service Times:
       - Both elective and non-elective patients: Uniform distribution (28–32 minutes).
    3. Emergency Room Stay Times:
       - Triangular distribution (min=5, mode=75, max=100 minutes).
    4. Pre-surgery Ward Stay Times:
       - Fixed duration of 2 days.
    5. Operating room:
       - Simple surgeries: Normal (mean=30.22, SD=4.96 minutes).
       - Moderate surgeries: Normal (mean=74.54, SD=9.95 minutes).
       - Complex surgeries: Normal (mean=242.03, SD=63.12 minutes).
       - Operating Room Preparation: 10 minutes.
    6. Post-Surgery Ward Stay Times:
       - General Ward: Exponential distribution (mean=50 hours).
       - ICU/CCU: Exponential distribution (mean=25 hours).

Assumptions:
    1. Non-elective patients are prioritized over elective ones.
    2. Resource constraints include limited beds, staff, and operating rooms.
    3. Service durations and transitions follow predefined distributions.

Outputs:
    1. Average patient time in the system.
    2. Queue statistics for each department.
    3. Resource utilization rates (beds, operating rooms).
    4. Patient outcomes, including reoperation rates and ICU transfer probabilities.

Author: Alireza Yazdanpanah
Date: Winter 2025
--------------------------------------------------------------------------------
"""

import pandas as pd
from simulation import starting_state, simulation
from utils import set_seed
from analysis import *
from output import export_patients_to_excel, create_simulation_log

# Initialize the simulation
state, future_event_list = starting_state()

# Set seed for reproducibility
set_seed(776)

print('hello')

simulation_time = 60 * 24 * 20
event_log, patients, table = simulation(simulation_time)

# print(type(event_log))

# print('hello again')
# Print the event log
'''for event in event_log:
    print('')
    # print(type(event))
    print(f"Time: {event['time']}, Event Type: {event['event_type']}, State Snapshot: {event['state_snapshot']}")'''

# print('')
# print('hello again2')
# print_all_patients(patients)

print('')
print('hello again3')
calculate_kpis(patients)

# ---------------------------------------------------  1  ------------------------------------------------
print('')
print('hello-kpi-1')
mean_time_in_system_elective, counter_elective, mean_time_in_system_emergency, counter_emergency = \
    calculate_mean_time_in_system(patients)
print("elective mean time in system  : ", mean_time_in_system_elective/(60*24),
      f" days for {counter_elective} elective patients")
print("emergency mean time in system : ", mean_time_in_system_emergency/(60*24),
      f" days for {counter_emergency} emergency patients")
# ---------------------------------------------------  2  ------------------------------------------------
print('')
print('hello-kpi-2')
emergency_queue_full_probability = calculate_emergency_queue_full_probability(event_log, simulation_time)
print('emergency_queue_full_probability', ' : ', emergency_queue_full_probability)
# ---------------------------------------------------  3  ------------------------------------------------
sections = ['lab', 'pre_surgery', 'surgery', 'icu', 'ward', 'ccu']
for section in sections:
    print_section_metrics(event_log, simulation_time, patients, section)
# ---------------------------------------------------  4  ------------------------------------------------
print('')
print('hello-kpi-4')
print("average re_surgeries for complex surgeries : ", calculate_average_re_surgeries(patients))
print("total re_surgeries                         : ", calculate_re_surgeries(patients))
# ---------------------------------------------------  5  ------------------------------------------------
print('')
print('hello-kpi-5')
# Define the sections and their configurations
sections = [
    {"name": "emergency", "capacity": 10, "display": "emergency_utilization  "},
    {"name": "lab", "capacity": 3, "display": "lab_utilization        "},
    {"name": "pre_surgery", "capacity": 25, "display": "pre_surgery_utilization"},
    {"name": "surgery", "capacity": 50, "display": "surgery_utilization    "},
    {"name": "icu", "capacity": 10, "display": "icu_utilization        "},
    {"name": "ward", "capacity": 40, "display": "ward_utilization       "},
    {"name": "ccu", "capacity": 5, "display": "ccu_utilization        "}
]
# Calculate utilization for each section
for section in sections:
    utilization = calculate_bed_utilization(
        patients,
        simulation_time,
        bed_capacity=section["capacity"],
        section_name=section["name"]
    )
    print(f'{section["display"]} : {utilization}')

print('bye bye')
print(len(event_log[-1]["state_snapshot"]["surgery_list"]))

# export_patients_to_excel(patients, filename="patients_output.xlsx")
file_name = create_simulation_log(event_log, simulation_time)
