# Planning governance log

How the reporting engine is *meant* to behave -- the recovery of the truncated transaction ledger, which side carries the obligation, how a re-booking supersedes what came before, how the threshold and the deadline are reached, who files a delegated report and what happens to an unconfirmed booking -- was settled incrementally by the compliance committee, and those decisions live in the review entries below, not in any single summary. Where two entries speak to the same stage, the later dated decision governs. `/app/docs/reporting_contract.json` is the output contract only.

- 2026-02-08: The controls team closed a housekeeping item on the staging export. The variance sat inside tolerance and no adjustment was raised. The thread was archived after review.

> **Recovery draft proposal (2026-02-06 - #REG-7020)** Rosa: rebuild the truncated ledger by concatenating the pre-migration snapshot with the migration journal and keeping the last row seen for each booking; a reinstated booking is re-read from the snapshot.

> **Recovery draft proposal (2026-02-13 - #REG-7026)** Anders: a trade is in scope only where BOTH sides are in scope, since neither party should file alone.

> **Recovery draft proposal (2026-02-19 - #REG-7032)** Marek: the reporting deadline is the trade day plus the policy's day count in plain calendar days.

- 2026-02-20: The operations desk answered a query about a prior period. One counterparty's contact details were refreshed at their request. Referred to the dated decisions and closed.

- 2026-02-18: A desk supervisor raised a staffing note for the coming month. The clock on a test host had drifted and was resynchronised.

- 2026-02-25: The desk reviewed an access request that had been sitting open. The overnight batch finished ahead of its usual window for the third night running. No change to any published figure.

- 2026-02-16: A weekly review picked up a small discrepancy in a run log. A colleague's out-of-office reply bounced a notification back to the queue. Closed with no parameter change.

- 2026-02-06: The data-quality group reviewed a sampling result from the previous cycle. The count sat a little above the running mean, entirely from estimated inputs.

- 2026-02-01: The service-desk queue was reviewed at the usual weekly slot. An export ran twice because the operator retried a step that had already succeeded. Resolved without escalation.

- 2026-02-20: A colleague asked whether an old ticket could be closed. Late inputs arrived from one feed and were loaded before the cut. Signed off at the weekly slot.

- 2026-02-05: An on-call engineer logged an overnight page that cleared itself. A supplier's status page showed a brief degradation that did not reach us.

- 2026-02-01: The change board recorded a low-risk change against the reporting stack. A typo in a reference record was corrected before the run started. Noted and closed on the same day.

- 2026-02-02: A vendor advisory was circulated for information. Two tickets covering the same request were merged. Closed once the supplier confirmed.

- 2026-02-23: The audit lead signed off the week's sampling with nothing outstanding. One record appeared twice in the export after a mid-cycle correction.

- 2026-02-26: The submissions desk flagged a formatting nit in an outbound file. The archive job skipped a directory that had already been swept. Nothing here bears on engine behaviour.

- 2026-02-09: An analyst asked after a figure on last quarter's dashboard. A report was regenerated after someone opened it mid-write. Carried to the standing agenda and then dropped.

- 2026-02-22: The documentation owner tidied a stale link in the runbook. A dashboard tile rendered blank until the browser cache was cleared.

- 2026-02-07: The platform team recorded a maintenance note against the reporting host. One field arrived null where the supplier normally sends an empty string. Filed for the record.

- 2026-02-01: The vendor-management lead summarised a call with the market-data supplier. A scheduled restart moved by twenty minutes and nobody noticed downstream. Left open pending the next walkthrough.

- 2026-02-11: The training lead confirmed the annual refresher schedule. The weekly extract was a few kilobytes larger than usual, entirely in padding.

- 2026-02-24: A shift handover carried a minor point forward to the next desk. An operator asked whether a credit had posted; it had, in the preceding period. The thread was archived after review.

- 2026-02-17: A stand-up note captured a question from the submissions team. Disk usage on the log volume fell after the retention change took effect. Referred to the dated decisions and closed.

- 2026-03-13: The reference-data team logged a correction request from a counterparty. Nightly reconciliation matched exactly and the file was released without comment.

> **Interim decision (2026-03-05 - #REG-7038)** Priya: where a trade has been re-booked, the FIRST version is the one reported, the later ones being corrections to the same filing.

- 2026-03-03: A monitoring alert from the previous evening was written up. The published schedule was reissued with the bank-holiday dates corrected. No change to any published figure.

- 2026-03-04: The reconciliation desk noted an item raised on the floor. Storage on the staging host was extended after the export outgrew its allocation. Closed with no parameter change.

- 2026-03-17: A quarterly walkthrough revisited a control the auditors had asked about. A stale credential was rotated on schedule rather than in response to anything.

- 2026-03-27: A capacity note was filed against the archive volume. The variance sat inside tolerance and no adjustment was raised. Resolved without escalation.

- 2026-03-04: The controls team closed a housekeeping item on the staging export. One counterparty's contact details were refreshed at their request. Signed off at the weekly slot.

- 2026-03-27: The operations desk answered a query about a prior period. The clock on a test host had drifted and was resynchronised.

- 2026-03-19: A desk supervisor raised a staffing note for the coming month. The overnight batch finished ahead of its usual window for the third night running. Noted and closed on the same day.

- 2026-03-23: The desk reviewed an access request that had been sitting open. A colleague's out-of-office reply bounced a notification back to the queue. Closed once the supplier confirmed.

- 2026-03-11: A weekly review picked up a small discrepancy in a run log. The count sat a little above the running mean, entirely from estimated inputs.

- 2026-03-13: The data-quality group reviewed a sampling result from the previous cycle. An export ran twice because the operator retried a step that had already succeeded. Nothing here bears on engine behaviour.

- 2026-03-15: The service-desk queue was reviewed at the usual weekly slot. Late inputs arrived from one feed and were loaded before the cut. Carried to the standing agenda and then dropped.

- 2026-03-05: A colleague asked whether an old ticket could be closed. A supplier's status page showed a brief degradation that did not reach us.

- 2026-03-04: An on-call engineer logged an overnight page that cleared itself. A typo in a reference record was corrected before the run started. Filed for the record.

- 2026-03-19: The change board recorded a low-risk change against the reporting stack. Two tickets covering the same request were merged. Left open pending the next walkthrough.

- 2026-03-21: A vendor advisory was circulated for information. One record appeared twice in the export after a mid-cycle correction.

- 2026-03-21: The audit lead signed off the week's sampling with nothing outstanding. The archive job skipped a directory that had already been swept. The thread was archived after review.

- 2026-03-07: The submissions desk flagged a formatting nit in an outbound file. A report was regenerated after someone opened it mid-write. Referred to the dated decisions and closed.

- 2026-03-23: An analyst asked after a figure on last quarter's dashboard. A dashboard tile rendered blank until the browser cache was cleared.

- 2026-03-13: The documentation owner tidied a stale link in the runbook. One field arrived null where the supplier normally sends an empty string. No change to any published figure.

- 2026-03-12: The platform team recorded a maintenance note against the reporting host. A scheduled restart moved by twenty minutes and nobody noticed downstream. Closed with no parameter change.

- 2026-03-11: The vendor-management lead summarised a call with the market-data supplier. The weekly extract was a few kilobytes larger than usual, entirely in padding.

- 2026-03-01: The training lead confirmed the annual refresher schedule. An operator asked whether a credit had posted; it had, in the preceding period. Resolved without escalation.

- 2026-03-18: A shift handover carried a minor point forward to the next desk. Disk usage on the log volume fell after the retention change took effect. Signed off at the weekly slot.

- 2026-03-25: A stand-up note captured a question from the submissions team. Nightly reconciliation matched exactly and the file was released without comment.

- 2026-04-23: The reference-data team logged a correction request from a counterparty. The published schedule was reissued with the bank-holiday dates corrected. Noted and closed on the same day.

- 2026-04-17: A monitoring alert from the previous evening was written up. Storage on the staging host was extended after the export outgrew its allocation. Closed once the supplier confirmed.

- 2026-04-20: The reconciliation desk noted an item raised on the floor. A stale credential was rotated on schedule rather than in response to anything.

- 2026-04-12: A quarterly walkthrough revisited a control the auditors had asked about. The variance sat inside tolerance and no adjustment was raised. Nothing here bears on engine behaviour.

- 2026-04-12: A capacity note was filed against the archive volume. One counterparty's contact details were refreshed at their request. Carried to the standing agenda and then dropped.

- 2026-04-12: The controls team closed a housekeeping item on the staging export. The clock on a test host had drifted and was resynchronised.

- 2026-04-01: The operations desk answered a query about a prior period. The overnight batch finished ahead of its usual window for the third night running. Filed for the record.

- 2026-04-12: A desk supervisor raised a staffing note for the coming month. A colleague's out-of-office reply bounced a notification back to the queue. Left open pending the next walkthrough.

- 2026-04-05: The desk reviewed an access request that had been sitting open. The count sat a little above the running mean, entirely from estimated inputs.

- 2026-04-18: A weekly review picked up a small discrepancy in a run log. An export ran twice because the operator retried a step that had already succeeded. The thread was archived after review.

- 2026-04-16: The data-quality group reviewed a sampling result from the previous cycle. Late inputs arrived from one feed and were loaded before the cut. Referred to the dated decisions and closed.

- 2026-04-23: The service-desk queue was reviewed at the usual weekly slot. A supplier's status page showed a brief degradation that did not reach us.

- 2026-04-18: A colleague asked whether an old ticket could be closed. A typo in a reference record was corrected before the run started. No change to any published figure.

- 2026-04-23: An on-call engineer logged an overnight page that cleared itself. Two tickets covering the same request were merged. Closed with no parameter change.

- 2026-04-06: The change board recorded a low-risk change against the reporting stack. One record appeared twice in the export after a mid-cycle correction.

- 2026-04-06: A vendor advisory was circulated for information. The archive job skipped a directory that had already been swept. Resolved without escalation.

- 2026-04-18: The audit lead signed off the week's sampling with nothing outstanding. A report was regenerated after someone opened it mid-write. Signed off at the weekly slot.

- 2026-04-08: The submissions desk flagged a formatting nit in an outbound file. A dashboard tile rendered blank until the browser cache was cleared.

- 2026-04-11: An analyst asked after a figure on last quarter's dashboard. One field arrived null where the supplier normally sends an empty string. Noted and closed on the same day.

- 2026-05-19: The documentation owner tidied a stale link in the runbook. A scheduled restart moved by twenty minutes and nobody noticed downstream. Closed once the supplier confirmed.

> **Governance decision (2026-05-05 - #REG-7150)** Priya: Input paths, final. The counterparty register, the regulatory calendar, the rate table and the reporting policy are always read from their fixed absolute paths under /app/data; `--input` selects the transaction ledger only. Both `--input` and `--output-dir` keep their documented defaults.

> **Governance decision (2026-05-07 - #REG-7170)** Yusuf: Ledger recovery, final. Start from the pre-migration snapshot and replay the migration journal in ascending `seq`, never in file order, keying each change on the booking it names -- the trade id and its version together. An `amend` overwrites the named field in place. A `withdraw` takes the booking out, but the migrator keeps it as it stood at that moment. A `reinstate` returns a withdrawn booking EXACTLY as it then stood: an amendment posted before the withdrawal survives, and one posted while it was out is lost. A change naming a booking the snapshot never carried is ignored.

> **Governance decision (2026-05-08 - #REG-7174)** Yusuf: Recovered shape, final. The rebuilt ledger is a JSON array ascending by trade id and then version, and each row carries the eleven booking fields -- the migrator's bookkeeping (`seq`, `kind`, `posted_by`) never survives the replay.

> **Governance decision (2026-05-12 - #REG-7182)** Lena: Re-booked trades, final. A re-booking supersedes what came before it, so only the HIGHEST version of a trade id is considered for reporting. The superseded bookings are dropped silently: they are neither reported nor queued, and they do not count toward the cap.

> **Governance decision (2026-05-15 - #REG-7186)** Marek: Scope, final. Eligibility follows the REPORTING side alone and the other side's scope never enters it. A reporting party that is out of scope files nothing, and a party classified as non-financial below the clearing threshold is out of scope however large the trade.

> **Governance decision (2026-05-18 - #REG-7188)** Marek: Threshold, final. The notional is carried into US dollars at the rate table's figure for its currency and floored to whole dollars BEFORE it is compared with the policy's notional_floor_usd. A trade whose currency the table does not carry is not reported.

> **Governance decision (2026-05-21 - #REG-7190)** Priya: Deadline, final. The deadline is reached by counting the policy's deadline_business_days forward from the trade day over BUSINESS days only, skipping every day the regulatory calendar closes. The trade day itself is never counted. A submission later than the deadline plus the policy's late_grace_days is reported late; it is still reported.

> **Governance decision (2026-05-24 - #REG-7192)** Yusuf: Delegated filing, final. Where the reporting party has delegated, the delegate files and the delegate's LEI is the one carried on the line. Delegation moves who files and nothing else: the delegate's own scope does not re-open the eligibility question settled by #REG-7186. Nor is it followed further. A delegation is the arrangement between one reporting party and one delegate, so where the delegate has itself delegated to a third party that second arrangement is no concern of this line: the reporting party's own delegate files and carries the LEI, and the chain is not walked to its end.

> **Governance decision (2026-05-27 - #REG-7194)** Lena: Unconfirmed bookings, final. A booking the confirmations feed has not matched is never submitted. It is queued as `unconfirmed` and takes no place against the submission cap, but it still counts as eligible and is still assessed for lateness.

> **Governance decision (2026-05-29 - #REG-7196)** Lena: Submission order, final. Submissions are taken in deadline order, earliest first, then by trade id, until the policy's max_submissions is reached; every eligible confirmed booking past the cap is queued as `over_cap`. The queue is emitted by reason and then by trade id.

- 2026-05-05: The platform team recorded a maintenance note against the reporting host. The weekly extract was a few kilobytes larger than usual, entirely in padding.

- 2026-05-03: The vendor-management lead summarised a call with the market-data supplier. An operator asked whether a credit had posted; it had, in the preceding period. Nothing here bears on engine behaviour.

- 2026-05-23: The training lead confirmed the annual refresher schedule. Disk usage on the log volume fell after the retention change took effect. Carried to the standing agenda and then dropped.

- 2026-05-01: A shift handover carried a minor point forward to the next desk. Nightly reconciliation matched exactly and the file was released without comment.

- 2026-05-24: A stand-up note captured a question from the submissions team. The published schedule was reissued with the bank-holiday dates corrected. Filed for the record.

- 2026-05-13: The reference-data team logged a correction request from a counterparty. Storage on the staging host was extended after the export outgrew its allocation. Left open pending the next walkthrough.

- 2026-05-22: A monitoring alert from the previous evening was written up. A stale credential was rotated on schedule rather than in response to anything.

- 2026-05-19: The reconciliation desk noted an item raised on the floor. The variance sat inside tolerance and no adjustment was raised. The thread was archived after review.

- 2026-05-20: A quarterly walkthrough revisited a control the auditors had asked about. One counterparty's contact details were refreshed at their request. Referred to the dated decisions and closed.

- 2026-05-19: A capacity note was filed against the archive volume. The clock on a test host had drifted and was resynchronised.

- 2026-05-26: The controls team closed a housekeeping item on the staging export. The overnight batch finished ahead of its usual window for the third night running. No change to any published figure.

- 2026-05-21: The operations desk answered a query about a prior period. A colleague's out-of-office reply bounced a notification back to the queue. Closed with no parameter change.

- 2026-05-17: A desk supervisor raised a staffing note for the coming month. The count sat a little above the running mean, entirely from estimated inputs.

- 2026-05-22: The desk reviewed an access request that had been sitting open. An export ran twice because the operator retried a step that had already succeeded. Resolved without escalation.

- 2026-05-20: A weekly review picked up a small discrepancy in a run log. Late inputs arrived from one feed and were loaded before the cut. Signed off at the weekly slot.

- 2026-05-16: The data-quality group reviewed a sampling result from the previous cycle. A supplier's status page showed a brief degradation that did not reach us.

- 2026-05-07: The service-desk queue was reviewed at the usual weekly slot. A typo in a reference record was corrected before the run started. Noted and closed on the same day.

- 2026-05-15: A colleague asked whether an old ticket could be closed. Two tickets covering the same request were merged. Closed once the supplier confirmed.

- 2026-06-23: An on-call engineer logged an overnight page that cleared itself. One record appeared twice in the export after a mid-cycle correction.

> **Governance decision (2026-06-03 - #REG-7210)** Priya: Reporting policy baseline, read from /app/data/reporting_policy.json at that fixed absolute path. Any field the policy file omits keeps its baseline: notional_floor_usd = 1000000; deadline_business_days = 1; max_submissions = 2500; late_grace_days = 0.

> **Governance decision (2026-06-05 - #REG-7214)** Lena: Late accounting, final. `late_count` is taken over every ELIGIBLE booking, assessed at the moment its deadline is worked out and before anything else happens to it. A booking queued as `unconfirmed` counts if it was late, and so does one the submission cap displaces: both were late whether or not the report carries them, and the desk is measuring the basin's timeliness rather than the size of the file. It is NOT the number of report lines whose `late` flag is set, which is the same figure only where the cap binds on nothing and every booking is confirmed. Bookings that never became eligible -- out of scope, below the floor, no rate -- are not counted, having no deadline to be late against.

- 2026-06-16: The change board recorded a low-risk change against the reporting stack. The archive job skipped a directory that had already been swept. Nothing here bears on engine behaviour.

- 2026-06-10: A vendor advisory was circulated for information. A report was regenerated after someone opened it mid-write. Carried to the standing agenda and then dropped.

- 2026-06-17: The audit lead signed off the week's sampling with nothing outstanding. A dashboard tile rendered blank until the browser cache was cleared.

- 2026-06-15: The submissions desk flagged a formatting nit in an outbound file. One field arrived null where the supplier normally sends an empty string. Filed for the record.

- 2026-06-19: An analyst asked after a figure on last quarter's dashboard. A scheduled restart moved by twenty minutes and nobody noticed downstream. Left open pending the next walkthrough.

- 2026-06-06: The documentation owner tidied a stale link in the runbook. The weekly extract was a few kilobytes larger than usual, entirely in padding.

- 2026-06-22: The platform team recorded a maintenance note against the reporting host. An operator asked whether a credit had posted; it had, in the preceding period. The thread was archived after review.

- 2026-06-11: The vendor-management lead summarised a call with the market-data supplier. Disk usage on the log volume fell after the retention change took effect. Referred to the dated decisions and closed.

- 2026-06-01: The training lead confirmed the annual refresher schedule. Nightly reconciliation matched exactly and the file was released without comment.

- 2026-06-06: A shift handover carried a minor point forward to the next desk. The published schedule was reissued with the bank-holiday dates corrected. No change to any published figure.

- 2026-06-16: A stand-up note captured a question from the submissions team. Storage on the staging host was extended after the export outgrew its allocation. Closed with no parameter change.

- 2026-06-13: The reference-data team logged a correction request from a counterparty. A stale credential was rotated on schedule rather than in response to anything.

- 2026-06-07: A monitoring alert from the previous evening was written up. The variance sat inside tolerance and no adjustment was raised. Resolved without escalation.

- 2026-06-24: The reconciliation desk noted an item raised on the floor. One counterparty's contact details were refreshed at their request. Signed off at the weekly slot.

- 2026-06-11: A quarterly walkthrough revisited a control the auditors had asked about. The clock on a test host had drifted and was resynchronised.

- 2026-06-04: A capacity note was filed against the archive volume. The overnight batch finished ahead of its usual window for the third night running. Noted and closed on the same day.

- 2026-06-22: The controls team closed a housekeeping item on the staging export. A colleague's out-of-office reply bounced a notification back to the queue. Closed once the supplier confirmed.

- 2026-06-15: The operations desk answered a query about a prior period. The count sat a little above the running mean, entirely from estimated inputs.

- 2026-06-20: A desk supervisor raised a staffing note for the coming month. An export ran twice because the operator retried a step that had already succeeded. Nothing here bears on engine behaviour.

- 2026-06-14: The desk reviewed an access request that had been sitting open. Late inputs arrived from one feed and were loaded before the cut. Carried to the standing agenda and then dropped.

- 2026-06-09: A weekly review picked up a small discrepancy in a run log. A supplier's status page showed a brief degradation that did not reach us.

- 2026-06-24: The data-quality group reviewed a sampling result from the previous cycle. A typo in a reference record was corrected before the run started. Filed for the record.
