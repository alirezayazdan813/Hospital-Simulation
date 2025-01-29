"""
Functions for saving and exporting simulation results.
"""

import pandas as pd
from datetime import datetime


def print_all_patients(patients):
    for patient_id, patient in patients.items():
        print(f"Patient ID: {patient_id}")
        print(f"  Arrival Time: {patient.arrival_time}")
        print(f"  Is Elective: {patient.is_elective}")
        print(f"  Current State: {patient.current_state}")
        print(f"  Surgery Type: {patient.surgery_type}")
        print(f"  Emergency Entry Time: {patient.emergency_entry_time}")
        print(f"  Pre-Surgery Entry Time: {patient.pre_surgery_entry_time}")
        print(f"  Lab Entry Time: {patient.lab_entry_time}")
        print(f"  Surgery Entry Time: {patient.surgery_entry_time}")
        print(f"  ICU Entry Time: {patient.icu_entry_time}")
        print(f"  CCU Entry Time: {patient.ccu_entry_time}")
        print(f"  Ward Entry Time: {patient.ward_entry_time}")
        print(f"  Exit Time: {patient.exit_time}")
        print(f"  Re-Surgeries: {patient.re_surgeries}")
        print("-" * 40)


def create_main_header(state, data):
    # This function creates the main part of header (returns a list)
    # A part of header which is used for future events will be created in create_excel()

    # Header consists of ...
    # 1. Step, Clock, Event Type and Event Customer
    header = ['Step', 'Clock', 'Event Type', 'Event Customer']
    # 2. Names of the state variables
    header.extend(list(state.keys()))
    # 3. Names of the cumulative stats
    header.extend(list(data['Cumulative Stats'].keys()))
    return header


'''
def create_excel(table, header):
    # This function creates and fine-tunes the Excel output file

    # Find length of each row in the table
    row_len = len(table[0])

    # Find length of header (header does not include cells for fel at this moment)
    header_len = len(header)

    # row_len exceeds header_len by (max_fel_length * 3) (Event Type, Event Time & Customer for each event in FEL)
    # Extend the header with 'Future Event Time', 'Future Event Type', 'Future Event Customer'
    # for each event in the fel with maximum size
    i = 1
    for col in range((row_len - header_len) // 3):
        header.append('Future Event Time ' + str(i))
        header.append('Future Event Type ' + str(i))
        header.append('Future Event Customer ' + str(i))
        i += 1

    # Dealing with the output
    # First create a pandas DataFrame
    df = pd.DataFrame(table, columns=header, index=None)

    # Create a handle to work on the Excel file
    writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')

    # Write out the Excel file to the hard drive
    df.to_excel(writer, sheet_name='Single-server Queue Output', header=False, startrow=1, index=False)

    # Use the handle to get the workbook (just library syntax, can be found with a simple search)
    workbook = writer.book

    # Get the sheet you want to work on
    worksheet = writer.sheets['Single-server Queue Output']

    # Create a cell-formatter object (this will be used for the cells in the header, hence: header_formatter!)
    header_formatter = workbook.add_format()

    # Define whatever format you want
    header_formatter.set_align('center')
    header_formatter.set_align('vcenter')
    header_formatter.set_font('Times New Roman')
    header_formatter.set_bold('True')

    # Write out the column names and apply the format to the cells in the header row
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_formatter)

    # Auto-fit columns
    # Copied from https://stackoverflow.com/questions/29463274/simulate-autofit-column-in-xslxwriter
    for i, width in enumerate(get_col_widths(df)):
        worksheet.set_column(i - 1, i - 1, width)

    # Create a cell-formatter object for the body of Excel file
    main_formatter = workbook.add_format()
    main_formatter.set_align('center')
    main_formatter.set_align('vcenter')
    main_formatter.set_font('Times New Roman')

    # Apply the format to the body cells
    for row in range(1, len(df) + 1):
        worksheet.set_row(row, None, main_formatter)

    # Save your edits
    writer.save()
'''


