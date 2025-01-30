import copy
from models import Patient
from utils import *

patients = {}


# Function to initialize the starting state
def starting_state():
    """
    Initialize the starting state of the simulation with defined variables.
    Returns:
        tuple: (state dictionary, future event list)
    """
    state = {
        # Patients and Queues
        "pre_surgery_patients": 0,  # Number of patients in pre-surgery section (N)
        "emergency_patients": 0,  # Number of emergency patients (E)
        "emergency_patients_entered": 0,  # Number of emergency patients entered the hospital (E0)
        "lab_patients": 0,  # Number of patients in the lab (L)
        "pre_surgery_queue": 0,  # Number of normal patients in pre-surgery queue (QN)
        "emergency_queue": 0,  # Number of emergency patients in emergency queue (QE)
        "rejected_patients": 0,  # Number of patients rejected due to full emergency queue (R)
        "operating_room_type": None,  # Type of operation for the patient (OT)
        "operating_room_patients": 0,  # Number of patients in the operating room (O)
        "deceased_patients": 0,  # Number of deceased patients (D)
        "ward_patients": 0,  # (W)
        "ccu_patients": 0,  # Number of patients in CCU (C)
        "icu_patients": 0,  # Number of patients in ICU (I)
        "finished_patients": 0,  # (F)

        # Capacities
        "emergency_queue_capacity": 10,
        "pre_surgery_capacity": 25,
        "emergency_capacity": 10,
        "lab_capacity": 3,
        "ward_capacity": 40,
        "icu_capacity": 10,
        "ccu_capacity": 5,
        "operating_room_capacity": 50,

        # Hospital Status
        "power_status": 1,  # Power status of the hospital (1 = On, 0 = Off) (ES)

        # Statistics
        "discharged_patients": 0,  # Number of discharged patients (F)

        # Queues and Lists
        "emergency_list": [],  # List of patients in ambulance
        "lab_list": [],  # List of patients in lab queue (Lab_List)
        "pre_surgery_list": [],  # List of patients in pre_surgery queue
        "surgery_list": [],  # List of patients in operating room queue (priority and arrival time) (OR)
        "icu_list": [],  # list of patients in operating room in queue of icu
        "ccu_list": [],  # list of patients in operating room in queue of icu
        "ward_list": []  # List of patients in ward queue (Ward_List)
    }

    future_event_list = []

    # Schedule first patient arrival
    new_patient = Patient(patient_id=1, arrival_time=0, is_elective=True)
    patients[1] = new_patient

    future_event_list.append({
        'event_type': 'new_arrival',
        'time': 0.1,
        'patient': new_patient  # ???
    })
    S = 24 * 60 * discrete_uniform(1, 30)
    fel_maker(future_event_list, "power_out", 0.1, S, None)

    return state, future_event_list


def fel_maker(future_event_list, event_type, current_time, s, patient):  # S = duration time
    event_time = current_time + s

    # Add the event to the future event list
    future_event_list.append({
        'event_type': event_type,
        'time': event_time,
        'patient': patient  # patient kind or operation type and other inf
    })

    # Sort the future event list by time
    future_event_list.sort(key=lambda x: x['time'])


def simulation(simulation_time):
    """
    Runs the hospital simulation for the given time period.
    Args:
        simulation_time (float): Total simulation time.
    Returns:
        list: Event log containing details of all processed events.
    """
    # Initialize starting state and future event list
    state, future_event_list = starting_state()
    event_log = []
    table = []
    step = 1

    # Run the simulation loop
    current_time = 0
    while current_time <= simulation_time and future_event_list:
        # Get the next event
        current_event = future_event_list.pop(0)
        current_time = current_event['time']
        patient = current_event.get('patient')

        # Process event
        if current_event['event_type'] == 'new_arrival':
            new_arrival(state, future_event_list, current_time)
        elif current_event['event_type'] == 'lab_free':
            lab_free(state, future_event_list, current_time, patient)
        elif current_event['event_type'] == 'emergency_done':
            emergency_done(state, future_event_list, current_time, patient)
        elif current_event['event_type'] == 'pre_surgery_done':
            pre_surgery_done(state, future_event_list, current_time, patient)
        elif current_event['event_type'] == 'surgery_done':
            surgery_done(state, future_event_list, current_time, patient)
        elif current_event['event_type'] == 'surgery_free':
            surgery_free(state, future_event_list, current_time)
        elif current_event['event_type'] == 'icu_done':
            icu_done(state, future_event_list, current_time, patient)
        elif current_event['event_type'] == 'ccu_done':
            ccu_done(state, future_event_list, current_time, patient)
        elif current_event['event_type'] == 'ward_done':
            ward_done(state, future_event_list, current_time, patient)
        elif current_event['event_type'] == 'power_out':
            power_out(state, future_event_list, current_time)
        elif current_event['event_type'] == 'power_restore':
            power_restore(state, future_event_list, current_time)

        # checking emergency queue list
        ''' assert state["emergency_queue"] == len(state["emergency_list"]), \
            f"Emergency queue mismatch: queue={state['emergency_queue']}, list={len(state['emergency_list'])} " \
            f"and event type : {current_event['event_type']}"'''

        # Log the event
        event_log.append({
            "time": current_time,
            "event_type": current_event['event_type'],
            "patient": current_event.get('patient'),
            "state_snapshot": copy.deepcopy(state),  # state.copy()
            "future_event_list": copy.deepcopy(future_event_list)
        })

        # create a row in the event_log (table)
        # table.append(create_row(step, current_event, state, data, future_event_list))
        step += 1
    print(f"deceased patients : {state['deceased_patients']}")
    print(f"Surgery Queue at {current_time}: {len(state['surgery_list'])}")

    return event_log, patients, table


