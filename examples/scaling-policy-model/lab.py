"""Tiny deterministic scaling-policy model; fictional arithmetic, no AWS calls."""
from math import ceil


def positive_number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f'{name} must be a positive number')


def backlog_per_task(visible_messages, running_tasks):
    for value, name in ((visible_messages, 'visible_messages'), (running_tasks, 'running_tasks')):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f'{name} must be a non-negative integer')
    if running_tasks == 0:
        raise ValueError('backlog per task is undefined when no tasks are running')
    return visible_messages / running_tasks


def target_backlog_per_task(acceptable_wait_seconds, seconds_per_message):
    positive_number(acceptable_wait_seconds, 'acceptable_wait_seconds')
    positive_number(seconds_per_message, 'seconds_per_message')
    return acceptable_wait_seconds / seconds_per_message


def candidate_tasks(visible_messages, target_messages_per_task):
    if isinstance(visible_messages, bool) or not isinstance(visible_messages, int) or visible_messages < 0:
        raise ValueError('visible_messages must be a non-negative integer')
    positive_number(target_messages_per_task, 'target_messages_per_task')
    return ceil(visible_messages / target_messages_per_task)


def processing_capacity(worker_capacity, dependency_capacity):
    for value, name in ((worker_capacity, 'worker_capacity'), (dependency_capacity, 'dependency_capacity')):
        positive_number(value, name)
    return min(worker_capacity, dependency_capacity)


def completions_for_new_arrivals(arrival_rate, process_capacity):
    positive_number(arrival_rate, 'arrival_rate')
    positive_number(process_capacity, 'process_capacity')
    return min(arrival_rate, process_capacity)


def backlog_change_per_second(arrival_rate, completions_per_second):
    positive_number(arrival_rate, 'arrival_rate')
    positive_number(completions_per_second, 'completions_per_second')
    return arrival_rate - completions_per_second


def backlog_clear_seconds(backlog, arrival_rate, completion_capacity):
    if isinstance(backlog, bool) or not isinstance(backlog, int) or backlog < 0:
        raise ValueError('backlog must be a non-negative integer')
    positive_number(arrival_rate, 'arrival_rate')
    positive_number(completion_capacity, 'completion_capacity')
    surplus = completion_capacity - arrival_rate
    if backlog == 0:
        return 0
    if surplus <= 0:
        return None
    return ceil(backlog / surplus)


def run():
    target = target_backlog_per_task(10, 0.1)
    observed = backlog_per_task(1_500, 10)
    tasks = candidate_tasks(1_500, target)
    limited_capacity = processing_capacity(20, 8)
    scaled_worker_capacity = processing_capacity(40, 8)
    limited = completions_for_new_arrivals(12, limited_capacity)
    scaled_workers = completions_for_new_arrivals(12, scaled_worker_capacity)
    backlog_growth = backlog_change_per_second(12, limited)
    improved_capacity = processing_capacity(20, 16)
    improved_save = completions_for_new_arrivals(12, improved_capacity)
    drain_seconds = backlog_clear_seconds(1_440, 12, improved_capacity)

    assert (target, observed, tasks) == (100, 150, 15)
    assert (limited, scaled_workers, backlog_growth) == (8, 8, 4)
    assert (improved_capacity, improved_save) == (16, 12)
    assert backlog_clear_seconds(1_440, 12, 16) == 360
    assert backlog_clear_seconds(100, 12, 12) is None
    print('Target backlog per task: 100 messages')
    print('Observed backlog per task: 150; candidate tasks for target: 15')
    print('Completions with 20 worker jobs/s and 8 database saves/s: 8 jobs/s')
    print('Completions after doubling workers only: 8 jobs/s; backlog grows 4 jobs/s')
    print(f'Fictional 1,440-job backlog clear time after verified 16-save/s path: {drain_seconds} seconds')
    print('All values are local model arithmetic, not AWS capacity or service behavior.')


if __name__ == '__main__':
    run()
