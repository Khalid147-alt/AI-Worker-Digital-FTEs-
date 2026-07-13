# Test Task: Ralph Loop Verification

**Task ID**: `TEST_RALPH_LOOP`

## Objective
Verify that the Ralph Loop correctly iterates, maintains context via the Plan file, and stops when complete.

## Steps
1.  Create a file `d:/Hackathon0/temp_step_1.txt` with content "Step 1 Done".
2.  Create a file `d:/Hackathon0/temp_step_2.txt` with content "Step 2 Done".
3.  Create a file `d:/Hackathon0/temp_step_3.txt` with content "Step 3 Done".
4.  Verify all 3 files exist.
5.  Create `d:/Hackathon0/AI_Employee_Vault/Done/TEST_RALPH_LOOP.md` with:
    -   Summary of operations.
    -   Timestamp.

## Expected Behavior
- Agent should create `Plans/TEST_RALPH_LOOP_PLAN.md`.
- Agent should run ~5 iterations (Planning + 3 Actions + Verification).
- Loop should exit successfully.