# ------------------------------------------------   events  -------------------------------------------------


def new_arrival(state, future_event_list, current_time):
    """
    Handles the arrival of a new patient at the hospital.
    Args:
        state (dict): Current state of the hospital.
        future_event_list (list): Future event list.
        current_time (float): Current simulation time.
    """
    # Generate a new patient
    print('New arrival at time:', current_time)

    is_emergency = random.random() > 0.75  # 25% chance of being an emergency patient
    is_emergency_group = random.random() > 0.995  # 5% chance of being grouped

    if is_emergency:
        if is_emergency_group:
            state["emergency_patients_entered"] = discrete_uniform(2, 5)
        else:
            state["emergency_patients_entered"] = 1

        if state["emergency_patients_entered"] + state["emergency_queue"] <= 10:
            for i in range(state["emergency_patients_entered"]):
                patient_id = len(patients) + 1
                new_patient = Patient(patient_id, current_time, is_elective=False)
                patients[patient_id] = new_patient
                new_patient.arrival_time = current_time
                # Check if the emergency queue is below capacity
                if state["emergency_patients"] + state["emergency_patients_entered"] <= state["emergency_capacity"]:
                    state["emergency_patients"] += 1
                    new_patient.emergency_entry_time = current_time
                    new_patient.current_state = 'emergency'
                    # print(f"Patient {patient_id} state updated to {new_patient.current_state}")
                    state["emergency_patients_entered"] -= 1

                    if state["lab_patients"] < state["lab_capacity"]:
                        state["lab_patients"] += 1
                        new_patient.lab_entry_time = current_time
                        S = discrete_uniform(28, 32) + 10
                        fel_maker(future_event_list, "lab_free", current_time, S, new_patient)
                    else:
                        print(f"Patient {patient_id} added to lab_list at time {current_time}")
                        state["lab_list"].append({
                            "time": current_time,
                            "is_elective": False,
                            "patient_id": patient_id
                        })
                        state["lab_list"].sort(key=lambda x: (x['is_elective'], x['time']))
                else:
                    state["emergency_queue"] += 1
                    state["emergency_list"].append({
                        "time": current_time,
                        "is_elective": False,
                        "patient_id": patient_id
                    })
                    new_patient.current_state = "In Emergency Queue"
                    state["emergency_patients_entered"] -= 1

        else:
            state["rejected_patients"] += state["emergency_patients_entered"]

    else:
        patient_id = len(patients) + 1
        new_patient = Patient(patient_id, current_time, is_elective=True)
        patients[patient_id] = new_patient
        new_patient.arrival_time = current_time
        # Handle normal patients
        if state["pre_surgery_queue"] == 0:
            process_pre_surgery(state, future_event_list, current_time, new_patient)
        else:
            state["pre_surgery_queue"] += 1
            state["pre_surgery_list"].append({
                "time": current_time,
                "is_elective": True,
                "patient_id": patient_id
            })

    # Schedule the next arrival
    interarrival_time = exponential(1 / 15)  # Assuming λ = 1/15
    fel_maker(future_event_list, "new_arrival", current_time, interarrival_time, None)


def lab_free(state, future_event_list, current_time, patient):  # patient is a model (an object) of models.Patient class
    print(f"\nLab free function called at time {current_time}")
    print(f"Current lab_list: {state['lab_list']}")

    patient.lab_end_time = current_time
    if patient.is_elective:
        S = 2 * 24 * 60
        fel_maker(future_event_list, "pre_surgery_done", current_time, S, patient=patient)
    else:
        S = triangular(5, 75, 100)
        fel_maker(future_event_list, "emergency_done", current_time, S, patient=patient)

    # Check if there are emergency patients in the lab queue
    if state["lab_list"]:
        process_next_lab_patient(state, future_event_list, current_time, patients)
    else:
        # No patients in the queues
        state["lab_patients"] -= 1
        print(f"Lab free with no patients at {current_time}. Remaining lab patients: {state['lab_patients']}.")


