# Planning governance log

How the reporting engine is *meant* to behave -- the recovery of the truncated transaction ledger, which side carries the obligation, how a re-booking supersedes what came before, how the threshold and the deadline are reached, who files a delegated report and what happens to an unconfirmed booking -- was settled incrementally by the compliance committee, and those decisions live in the review entries below, not in any single summary. Several stages deliberately DEVIATE from the intuitive reading: the obligation follows the reporting side alone rather than both sides, the latest re-booking supersedes the first, the deadline counts business days rather than calendar days, and an unconfirmed booking is queued without consuming the cap. The February draft proposals were revisited during the 2026-05 controls review and several were reversed; where a draft or interim conflicts with a later decision, the later dated decision governs. `/app/docs/reporting_contract.json` is the output contract only.

- 2026-02-08: Surveillance desk noted rejected acknowledgements from the reconciliation batch in window 1003. Raised with the venue owner; the reporting parameters were not touched.

> **Recovery draft proposal (2026-02-06 - #REG-7020)** Rosa: rebuild the truncated ledger by concatenating the pre-migration snapshot with the migration journal and keeping the last row seen for each booking; a reinstated booking is re-read from the snapshot *(Superseded -- reversed in the 2026-05 controls review.)*

> **Recovery draft proposal (2026-02-13 - #REG-7026)** Anders: a trade is in scope only where BOTH sides are in scope, since neither party should file alone *(Superseded -- reversed in the 2026-05 controls review.)*

> **Recovery draft proposal (2026-02-19 - #REG-7032)** Marek: the reporting deadline is the trade day plus the policy's day count in plain calendar days *(Superseded -- reversed in the 2026-05 controls review.)*

- 2026-02-20: Surveillance desk noted rejected acknowledgements from the confirmations feed in window 1004. Raised with the venue owner; the reporting parameters were not touched.

- 2026-02-18: Compliance stand-up recorded a routine note against the reconciliation batch for window 1005. The resubmission backlog was cleared with no amendment raised.

- 2026-02-25: Controls review of the venue adaptor in window 1008 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-02-16: Compliance stand-up recorded a routine note against the reconciliation batch for window 1009. The resubmission backlog was cleared with no amendment raised.

- 2026-02-06: Surveillance desk noted rejected acknowledgements from the venue adaptor in window 1010. Raised with the venue owner; the reporting parameters were not touched.

- 2026-02-01: Surveillance desk noted rejected acknowledgements from the venue adaptor in window 1013. Raised with the venue owner; the reporting parameters were not touched.

- 2026-02-20: Officer on duty logged a routine observation for the reference-data service during review window 1015. Rejection-rate drift reviewed; no policy change requested.

- 2026-02-05: Controls review of the confirmations feed in window 1016 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-02-01: Surveillance desk noted rejected acknowledgements from the submission gateway in window 1019. Raised with the venue owner; the reporting parameters were not touched.

- 2026-02-02: Compliance stand-up recorded a routine note against the reference-data service for window 1022. The resubmission backlog was cleared with no amendment raised.

- 2026-02-23: Compliance stand-up recorded a routine note against the venue adaptor for window 1023. The resubmission backlog was cleared with no amendment raised.

- 2026-02-26: Controls review of the reference-data service in window 1024 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-02-09: Surveillance desk noted rejected acknowledgements from the venue adaptor in window 1025. Raised with the venue owner; the reporting parameters were not touched.

- 2026-02-22: Controls review of the submission gateway in window 1027 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-02-07: Surveillance desk noted rejected acknowledgements from the submission gateway in window 1029. Raised with the venue owner; the reporting parameters were not touched.

- 2026-02-01: Officer on duty logged a routine observation for the venue adaptor during review window 1032. Rejection-rate drift reviewed; no policy change requested.

- 2026-02-11: Officer on duty logged a routine observation for the confirmations feed during review window 1033. Rejection-rate drift reviewed; no policy change requested.

- 2026-02-24: Compliance stand-up recorded a routine note against the submission gateway for window 1035. The resubmission backlog was cleared with no amendment raised.

- 2026-02-17: Compliance stand-up recorded a routine note against the venue adaptor for window 1037. The resubmission backlog was cleared with no amendment raised.

- 2026-03-13: Surveillance desk noted rejected acknowledgements from the submission gateway in window 1038. Raised with the venue owner; the reporting parameters were not touched.

> **Interim decision (2026-03-05 - #REG-7038)** Priya: where a trade has been re-booked, the FIRST version is the one reported, the later ones being corrections to the same filing *(Revised -- see the 2026-05 controls review.)*

- 2026-03-03: Controls review of the confirmations feed in window 1039 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-03-04: Controls review of the submission gateway in window 1042 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-03-17: Controls review of the reference-data service in window 1044 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-03-27: Controls review of the submission gateway in window 1047 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-03-04: Compliance stand-up recorded a routine note against the venue adaptor for window 1048. The resubmission backlog was cleared with no amendment raised.

- 2026-03-27: Controls review of the reference-data service in window 1051 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-03-19: Surveillance desk noted rejected acknowledgements from the submission gateway in window 1052. Raised with the venue owner; the reporting parameters were not touched.

- 2026-03-23: Controls review of the reference-data service in window 1055 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-03-11: Controls review of the submission gateway in window 1056 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-03-13: Officer on duty logged a routine observation for the reference-data service during review window 1058. Rejection-rate drift reviewed; no policy change requested.

- 2026-03-15: Officer on duty logged a routine observation for the venue adaptor during review window 1059. Rejection-rate drift reviewed; no policy change requested.

- 2026-03-05: Compliance stand-up recorded a routine note against the reconciliation batch for window 1060. The resubmission backlog was cleared with no amendment raised.

- 2026-03-04: Compliance stand-up recorded a routine note against the confirmations feed for window 1063. The resubmission backlog was cleared with no amendment raised.

- 2026-03-19: Officer on duty logged a routine observation for the venue adaptor during review window 1065. Rejection-rate drift reviewed; no policy change requested.

- 2026-03-21: Controls review of the submission gateway in window 1066 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-03-21: Officer on duty logged a routine observation for the reconciliation batch during review window 1067. Rejection-rate drift reviewed; no policy change requested.

- 2026-03-07: Compliance stand-up recorded a routine note against the reconciliation batch for window 1068. The resubmission backlog was cleared with no amendment raised.

- 2026-03-23: Officer on duty logged a routine observation for the reconciliation batch during review window 1069. Rejection-rate drift reviewed; no policy change requested.

- 2026-03-13: Surveillance desk noted rejected acknowledgements from the reconciliation batch in window 1071. Raised with the venue owner; the reporting parameters were not touched.

- 2026-03-12: Compliance stand-up recorded a routine note against the venue adaptor for window 1073. The resubmission backlog was cleared with no amendment raised.

- 2026-03-11: Compliance stand-up recorded a routine note against the reconciliation batch for window 1075. The resubmission backlog was cleared with no amendment raised.

- 2026-03-01: Surveillance desk noted rejected acknowledgements from the confirmations feed in window 1076. Raised with the venue owner; the reporting parameters were not touched.

- 2026-03-18: Controls review of the reconciliation batch in window 1079 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-03-25: Officer on duty logged a routine observation for the reconciliation batch during review window 1082. Rejection-rate drift reviewed; no policy change requested.

- 2026-04-23: Officer on duty logged a routine observation for the reconciliation batch during review window 1083. Rejection-rate drift reviewed; no policy change requested.

- 2026-04-17: Controls review of the venue adaptor in window 1085 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-04-20: Compliance stand-up recorded a routine note against the reference-data service for window 1087. The resubmission backlog was cleared with no amendment raised.

- 2026-04-12: Compliance stand-up recorded a routine note against the reference-data service for window 1088. The resubmission backlog was cleared with no amendment raised.

- 2026-04-12: Controls review of the reconciliation batch in window 1090 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-04-12: Controls review of the confirmations feed in window 1093 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-04-01: Officer on duty logged a routine observation for the venue adaptor during review window 1094. Rejection-rate drift reviewed; no policy change requested.

- 2026-04-12: Surveillance desk noted rejected acknowledgements from the confirmations feed in window 1097. Raised with the venue owner; the reporting parameters were not touched.

- 2026-04-05: Compliance stand-up recorded a routine note against the venue adaptor for window 1100. The resubmission backlog was cleared with no amendment raised.

- 2026-04-18: Officer on duty logged a routine observation for the reconciliation batch during review window 1103. Rejection-rate drift reviewed; no policy change requested.

- 2026-04-16: Surveillance desk noted rejected acknowledgements from the submission gateway in window 1104. Raised with the venue owner; the reporting parameters were not touched.

- 2026-04-23: Officer on duty logged a routine observation for the submission gateway during review window 1107. Rejection-rate drift reviewed; no policy change requested.

- 2026-04-18: Controls review of the reference-data service in window 1108 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-04-23: Surveillance desk noted rejected acknowledgements from the reference-data service in window 1110. Raised with the venue owner; the reporting parameters were not touched.

- 2026-04-06: Surveillance desk noted rejected acknowledgements from the venue adaptor in window 1111. Raised with the venue owner; the reporting parameters were not touched.

- 2026-04-06: Surveillance desk noted rejected acknowledgements from the venue adaptor in window 1114. Raised with the venue owner; the reporting parameters were not touched.

- 2026-04-18: Controls review of the confirmations feed in window 1117 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-04-08: Surveillance desk noted rejected acknowledgements from the reconciliation batch in window 1118. Raised with the venue owner; the reporting parameters were not touched.

- 2026-04-11: Surveillance desk noted rejected acknowledgements from the reference-data service in window 1121. Raised with the venue owner; the reporting parameters were not touched.

- 2026-05-19: Officer on duty logged a routine observation for the confirmations feed during review window 1123. Rejection-rate drift reviewed; no policy change requested.

> **Governance decision (2026-05-05 - #REG-7150)** Priya: Input paths, final. The counterparty register, the regulatory calendar, the rate table and the reporting policy are always read from their fixed absolute paths under /app/data; `--input` selects the transaction ledger only. Both `--input` and `--output-dir` keep their documented defaults.

> **Governance decision (2026-05-07 - #REG-7170)** Yusuf: Ledger recovery, final (supersedes #REG-7020). Start from the pre-migration snapshot and replay the migration journal in ascending `seq`, never in file order, keying each change on the booking it names -- the trade id and its version together. An `amend` overwrites the named field in place. A `withdraw` takes the booking out, but the migrator keeps it as it stood at that moment. A `reinstate` returns a withdrawn booking EXACTLY as it then stood: an amendment posted before the withdrawal survives, and one posted while it was out is lost. A change naming a booking the snapshot never carried is ignored.

> **Governance decision (2026-05-08 - #REG-7174)** Yusuf: Recovered shape, final. The rebuilt ledger is a JSON array ascending by trade id and then version, and each row carries the eleven booking fields -- the migrator's bookkeeping (`seq`, `kind`, `posted_by`) never survives the replay.

> **Governance decision (2026-05-12 - #REG-7182)** Lena: Re-booked trades, final (revises #REG-7038; deviates from the first-version interim). A re-booking supersedes what came before it, so only the HIGHEST version of a trade id is considered for reporting. The superseded bookings are dropped silently: they are neither reported nor queued, and they do not count toward the cap.

> **Governance decision (2026-05-15 - #REG-7186)** Marek: Scope, final (supersedes #REG-7026; deviates from the both-sides reading). Eligibility follows the REPORTING side alone and the other side's scope never enters it. A reporting party that is out of scope files nothing, and a party classified as non-financial below the clearing threshold is out of scope however large the trade.

> **Governance decision (2026-05-18 - #REG-7188)** Marek: Threshold, final. The notional is carried into US dollars at the rate table's figure for its currency and floored to whole dollars BEFORE it is compared with the policy's notional_floor_usd. A trade whose currency the table does not carry is not reported.

> **Governance decision (2026-05-21 - #REG-7190)** Priya: Deadline, final (supersedes #REG-7032; deviates from the calendar-day offset). The deadline is reached by counting the policy's deadline_business_days forward from the trade day over BUSINESS days only, skipping every day the regulatory calendar closes. The trade day itself is never counted. A submission later than the deadline plus the policy's late_grace_days is reported late; it is still reported.

> **Governance decision (2026-05-24 - #REG-7192)** Yusuf: Delegated filing, final. Where the reporting party has delegated, the delegate files and the delegate's LEI is the one carried on the line. Delegation moves who files and nothing else: the delegate's own scope does not re-open the eligibility question settled by #REG-7186.

> **Governance decision (2026-05-27 - #REG-7194)** Lena: Unconfirmed bookings, final. A booking the confirmations feed has not matched is never submitted. It is queued as `unconfirmed` and takes no place against the submission cap, but it still counts as eligible and is still assessed for lateness.

> **Governance decision (2026-05-29 - #REG-7196)** Lena: Submission order, final. Submissions are taken in deadline order, earliest first, then by trade id, until the policy's max_submissions is reached; every eligible confirmed booking past the cap is queued as `over_cap`. The queue is emitted by reason and then by trade id.

- 2026-05-05: Compliance stand-up recorded a routine note against the venue adaptor for window 1126. The resubmission backlog was cleared with no amendment raised.

- 2026-05-03: Surveillance desk noted rejected acknowledgements from the confirmations feed in window 1129. Raised with the venue owner; the reporting parameters were not touched.

- 2026-05-23: Officer on duty logged a routine observation for the confirmations feed during review window 1131. Rejection-rate drift reviewed; no policy change requested.

- 2026-05-01: Controls review of the reconciliation batch in window 1134 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-05-24: Compliance stand-up recorded a routine note against the reconciliation batch for window 1135. The resubmission backlog was cleared with no amendment raised.

- 2026-05-13: Officer on duty logged a routine observation for the confirmations feed during review window 1136. Rejection-rate drift reviewed; no policy change requested.

- 2026-05-22: Officer on duty logged a routine observation for the reference-data service during review window 1139. Rejection-rate drift reviewed; no policy change requested.

- 2026-05-19: Controls review of the venue adaptor in window 1142 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-05-20: Controls review of the confirmations feed in window 1145 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-05-19: Officer on duty logged a routine observation for the reference-data service during review window 1147. Rejection-rate drift reviewed; no policy change requested.

- 2026-05-26: Compliance stand-up recorded a routine note against the confirmations feed for window 1148. The resubmission backlog was cleared with no amendment raised.

- 2026-05-21: Controls review of the reference-data service in window 1151 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-05-17: Officer on duty logged a routine observation for the reconciliation batch during review window 1153. Rejection-rate drift reviewed; no policy change requested.

- 2026-05-22: Controls review of the submission gateway in window 1155 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-05-20: Controls review of the venue adaptor in window 1156 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-05-16: Compliance stand-up recorded a routine note against the confirmations feed for window 1158. The resubmission backlog was cleared with no amendment raised.

- 2026-05-07: Compliance stand-up recorded a routine note against the submission gateway for window 1159. The resubmission backlog was cleared with no amendment raised.

- 2026-05-15: Officer on duty logged a routine observation for the reconciliation batch during review window 1162. Rejection-rate drift reviewed; no policy change requested.

- 2026-06-23: Compliance stand-up recorded a routine note against the confirmations feed for window 1163. The resubmission backlog was cleared with no amendment raised.

> **Governance decision (2026-06-03 - #REG-7210)** Priya: Reporting policy baseline, read from /app/data/reporting_policy.json at that fixed absolute path. Any field the policy file omits keeps its baseline: notional_floor_usd = 1000000; deadline_business_days = 1; max_submissions = 2500; late_grace_days = 0.

- 2026-06-16: Compliance stand-up recorded a routine note against the confirmations feed for window 1166. The resubmission backlog was cleared with no amendment raised.

- 2026-06-10: Compliance stand-up recorded a routine note against the confirmations feed for window 1167. The resubmission backlog was cleared with no amendment raised.

- 2026-06-17: Officer on duty logged a routine observation for the reference-data service during review window 1170. Rejection-rate drift reviewed; no policy change requested.

- 2026-06-15: Controls review of the reconciliation batch in window 1173 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-06-19: Compliance stand-up recorded a routine note against the reconciliation batch for window 1176. The resubmission backlog was cleared with no amendment raised.

- 2026-06-06: Officer on duty logged a routine observation for the reference-data service during review window 1178. Rejection-rate drift reviewed; no policy change requested.

- 2026-06-22: Controls review of the reconciliation batch in window 1179 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-06-11: Controls review of the confirmations feed in window 1182 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-06-01: Controls review of the venue adaptor in window 1185 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-06-06: Compliance stand-up recorded a routine note against the reconciliation batch for window 1187. The resubmission backlog was cleared with no amendment raised.

- 2026-06-16: Controls review of the venue adaptor in window 1188 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-06-13: Officer on duty logged a routine observation for the confirmations feed during review window 1191. Rejection-rate drift reviewed; no policy change requested.

- 2026-06-07: Surveillance desk noted rejected acknowledgements from the reference-data service in window 1193. Raised with the venue owner; the reporting parameters were not touched.

- 2026-06-24: Officer on duty logged a routine observation for the submission gateway during review window 1196. Rejection-rate drift reviewed; no policy change requested.

- 2026-06-11: Compliance stand-up recorded a routine note against the reference-data service for window 1198. The resubmission backlog was cleared with no amendment raised.

- 2026-06-04: Controls review of the reference-data service in window 1201 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-06-22: Officer on duty logged a routine observation for the confirmations feed during review window 1204. Rejection-rate drift reviewed; no policy change requested.

- 2026-06-15: Surveillance desk noted rejected acknowledgements from the reconciliation batch in window 1207. Raised with the venue owner; the reporting parameters were not touched.

- 2026-06-20: Surveillance desk noted rejected acknowledgements from the confirmations feed in window 1210. Raised with the venue owner; the reporting parameters were not touched.

- 2026-06-14: Controls review of the submission gateway in window 1211 closed with no action; the standing thresholds were reconfirmed as they are.

- 2026-06-09: Surveillance desk noted rejected acknowledgements from the venue adaptor in window 1212. Raised with the venue owner; the reporting parameters were not touched.

- 2026-06-24: Officer on duty logged a routine observation for the venue adaptor during review window 1214. Rejection-rate drift reviewed; no policy change requested.
