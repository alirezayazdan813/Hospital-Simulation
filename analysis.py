# :)
def calculate_kpis(patients):
    total_patients = len(patients)
    total_emergency_patients = sum(1 for patient in patients.values() if not patient.is_elective)
    total_elective_patients = total_patients - total_emergency_patients

    print(f"Total Patients: {total_patients}")
    print(f"Total Emergency Patients: {total_emergency_patients}")
    print(f"Total Elective Patients: {total_elective_patients}")

    # Add more KPI calculations as needed


# 1

# 2
def calculate_emergency_queue_full_probability(event_log, simulation_time):
    """
    Calculates the probability of the emergency queue being full during the simulation.

    Args:
        event_log (list): List of events with time and emergency queue length.
        simulation_time (float): Total simulation time.

    Returns:
        float: Probability of the emergency queue being full.
    """
    total_full_time = 0

    # Iterate through the event log
    for i in range(len(event_log) - 1):
        current_event = event_log[i]
        next_event = event_log[i + 1]

        # Extract time and queue length
        current_time = current_event["time"]
        next_time = next_event["time"]
        current_queue_length = current_event["state_snapshot"]["emergency_queue"]

        # Check if the queue was full during this interval
        if current_queue_length == 10:
            full_time = next_time - current_time
            total_full_time += full_time

    # Calculate the probability
    return total_full_time / simulation_time


# 3
# calculate queue length stats for every queue *
def calculate_queue_length_stats(event_log, simulation_time, queue_name):
    """
    Calculates the maximum and average queue length for a given queue using event logs.

    Args:
        event_log (list): List of events with time and queue length information.
        simulation_time (float): Total simulation time.
        queue_name (str): The key for the queue length in the event log.

    Returns:
        tuple: (average_queue_length, max_queue_length)
    """
    total_area = 0
    max_queue_length = 0

    # Iterate through the event log to calculate area under the curve and max length
    for i in range(len(event_log) - 1):
        current_event = event_log[i]
        # print(current_event)
        next_event = event_log[i + 1]

        # Extract time and queue length
        current_time = current_event["time"]
        next_time = next_event["time"]
        current_queue_length = len(current_event["state_snapshot"][queue_name])

        # Calculate the area under the curve for this interval
        elapsed_time = next_time - current_time
        total_area += current_queue_length * elapsed_time

        # Update the maximum queue length
        max_queue_length = max(max_queue_length, current_queue_length)
        # print(current_event["state_snapshot"][queue_name])

    # Calculate the average queue length
    average_queue_length = total_area / simulation_time if simulation_time > 0 else 0

    return average_queue_length, max_queue_length


# calculate waiting time for lab - what about others ???
def calculate_waiting_times(patients):
    total_waiting_time = 0
    max_waiting_time = 0
    num_patients = 0

    for patient in patients.values():
        if patient.lab_entry_time != 0:  # Patient entered the lab
            if not patient.is_elective and patient.emergency_entry_time != 0:
                waiting_time = patient.lab_entry_time - patient.emergency_entry_time
                # print(f"Emergency Patient {patient.id}:")
                # print(f"  Lab Entry Time: {patient.lab_entry_time}")
                # print(f"  Emergency Entry Time: {patient.emergency_entry_time}")
                # print(f"  Waiting Time: {waiting_time}")

            elif patient.is_elective and patient.pre_surgery_entry_time != 0:
                waiting_time = patient.lab_entry_time - patient.pre_surgery_entry_time
                # print(f"Elective Patient {patient.id}:")
                # print(f"  Lab Entry Time: {patient.lab_entry_time}")
                # print(f"  Pre-surgery Entry Time: {patient.pre_surgery_entry_time}")
                # print(f"  Waiting Time: {waiting_time}")
            else:
                raise Exception("Error in code patients timing")
            total_waiting_time += waiting_time
            max_waiting_time = max(max_waiting_time, waiting_time)
            num_patients += 1
    # print(num_patients)

    average_waiting_time = total_waiting_time / num_patients if num_patients > 0 else 0
    return average_waiting_time, max_waiting_time


def calculate_pre_surgery_waiting_times(patients):
    total_waiting_time = 0
    max_waiting_time = 0
    num_patients = 0

    for patient in patients.values():
        if patient.is_elective:  # elective patients entered pre-surgery
            if patient.pre_surgery_entry_time != 0:
                waiting_time = patient.pre_surgery_entry_time - patient.arrival_time
                total_waiting_time += waiting_time
                max_waiting_time = max(max_waiting_time, waiting_time)
                num_patients += 1
            else:
                pass  # assume that we don't calculate waiting time fo whom waiting is not finished

    average_waiting_time = total_waiting_time / num_patients if \
        num_patients > 0 else Exception(" problem in pre surgery waiting_times")
    return average_waiting_time, max_waiting_time