def emergency_done(state, future_event_list, current_time, patient):
    """
    Handles the event of a patient completing their time in the emergency section.
    Args:
        state (dict): Current state of the hospital.
        future_event_list (list): Future event list.
        current_time (float): Current simulation time.
        patient (Patient): The patient who is completing their emergency stay.
    """
    print(f"\nEmergency done for patient {patient.id} at time {current_time}")
    patient.emergency_end_time = current_time

    # Check if there is space in the operating room
    if state["operating_room_patients"] < state["operating_room_capacity"]:
        # new block
        state["operating_room_patients"] += 1
        patient.surgery_entry_time = current_time
        patient.current_state = "surgery"
        state["emergency_patients"] -= 1
        print(f"Patient {patient.id} moved to operating room from emergency at time {current_time}")

        # Determine surgery type
        r = random.random()
        if r < 0.5:
            patient.operation_type = "simple"
        elif r < 0.95:
            patient.operation_type = "medium"
        else:
            patient.operation_type = "complex"

        # Schedule surgery completion event based on operation type
        if patient.operation_type == "simple":
            S = generate_simple_duration()  # Surgery time for simple operation
            fel_maker(future_event_list, "surgery_done", current_time, S, patient)
        elif patient.operation_type == "medium":
            S = generate_medium_duration()  # Surgery time for medium operation
            fel_maker(future_event_list, "surgery_done", current_time, S, patient)
        elif patient.operation_type == "complex":
            S = generate_complex_duration()  # Surgery time for complex operation
            fel_maker(future_event_list, "surgery_done", current_time, S, patient)

    else:
        # If operating room is full, handle patient differently
        print(f"Operating room is full. Patient {patient.id} added to queue wainting in emergency")
        state["surgery_list"].append({
            "time": current_time,
            "is_elective": patient.is_elective,
            "patient_id": patient.id
        })

        state["surgery_list"].sort(key=lambda x: (x['is_elective'], x['time']))
        print(f"surgery_list :  {len(state['surgery_list'])}")

    # ----------------------                     Look backward                     -----------------------
    # Check the emergency queue
    print(state["emergency_queue"], f" : {state['emergency_list']}")
    if state["emergency_queue"] > 0 and state["emergency_patients"] < state["emergency_capacity"]:
        state["emergency_queue"] -= 1
        state["emergency_patients"] += 1
        first_patient = state["emergency_list"].pop(0)
        patient = patients[first_patient["patient_id"]]
        patient.emergency_entry_time = current_time
        patient.current_state = "emergency"
        print(f"emergency queue updated. Remaining: {state['pre_surgery_queue']}")
        print(f"Patient {patient.id} added to lab_list at time {current_time} and going to check lab if is empty")
        state["lab_list"].append({
            "time": current_time,
            "is_elective": False,
            "patient_id": patient.id
        })
        state["lab_list"].sort(key=lambda x: (x['is_elective'], x['time']))
        if state["lab_patients"] < state["lab_capacity"]:
            if state["lab_list"]:
                state["lab_patients"] += 1
                # process patient
                process_next_lab_patient(state, future_event_list, current_time, patients)
            else:
                # No patients in the lab queue
                print(f"Lab free with no patients at {current_time}. Remaining lab patients: {state['lab_patients']}.")
                print('')
    # Update stats or logs if required
    print(f"Updated state after emergency_done for patient {patient.id}:")
    print(f"Emergency Patients: {state['emergency_patients']},"
          f" Operating Room Patients: {state['operating_room_patients']}")


def pre_surgery_done(state, future_event_list, current_time, patient):
    """
    Handles the event of a patient completing their pre-surgery stay.

    Args:
        state (dict): Current state of the hospital.
        future_event_list (list): Future event list.
        current_time (float): Current simulation time.
        patient (Patient): The patient completing their pre-surgery stay.
    """
    print(f"\nPre-surgery done for patient {patient.id} at time {current_time}")
    patient.pre_surgery_end_time = current_time

    # Check if there is space in the operating room
    if state["operating_room_patients"] < state["operating_room_capacity"]:
        state["operating_room_patients"] += 1
        state["pre_surgery_patients"] -= 1
        patient.surgery_entry_time = current_time
        patient.current_state = "surgery"
        print(f"Patient {patient.id} moved to operating room queue at time {current_time}")

        # Determine the type of surgery
        r = random.random()
        if r < 0.5:
            patient.operation_type = "simple"
        elif r < 0.95:
            patient.operation_type = "medium"
        else:
            patient.operation_type = "complex"

        # Schedule the surgery completion event based on operation type
        if patient.operation_type == "simple":
            S = generate_simple_duration()  # Surgery time for simple operation
            fel_maker(future_event_list, "surgery_done", current_time, S, patient)
        elif patient.operation_type == "medium":
            S = generate_medium_duration()  # Surgery time for medium operation
            fel_maker(future_event_list, "surgery_done", current_time, S, patient)
        elif patient.operation_type == "complex":
            S = generate_complex_duration()  # Surgery time for complex operation
            fel_maker(future_event_list, "surgery_done", current_time, S, patient)

    else:
        # Operating room is full  --- add to OR list
        print(f"Operating room is full. Patient {patient.id} added to queue.")
        state["surgery_list"].append({
            "time": current_time,
            "patient_id": patient.id,
            "is_elective": patient.is_elective,
        })
        state["surgery_list"].sort(key=lambda x: (x['is_elective'], x['time']))
        print(f"surgery_list :  {len(state['surgery_list'])}")

    # -------------------------------------  Backward  -----------------------------------
    # Manage pre-surgery queue
    if state["pre_surgery_queue"] > 0 and state["pre_surgery_patients"] < state["pre_surgery_capacity"]:

        state["pre_surgery_queue"] -= 1
        state["pre_surgery_patients"] += 1
        first_patient = state["pre_surgery_list"].pop(0)
        patient = patients[first_patient["patient_id"]]
        patient.pre_surgery_entry_time = current_time
        patient.current_state = "pre_surgery"
        print(f"Pre-surgery queue updated. Remaining: {state['pre_surgery_queue']}")

        print(f"Patient {patient.id} added to lab_list at time {current_time}")
        state["lab_list"].append({
            "time": current_time,
            "is_elective": True,
            "patient_id": patient.id
        })
        state["lab_list"].sort(key=lambda x: (x['is_elective'], x['time']))
        if state["lab_patients"] < state["lab_capacity"]:
            if state["lab_list"]:
                state["lab_patients"] += 1
                # process patient
                process_next_lab_patient(state, future_event_list, current_time, patients)
            else:
                # No patients in the lab queue
                print(f"Lab free with no patients at {current_time}. Remaining lab patients: {state['lab_patients']}.")
                print('')
        else:
            pass
    else:
        print("No patients left in pre_surgery queue.")

    # Update stats or logs

    print(f"Updated state after patient {patient.id} entering the pre surgery section: ")
    print(f"Operating Room Patients: {state['operating_room_patients']},"
          f" Pre-Surgery Patients: {state['pre_surgery_patients']}")


