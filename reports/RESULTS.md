# Evaluation results

| System | Split | N | Micro F1 | Macro F1 | Exact | Schema OK | Halluc. | Latency s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rules | test_seen | 300 | 0.978 | 0.9761 | 0.6333 | 1.0 | 0.0 | 0.001 |
| rules | test_unseen_layout | 300 | 0.6454 | 0.516 | 0.0 | 1.0 | 0.0 | 0.001 |

## rules on test_seen

| Field | P | R | F1 | Null acc. | Support |
| --- | --- | --- | --- | --- | --- |
| fund_name | 1.000 | 1.000 | 1.000 | 1.000 | 300 |
| isin | 1.000 | 1.000 | 1.000 | 1.000 | 288 |
| currency | 1.000 | 1.000 | 1.000 | 1.000 | 261 |
| ongoing_charges_pct | 1.000 | 1.000 | 1.000 | 1.000 | 300 |
| entry_charge_pct | 1.000 | 1.000 | 1.000 | 1.000 | 259 |
| exit_charge_pct | 1.000 | 1.000 | 1.000 | 1.000 | 261 |
| transaction_costs_pct | 1.000 | 1.000 | 1.000 | 1.000 | 195 |
| performance_fee_pct | 1.000 | 1.000 | 1.000 | 1.000 | 106 |
| benchmark | 1.000 | 1.000 | 1.000 | 1.000 | 226 |
| domicile | 1.000 | 1.000 | 1.000 | 1.000 | 221 |
| management_company | 1.000 | 1.000 | 1.000 | 1.000 | 235 |
| sri | 0.966 | 0.996 | 0.980 | 0.893 | 225 |
| scenarios.stress.return_pct | 1.000 | 0.960 | 0.980 | 1.000 | 225 |
| investment_objective | 1.000 | 0.930 | 0.964 | 1.000 | 300 |
| scenarios.stress.value | 0.977 | 0.938 | 0.957 | 0.938 | 225 |
| recommended_holding_period_years | 1.000 | 0.916 | 0.956 | 1.000 | 263 |
| scenarios.moderate.return_pct | 1.000 | 0.911 | 0.954 | 1.000 | 225 |
| scenarios.favourable.return_pct | 1.000 | 0.911 | 0.954 | 1.000 | 225 |
| scenarios.favourable.value | 0.990 | 0.902 | 0.944 | 0.974 | 225 |
| srri | 1.000 | 0.893 | 0.944 | 1.000 | 75 |
| scenarios.unfavourable.return_pct | 1.000 | 0.893 | 0.944 | 1.000 | 225 |
| scenarios.moderate.value | 0.985 | 0.898 | 0.940 | 0.962 | 225 |
| scenarios.unfavourable.value | 0.990 | 0.884 | 0.934 | 0.974 | 225 |

## rules on test_unseen_layout

| Field | P | R | F1 | Null acc. | Support |
| --- | --- | --- | --- | --- | --- |
| fund_name | 1.000 | 1.000 | 1.000 | 1.000 | 300 |
| isin | 1.000 | 1.000 | 1.000 | 1.000 | 289 |
| sri | 0.974 | 1.000 | 0.987 | 0.920 | 225 |
| srri | 1.000 | 0.920 | 0.958 | 1.000 | 75 |
| scenarios.stress.return_pct | 1.000 | 0.911 | 0.954 | 1.000 | 225 |
| scenarios.favourable.value | 1.000 | 0.898 | 0.946 | 1.000 | 225 |
| scenarios.favourable.return_pct | 1.000 | 0.898 | 0.946 | 1.000 | 225 |
| scenarios.unfavourable.value | 1.000 | 0.889 | 0.941 | 1.000 | 225 |
| scenarios.unfavourable.return_pct | 1.000 | 0.889 | 0.941 | 1.000 | 225 |
| scenarios.moderate.value | 1.000 | 0.889 | 0.941 | 1.000 | 225 |
| scenarios.moderate.return_pct | 1.000 | 0.889 | 0.941 | 1.000 | 225 |
| scenarios.stress.value | 0.976 | 0.889 | 0.930 | 0.938 | 225 |
| currency | 1.000 | 0.236 | 0.382 | 1.000 | 263 |
| ongoing_charges_pct | 0.000 | 0.000 | 0.000 | 1.000 | 300 |
| entry_charge_pct | 0.000 | 0.000 | 0.000 | 1.000 | 264 |
| exit_charge_pct | 0.000 | 0.000 | 0.000 | 1.000 | 258 |
| transaction_costs_pct | 0.000 | 0.000 | 0.000 | 1.000 | 204 |
| performance_fee_pct | 0.000 | 0.000 | 0.000 | 1.000 | 91 |
| recommended_holding_period_years | 0.000 | 0.000 | 0.000 | 1.000 | 300 |
| investment_objective | 0.000 | 0.000 | 0.000 | 1.000 | 300 |
| benchmark | 0.000 | 0.000 | 0.000 | 1.000 | 224 |
| domicile | 0.000 | 0.000 | 0.000 | 1.000 | 209 |
| management_company | 0.000 | 0.000 | 0.000 | 1.000 | 247 |
