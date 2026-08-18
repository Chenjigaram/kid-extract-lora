# Evaluation results

| System | Split | N | Micro F1 | Macro F1 | Exact | Schema OK | Halluc. | Latency s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| finetuned | test_seen | 50 | 0.9876 | 0.9884 | 0.82 | 1.0 | 0.00562 | 21.056 |
| rules | test_seen | 50 | 0.9834 | 0.9816 | 0.72 | 1.0 | 0.0 | 0.001 |
| finetuned | test_unseen_layout | 50 | 0.8583 | 0.8296 | 0.02 | 0.88 | 0.00509 | 21.342 |
| rules | test_unseen_layout | 50 | 0.6435 | 0.5137 | 0.0 | 1.0 | 0.0 | 0.001 |
| few-shot | test_unseen_layout | 50 | 0.1687 | 0.1546 | 0.0 | 0.5 | 0.49103 | 40.002 |
| zero-shot | test_unseen_layout | 50 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 28.126 |

## finetuned on test_seen

| Field | P | R | F1 | Null acc. | Support |
| --- | --- | --- | --- | --- | --- |
| fund_name | 1.000 | 1.000 | 1.000 | 1.000 | 50 |
| isin | 1.000 | 1.000 | 1.000 | 1.000 | 50 |
| sri | 1.000 | 1.000 | 1.000 | 1.000 | 38 |
| srri | 1.000 | 1.000 | 1.000 | 1.000 | 12 |
| ongoing_charges_pct | 1.000 | 1.000 | 1.000 | 1.000 | 50 |
| exit_charge_pct | 1.000 | 1.000 | 1.000 | 1.000 | 43 |
| performance_fee_pct | 1.000 | 1.000 | 1.000 | 1.000 | 23 |
| recommended_holding_period_years | 1.000 | 1.000 | 1.000 | 1.000 | 44 |
| benchmark | 1.000 | 1.000 | 1.000 | 1.000 | 36 |
| domicile | 1.000 | 1.000 | 1.000 | 1.000 | 35 |
| scenarios.stress.value | 1.000 | 1.000 | 1.000 | 1.000 | 38 |
| scenarios.stress.return_pct | 1.000 | 1.000 | 1.000 | 1.000 | 38 |
| scenarios.moderate.return_pct | 1.000 | 1.000 | 1.000 | 1.000 | 38 |
| scenarios.favourable.value | 1.000 | 1.000 | 1.000 | 1.000 | 38 |
| scenarios.favourable.return_pct | 1.000 | 1.000 | 1.000 | 1.000 | 38 |
| currency | 0.974 | 1.000 | 0.987 | 0.923 | 37 |
| management_company | 0.972 | 1.000 | 0.986 | 0.933 | 35 |
| transaction_costs_pct | 0.971 | 1.000 | 0.986 | 0.938 | 34 |
| scenarios.unfavourable.value | 0.974 | 0.974 | 0.974 | 0.923 | 38 |
| scenarios.unfavourable.return_pct | 0.974 | 0.974 | 0.974 | 0.923 | 38 |
| entry_charge_pct | 0.956 | 0.977 | 0.966 | 0.714 | 44 |
| investment_objective | 0.940 | 0.940 | 0.940 | 0.000 | 50 |
| scenarios.moderate.value | 0.921 | 0.921 | 0.921 | 0.800 | 38 |

## rules on test_seen

| Field | P | R | F1 | Null acc. | Support |
| --- | --- | --- | --- | --- | --- |
| fund_name | 1.000 | 1.000 | 1.000 | 1.000 | 50 |
| isin | 1.000 | 1.000 | 1.000 | 1.000 | 50 |
| currency | 1.000 | 1.000 | 1.000 | 1.000 | 37 |
| ongoing_charges_pct | 1.000 | 1.000 | 1.000 | 1.000 | 50 |
| entry_charge_pct | 1.000 | 1.000 | 1.000 | 1.000 | 44 |
| exit_charge_pct | 1.000 | 1.000 | 1.000 | 1.000 | 43 |
| transaction_costs_pct | 1.000 | 1.000 | 1.000 | 1.000 | 34 |
| performance_fee_pct | 1.000 | 1.000 | 1.000 | 1.000 | 23 |
| benchmark | 1.000 | 1.000 | 1.000 | 1.000 | 36 |
| domicile | 1.000 | 1.000 | 1.000 | 1.000 | 35 |
| management_company | 1.000 | 1.000 | 1.000 | 1.000 | 35 |
| scenarios.stress.value | 1.000 | 1.000 | 1.000 | 1.000 | 38 |
| scenarios.stress.return_pct | 1.000 | 1.000 | 1.000 | 1.000 | 38 |
| investment_objective | 1.000 | 0.980 | 0.990 | 1.000 | 50 |
| sri | 0.974 | 1.000 | 0.987 | 0.917 | 38 |
| recommended_holding_period_years | 1.000 | 0.955 | 0.977 | 1.000 | 44 |
| scenarios.moderate.value | 1.000 | 0.921 | 0.959 | 1.000 | 38 |
| scenarios.moderate.return_pct | 1.000 | 0.921 | 0.959 | 1.000 | 38 |
| scenarios.favourable.value | 1.000 | 0.921 | 0.959 | 1.000 | 38 |
| scenarios.favourable.return_pct | 1.000 | 0.921 | 0.959 | 1.000 | 38 |
| srri | 1.000 | 0.917 | 0.957 | 1.000 | 12 |
| scenarios.unfavourable.return_pct | 1.000 | 0.868 | 0.930 | 1.000 | 38 |
| scenarios.unfavourable.value | 0.970 | 0.842 | 0.901 | 0.923 | 38 |

