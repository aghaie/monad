"""رجیستریِ پریدیکیت‌ها — سطحِ پروتکل، دامنه‌مستقل. فقط قرارداد؛ اجرا در DomainAdapter."""
REGISTRY = {
    "masked_recovery": {
        "params_schema": {},
        "pass_rule_doc": "score > baseline * 1.5"},
    "cooccurrence_constraint": {
        "params_schema": {"with_root_id": "int"},
        "pass_rule_doc": "lift > 1.5 ∧ null_p < 0.05"},
    "two_half_stability": {
        "params_schema": {"with_root_id": "int"},
        "pass_rule_doc": "present in both mushaf halves (presence check, not a significance test)"},
}


def known(name) -> bool:
    return name in REGISTRY
