# Planning governance log

How the reporting engine is *meant* to behave -- the recovery of the truncated transaction ledger, which side carries the obligation, how a re-booking supersedes what came before, how the threshold and the deadline are reached, who files a delegated report and what happens to an unconfirmed booking -- was settled incrementally by the compliance committee, and those decisions live in the review entries below, not in any single summary. Several stages deliberately depart from the intuitive reading, and which ones they are is settled in the entries below rather than here. The February draft proposals were revisited during the 2026-05 controls review and several were reversed; where a draft or interim conflicts with a later decision, the later dated decision governs. `/app/docs/reporting_contract.json` is the output contract only.

- 2026-02-08: A stand-up note carried forward a routine observation. A question raised on the floor was withdrawn once the entry was reread. The thread was archived after review.

> **Recovery draft proposal (2026-02-06 - #REG-7020)** Rosa: rebuild the truncated ledger by concatenating the pre-migration snapshot with the migration journal and keeping the last row seen for each booking; a reinstated booking is re-read from the snapshot *(Superseded -- reversed in the 2026-05 controls review.)*

> **Recovery draft proposal (2026-02-13 - #REG-7026)** Anders: a trade is in scope only where BOTH sides are in scope, since neither party should file alone *(Superseded -- reversed in the 2026-05 controls review.)*

> **Recovery draft proposal (2026-02-19 - #REG-7032)** Marek: the reporting deadline is the trade day plus the policy's day count in plain calendar days *(Superseded -- reversed in the 2026-05 controls review.)*

- 2026-02-20: A stand-up note spot-checked a routine observation. The variance sat inside tolerance and no adjustment was raised.

- 2026-02-18: The controls team signed off a routine observation. A query about a prior-period entry was answered from the published schedule. No follow-up was requested.

- 2026-02-25: A weekly review spot-checked a routine observation. Nightly reconciliation matched exactly and the file was released without comment.

- 2026-02-16: The controls team carried forward a routine observation. Nightly reconciliation matched exactly and the file was released without comment. No action was carried forward.

- 2026-02-06: The controls team spot-checked a routine observation. The count sat a little above the running mean, entirely from estimated inputs. The thread was archived after review.

- 2026-02-01: The audit lead signed off a routine observation. Late inputs arrived from one feed and were loaded before the cut. The desk confirmed no downstream impact.

- 2026-02-20: A shift handover raised and closed a routine observation. Late inputs arrived from one feed and were loaded before the cut. Referred to the dated decisions and closed.

- 2026-02-05: A weekly review spot-checked a routine observation. A query about a prior-period entry was answered from the published schedule.

- 2026-02-01: The reconciliation desk logged a routine observation. A duplicate order was cancelled at source and never reached the run. Closed with no parameter change.

- 2026-02-02: The audit lead noted a routine observation. A typo in a reference record was corrected before the run started. The desk confirmed no downstream impact.

- 2026-02-23: A reviewer on shift reviewed a routine observation. The overnight window ran long behind an unrelated platform patch. The desk confirmed no downstream impact.

- 2026-02-26: The exceptions queue owner signed off a routine observation. Storage on the staging host was extended after the export outgrew its allocation. No follow-up was requested.

- 2026-02-09: A shift handover opened a query on a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine. Referred to the dated decisions and closed.

- 2026-02-22: The platform team recorded a routine observation. A question raised on the floor was withdrawn once the entry was reread. The desk confirmed no downstream impact.

- 2026-02-07: The reconciliation desk signed off a routine observation. A batch retried once after a transient timeout and completed on the second pass. No follow-up was requested.

- 2026-02-01: The duty analyst spot-checked a routine observation. The overnight window ran long behind an unrelated platform patch. Nothing here bears on engine behaviour.

- 2026-02-11: The operations desk opened a query on a routine observation. An operator asked whether a credit had posted; it had, in the preceding period. Referred to the dated decisions and closed.

- 2026-02-24: The controls team noted a routine observation. One record appeared twice in the export after a mid-cycle correction. The thread was archived after review.

- 2026-02-17: A stand-up note raised and closed a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine.

- 2026-03-13: An on-call engineer opened a query on a routine observation. A duplicate order was cancelled at source and never reached the run.

> **Interim decision (2026-03-05 - #REG-7038)** Priya: where a trade has been re-booked, the FIRST version is the one reported, the later ones being corrections to the same filing *(Revised -- see the 2026-05 controls review.)*

- 2026-03-03: The reconciliation desk raised and closed a routine observation. The variance sat inside tolerance and no adjustment was raised. Filed for the record.

- 2026-03-04: The exceptions queue owner carried forward a routine observation. Storage on the staging host was extended after the export outgrew its allocation. Referred to the dated decisions and closed.

- 2026-03-17: A shift handover filed a routine observation. One record appeared twice in the export after a mid-cycle correction.

- 2026-03-27: The controls team carried forward a routine observation. Late inputs arrived from one feed and were loaded before the cut. No follow-up was requested.

- 2026-03-04: The exceptions queue owner logged a routine observation. A batch retried once after a transient timeout and completed on the second pass. Filed for the record.

- 2026-03-27: The reconciliation desk filed a routine observation. An operator asked whether a credit had posted; it had, in the preceding period.

- 2026-03-19: The duty analyst carried forward a routine observation. The overnight window ran long behind an unrelated platform patch.

- 2026-03-23: A reviewer on shift raised and closed a routine observation. The count sat a little above the running mean, entirely from estimated inputs. No follow-up was requested.

- 2026-03-11: The exceptions queue owner recorded a routine observation. A typo in a reference record was corrected before the run started. The desk confirmed no downstream impact.

- 2026-03-13: The platform team opened a query on a routine observation. One record appeared twice in the export after a mid-cycle correction. Filed for the record.

- 2026-03-15: A shift handover signed off a routine observation. A query about a prior-period entry was answered from the published schedule.

- 2026-03-05: A weekly review logged a routine observation. Storage on the staging host was extended after the export outgrew its allocation. The thread was archived after review.

- 2026-03-04: A shift handover recorded a routine observation. An operator asked whether a credit had posted; it had, in the preceding period. Referred to the dated decisions and closed.

- 2026-03-19: The audit lead raised and closed a routine observation. Storage on the staging host was extended after the export outgrew its allocation. Referred to the dated decisions and closed.

- 2026-03-21: The operations desk spot-checked a routine observation. A query about a prior-period entry was answered from the published schedule. The thread was archived after review.

- 2026-03-21: The exceptions queue owner opened a query on a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine. The thread was archived after review.

- 2026-03-07: A shift handover recorded a routine observation. Storage on the staging host was extended after the export outgrew its allocation. Nothing here bears on engine behaviour.

- 2026-03-23: The audit lead raised and closed a routine observation. Nightly reconciliation matched exactly and the file was released without comment. No action was carried forward.

- 2026-03-13: The platform team opened a query on a routine observation. One record appeared twice in the export after a mid-cycle correction. Nothing here bears on engine behaviour.

- 2026-03-12: A shift handover noted a routine observation. Storage on the staging host was extended after the export outgrew its allocation.

- 2026-03-11: The reconciliation desk logged a routine observation. Late inputs arrived from one feed and were loaded before the cut. The desk confirmed no downstream impact.

- 2026-03-01: A weekly review carried forward a routine observation. Dashboard tiles lagged the refresh; traced to cache staleness rather than the engine. The thread was archived after review.

- 2026-03-18: The exceptions queue owner noted a routine observation. Nightly reconciliation matched exactly and the file was released without comment. No action was carried forward.

- 2026-03-25: The audit lead filed a routine observation. Late inputs arrived from one feed and were loaded before the cut. Referred to the dated decisions and closed.

- 2026-04-23: A stand-up note carried forward a routine observation. One record appeared twice in the export after a mid-cycle correction. The thread was archived after review.

- 2026-04-17: A shift handover carried forward a routine observation. An operator asked whether a credit had posted; it had, in the preceding period.

- 2026-04-20: A stand-up note raised and closed a routine observation. The downstream vendor confirmed receipt inside the agreed window. The thread was archived after review.

- 2026-04-12: The exceptions queue owner filed a routine observation. An operator asked whether a credit had posted; it had, in the preceding period. No action was carried forward.

- 2026-04-12: The operations desk recorded a routine observation. The variance sat inside tolerance and no adjustment was raised.

- 2026-04-12: The exceptions queue owner spot-checked a routine observation. The variance sat inside tolerance and no adjustment was raised. Nothing here bears on engine behaviour.

- 2026-04-01: The audit lead filed a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. No follow-up was requested.

- 2026-04-12: The controls team reviewed a routine observation. Late inputs arrived from one feed and were loaded before the cut. Nothing here bears on engine behaviour.

- 2026-04-05: A weekly review logged a routine observation. Nightly reconciliation matched exactly and the file was released without comment.

- 2026-04-18: The reconciliation desk logged a routine observation. A question raised on the floor was withdrawn once the entry was reread.

- 2026-04-16: A weekly review recorded a routine observation. An operator asked whether a credit had posted; it had, in the preceding period. Referred to the dated decisions and closed.

- 2026-04-23: A shift handover carried forward a routine observation. Storage on the staging host was extended after the export outgrew its allocation. Closed with no parameter change.

- 2026-04-18: A stand-up note recorded a routine observation. The variance sat inside tolerance and no adjustment was raised. Nothing here bears on engine behaviour.

- 2026-04-23: An on-call engineer signed off a routine observation. The count sat a little above the running mean, entirely from estimated inputs. Referred to the dated decisions and closed.

- 2026-04-06: The reconciliation desk signed off a routine observation. An operator asked whether a credit had posted; it had, in the preceding period. Filed for the record.

- 2026-04-06: The audit lead filed a routine observation. A batch retried once after a transient timeout and completed on the second pass. Closed with no parameter change.

- 2026-04-18: The exceptions queue owner noted a routine observation. A typo in a reference record was corrected before the run started. Closed with no parameter change.

- 2026-04-08: The duty analyst carried forward a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. No follow-up was requested.

- 2026-04-11: A reviewer on shift recorded a routine observation. Nightly reconciliation matched exactly and the file was released without comment.

- 2026-05-19: An on-call engineer signed off a routine observation. A duplicate order was cancelled at source and never reached the run. Filed for the record.

> **Governance decision (2026-05-05 - #REG-7150)** Priya: Input paths, final. The counterparty register, the regulatory calendar, the rate table and the reporting policy are always read from their fixed absolute paths under /app/data; `--input` selects the transaction ledger only. Both `--input` and `--output-dir` keep their documented defaults.

> **Governance decision (2026-05-07 - #REG-7170)** Yusuf: Ledger recovery, final (supersedes #REG-7020). Start from the pre-migration snapshot and replay the migration journal in ascending `seq`, never in file order, keying each change on the booking it names -- the trade id and its version together. An `amend` overwrites the named field in place. A `withdraw` takes the booking out, but the migrator keeps it as it stood at that moment. A `reinstate` returns a withdrawn booking EXACTLY as it then stood: an amendment posted before the withdrawal survives, and one posted while it was out is lost. A change naming a booking the snapshot never carried is ignored.

> **Governance decision (2026-05-08 - #REG-7174)** Yusuf: Recovered shape, final. The rebuilt ledger is a JSON array ascending by trade id and then version, and each row carries the eleven booking fields -- the migrator's bookkeeping (`seq`, `kind`, `posted_by`) never survives the replay.

> **Governance decision (2026-05-12 - #REG-7182)** Lena: Re-booked trades, final (revises #REG-7038; deviates from the first-version interim). A re-booking supersedes what came before it, so only the HIGHEST version of a trade id is considered for reporting. The superseded bookings are dropped silently: they are neither reported nor queued, and they do not count toward the cap.

> **Governance decision (2026-05-15 - #REG-7186)** Marek: Scope, final (supersedes #REG-7026; deviates from the both-sides reading). Eligibility follows the REPORTING side alone and the other side's scope never enters it. A reporting party that is out of scope files nothing, and a party classified as non-financial below the clearing threshold is out of scope however large the trade.

> **Governance decision (2026-05-18 - #REG-7188)** Marek: Threshold, final. The notional is carried into US dollars at the rate table's figure for its currency and floored to whole dollars BEFORE it is compared with the policy's notional_floor_usd. A trade whose currency the table does not carry is not reported.

> **Governance decision (2026-05-21 - #REG-7190)** Priya: Deadline, final (supersedes #REG-7032; deviates from the calendar-day offset). The deadline is reached by counting the policy's deadline_business_days forward from the trade day over BUSINESS days only, skipping every day the regulatory calendar closes. The trade day itself is never counted. A submission later than the deadline plus the policy's late_grace_days is reported late; it is still reported.

> **Governance decision (2026-05-24 - #REG-7192)** Yusuf: Delegated filing, final. Where the reporting party has delegated, the delegate files and the delegate's LEI is the one carried on the line. Delegation moves who files and nothing else: the delegate's own scope does not re-open the eligibility question settled by #REG-7186. Nor is it followed further. A delegation is the arrangement between one reporting party and one delegate, so where the delegate has itself delegated to a third party that second arrangement is no concern of this line: the reporting party's own delegate files and carries the LEI, and the chain is not walked to its end.

> **Governance decision (2026-05-27 - #REG-7194)** Lena: Unconfirmed bookings, final. A booking the confirmations feed has not matched is never submitted. It is queued as `unconfirmed` and takes no place against the submission cap, but it still counts as eligible and is still assessed for lateness.

> **Governance decision (2026-05-29 - #REG-7196)** Lena: Submission order, final. Submissions are taken in deadline order, earliest first, then by trade id, until the policy's max_submissions is reached; every eligible confirmed booking past the cap is queued as `over_cap`. The queue is emitted by reason and then by trade id.

- 2026-05-05: The platform team noted a routine observation. Storage on the staging host was extended after the export outgrew its allocation.

- 2026-05-03: The platform team logged a routine observation. One record appeared twice in the export after a mid-cycle correction. No follow-up was requested.

- 2026-05-23: The controls team reviewed a routine observation. Two accounts showed a same-day transfer the export had not yet picked up.

- 2026-05-01: A stand-up note logged a routine observation. The count sat a little above the running mean, entirely from estimated inputs. No follow-up was requested.

- 2026-05-24: The exceptions queue owner raised and closed a routine observation. One record appeared twice in the export after a mid-cycle correction.

- 2026-05-13: The reconciliation desk logged a routine observation. A batch retried once after a transient timeout and completed on the second pass. Closed with no parameter change.

- 2026-05-22: The reconciliation desk recorded a routine observation. A question raised on the floor was withdrawn once the entry was reread. The desk confirmed no downstream impact.

- 2026-05-19: The duty analyst spot-checked a routine observation. Storage on the staging host was extended after the export outgrew its allocation. No action was carried forward.

- 2026-05-20: The exceptions queue owner reviewed a routine observation. A typo in a reference record was corrected before the run started. Filed for the record.

- 2026-05-19: A reviewer on shift signed off a routine observation. A typo in a reference record was corrected before the run started. Filed for the record.

- 2026-05-26: The operations desk carried forward a routine observation. Nightly reconciliation matched exactly and the file was released without comment. The thread was archived after review.

- 2026-05-21: The audit lead signed off a routine observation. One record appeared twice in the export after a mid-cycle correction. The desk confirmed no downstream impact.

- 2026-05-17: The controls team recorded a routine observation. A typo in a reference record was corrected before the run started. Filed for the record.

- 2026-05-22: The exceptions queue owner opened a query on a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. Nothing here bears on engine behaviour.

- 2026-05-20: The platform team reviewed a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. No follow-up was requested.

- 2026-05-16: The duty analyst raised and closed a routine observation. The downstream vendor confirmed receipt inside the agreed window. Closed with no parameter change.

- 2026-05-07: An on-call engineer reviewed a routine observation. One record appeared twice in the export after a mid-cycle correction. No follow-up was requested.

- 2026-05-15: A reviewer on shift filed a routine observation. The variance sat inside tolerance and no adjustment was raised.

- 2026-06-23: An on-call engineer logged a routine observation. Storage on the staging host was extended after the export outgrew its allocation. The thread was archived after review.

> **Governance decision (2026-06-03 - #REG-7210)** Priya: Reporting policy baseline, read from /app/data/reporting_policy.json at that fixed absolute path. Any field the policy file omits keeps its baseline: notional_floor_usd = 1000000; deadline_business_days = 1; max_submissions = 2500; late_grace_days = 0.

- 2026-06-16: An on-call engineer reviewed a routine observation. The overnight window ran long behind an unrelated platform patch. The thread was archived after review.

- 2026-06-10: A stand-up note signed off a routine observation. A duplicate order was cancelled at source and never reached the run. Closed with no parameter change.

- 2026-06-17: The reconciliation desk raised and closed a routine observation. Late inputs arrived from one feed and were loaded before the cut. The desk confirmed no downstream impact.

- 2026-06-15: A reviewer on shift carried forward a routine observation. One record appeared twice in the export after a mid-cycle correction. Filed for the record.

- 2026-06-19: A stand-up note carried forward a routine observation. The variance sat inside tolerance and no adjustment was raised. Closed with no parameter change.

- 2026-06-06: A stand-up note opened a query on a routine observation. The variance sat inside tolerance and no adjustment was raised.

- 2026-06-22: The platform team noted a routine observation. A batch retried once after a transient timeout and completed on the second pass. Filed for the record.

- 2026-06-11: A stand-up note recorded a routine observation. Storage on the staging host was extended after the export outgrew its allocation.

- 2026-06-01: A weekly review recorded a routine observation. The overnight window ran long behind an unrelated platform patch. No follow-up was requested.

- 2026-06-06: The controls team opened a query on a routine observation. One record appeared twice in the export after a mid-cycle correction.

- 2026-06-16: The operations desk reviewed a routine observation. Storage on the staging host was extended after the export outgrew its allocation. Closed with no parameter change.

- 2026-06-13: An on-call engineer recorded a routine observation. An operator asked whether a credit had posted; it had, in the preceding period. Nothing here bears on engine behaviour.

- 2026-06-07: A reviewer on shift logged a routine observation. A duplicate order was cancelled at source and never reached the run. The thread was archived after review.

- 2026-06-24: The exceptions queue owner spot-checked a routine observation. Two accounts showed a same-day transfer the export had not yet picked up.

- 2026-06-11: The duty analyst logged a routine observation. The downstream vendor confirmed receipt inside the agreed window. Closed with no parameter change.

- 2026-06-04: The reconciliation desk signed off a routine observation. The overnight window ran long behind an unrelated platform patch. The thread was archived after review.

- 2026-06-22: A stand-up note noted a routine observation. Storage on the staging host was extended after the export outgrew its allocation. No action was carried forward.

- 2026-06-15: A shift handover opened a query on a routine observation. Two accounts showed a same-day transfer the export had not yet picked up. Closed with no parameter change.

- 2026-06-20: The platform team reviewed a routine observation. The variance sat inside tolerance and no adjustment was raised.

- 2026-06-14: The reconciliation desk opened a query on a routine observation. A typo in a reference record was corrected before the run started.

- 2026-06-09: The operations desk reviewed a routine observation. A question raised on the floor was withdrawn once the entry was reread. No action was carried forward.

- 2026-06-24: The controls team reviewed a routine observation. A typo in a reference record was corrected before the run started.
