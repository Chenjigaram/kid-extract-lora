# Dataset card — kid-extract synthetic corpus

## Summary

Generated European fund disclosure documents (PRIIPs KID and UCITS KIID) paired with exact
structured ground truth, for training and evaluating extraction models.

Documents are **synthetic**. They are rendered by this repository, not collected from fund
providers. No real disclosure document is redistributed here.

## Why synthetic

No public corpus of KIDs exists. ESMA states that where a member state does not require KID
notification to the national competent authority, no central European database of these
documents exists. Building a real corpus would mean scraping several dozen provider websites.

Generating documents instead gives exact labels at any volume with no annotation cost and no
teacher model. The ground truth is produced by the same code that renders the document, so a
label can never disagree with the text it describes.

## Fields

Fifteen scalar fields plus four performance scenarios, each with a value and an annualised
return, giving 23 scored fields. Every field is optional; a field absent from the document is
null in the label.

`fund_name`, `isin`, `currency`, `sri`, `srri`, `ongoing_charges_pct`, `entry_charge_pct`,
`exit_charge_pct`, `transaction_costs_pct`, `performance_fee_pct`,
`recommended_holding_period_years`, `investment_objective`, `benchmark`, `domicile`,
`management_company`, `scenarios.{stress,unfavourable,moderate,favourable}.{value,return_pct}`

PRIIPs KIDs carry `sri` and a scenario table. UCITS KIIDs carry `srri` and neither.

## Variation

| Dimension | Values |
| --- | --- |
| Layouts | 12 |
| Languages | English, German, French, Dutch |
| Document types | PRIIPs KID, UCITS KIID |
| Cost presentation | table, bullets, prose |
| Risk presentation | scale drawing, `n / 7`, sentence |
| Number notation | decimal point, decimal comma, basis points |
| Label wordings | 3 to 4 per field per language |
| Field dropout | per field, 5% to 35% |

Documents also carry simulated PDF extraction artefacts: ligatures, hyphenation across line
breaks, irregular column spacing, and page headers and footers landing mid-content. Lines
carrying a labelled value are exempt from character corruption, so every label stays
recoverable from the text.

Practical-information sections contain unrelated percentages — depositary fees, switching
charges — so that taking the first number on the page is not a winning strategy.

## Splits

| Split | Layouts | Vocabulary | Purpose |
| --- | --- | --- | --- |
| `train` | 9 | known | training |
| `validation` | 9 | known | model selection |
| `test_seen` | 9 | known | in-distribution score |
| `test_unseen_layout` | 3 held out | **reserved** | generalisation |

The last label wording of every field is reserved and appears only in `test_unseen_layout`.
That split therefore combines layouts and vocabulary the system has never seen, which is the
position a deployed extractor is in when a new provider appears.

Funds do not repeat across splits; ISIN overlap between training and every evaluation split is
zero and asserted in the test suite.

## Known limitations

- Generated documents are more regular than real ones. Absolute scores are optimistic.
- Twelve layouts stand in for hundreds of real providers. Structural variety is understated
  even though label variety is modelled explicitly.
- Objective text is drawn from templates, so `investment_objective` is easier to copy than
  free prose in a real document.
- Scenario values are modelled from risk level rather than from real fund performance.

## Grounding in real fund attributes

Passing `--reference-csv` with the Morningstar European funds dataset from Kaggle substitutes
real fund names, ISINs, ongoing charges and risk ratings for the synthesised ones. Only the
attributes that dataset lacks are generated. Document text remains synthetic either way.

## Reproduction

```bash
python -m kidextract.cli.build_dataset --out data/processed --train 6000 --validation 500 --test 500
```

Generation is deterministic given the split seeds, which are fixed in
`kidextract.dataset.build.default_plans`.

## Licence

MIT, matching the repository. Contains no proprietary or confidential material.
