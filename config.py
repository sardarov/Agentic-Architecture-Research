ARC_DATASET = {
    "easy": [
        "easy/66e6c45b.json",
        "easy/e21a174a.json",
        "easy/e74e1818.json",
        "easy/f3e62deb.json",
    ],
    "hard": [
        "hard/0c9aba6e.json",
        "hard/6f473927.json",   
        "hard/cd3c21df.json",
        "hard/e9b4f6fc.json",
    ]
}

SCHEDULING_DATASET = {
    "easy": [
        {
            "task_id": "sched_easy_1",
            "description": "Find a matching 1-hour slot between two individuals in the exact same timezone.",
            "constraints": "Alice is free from 09:00 to 11:00 UTC. Bob is free from 10:00 to 13:00 UTC. Find the earliest single 1-hour window where both are free.",
            "expected_output": "10:00-11:00 UTC"
        },
        {
            "task_id": "sched_easy_2",
            "description": "Find a matching 1-hour slot when one person has split availability.",
            "constraints": "Alice is free from 13:00 to 14:00 UTC. Bob is free from 09:00 to 11:00 UTC and again from 13:00 to 15:00 UTC. Find the earliest 1-hour window.",
            "expected_output": "13:00-14:00 UTC"
        },
        {
            "task_id": "sched_easy_3",
            "description": "Coordinate three people in the same timezone with a wide overlap.",
            "constraints": "Alice is free 14:00-17:00 UTC. Bob is free 15:00-18:00 UTC. Charlie is free 14:00-16:00 UTC. Identify the 1-hour slot where all three can meet.",
            "expected_output": "15:00-16:00 UTC"
        },
        {
            "task_id": "sched_easy_4",
            "description": "Find a sub-hour meeting duration (30 minutes).",
            "constraints": "Alice is free 08:30-10:00 UTC. Bob is free 09:00-10:30 UTC. Find the earliest possible 30-minute slot they share.",
            "expected_output": "09:00-09:30 UTC"
        }
    ],
    "hard": [
        {
            "task_id": "sched_hard_1",
            "description": "Multi-person coordination across different offset timezones.",
            "constraints": "Alice (UTC+0) is free 14:00-16:00 local time. Bob (UTC+1) is free 14:00-17:00 local time. Charlie (UTC-5) is free 09:00-11:00 local time. Identify the earliest 1-hour slot expressed in UTC time that accommodates everyone.",
            "expected_output": "14:00-15:00 UTC"
        },
        {
            "task_id": "sched_hard_2",
            "description": "Scheduling coordination involving strict corporate rules.",
            "constraints": "Alice (UTC+0) is free 09:00-17:00 UTC. Bob (UTC+0) is free 11:00-15:00 UTC. Corporate policy states no meetings can occur during the strict lunch hour of 12:00-13:00 UTC. Find the earliest 1-hour window they can meet.",
            "expected_output": "11:00-12:00 UTC"
        },
        {
            "task_id": "sched_hard_3",
            "description": "Day-of-the-week conditional dependency.",
            "constraints": "A project requires Alice, Bob, and their Manager to meet for 30 minutes. The Manager is only free on Tuesdays between 10:00-12:00 UTC. Alice is free Monday-Wednesday 09:00-11:00 UTC. Bob is free Tuesday-Thursday 10:30-14:00 UTC. Identify the exact day and 30-minute time slot for this meeting.",
            "expected_output": "Tuesday 10:30-11:00 UTC"
        },
        {
            "task_id": "sched_hard_4",
            "description": "Global distributed team coordination with overlapping local hours.",
            "constraints": "San Francisco (UTC-8) is free 08:00-10:00 local time. New York (UTC-5) is free 10:00-14:00 local time. London (UTC+0) is free 15:00-18:00 local time. Find the earliest 1-hour overlap expressed in UTC.",
            # SF: 16:00-18:00 UTC | NY: 15:00-19:00 UTC | LDN: 15:00-18:00 UTC
            "expected_output": "16:00-17:00 UTC"
        }
    ]
}

