import unittest
from scripts.validation.loop_policy import check_loop_policy


TEXT = '''---
name: loop-example
description: Example formatting fixture.
user-invocable: true
disable-model-invocation: false
---
# Example
## Use when
A scoped task.
## Inputs
Target.
## Workflow
Do the task.
## Output
PASS FAIL BLOCKED NOT_RUN.
## Boundaries and evidence
Stop when asked. Never
sleep to consume time.
## Example
/loop-example task
'''


class SkillFormattingTests(unittest.TestCase):
    def test_wrapped_never_sleep_policy_is_recognized_without_changing_meaning(self):
        self.assertEqual(check_loop_policy(TEXT,'loop-example','fixture'),[])

    def test_absent_policy_and_prefix_word_do_not_satisfy_it(self):
        for replacement in ('Do not wait','Never sleepy'):
            text=TEXT.replace('Never\nsleep',replacement)
            self.assertTrue(any('never-sleep' in e for e in check_loop_policy(text,'loop-example','fixture')))
