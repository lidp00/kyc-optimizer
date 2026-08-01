from abc import ABC, abstractmethod
from typing import List, Dict, Any
from models import Ticket, Agent, ScheduledTask, SolverResult

class BaseSolver(ABC):
    """
    Abstract base class defining a uniform interface for all scheduling solvers.
    Ensures that both naive heuristics and advanced optimization models 
    can be used interchangeably by the simulator.
    """

    @abstractmethod
    def solve(self, tickets: List[Ticket], agents: List[Agent], current_time: int) -> SolverResult:
        """
        Calculates the optimal task assignment based on the current system state.

        Args:
            tickets (List[Ticket]): Tickets currently waiting in the queue.
            agents (List[Agent]): Employees available for work.
            current_time (int): Current simulation time in minutes.

        Returns:
            SolverResult: An instance of SolverResult containing the generated schedule and metrics.
        """
        pass

class FifoSolver(BaseSolver):
    """
    Naive First-In, First-Out scheduling algorithm.
    Assigns the oldest ticket to the first available agent with matching skills.
    """

    def solve(self, tickets: List[Ticket], agents: List[Agent], current_time: int) -> SolverResult:
        # Initialize an empty schedule for every agent
        schedule = {agent.agent_id: [] for agent in agents}
        unassigned_tickets = []

        # 1. Sort tickets strictly by arrival time (Oldest first)
        sorted_tickets = sorted(tickets, key=lambda t: t.arrival_minutes)

        # 2. Track when each agent is free to take a new task.
        agent_available_time = {
            agent.agent_id: max(current_time, agent.shift_start) for agent in agents
        }

        # 3. Assign tickets one by one
        for ticket in sorted_tickets:
            assigned = False
            
            for agent in agents:
                # Check skills (Language and Tier)
                if ticket.required_language not in agent.languages:
                    continue
                if ticket.tier > agent.max_tier:
                    continue

                # The agent can start either when they finish their previous task, 
                # or when the ticket physically arrives - whichever happens later.
                time_cursor = max(agent_available_time[agent.agent_id], ticket.arrival_minutes)

                # Calculate the total duration of all subtasks in the ticket
                total_duration = sum(task.duration_minutes for task in ticket.subtasks)
                
                # If the ticket cannot be finished before the shift ends, skip this agent
                if time_cursor + total_duration > agent.shift_end:
                    continue

                # Process all subtasks sequentially
                for task in ticket.subtasks:
                    schedule[agent.agent_id].append(
                        ScheduledTask(
                            ticket_id=ticket.ticket_id,
                            task_id=task.task_id,
                            task_name=task.name,
                            start_time=time_cursor,
                            end_time=time_cursor + task.duration_minutes
                        )
                    )
                    # Move the cursor forward in time
                    time_cursor += task.duration_minutes

                # Update agent's availability so they can't take two things at once
                agent_available_time[agent.agent_id] = time_cursor
                assigned = True
                
                # Stop looking for agents for this ticket, move to the next ticket
                break 

            if not assigned:
                unassigned_tickets.append(ticket)

        # 4. Pack results into our explicit data contract
        return SolverResult(
            schedule=schedule,
            metrics={
                "unassigned_count": len(unassigned_tickets)
            }
        )