def surgery_free(state, future_event_list, current_time):
    """
    Handles the event when the operating room becomes ready.

    Args:
        state (dict): Current state of the hospital.
        future_event_list (list): Future event list.
        current_time (float): Current simulation time.
    """
    print(f"\nOperating room ready at time {current_time}")

    # Check if the operating room queue is empty
    print("op patients", state["operating_room_patients"], "  -  op cap :", state["operating_room_capacity"])
    if len(state["surgery_list"]) > 0 and state["operating_room_patients"] < state["operating_room_capacity"]:
        # Get the first patient from the queue
        first_patient = state["surgery_list"].pop(0)
        patient_id = first_patient["patient_id"]
        patient = patients[patient_id]

        # Increment operating room count (O++)
        state["operating_room_patients"] += 1
        patient.surgery_entry_time = current_time
        print(f"Patient {patient.id} moved to operating room at time {current_time}")

        # Where is the patient from
        if patient.current_state == "pre_surgery":
            state["pre_surgery_patients"] -= 1
            if len(state["pre_surgery_list"]) > 0:
                state["pre_surgery_queue"] -= 1
                pre_surgery_patient = state["pre_surgery_list"].pop(0)
                patient_id = pre_surgery_patient["patient_id"]
                afterward_patient = patients[patient_id]
                process_pre_surgery(state, future_event_list, current_time, afterward_patient)
        elif patient.current_state == "emergency":
            state["emergency_patients"] -= 1
            if len(state["emergency_list"]) > 0:
                state["emergency_queue"] -= 1
                emergency_patient = state["emergency_list"].pop(0)
                patient_id = emergency_patient["patient_id"]
                afterward_patient = patients[patient_id]
                process_emergency(state, future_event_list, current_time, afterward_patient)
        elif patient.current_state == "icu":
            state["icu_patients"] -= 1

            if len(state["icu_list"]) > 0:
                process_icu(state, future_event_list, current_time, patient)
        elif patient.current_state == "ccu":
            state["ccu_patients"] -= 1

            if len(state["ccu_list"]) > 0:
                ccu_patient = state["ccu_list"].pop(0)
                patient_id = ccu_patient["patient_id"]
                afterward_patient = patients[patient_id]
                process_ccu(state, future_event_list, current_time, afterward_patient)

        # Determine the type of surgery
        # assuming icu and ccu patients would have the same prob of determine op type
        r = random.random()
        if r < 0.5:
            patient.operation_type = "simple"
        elif r < 0.95:
            patient.operation_type = "medium"
        else:
            patient.operation_type = "complex"

        patient.current_state = "surgery"
        if patient.operation_type == "simple":
            S = generate_simple_duration()  # Surgery time for simple operation
            fel_maker(future_event_list, "surgery_done", current_time, S, patient)
        elif patient.operation_type == "medium":
            S = generate_medium_duration()  # Surgery time for medium operation
            fel_maker(future_event_list, "surgery_done", current_time, S, patient)
        elif patient.operation_type == "complex":
            S = generate_complex_duration()  # Surgery time for complex operation
            fel_maker(future_event_list, "surgery_done", current_time, S, patient)

    elective_count = sum(1 for p in state["surgery_list"] if p["is_elective"])
    emergency_count = len(state["surgery_list"]) - elective_count
    print(
        f"Surgery List: {len(state['surgery_list'])} "
        f"patients (Elective: {elective_count}, Emergency: {emergency_count})")

    # Log updated state
    print(f"Updated state after operating_room_ready:")
    print(f"Operating Room Patients: {state['operating_room_patients']}, Surgery Queue: {len(state['surgery_list'])}")


