# Evaluation results

| System | Split | N | Micro F1 | Macro F1 | Exact | Schema OK | Halluc. | Latency s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rules | test_seen | 300 | 0.9782 | 0.9752 | 0.65 | 1.0 | 0.0 | 0.001 |
| rules | test_unseen_layout | 300 | 0.6835 | 0.4858 | 0.0 | 1.0 | 0.0 | 0.002 |

## rules on test_seen

| Field | P | R | F1 | Null acc. | Support |
| --- | --- | --- | --- | --- | --- |
| fund_name | 1.000 | 1.000 | 1.000 | 1.000 | 300 |
| isin | 1.000 | 1.000 | 1.000 | 1.000 | 289 |
| currency | 1.000 | 1.000 | 1.000 | 1.000 | 260 |
| ongoing_charges_pct | 1.000 | 1.000 | 1.000 | 1.000 | 300 |
| entry_charge_pct | 1.000 | 1.000 | 1.000 | 1.000 | 250 |
| exit_charge_pct | 1.000 | 1.000 | 1.000 | 1.000 | 253 |
| transaction_costs_pct | 1.000 | 1.000 | 1.000 | 1.000 | 175 |
| performance_fee_pct | 1.000 | 1.000 | 1.000 | 1.000 | 91 |
| benchmark | 1.000 | 1.000 | 1.000 | 1.000 | 232 |
| domicile | 1.000 | 1.000 | 1.000 | 1.000 | 221 |
| management_company | 1.000 | 1.000 | 1.000 | 1.000 | 243 |
| investment_objective | 1.000 | 0.950 | 0.974 | 1.000 | 300 |
| sri | 0.948 | 1.000 | 0.973 | 0.889 | 201 |
| scenarios.stress.return_pct | 1.000 | 0.930 | 0.964 | 1.000 | 201 |
| recommended_holding_period_years | 1.000 | 0.914 | 0.955 | 1.000 | 267 |
| scenarios.stress.value | 0.989 | 0.920 | 0.954 | 0.980 | 201 |
| scenarios.favourable.value | 1.000 | 0.910 | 0.953 | 1.000 | 201 |
| scenarios.favourable.return_pct | 1.000 | 0.910 | 0.953 | 1.000 | 201 |
| scenarios.unfavourable.value | 1.000 | 0.890 | 0.942 | 1.000 | 201 |
| scenarios.unfavourable.return_pct | 1.000 | 0.890 | 0.942 | 1.000 | 201 |
| srri | 1.000 | 0.889 | 0.941 | 1.000 | 99 |
| scenarios.moderate.value | 1.000 | 0.886 | 0.939 | 1.000 | 201 |
| scenarios.moderate.return_pct | 1.000 | 0.886 | 0.939 | 1.000 | 201 |

## rules on test_unseen_layout

| Field | P | R | F1 | Null acc. | Support |
| --- | --- | --- | --- | --- | --- |
| fund_name | 1.000 | 1.000 | 1.000 | 1.000 | 300 |
| isin | 1.000 | 1.000 | 1.000 | 1.000 | 279 |
| sri | 1.000 | 1.000 | 1.000 | 1.000 | 300 |
| scenarios.favourable.return_pct | 1.000 | 0.963 | 0.981 | 1.000 | 300 |
| scenarios.favourable.value | 0.997 | 0.960 | 0.978 | 0.000 | 300 |
| scenarios.stress.return_pct | 1.000 | 0.950 | 0.974 | 1.000 | 300 |
| scenarios.unfavourable.return_pct | 1.000 | 0.930 | 0.964 | 1.000 | 300 |
| scenarios.moderate.return_pct | 1.000 | 0.930 | 0.964 | 1.000 | 300 |
| scenarios.moderate.value | 0.993 | 0.923 | 0.957 | 0.000 | 300 |
| scenarios.unfavourable.value | 0.971 | 0.903 | 0.936 | 0.000 | 300 |
| scenarios.stress.value | 0.958 | 0.910 | 0.933 | 0.000 | 300 |
| currency | 0.000 | 0.000 | 0.000 | 1.000 | 249 |
| srri | 0.000 | 0.000 | 0.000 | 1.000 | 0 |
| ongoing_charges_pct | 0.000 | 0.000 | 0.000 | 1.000 | 300 |
| entry_charge_pct | 0.000 | 0.000 | 0.000 | 1.000 | 252 |
| exit_charge_pct | 0.000 | 0.000 | 0.000 | 1.000 | 249 |
| transaction_costs_pct | 0.000 | 0.000 | 0.000 | 1.000 | 273 |
| performance_fee_pct | 0.000 | 0.000 | 0.000 | 1.000 | 134 |
| recommended_holding_period_years | 0.000 | 0.000 | 0.000 | 1.000 | 300 |
| investment_objective | 0.000 | 0.000 | 0.000 | 1.000 | 300 |
| benchmark | 0.000 | 0.000 | 0.000 | 1.000 | 219 |
| domicile | 0.000 | 0.000 | 0.000 | 1.000 | 189 |
| management_company | 0.000 | 0.000 | 0.000 | 1.000 | 243 |
