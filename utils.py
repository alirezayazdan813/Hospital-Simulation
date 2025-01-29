import random
import numpy as np
import math


def create_row(step, current_event, state, data, future_event_list):
    # This function will create a list, which will eventually become a row of the output Excel file
    sorted_fel = sorted(future_event_list, key=lambda x: x['time'])
    # What should this row contain?
    # 1. Step, Clock, Event Type and Event Customer
    row = [step, current_event['time'], current_event['event_type'], current_event['patient']]
    # 2. All state variables
    row.extend(list(state.values()))
    # 3. All Cumulative Stats
    row.extend(list(data.values()))
    # 4. fel
    row.append(sorted_fel)

    return row


def set_seed(seed_value):
    # Set the seed for reproducibility
    random.seed(seed_value)
    np.random.seed(seed_value)


# اگ گفت نمایی با پارامتر فلان دیگ نمیخواد معکوس کنی
def exponential(lambd):
    """Generate a random number from an exponential distribution."""
    r = random.random()
    return -(1 / lambd) * math.log(r)


def discrete_uniform(a, b):
    r = random.random()
    return a + int(r * (b - a + 1))


def uniform(a, b):
    """Generate a random number from a uniform distribution."""
    r = random.random()
    return a + (b - a) * r


def triangular(minimum, mean, maximum):
    """Generate a random number from a triangular distribution."""
    r = random.random()
    F_c = (maximum - minimum) / (mean - minimum)
    if r <= F_c:
        return minimum + math.sqrt(r * (mean - minimum) * (maximum - minimum))
    else:
        return mean - math.sqrt((1 - r) * (mean - minimum) * (mean - maximum))


def generate_normal(mean, std_dev):
    r1 = random.random()
    r2 = random.random()
    z0 = math.sqrt(-2 * math.log(r1)) * math.cos(2 * math.pi * r2)
    num = mean + z0 * std_dev
    return num


def generate_simple_duration():
    return generate_normal(mean=30.22, std_dev=4.96)


def generate_medium_duration():
    return generate_normal(mean=74.54, std_dev=9.95)


def generate_complex_duration():
    return generate_normal(mean=242.03, std_dev=63.12)


def nice_print(current_state, current_event):
    """
    Print the current state and event in a readable format.
    :param current_state: Dictionary containing the current state of the system
    :param current_event: Dictionary containing the current event being processed
    """
    print(str(current_event['Event Type']).ljust(20) + '\t' +
          str(round(current_event['Event Time'], 3)).ljust(15))
    ''' + '\t' +
          str(current_state['Queue Length']).ljust(15) + '\t' +
          str(current_state['Server Status']).ljust(25)'''


mmd = 4
if mmd == 1:
    print('hello')
elif mmd == 2:
    print('hello2')
elif mmd == 3:
    print('hello3')