def surgery_done(state, future_event_list, current_time, patient):
    """
    Handles the event of a patient completing their surgery.

    Args:
        state (dict): Current state of the hospital.
        future_event_list (list): Future event list.
        current_time (float): Current simulation time.
        patient (Patient): The patient completing their surgery.
    """
    print(f"\nSurgery done for patient {patient.id} at time {current_time}")
    patient.surgery_end_time = current_time

    # Determine the destination based on the surgery type (operation type)
    if patient.operation_type == "simple":  # OT=1
        state["ward_list"].append({
            "time": current_time,
            "patient_id": patient.id,
            "is_elective": patient.is_elective,
        })
        state["ward_list"].sort(key=lambda x: x["time"])
        process_ward(state, future_event_list, current_time, patient)

    elif patient.operation_type == "medium":  # OT=2
        r = random.random()
        if r < 0.7:
            state["ward_list"].append({
                "time": current_time,
                "patient_id": patient.id,
                "is_elective": patient.is_elective,
            })
            state["ward_list"].sort(key=lambda x: x["time"])
            process_ward(state, future_event_list, current_time, patient)
        elif r < 0.8:
            state["icu_list"].append({
                "time": current_time,
                "patient_id": patient.id,
                "is_elective": patient.is_elective,
            })
            state["icu_list"].sort(key=lambda x: x["time"])
            process_icu(state, future_event_list, current_time, patient)
        else:
            state["ccu_list"].append({
                "time": current_time,
                "patient_id": patient.id,
                "is_elective": patient.is_elective,
            })
            state["ccu_list"].sort(key=lambda x: x["time"])
            process_ccu(state, future_event_list, current_time, patient)

    elif patient.operation_type == "complex":  # OT=3, 4
        r = random.random()
        if r < 0.1:
            state["deceased_patients"] += 1
            state["operating_room_patients"] -= 1
        else:
            r = random.random()
            if r < 0.75:  # not heart (OT = 3) icu
                state["icu_list"].append({"time": current_time, "patient_id": patient.id,
                                          "is_elective": patient.is_elective})
                state["icu_list"].sort(key=lambda x: x["time"])
                process_icu(state, future_event_list, current_time, patient)
            else:  # heart (OT = 4) ccu
                state["ccu_list"].append({"time": current_time, "patient_id": patient.id,
                                          "is_elective": patient.is_elective})
                state["ccu_list"].sort(key=lambda x: x["time"])
                process_ccu(state, future_event_list, current_time, patient)

    # Update statistics and schedule next events for operating room readiness
    print(f"Operating room freed at time {current_time}.")

    # Log the updated state
    print(f"Updated state after surgery_done for patient {patient.id}:")
    print(f"Operating Room Patients: {state['operating_room_patients']}, "
          f"Ward Patients: {(state['ward_patients'])}, "
          f"ICU Patients: {state['icu_patients']}, "
          f"CCU Patients: {state['ccu_patients']}, "
          f"Deceased Patients: {state['deceased_patients']}")


def icu_done(state, future_event_list, current_time, patient):
    """
    Handles the event of a patient completing their ICU stay.

    Args:
        state (dict): Current state of the hospital.
        future_event_list (list): Future event list.
        current_time (float): Current simulation time.
        patient (Patient): The patient completing their ICU stay.
    """
    print(f"\nICU Done event for patient {patient.id} at time {current_time}")
    patient.icu_end_time = current_time

    r = random.random()
    if r < 0.01:
        patient.re_surgeries += 1
        if state["operating_room_patients"] < state["operating_room_capacity"]:
            state["operating_room_patients"] += 1
            state["icu_patients"] -= 1
            patient.surgery_entry_time = current_time
            patient.current_state = "surgery"
            print(f"Patient {patient.id} moved to operating room from icu at time {current_time}")

            # Determine the type of surgery -- hypothesis of that re-surgeries have complex surgery
            patient.operation_type = "complex"
            patient.is_elective = False
            # Schedule the surgery completion event based on operation type
            S = generate_complex_duration()  # Surgery time for complex operation
            fel_maker(future_event_list, "surgery_done", current_time, S, patient)

        else:
            # Operating room is full  --- add to OR list
            print(f"Operating room is full. Patient {patient.id} added to queue standing in icu")
            state["surgery_list"].append({
                "time": current_time,
                "patient_id": patient.id,
                "is_elective": False,
            })
            state["surgery_list"].sort(key=lambda x: (x['is_elective'], x['time']))
            print(f"surgery_list :  {len(state['surgery_list'])}")
    else:
        if state["ward_patients"] < state["ward_capacity"]:

            print(f"Patient {patient.id} moved to ward from icu at time {current_time}.")
            patient.ward_entry_time = current_time
            state["icu_patients"] -= 1
            state["ward_patients"] += 1
            S = 60 * exponential(lambd=50)
            fel_maker(future_event_list, "ward_done", current_time, S, patient)
        else:
            state["ward_list"].append({
                "time": current_time,
                "patient_id": patient.id,
                "is_elective": patient.is_elective,
            })
            state["ward_list"].sort(key=lambda x: x["time"])
            print(f"Patient {patient.id} added to ward queue (in icu) due to full ward capacity.")

    '''
    # Check if the patient is critical (acute case)
    if patient.is_critical:
        pass
    else:
        print(f"Patient {patient.id} is critical.")
        if state["operating_room_patients"] < state["operating_room_capacity"]:
            # Move to the operating room
            state["operating_room_patients"] += 1
            patient.surgery_entry_time = current_time
            print(f"Patient {patient.id} moved to operating room at time {current_time}.")

            # Determine surgery type (OT)
            r = random.random()
            if r < 0.5:
                patient.operation_type = "simple"
                S = generate_simple_duration()
                fel_maker(future_event_list, "surgery_done", current_time, S, patient)
            elif r < 0.85:
                patient.operation_type = "medium"
                S = generate_medium_duration()
                fel_maker(future_event_list, "surgery_done", current_time, S, patient)
            else:
                patient.operation_type = "complex"
                S = generate_complex_duration()
                fel_maker(future_event_list, "surgery_done", current_time, S, patient)

            print(f"Scheduled surgery for patient {patient.id} with operation type: {patient.operation_type}")
        else:
            # Add to operating room queue
            state["surgery_list"].append({
                "time": current_time,
                "patient_id": patient.id,
                "is_elective": patient.is_elective,
            })
            state["surgery_list"].sort(key=lambda x: x["time"])
            print(f"Patient {patient.id} added to surgery queue due to full operating room capacity.")'''

    # -------------------------------  backward look  -----------------------------
    # Handle ICU queue
    if len(state["icu_list"]) > 0:
        process_icu(state, future_event_list, current_time, patient)

    # Log updated state
    print(f"Updated state after ICU Done event:")
    print(f"ICU Patients: {state['icu_patients']}, Ward Patients: {state['ward_patients']}, "
          f"Operating Room Patients: {state['operating_room_patients']}, Surgery Queue: {len(state['surgery_list'])}")


