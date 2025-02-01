import numpy as np
import math
from simulation import starting_state, simulation
from utils import set_seed
from analysis import *


def confidence_interval(data):
    """
    Calculate the two-sided confidence interval for a list of data using a z-distribution.
    Assumes data is at least roughly normal or n is large enough for CLT.
    and alpha is 5%
    """
    z = 1.96  # z-score for 95% confidence
    mean_value = np.mean(data)
    std_dev = np.std(data, ddof=1)  # sample standard deviation
    n = len(data)
    if n < 2:
        return (mean_value, None, None)  # Cannot compute CI with fewer than 2 data points

    margin_of_error = z * (std_dev / math.sqrt(n))
    lower_bound = mean_value - margin_of_error
    upper_bound = mean_value + margin_of_error
    return mean_value, lower_bound, upper_bound


def run_single_replication(seed, simulation_time):
    """Run a single replication of the simulation with the given seed."""
    set_seed(seed)
    state, future_event_list = starting_state()
    event_log, patients, table = simulation(simulation_time)
    return event_log, patients


def run_multiple_replications(n_replications, simulation_time=60 * 24 * 30):
    """Run multiple replications and collect metrics in lists."""

    # Initialize lists for each metric
    metrics = {
        'elective_mean_time': [],
        'emergency_mean_time': [],
        'elective_count': [],
        'emergency_count': [],
        'emergency_queue_full_prob': [],
        'avg_re_surgeries': [],
        'total_re_surgeries': []
    }

    # Initialize section-specific metrics
    sections = ['lab', 'pre_surgery', 'surgery', 'icu', 'ward', 'ccu']
    for section in sections:
        metrics[f'{section}_avg_queue'] = []
        metrics[f'{section}_max_queue'] = []
        metrics[f'{section}_avg_wait'] = []
        metrics[f'{section}_max_wait'] = []
        metrics[f'{section}_utilization'] = []

    # Add emergency utilization
    metrics['emergency_utilization'] = []

    print(f"Running {n_replications} replications...")
    for i in range(n_replications):
        print(f"Replication {i + 1}/{n_replications}")
        event_log, patients = run_single_replication(seed=776 + i, simulation_time=simulation_time)

        # KPI 1: Mean time in system
        mean_time_elective, counter_elective, mean_time_emergency, counter_emergency = calculate_mean_time_in_system(
            patients)
        metrics['elective_mean_time'].append(mean_time_elective / (60 * 24))  # Convert to days
        metrics['emergency_mean_time'].append(mean_time_emergency / (60 * 24))  # Convert to days
        metrics['elective_count'].append(counter_elective)
        metrics['emergency_count'].append(counter_emergency)

        # KPI 2: Emergency queue full probability
        emergency_prob = calculate_emergency_queue_full_probability(event_log, simulation_time)
        metrics['emergency_queue_full_prob'].append(emergency_prob)

        # KPI 3: Section metrics
        for section in sections:
            avg_queue, max_queue, avg_wait, max_wait = calculate_section_metrics(event_log, simulation_time, patients,
                                                                                 section)
            metrics[f'{section}_avg_queue'].append(avg_queue)
            metrics[f'{section}_max_queue'].append(max_queue)
            metrics[f'{section}_avg_wait'].append(avg_wait)
            metrics[f'{section}_max_wait'].append(max_wait)

        # KPI 4: Re-surgeries
        metrics['avg_re_surgeries'].append(calculate_average_re_surgeries(patients))
        metrics['total_re_surgeries'].append(calculate_re_surgeries(patients))

        # KPI 5: Utilizations
        section_configs = [
            {"name": "emergency", "capacity": 10},
            {"name": "lab", "capacity": 3},
            {"name": "pre_surgery", "capacity": 25},
            {"name": "surgery", "capacity": 50},
            {"name": "icu", "capacity": 10},
            {"name": "ward", "capacity": 40},
            {"name": "ccu", "capacity": 5}
        ]

        for config in section_configs:
            utilization = calculate_bed_utilization(
                patients,
                simulation_time,
                bed_capacity=config["capacity"],
                section_name=config["name"]
            )
            '''assert 0 <= utilization <= 100.0, f"""Invalid utilization detected!
                                Section: {config['name']}
                                Utilization: {utilization:.2f}%
                                Replication: {i + 1}
                                Date and Time: 2025-01-31 10:56:42
                                User: alirezayazdan813
                                """'''
            # utilization /= (i + 1)
            for j in metrics[f'{config["name"]}_utilization']:
                utilization -= j
            # Debug print
            print(f"""
                Section: {config['name']}
                Capacity: {config['capacity']}
                Utilization: {utilization:.2f}%
                """)

            # Assert with detailed error message
            assert 0 <= utilization <= 100.0, f"""
                Invalid utilization detected!
                seed: {776+i}
                Section: {config['name']}
                Capacity: {config['capacity']}
                Utilization: {utilization:.2f}%
                Replication: {i + 1}
                Date and Time: 2025-01-31 11:12:20
                User: alirezayazdan813
                """
            metrics[f'{config["name"]}_utilization'].append(utilization)

    return metrics


def print_results(metrics):
    """Print results with confidence intervals for all metrics."""
    categories = {
        'Patient Time in System (days)': [
            'elective_mean_time',
            'emergency_mean_time'
        ],
        'Finished Patient Counts': [
            'elective_count',
            'emergency_count'
        ],
        'Emergency Queue': [
            'emergency_queue_full_prob'
        ],
        'Complex Re-surgeries': [
            'avg_re_surgeries',
            'total_re_surgeries'
        ],
        'Queue Lengths': [
                             f'{section}_avg_queue' for section in
                             ['lab', 'pre_surgery', 'surgery', 'icu', 'ward', 'ccu']
                         ] + [
                             f'{section}_max_queue' for section in
                             ['lab', 'pre_surgery', 'surgery', 'icu', 'ward', 'ccu']
                         ],
        'Waiting Times (days)': [
                                    f'{section}_avg_wait' for section in
                                    ['lab', 'pre_surgery', 'surgery', 'icu', 'ward', 'ccu']
                                ] + [
                                    f'{section}_max_wait' for section in
                                    ['lab', 'pre_surgery', 'surgery', 'icu', 'ward', 'ccu']
                                ],
        'Utilizations': [
            f'{section}_utilization' for section in ['emergency', 'lab', 'pre_surgery', 'surgery', 'icu', 'ward', 'ccu']
        ]
    }

    print("\nSimulation Results with 95% Confidence Intervals:")
    print("-" * 80)

    for category, metric_names in categories.items():
        print(f"\n{category}:")
        print("-" * 40)
        for metric_name in metric_names:
            if metric_name in metrics:
                mean, lower, upper = confidence_interval(metrics[metric_name])
                print(f"{metric_name}:")
                print(f"  Mean: {mean:.4f}")
                if lower is not None and upper is not None:
                    print(f"  95% CI: [{lower:.4f}, {upper:.4f}]")
                    print(f"  Half-width: {(upper - lower) / 2:.4f}")
                else:
                    print("  95% CI: Insufficient data for confidence interval")
                    print("  Half-width: Not available")
                print(f"  Sample size: {len(metrics[metric_name])}")


if __name__ == "__main__":
    # Run simulation with 10 replications and collect metrics
    metrics = run_multiple_replications(n_replications=10)

    # Print results with confidence intervals
    print_results(metrics)