## few-shot on test_unseen_layout

| Field | P | R | F1 | Null acc. | Support |
| --- | --- | --- | --- | --- | --- |
| management_company | 0.850 | 0.405 | 0.548 | 0.625 | 42 |
| fund_name | 0.692 | 0.360 | 0.474 | 0.000 | 50 |
| currency | 0.500 | 0.302 | 0.377 | 0.188 | 43 |
| isin | 0.500 | 0.271 | 0.351 | 0.133 | 48 |
| sri | 0.308 | 0.210 | 0.250 | 0.182 | 38 |
| recommended_holding_period_years | 0.346 | 0.180 | 0.237 | 0.000 | 50 |
| scenarios.stress.value | 0.417 | 0.132 | 0.200 | 0.462 | 38 |
| benchmark | 0.227 | 0.135 | 0.170 | 0.292 | 37 |
| scenarios.stress.return_pct | 0.333 | 0.105 | 0.160 | 0.429 | 38 |
| exit_charge_pct | 0.192 | 0.132 | 0.156 | 0.222 | 38 |
| domicile | 0.182 | 0.121 | 0.145 | 0.379 | 33 |
| performance_fee_pct | 0.115 | 0.176 | 0.140 | 0.425 | 17 |
| scenarios.unfavourable.return_pct | 0.250 | 0.079 | 0.120 | 0.400 | 38 |
| scenarios.favourable.return_pct | 0.167 | 0.053 | 0.080 | 0.375 | 38 |
| scenarios.unfavourable.value | 0.083 | 0.026 | 0.040 | 0.353 | 38 |
| scenarios.moderate.value | 0.083 | 0.026 | 0.040 | 0.353 | 38 |
| scenarios.moderate.return_pct | 0.083 | 0.026 | 0.040 | 0.353 | 38 |
| entry_charge_pct | 0.038 | 0.022 | 0.028 | 0.038 | 46 |
| srri | 0.000 | 0.000 | 0.000 | 1.000 | 12 |
| ongoing_charges_pct | 0.000 | 0.000 | 0.000 | 0.000 | 50 |
| transaction_costs_pct | 0.000 | 0.000 | 0.000 | 0.161 | 36 |
| investment_objective | 0.000 | 0.000 | 0.000 | 0.000 | 50 |
| scenarios.favourable.value | 0.000 | 0.000 | 0.000 | 0.333 | 38 |

## finetuned on test_unseen_layout

| Field | P | R | F1 | Null acc. | Support |
| --- | --- | --- | --- | --- | --- |
| srri | 1.000 | 1.000 | 1.000 | 1.000 | 12 |
| recommended_holding_period_years | 1.000 | 0.960 | 0.980 | 1.000 | 50 |
| sri | 1.000 | 0.947 | 0.973 | 1.000 | 38 |
| entry_charge_pct | 0.956 | 0.935 | 0.945 | 0.500 | 46 |
| management_company | 0.930 | 0.952 | 0.941 | 0.667 | 42 |
| fund_name | 0.958 | 0.920 | 0.939 | 0.000 | 50 |
| scenarios.stress.value | 1.000 | 0.868 | 0.930 | 1.000 | 38 |
| scenarios.stress.return_pct | 1.000 | 0.868 | 0.930 | 1.000 | 38 |
| scenarios.unfavourable.value | 1.000 | 0.868 | 0.930 | 1.000 | 38 |
| scenarios.unfavourable.return_pct | 1.000 | 0.868 | 0.930 | 1.000 | 38 |
| scenarios.moderate.return_pct | 1.000 | 0.868 | 0.930 | 1.000 | 38 |
| scenarios.favourable.return_pct | 1.000 | 0.868 | 0.930 | 1.000 | 38 |
| isin | 0.917 | 0.917 | 0.917 | 0.000 | 48 |
| currency | 0.950 | 0.884 | 0.916 | 0.714 | 43 |
| scenarios.moderate.value | 0.970 | 0.842 | 0.901 | 0.923 | 38 |
| scenarios.favourable.value | 0.970 | 0.842 | 0.901 | 0.923 | 38 |
| benchmark | 0.833 | 0.811 | 0.822 | 0.647 | 37 |
| exit_charge_pct | 0.780 | 0.842 | 0.810 | 0.308 | 38 |
| investment_objective | 0.812 | 0.780 | 0.796 | 0.000 | 50 |
| ongoing_charges_pct | 0.750 | 0.720 | 0.735 | 0.000 | 50 |
| performance_fee_pct | 0.857 | 0.353 | 0.500 | 0.970 | 17 |
| domicile | 1.000 | 0.212 | 0.350 | 1.000 | 33 |
| transaction_costs_pct | 0.133 | 0.056 | 0.078 | 0.518 | 36 |