def ccu_done(state, future_event_list, current_time, patient):
    """
    Handles the event of a patient completing their CCU stay.

    Args:
        state (dict): Current state of the hospital.
        future_event_list (list): Future event list.
        current_time (float): Current simulation time.
        patient (Patient): The patient completing their ICU stay.
    """
    print(f"\nICU Done event for patient {patient.id} at time {current_time}")
    patient.ccu_end_time = current_time

    r = random.random()
    if r < 0.01:
        patient.re_surgeries += 1
        if state["operating_room_patients"] < state["operating_room_capacity"]:
            state["operating_room_patients"] += 1
            state["ccu_patients"] -= 1
            patient.surgery_entry_time = current_time
            patient.current_state = "surgery"
            print(f"Patient {patient.id} moved to operating room from icu at time {current_time}")

            # Determine the type of surgery -- hypothesis of that re-surgeries have complex surgery
            patient.operation_type = "complex"
            patient.is_elective = False
            # Schedule the surgery completion event based on operation type
            S = generate_complex_duration()  # Surgery time for complex operation
            fel_maker(future_event_list, "surgery_done", current_time, S, patient)

        else:
            # Operating room is full  --- add to OR list
            print(f"Operating room is full. Patient {patient.id} added to queue standing in ccu")
            state["surgery_list"].append({
                "time": current_time,
                "patient_id": patient.id,
                "is_elective": False,
            })
            state["surgery_list"].sort(key=lambda x: (x['is_elective'], x['time']))
            print(f"surgery_list :  {len(state['surgery_list'])}")
    else:
        if state["ward_patients"] < state["ward_capacity"]:

            print(f"Patient {patient.id} moved to ward from ccu at time {current_time}.")
            patient.ward_entry_time = current_time
            state["ccu_patients"] -= 1
            state["ward_patients"] += 1
            S = 60 * exponential(lambd=50)
            fel_maker(future_event_list, "ward_done", current_time, S, patient)
        else:
            state["ward_list"].append({
                "time": current_time,
                "patient_id": patient.id,
                "is_elective": patient.is_elective,
            })
            state["ward_list"].sort(key=lambda x: x["time"])
            print(f"Patient {patient.id} added to ward queue (in icu) due to full ward capacity.")
    # -------------------------------  backward look  -----------------------------
    # Handle CCU queue
    if len(state["ccu_list"]) > 0:
        process_ccu(state, future_event_list, current_time, patient)

    # Log updated state
    print(f"Updated state after CCU Done event:")
    print(f"CCU Patients: {state['ccu_patients']}, Ward Patients: {state['ward_patients']}"
          , f"Operating Room Patients: {state['operating_room_patients']}, Surgery Queue: {len(state['surgery_list'])}")


def ward_done(state, future_event_list, current_time, patient):
    state['ward_patients'] -= 1
    state["finished_patients"] += 1
    patient.exit_time = current_time
    patient.current_state = "finished"
    if state["ward_list"]:
        process_ward(state, future_event_list, current_time, patient)
    else:
        pass


def power_out(state, future_event_list, current_time):
    print(f"\nPower outage occurred at time {current_time}")
    # Set power status to 0 (off)
    state["power_status"] = 0
    state["icu_capacity"] = 8
    state["ccu_capacity"] = 4

    S = 24 * 60
    fel_maker(future_event_list, "power_restore", current_time, S, None)


def power_restore(state, future_event_list, current_time):
    print(f"\nPower restored at time {current_time}")
    # Set power status to 1 (on)
    state["power_status"] = 1
    state["icu_capacity"] = 10
    state["ccu_capacity"] = 5

    # S = 24 * 60 * discrete_uniform(1, 30)
    # fel_maker(future_event_list, "power_out", current_time, S, None)