def export_patients_to_excel(patients, filename="patients_output.xlsx"):
    """
    Exports a dictionary of Patient objects to an Excel file.

    Args:
        patients (dict): Dictionary of Patient objects (key: patient_id, value: Patient object).
        filename (str): Name of the output Excel file.
    """
    # Convert Patient objects to a list of dictionaries
    data = []
    for patient_id, patient in patients.items():
        patient_data = {
            "Patient ID": patient.id,
            "Arrival Time": patient.arrival_time,
            "Is Elective": patient.is_elective,
            "Current State": patient.current_state,
            "Surgery Type": patient.surgery_type,
            "Kind": patient.kind,
            "Emergency Entry Time": patient.emergency_entry_time,
            "Pre-Surgery Entry Time": patient.pre_surgery_entry_time,
            "Lab Entry Time": patient.lab_entry_time,
            "Surgery Entry Time": patient.surgery_entry_time,
            "ICU Entry Time": patient.icu_entry_time,
            "CCU Entry Time": patient.ccu_entry_time,
            "Ward Entry Time": patient.ward_entry_time,
            "Exit Time": patient.exit_time,
            "Emergency End Time": patient.emergency_end_time,
            "Pre-Surgery End Time": patient.pre_surgery_end_time,
            "Lab End Time": patient.lab_end_time,
            "Surgery End Time": patient.surgery_end_time,
            "ICU End Time": patient.icu_end_time,
            "CCU End Time": patient.ccu_end_time,
            "Ward End Time": patient.ward_end_time,
            "Operation Type": patient.operation_type,
            "Re-Surgeries": patient.re_surgeries,
        }
        data.append(patient_data)

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(data)

    # Save the DataFrame to an Excel file
    df.to_excel(filename, index=False, engine="openpyxl")
    print(f"Patient data exported to {filename}")


def create_simulation_log(event_log, simulation_time):
    """
    Create an Excel file with simulation results.

    Args:
        event_log (list): List of events from the simulation
        simulation_time (float): Total simulation time
    """
    # Create a list to store all rows
    rows = []
    step = 1

    # Process each event in the event_log
    for event in event_log:
        # Create a row for each event
        row = {
            'Step': step,
            'Time': round(event['time'], 2),
            'Event_Type': event['event_type'],
            'Patient_ID': event.get('patient').id if event.get('patient') else None,
            'Patient_Type': 'Emergency' if event.get('patient') and not event.get(
                'patient').is_elective else 'Elective' if event.get('patient') else None,
            'Patient_State': event.get('patient').current_state if event.get('patient') else None,
            'Emergency_Patients': event['state_snapshot']['emergency_patients'],
            'Pre_Surgery_Patients': event['state_snapshot']['pre_surgery_patients'],
            'Lab_Patients': event['state_snapshot']['lab_patients'],
            'OR_Patients': event['state_snapshot']['operating_room_patients'],
            'ICU_Patients': event['state_snapshot']['icu_patients'],
            'CCU_Patients': event['state_snapshot']['ccu_patients'],
            'Ward_Patients': event['state_snapshot']['ward_patients'],
            'Emergency_Queue': event['state_snapshot']['emergency_queue'],
            'Pre_Surgery_Queue': event['state_snapshot']['pre_surgery_queue'],
            'Lab_Queue': len(event['state_snapshot']['lab_list']),
            'Surgery_Queue': len(event['state_snapshot']['surgery_list']),
            'Ward_Queue': len(event['state_snapshot']['ward_list']),
            'ICU_Queue': len(event['state_snapshot']['icu_list']),
            'CCU_Queue': len(event['state_snapshot']['ccu_list']),
            'Deceased_Patients': event['state_snapshot']['deceased_patients'],
            'Finished_Patients': event['state_snapshot']['finished_patients'],
        }
        rows.append(row)
        step += 1

    # Create DataFrame
    df = pd.DataFrame(rows)

    # Generate filename with current timestamp
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'simulation_results_{current_time}.xlsx'

    # Create Excel writer object
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        # Write main simulation data
        df.to_excel(writer, sheet_name='Simulation_Log', index=False)

        # Create a summary sheet
        summary_data = {
            'Metric': [
                'Total Simulation Time',
                'Total Steps',
                'Final Emergency Patients',
                'Final Pre-Surgery Patients',
                'Final OR Patients',
                'Final ICU Patients',
                'Final CCU Patients',
                'Final Ward Patients',
                'Total Deceased Patients',
                'Total Finished Patients',
                'Final Emergency Queue',
                'Final Pre-Surgery Queue',
                'Final Surgery Queue',
                'Final Ward Queue',
            ],
            'Value': [
                simulation_time,
                len(event_log),
                df['Emergency_Patients'].iloc[-1],
                df['Pre_Surgery_Patients'].iloc[-1],
                df['OR_Patients'].iloc[-1],
                df['ICU_Patients'].iloc[-1],
                df['CCU_Patients'].iloc[-1],
                df['Ward_Patients'].iloc[-1],
                df['Deceased_Patients'].iloc[-1],
                df['Finished_Patients'].iloc[-1],
                df['Emergency_Queue'].iloc[-1],
                df['Pre_Surgery_Queue'].iloc[-1],
                df['Surgery_Queue'].iloc[-1],
                df['Ward_Queue'].iloc[-1],
            ]
        }

        # Write summary to new sheet
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Simulation_Log']

        # Add some formats
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })

        # Write headers with format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Adjust columns width
        for idx, col in enumerate(df.columns):
            series = df[col]
            max_len = max(
                series.astype(str).map(len).max(),
                len(str(series.name))
            ) + 1
            worksheet.set_column(idx, idx, max_len)

    print(f"Simulation results have been saved to {filename}")
    return filename