## rules on test_unseen_layout

| Field | P | R | F1 | Null acc. | Support |
| --- | --- | --- | --- | --- | --- |
| fund_name | 1.000 | 1.000 | 1.000 | 1.000 | 50 |
| isin | 1.000 | 1.000 | 1.000 | 1.000 | 48 |
| sri | 0.974 | 1.000 | 0.987 | 0.917 | 38 |
| scenarios.stress.return_pct | 1.000 | 0.921 | 0.959 | 1.000 | 38 |
| srri | 1.000 | 0.917 | 0.957 | 1.000 | 12 |
| scenarios.moderate.value | 1.000 | 0.895 | 0.944 | 1.000 | 38 |
| scenarios.moderate.return_pct | 1.000 | 0.895 | 0.944 | 1.000 | 38 |
| scenarios.favourable.value | 1.000 | 0.895 | 0.944 | 1.000 | 38 |
| scenarios.favourable.return_pct | 1.000 | 0.895 | 0.944 | 1.000 | 38 |
| scenarios.stress.value | 0.971 | 0.895 | 0.931 | 0.923 | 38 |
| scenarios.unfavourable.value | 1.000 | 0.816 | 0.899 | 1.000 | 38 |
| scenarios.unfavourable.return_pct | 1.000 | 0.816 | 0.899 | 1.000 | 38 |
| currency | 1.000 | 0.256 | 0.407 | 1.000 | 43 |
| ongoing_charges_pct | 0.000 | 0.000 | 0.000 | 1.000 | 50 |
| entry_charge_pct | 0.000 | 0.000 | 0.000 | 1.000 | 46 |
| exit_charge_pct | 0.000 | 0.000 | 0.000 | 1.000 | 38 |
| transaction_costs_pct | 0.000 | 0.000 | 0.000 | 1.000 | 36 |
| performance_fee_pct | 0.000 | 0.000 | 0.000 | 1.000 | 17 |
| recommended_holding_period_years | 0.000 | 0.000 | 0.000 | 1.000 | 50 |
| investment_objective | 0.000 | 0.000 | 0.000 | 1.000 | 50 |
| benchmark | 0.000 | 0.000 | 0.000 | 1.000 | 37 |
| domicile | 0.000 | 0.000 | 0.000 | 1.000 | 33 |
| management_company | 0.000 | 0.000 | 0.000 | 1.000 | 42 |

## zero-shot on test_unseen_layout

| Field | P | R | F1 | Null acc. | Support |
| --- | --- | --- | --- | --- | --- |
| fund_name | 0.000 | 0.000 | 0.000 | 1.000 | 50 |
| isin | 0.000 | 0.000 | 0.000 | 1.000 | 48 |
| currency | 0.000 | 0.000 | 0.000 | 1.000 | 43 |
| sri | 0.000 | 0.000 | 0.000 | 1.000 | 38 |
| srri | 0.000 | 0.000 | 0.000 | 1.000 | 12 |
| ongoing_charges_pct | 0.000 | 0.000 | 0.000 | 1.000 | 50 |
| entry_charge_pct | 0.000 | 0.000 | 0.000 | 1.000 | 46 |
| exit_charge_pct | 0.000 | 0.000 | 0.000 | 1.000 | 38 |
| transaction_costs_pct | 0.000 | 0.000 | 0.000 | 1.000 | 36 |
| performance_fee_pct | 0.000 | 0.000 | 0.000 | 1.000 | 17 |
| recommended_holding_period_years | 0.000 | 0.000 | 0.000 | 1.000 | 50 |
| investment_objective | 0.000 | 0.000 | 0.000 | 1.000 | 50 |
| benchmark | 0.000 | 0.000 | 0.000 | 1.000 | 37 |
| domicile | 0.000 | 0.000 | 0.000 | 1.000 | 33 |
| management_company | 0.000 | 0.000 | 0.000 | 1.000 | 42 |
| scenarios.stress.value | 0.000 | 0.000 | 0.000 | 1.000 | 38 |
| scenarios.stress.return_pct | 0.000 | 0.000 | 0.000 | 1.000 | 38 |
| scenarios.unfavourable.value | 0.000 | 0.000 | 0.000 | 1.000 | 38 |
| scenarios.unfavourable.return_pct | 0.000 | 0.000 | 0.000 | 1.000 | 38 |
| scenarios.moderate.value | 0.000 | 0.000 | 0.000 | 1.000 | 38 |
| scenarios.moderate.return_pct | 0.000 | 0.000 | 0.000 | 1.000 | 38 |
| scenarios.favourable.value | 0.000 | 0.000 | 0.000 | 1.000 | 38 |
| scenarios.favourable.return_pct | 0.000 | 0.000 | 0.000 | 1.000 | 38 |