# ----------------------------------------------  help-functions  -----------------------------------------------
def process_next_lab_patient(state, future_event_list, current_time, patients):
    """
    Process the next patient from the lab queue and schedule their lab service.

    Args:
        state (dict): Current state of the system
        future_event_list (list): List of future events
        current_time (float): Current simulation time
        patients (dict) : list of patients with key patient_id

    Returns:
        bool: True if a patient was processed, False if lab queue was empty
    """

    # Check if there's an emergency patient in the queue
    if any(not patient['is_elective'] for patient in state["lab_list"]):
        # Process emergency patient
        first_patient = state["lab_list"].pop(0)
        patient = patients[first_patient["patient_id"]]
        patient.lab_entry_time = current_time
        S = discrete_uniform(28, 32) + 10  # Lab service time for emergency
        fel_maker(future_event_list, "lab_free", current_time, S, patient)
        print(
            f"Emergency patient {patient.id} handled"
            f" in lab at {current_time}. Lab patients: {state['lab_patients']}.")
    else:
        # Process normal patient
        first_patient = state["lab_list"].pop(0)
        patient = patients[first_patient["patient_id"]]
        patient.lab_entry_time = current_time
        S = discrete_uniform(28, 32) + 60  # Lab service time for normal
        fel_maker(future_event_list, "lab_free", current_time, S, patient)
        print(f"Normal patient {patient.id} handled"
              f" in lab at {current_time}. Lab patients: {state['lab_patients']}.")


def process_emergency(state, future_event_list, current_time, new_patient):
    """
    Process an emergency patient's admission or add to emergency queue.

    Args:
        state (dict): Current state of the system
        future_event_list (list): List of future events
        current_time (float): Current simulation time
        new_patient (Patient): Emergency patient to be processed

    Returns:
        bool: True if patient was admitted to emergency, False if added to queue or rejected
    """
    patient_id = new_patient.id

    # Check if emergency section has capacity
    if state["emergency_patients"] < state["emergency_capacity"]:
        # Admit patient to emergency
        state["emergency_patients"] += 1
        new_patient.emergency_entry_time = current_time
        new_patient.current_state = 'emergency'

        print(f"Patient {patient_id} admitted to emergency at {current_time}."
              f" Current count: {state['emergency_patients']}/{state['emergency_capacity']}")

        # Check lab availability
        if state["lab_patients"] < state["lab_capacity"]:
            # Lab is available
            state["lab_patients"] += 1
            new_patient.lab_entry_time = current_time
            S = discrete_uniform(28, 32) + 10  # Shorter lab time for emergency
            fel_maker(future_event_list, "lab_free", current_time, S, patient=new_patient)
            print(f"Emergency patient {patient_id} directly admitted to lab")
        else:
            # Add to lab queue with priority
            print(f"Emergency patient {patient_id} added to lab_list at time {current_time}")
            state["lab_list"].append({
                "time": current_time,
                "is_elective": False,  # Emergency patients get priority
                "patient_id": patient_id
            })
            state["lab_list"].sort(key=lambda x: (x['is_elective'], x['time']))

        return True

    else:
        # Check if emergency queue has capacity
        if state["emergency_queue"] < state["emergency_queue_capacity"]:
            # Add to emergency queue
            state["emergency_queue"] += 1
            state["emergency_list"].append({
                "time": current_time,
                "is_elective": False,
                "patient_id": patient_id
            })
            new_patient.current_state = "In Emergency Queue"
            print(f"Emergency patient {patient_id} added to emergency queue. Queue size: {state['emergency_queue']}")
            return False
        else:
            # Emergency queue is full, patient is rejected
            state["rejected_patients"] += 1
            new_patient.current_state = "Rejected"
            print(f"Emergency patient {patient_id} rejected due to full emergency queue")
            return False


def process_pre_surgery(state, future_event_list, current_time, patient):
    """
    Process a patient's admission to pre-surgery section or add to pre-surgery queue.

    Args:
        state (dict): Current state of the system
        future_event_list (list): List of future events
        current_time (float): Current simulation time
        patient (Patient): Patient to be processed

    Returns:
        bool: True if patient was admitted to pre-surgery, False if added to queue
    """
    patient_id = patient.id

    if state["pre_surgery_patients"] < state["pre_surgery_capacity"]:
        # Admit patient to pre-surgery
        state["pre_surgery_patients"] += 1
        patient.pre_surgery_entry_time = current_time
        patient.current_state = 'pre_surgery'

        print(f"Patient {patient_id} state updated to {patient.current_state}")
        print(f"Patient {patient_id} admitted to pre-surgery."
              f" Current count: {state['pre_surgery_patients']}/{state['pre_surgery_capacity']}")

        # Check lab availability
        if state["lab_patients"] < state["lab_capacity"]:
            # Lab is available
            state["lab_patients"] += 1
            patient.lab_entry_time = current_time
            if patient.is_elective:
                S = discrete_uniform(28, 32) + 60
            else:
                S = discrete_uniform(28, 32) + 10

            fel_maker(future_event_list, "lab_free", current_time, S, patient=patient)
        else:
            # Add to lab queue
            print(f"Patient {patient_id} added to lab_list at time {current_time}")
            state["lab_list"].append({
                "time": current_time,
                "is_elective": patient.is_elective,
                "patient_id": patient_id
            })
            state["lab_list"].sort(key=lambda x: (x['is_elective'], x['time']))

        return True

    else:
        # Add to pre-surgery queue
        state["pre_surgery_queue"] += 1
        state["pre_surgery_list"].append({
            "time": current_time,
            "is_elective": True,
            "patient_id": patient_id
        })
        print(f"Patient {patient_id} added to pre-surgery queue. Queue size: {state['pre_surgery_queue']}")

        return False


