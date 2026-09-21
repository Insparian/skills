"""Hypothetical recurring-check timings, not a measurement of Codex scheduling."""
import json
import math


def simulate(interval=30, first_reset=302, rounds=4, work_minutes=60,
             window_minutes=300, later_reset_delay=0, missed_ticks=()):
    if interval <= 0 or rounds < 1 or work_minutes <= 0 or work_minutes >= window_minutes:
        raise ValueError('invalid simulation inputs')
    starts = [0]
    events = []
    ready = first_reset
    for index in range(1, rounds):
        tick = math.ceil(ready / interval) * interval
        while tick in missed_ticks:
            tick += interval
        events.append(dict(round=index + 1, quota_restored_at_minute=ready,
                           resumed_at_minute=tick, extra_wait_minutes=tick - ready))
        starts.append(tick)
        ready = tick + window_minutes + later_reset_delay
    return dict(interval_minutes=interval, events=events, completed_at_minute=starts[-1] + work_minutes,
                extra_wait_minutes=sum(e['extra_wait_minutes'] for e in events),
                scheduler_assumption='Each unmissed future recurrence executes once quota is usable; not platform-tested.')


def main():
    scenarios = {}
    for delay in (2, 12):
        scenarios['first_reset_' + str(delay) + '_minutes_late'] = [simulate(interval=i, first_reset=300 + delay) for i in (300, 305, 310, 30)]
    scenarios['one_post_reset_tick_also_missed'] = simulate(missed_ticks=(330,))
    scenarios['weekly_block'] = simulate(first_reset=10080, rounds=2)
    scenarios['every_window_two_minutes_late'] = simulate(later_reset_delay=2)
    print(json.dumps({'simulation_only': True, 'origin': '22:00, minute zero', 'scenarios': scenarios}, indent=2))


if __name__ == '__main__':
    main()
