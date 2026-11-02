Act as an independent reviewer. Do not edit files.

Review the other agent's committed diff against the exact base commit and collaboration/TASK.md. Focus on correctness, security, data loss, concurrency, compatibility, error handling, and missing tests. For this project also check that no drawing discrepancy was silently resolved and no provisional content was described as approved. Ignore harmless style preferences.

For each actionable finding provide:
- severity
- file and line/symbol
- failure mode
- evidence or reproducer
- smallest safe remedy
- confidence

If no actionable finding exists, say so explicitly. Do not invent a finding to appear balanced.