def process_ward(state, future_event_list, current_time, patient):
    """
    Process a patient's transfer to the ward or ward queue.

    Args:
        state (dict): Current state of the system
        future_event_list (list): List of future events
        current_time (float): Current simulation time
        patient (Patient): Patient to be processed

    Returns:
        bool: True if patient was transferred to ward, False if added to queue
    """

    if state["ward_patients"] < state["ward_capacity"] and len(state["ward_list"]) > 0:
        processing_patient = state["ward_list"].pop(0)
        processing_patient = patients[processing_patient["patient_id"]]

        # Patient goes to the ward
        if processing_patient.current_state == "surgery":
            state["operating_room_patients"] -= 1  # Decrement operating room count (O--)
        elif processing_patient.current_state == "icu":
            state["icu_patients"] -= 1
        elif processing_patient.current_state == "ccu":
            state["ccu_patients"] -= 1

        # Update patient state
        processing_patient.current_state = "ward"
        state["ward_patients"] += 1
        processing_patient.ward_entry_time = current_time

        print(f"Patient {processing_patient.id} moved to ward at time {current_time}")

        # Schedule ward completion
        S = 60 * exponential(lambd=1 / 50)
        fel_maker(future_event_list, "ward_done", current_time, S, processing_patient)

        # Schedule surgery room to be free
        S = 10
        fel_maker(future_event_list, "surgery_free", current_time, S, processing_patient)
        # Do not use this patient for free

    '''else:
        # Ward is full; patient waits in the queue
        state["ward_list"].append({
            "time": current_time,
            "patient_id": processing_patient.id,
            "is_elective": processing_patient.is_elective,
        })
        state["ward_list"].sort(key=lambda x: (x['time']))
        print(f"Patient {processing_patient.id} added to ward queue due to full capacity.")'''


def process_icu(state, future_event_list, current_time, patient):
    """
    Process a patient's transfer to the ICU or ICU queue.

    Args:
        state (dict): Current state of the system
        future_event_list (list): List of future events
        current_time (float): Current simulation time
        patient (Patient): Patient to be processed

    Returns:
        bool: True if patient was transferred to ICU, False if added to queue
    """
    processing_patient = state["icu_list"].pop(0)
    processing_patient = patients[processing_patient["patient_id"]]

    if state["icu_patients"] < state["icu_capacity"]:
        # Patient goes to the ICU
        state["operating_room_patients"] -= 1  # Decrement operating room count
        state["icu_patients"] += 1
        processing_patient.current_state = "icu"
        processing_patient.icu_entry_time = current_time

        print(f"Patient {processing_patient.id} moved to ICU at time {current_time}")

        # Schedule ICU completion - using different lambda for ICU stay duration
        S = 60 * exponential(lambd=1 / 25)  # Assuming average ICU-stay is 25 hours
        fel_maker(future_event_list, "icu_done", current_time, S, processing_patient)

        # Schedule surgery room to be free
        S = 10
        fel_maker(future_event_list, "surgery_free", current_time, S,
                  processing_patient)  # Do not use this patient surgery entry

        return True

    '''else:
        # ICU is full; patient waits in the queue
        state["icu_list"].append({
            "time": current_time,
            "patient_id": patient.id,
            "is_elective": patient.is_elective,
        })
        state["icu_list"].sort(key=lambda x: (x['time']))
        print(f"Patient {patient.id} added to ICU queue due to full capacity.")

        return False'''


def process_ccu(state, future_event_list, current_time, patient):
    """
    Process a patient's transfer to the CCU or CCU queue.

    Args:
        state (dict): Current state of the system
        future_event_list (list): List of future events
        current_time (float): Current simulation time
        patient (Patient): Patient to be processed

    Returns:
        bool: True if patient was transferred to CCU, False if added to queue
    """
    processing_patient = state["ccu_list"].pop(0)
    processing_patient = patients[processing_patient["patient_id"]]

    if state["ccu_patients"] < state["ccu_capacity"]:
        # Patient goes to the CCU
        state["operating_room_patients"] -= 1  # Decrement operating room count
        state["ccu_patients"] += 1
        processing_patient.current_state = "ccu"
        processing_patient.ccu_entry_time = current_time

        print(f"Patient {processing_patient.id} moved to CCU at time {current_time}")

        # Schedule CCU completion - using specific lambda for CCU stay duration
        S = 60 * exponential(lambd=1 / 25)  # Assuming average CCU stay is 25 hours
        fel_maker(future_event_list, "ccu_done", current_time, S, processing_patient)

        # Schedule surgery room to be free
        S = 10
        fel_maker(future_event_list, "surgery_free", current_time, S,
                  processing_patient)  # Do not use this patient for free

        return True

    '''else:
        # CCU is full; patient waits in the queue
        state["ccu_list"].append({
            "time": current_time,
            "patient_id": patient.id,
            "is_elective": patient.is_elective,
        })
        state["ccu_list"].sort(key=lambda x: (x['time']))
        print(f"Patient {patient.id} added to CCU queue due to full capacity.")

        return False'''
