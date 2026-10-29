# Missing-source follow-up

Authorised separately on 29 October 2026 after the bounded audit finished. This pass attempts all 255 deduplicated sources unavailable for 857 original/replication sides, then checks affected rows against newly retrieved primary sources. The original run deadlines and completion record remain historical records.

Acquisition uses OpenCode's `opencode/deepseek-v4.1-flash-free` with high reasoning, through the T3 child task recorded in `state.json`. It follows `/home/lukas/agent-skills/download-paper/SKILL.md`, including the actual download script, identity checks and a finite fallback sweep. Linux does not provide the skill's macOS signed-in Chrome route. No paid acquisition or incremental model charges are authorised for this pass.

`missing_sources.json` is deduplicated by normalised DOI, then URL, then reference, and ordered by affected-side count. It contains neutral extraction targets, without shipped statistics. `baseline.json` records the pre-follow-up hashes and counts. Acquisition outcomes and heartbeat belong in `acquisitions/` and `progress.json`; full source artifacts and logs stay outside Git.

One acquisition task owns its outputs. The parent owns source acceptance, blind extraction dispatch, comparison, evidence validation and Git. Do not duplicate active work. Each source gets one script attempt, with at most six download processes and a 150-second process-group timeout. A fallback may try at most two new URLs per source. Cancel on five minutes without completed-source progress, ten consecutive infrastructure failures, or the 100-minute acquisition ceiling. Do not retry unchanged access failures.

For retrieved sources, verify identity and full-text completeness independently, then supply only the neutral target plus source to a fresh blind extractor. Preserve all previously completed sides and verdicts. Verify exact quotations, target identity, analytic sample role, requested metric and p-value bound before accepting a comparison. Newly supported disagreements need independent adjudication; source retrieval alone establishes no correction. Keep the six terminal scope holds unless new evidence specifically resolves them. Never change the shipped workbook or pipeline.

Record follow-up findings separately with their provenance, then reconcile any accepted updates with the audit exports and report. Preserve the completed audit's original headline counts as the baseline. Archive new full texts privately, verify the upload, and commit/push only scripts, metadata, short evidence and results.
