"""Compatibility facade for the retained smoke fixture API.

Implementation lives in smoke.fixtures and smoke.grading. Keep existing imports
working for runtime_smoke, callers and retained evidence tools.
"""
if __package__:
    from .smoke.fixtures import NEW_SKILLS,REGRESSION_SKILLS,SMOKE_SKILLS,CALC,RECORDS,RUBRIC,BASELINE,CANDIDATE,TASKS,prepare,snapshot
    from .smoke.grading import command,verification_directory,metrics_match,grade
else:
    from smoke.fixtures import NEW_SKILLS,REGRESSION_SKILLS,SMOKE_SKILLS,CALC,RECORDS,RUBRIC,BASELINE,CANDIDATE,TASKS,prepare,snapshot
    from smoke.grading import command,verification_directory,metrics_match,grade
