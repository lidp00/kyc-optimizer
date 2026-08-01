from models import Agent, Ticket, SubTask
from solvers import FifoSolver

def test_fifo_solver_assigns_ticket_to_first_available_agent():
    # 1. ARRANGE (Setup data)
    agent = Agent(agent_id="A1", languages={"EN"}, max_tier=1, shift_start=0, shift_end=480)
    task = SubTask(task_id="T1", name="Check", duration_minutes=15)
    
    ticket = Ticket(
        ticket_id="K1",
        subtasks=[task],
        required_language="EN",
        tier=1,
        arrival_minutes=10,
        deadline_minutes=120,
        penalty_per_minute=1.0
    )

    solver = FifoSolver()

    # 2. ACT (Execute logic)
    # We call the solver at current_time = 10
    result = solver.solve(tickets=[ticket], agents=[agent], current_time=10)

    # 3. ASSERT (Verify outcome)
    # Checking the SolverResult object properties
    assert result.schedule is not None
    assert "A1" in result.schedule
    assert len(result.schedule["A1"]) == 1

    # Verify that there are no unassigned tickets
    assert len(result.metrics) == 1
    assert result.metrics["unassigned_count"] == 0

    # Verify the task details using the ScheduledTask object attributes
    assigned_task = result.schedule["A1"][0]
    assert assigned_task.ticket_id == "K1"
    assert assigned_task.task_id == "T1"
    assert assigned_task.start_time == 10
    assert assigned_task.end_time == 25

def test_fifo_solver_skips_ineligible_agent():
    # 1. ARRANGE
    # Agent 1 speaks only German, Agent 2 speaks English
    agent_bad = Agent(agent_id="A_BAD", languages={"DE"}, max_tier=1, shift_start=0, shift_end=480)
    agent_good = Agent(agent_id="A_GOOD", languages={"EN"}, max_tier=1, shift_start=0, shift_end=480)
    
    task = SubTask(task_id="T1", name="Check", duration_minutes=15)
    ticket = Ticket(
        ticket_id="K1",
        subtasks=[task],
        required_language="EN",
        tier=1,
        arrival_minutes=10,
        deadline_minutes=120,
        penalty_per_minute=1.0
    )

    solver = FifoSolver()

    # 2. ACT
    # Pass both agents to the solver
    result = solver.solve(tickets=[ticket], agents=[agent_bad, agent_good], current_time=10)

    # 3. ASSERT
    assert len(result.schedule["A_BAD"]) == 0    # Bad agent has no tasks
    assert len(result.schedule["A_GOOD"]) == 1   # Good agent got the task
    assert result.schedule["A_GOOD"][0].ticket_id == "K1"
    assert result.metrics["unassigned_count"] == 0

def test_fifo_solver_leaves_ticket_unassigned_if_no_eligible_agent():
    # 1. ARRANGE
    agent = Agent(agent_id="A1", languages={"ES"}, max_tier=1, shift_start=0, shift_end=480)
    task = SubTask(task_id="T1", name="Check", duration_minutes=15)
    
    ticket = Ticket(
        ticket_id="K1",
        subtasks=[task],
        required_language="EN", # Agent only speaks ES
        tier=1,
        arrival_minutes=10,
        deadline_minutes=120,
        penalty_per_minute=1.0
    )

    solver = FifoSolver()

    # 2. ACT
    result = solver.solve(tickets=[ticket], agents=[agent], current_time=10)

    # 3. ASSERT
    assert len(result.schedule["A1"]) == 0        # Agent didn't get it
    assert result.metrics["unassigned_count"] == 1 # Ticket remains unassigned

def test_fifo_solver_skips_agent_with_insufficient_tier():
    # 1. ARRANGE
    agent = Agent(agent_id="A1", languages={"EN"}, max_tier=1, shift_start=0, shift_end=480)
    task = SubTask(task_id="T1", name="Check", duration_minutes=15)
    
    ticket = Ticket(
        ticket_id="K1",
        subtasks=[task],
        required_language="EN",
        tier=2, # Ticket requires tier 2, agent can only handle tier 1
        arrival_minutes=10,
        deadline_minutes=120,
        penalty_per_minute=1.0
    )

    solver = FifoSolver()

    # 2. ACT
    result = solver.solve(tickets=[ticket], agents=[agent], current_time=10)

    # 3. ASSERT
    assert len(result.schedule["A1"]) == 0
    assert result.metrics["unassigned_count"] == 1

def test_fifo_solver_respects_ticket_arrival_time():
    # 1. ARRANGE
    # Agent is available immediately from minute 0
    agent = Agent(agent_id="A1", languages={"EN"}, max_tier=1, shift_start=0, shift_end=480)
    task = SubTask(task_id="T1", name="Check", duration_minutes=15)
    
    # The ticket doesn't arrive until minute 100
    ticket = Ticket(
        ticket_id="K1",
        subtasks=[task],
        required_language="EN",
        tier=1,
        arrival_minutes=100, 
        deadline_minutes=200,
        penalty_per_minute=1.0
    )

    solver = FifoSolver()

    # 2. ACT
    # We call the solver at current_time = 0
    result = solver.solve(tickets=[ticket], agents=[agent], current_time=0)

    # 3. ASSERT
    assert len(result.schedule["A1"]) == 1
    assigned_task = result.schedule["A1"][0]
    
    # The task must not start at minute 0, it must wait for the arrival at minute 100
    assert assigned_task.start_time == 100
    assert assigned_task.end_time == 115


def test_fifo_solver_respects_shift_end():
    # 1. ARRANGE
    # Agent has a very short shift - it ends at minute 60
    agent = Agent(agent_id="A1", languages={"EN"}, max_tier=1, shift_start=0, shift_end=60)
    
    # The task takes 90 minutes (longer than the agent's total remaining shift)
    task = SubTask(task_id="T1", name="Check", duration_minutes=90) 
    
    ticket = Ticket(
        ticket_id="K1",
        subtasks=[task],
        required_language="EN",
        tier=1,
        arrival_minutes=0,
        deadline_minutes=120,
        penalty_per_minute=1.0
    )

    solver = FifoSolver()

    # 2. ACT
    result = solver.solve(tickets=[ticket], agents=[agent], current_time=0)

    # 3. ASSERT
    # The agent must not receive the task because they cannot finish it before their shift ends
    assert len(result.schedule["A1"]) == 0
    assert result.metrics["unassigned_count"] == 1