def calculate_surgery_waiting_times(patients):
    """
    Calculate the average and maximum waiting times for surgery.

    Args:
        patients (dict): Dictionary of Patient objects.

    Returns:
        tuple: (average_waiting_time, max_waiting_time)
    """
    total_waiting_time = 0
    max_waiting_time = 0
    num_patients = 0

    for patient in patients.values():
        # Check if the patient has entered surgery
        if patient.surgery_entry_time != 0:
            if not patient.is_elective:  # Emergency patient
                if patient.emergency_end_time != 0:
                    waiting_time = patient.surgery_entry_time - patient.emergency_end_time
                    total_waiting_time += waiting_time
                    max_waiting_time = max(max_waiting_time, waiting_time)
                    num_patients += 1
            else:  # Elective patient
                if patient.pre_surgery_end_time != 0:
                    waiting_time = patient.surgery_entry_time - patient.pre_surgery_end_time
                    total_waiting_time += waiting_time
                    max_waiting_time = max(max_waiting_time, waiting_time)
                    num_patients += 1
        else:
            pass  # Ignore patients who haven't completed pre-surgery (or emergency) or entered surgery yet

    # Avoid division by zero
    if num_patients > 0:
        average_waiting_time = total_waiting_time / num_patients
    else:
        raise Exception("No patients have completed surgery waiting times calculation.")

    return average_waiting_time, max_waiting_time


# 4
def calculate_average_re_surgeries(patients):
    """
    Calculates the average number of re-surgeries for patients with complex surgeries.

    Args:
        patients (dict): Dictionary of Patient objects (keyed by patient_id).

    Returns:
        float: Average number of re-surgeries for complex surgery patients.
    """
    total_re_surgeries = 0
    num_complex_patients = 0

    for patient in patients.values():
        if patient.operation_type == "complex":  # Check if the surgery type is complex
            total_re_surgeries += patient.re_surgeries
            num_complex_patients += 1

    # Avoid division by zero
    if num_complex_patients == 0:
        return 0

    return total_re_surgeries / num_complex_patients


# 5
def calculate_bed_utilization(patients, simulation_time, bed_capacity, section_name):
    """
    Calculates the average bed utilization for a given section (ICU, CCU, Ward).

    Args:
        patients (dict): Dictionary of Patient objects.
        simulation_time (float): Total simulation time.
        bed_capacity (int): Number of beds in the section.
        section_name (str): Name of the section (e.g., "icu", "ccu", "ward").

    Returns:
        float: Average bed utilization for the section.
    """
    total_bed_time = 0
    if section_name == "emergency":
        # Calculate total bed usage time for the given section
        for patient in patients.values():
            entry_time = getattr(patient, "emergency_entry_time", None)
            end_time = getattr(patient, "surgery_entry_time", None)

            if entry_time != 0:
                if end_time != 0:  # Ensure both entry and exit times are available
                    total_bed_time += end_time - entry_time
                elif end_time == 0:
                    total_bed_time += simulation_time - entry_time
            # print(f'entry_time : {entry_time}')
            # print(f'end_time : {end_time}')

    elif section_name == "lab":
        # Calculate total bed usage time for the given section
        for patient in patients.values():
            entry_time = getattr(patient, f"{section_name}_entry_time", None)
            end_time = getattr(patient, f"{section_name}_end_time", None)

            if entry_time != 0:
                if end_time != 0:  # Ensure both entry and exit times are available
                    total_bed_time += end_time - entry_time
                elif end_time == 0:
                    total_bed_time += simulation_time - entry_time
            # print(f'entry_time : {entry_time}')
            # print(f'end_time : {end_time}')

    elif section_name == "pre_surgery":
        # Calculate total bed usage time for the given section
        # counter = 0
        for patient in patients.values():
            entry_time = getattr(patient, f"{section_name}_entry_time", None)
            end_time = getattr(patient, "surgery_entry_time", None)

            if entry_time != 0:
                if end_time != 0:  # Ensure both entry and exit times are available
                    total_bed_time += end_time - entry_time
                elif end_time == 0:
                    total_bed_time += simulation_time - entry_time
                # counter += 1
                # print(counter)
                # print(f'entry_time : {entry_time}')
                # print(f'end_time : {end_time}')

    # Calculate bed utilization
    return (total_bed_time * 100) / (simulation_time * bed_capacity)

# 6
