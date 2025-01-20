
class Patient:
    def __init__(self, patient_id, arrival_time, is_elective):
        self.id = patient_id
        self.arrival_time = arrival_time
        self.is_elective = is_elective
        self.current_state = "Arrived"
        self.surgery_type = None

        self.kind = None

        # Timings for patient journey
        self.arrival_time = 0
        self.emergency_entry_time = 0
        self.pre_surgery_entry_time = 0
        self.lab_entry_time = 0
        self.surgery_entry_time = 0
        self.icu_entry_time = 0
        self.ccu_entry_time = 0
        self.ward_entry_time = 0
        self.exit_time = 0

        self.emergency_end_time = 0
        self.pre_surgery_end_time = 0
        self.lab_end_time = 0
        self.surgery_end_time = 0
        self.icu_end_time = 0
        self.ccu_end_time = 0
        self.ward_end_time = 0

        self.operation_type = None

        # Re-surgery counter for complex surgeries
        self.re_surgeries = 0
