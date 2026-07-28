from dataclasses import dataclass
from typing import List, Set

@dataclass
class SubTask:
    """
    Represents a single specific step in the workflow (e.g., OCR check, AML Screening).

    Attributes:
        task_id (str): Unique identifier for the sub-task.
        name (str): The name of the operation.
        duration_minutes (int): Estimated time required to complete this step.
    """
    task_id: str
    name: str
    duration_minutes: int

@dataclass
class Ticket:
    """
    Represents a complete KYC case from a client.

    Attributes:
        ticket_id (str): Unique identifier for the case.
        subtasks (List[SubTask]): A sequential list of steps required to complete the ticket.
        required_language (str): Language required to process the case (e.g., 'CZ', 'EN').
        tier (int): Complexity level (1 = Standard case, 2 = Complex VIP case).
        arrival_minutes (int): Absolute time the ticket entered the system (minutes from start).
        deadline_minutes (int): Absolute deadline time to avoid SLA breach.
        penalty_per_minute (float): Financial penalty in EUR for every minute of delay.
    """
    ticket_id: str
    subtasks: List[SubTask]
    required_language: str
    tier: int
    arrival_minutes: int
    deadline_minutes: int
    penalty_per_minute: float

@dataclass
class Agent:
    """
    Represents an employee in the KYC department.

    Attributes:
        agent_id (str): Unique identifier for the employee.
        languages (Set[str]): A set of languages the agent can speak (e.g., {'CZ', 'EN'}).
        max_tier (int): The maximum complexity level the agent is certified to handle (1 or 2).
        shift_start (int): Shift start time in minutes from the simulation start (e.g., 0 for 8:00 AM).
        shift_end (int): Shift end time in minutes (e.g., 480 for 4:00 PM).
    """
    agent_id: str
    languages: Set[str]
    max_tier: int
    shift_start: int
    shift_end: int