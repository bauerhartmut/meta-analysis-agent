from __future__ import annotations

import json
from pathlib import Path

import pytest

from research_agent.meta.verified_pool import (
    UnverifiedRecordError, build_verified_analysis, gate_rows,
)
from research_agent.verification.compare import comparison_entry, evidence_supports
from research_agent.verification.schema import (
    compare_values, transition_field, transition_record,
)
from research_agent.verification.store import VerificationStore
from research_agent.verification.workflow import (
    finalize_after_review, invalidate_on_source_change,
)


def _verified_state(record_id="r1"):
    return {
        "records": {
            record_id: {
                "record_id": record_id,
                "status": "verified",
                "required_fields": ["intervention_n", "comparator_n"],
                "fields": {
                    "intervention_n": {
                        "status": "verified", "reported": True,
                        "final_value": 10, "evidence_id": "ev:n1",
                    },
                    "comparator_n": {
                        "status": "verified", "reported": True,
                        "final_value": 20, "evidence_id": "ev:n2",
                    },
                },
                "evidence": {
                    "ev:n1": {
                        "field": "intervention_n", "row_label": "Arm A",
                        "column_label": "N", "raw_cell": "10",
                    },
                    "ev:n2": {
                        "field": "comparator_n", "row_label": "Arm B",
                        "column_label": "N", "raw_cell": "20",
                    },
                },
            }
        }
    }


def _evidence(**overrides):
    base = {
        "evidence_id": "ev:1",
        "table_id": "md:1",
        "row_label": "Posttreatment VAS",
        "column_label": "Group I",
        "raw_cell": "3.76 (1.45)",
        "line_start": 4,
    }
    base.update(overrides)
    return base


def _review_store(tmp_path, field="intervention_mean", comparison="match",
                  value_a=1.0, value_b=1.0):
    store = VerificationStore(str(tmp_path / "audit.json"))
    store.register_record("r1", {
        "document_hash": "x", "outcome_type": "continuous",
        "required_fields": [field],
    })
    store.record_comparison("r1", {
        "field": field, "value_a": value_a, "value_b": value_b,
        "comparison": comparison, "rule": "test",
        "field_status": "cross_checked",
    })
    store.set_status("r1", "cross_checked", "test")
    store.set_status("r1", "pending_review", "test")
    return store


def test_missing_evidence_is_never_a_match():
    entry = comparison_entry("intervention_mean", 3.76, 3.76, None)
    assert entry["comparison"] == "evidence_missing"
    assert entry["field_status"] == "unresolved"


def test_exact_cell_supports_value_in_context():
    assert evidence_supports(_evidence(), "intervention_mean", 3.76)
    assert not evidence_supports(_evidence(row_label="Baseline VAS"),
                                 "intervention_mean", 3.76)
    assert not evidence_supports(_evidence(column_label=""),
                                 "intervention_mean", 3.76)


def test_rounding_tolerance_is_explicit_and_narrow():
    assert compare_values("intervention_mean", 0.333, 0.33)[0] == "numeric_match"
    assert compare_values("intervention_mean", 0.333, 0.34)[0] == "mismatch"
    assert compare_values("intervention_n", 103.0, 103)[0] == "match"


def test_invalid_status_transitions_raise():
    with pytest.raises(ValueError):
        transition_record("rejected", "verified")
    with pytest.raises(ValueError):
        transition_field("extracted", "verified")


def test_gate_refuses_unverified_without_silent_filtering():
    state = _verified_state()
    state["records"]["r1"]["status"] = "pending_review"
    with pytest.raises(UnverifiedRecordError):
        gate_rows([{"verification_record_id": "r1", "label": "A"}], state)


def test_gate_accepts_verified_and_refuses_unknown():
    state = _verified_state()
    accepted, refused = gate_rows(
        [{"verification_record_id": "r1", "label": "A"},
         {"verification_record_id": "missing", "label": "B"}],
        state, allow_unverified=True,
    )
    assert [row["label"] for row in accepted] == ["A"]
    assert refused[0]["status"] == "missing"


def test_gate_does_not_infer_from_generic_record_id():
    with pytest.raises(UnverifiedRecordError):
        gate_rows([{"record_id": "r1", "label": "A"}], _verified_state())


def test_gate_rechecks_value_and_evidence_not_only_status():
    state = _verified_state()
    state["records"]["r1"]["fields"]["intervention_n"].pop("final_value")
    with pytest.raises(UnverifiedRecordError):
        gate_rows([{"verification_record_id": "r1", "label": "A"}], state)


def test_gate_rejects_evidence_that_does_not_support_value():
    state = _verified_state()
    state["records"]["r1"]["evidence"]["ev:n1"]["raw_cell"] = "99"
    with pytest.raises(UnverifiedRecordError):
        gate_rows([{"verification_record_id": "r1", "label": "A"}], state)


def test_verified_analysis_receives_only_gated_rows(monkeypatch):
    captured = {}
    def fake_build(rows, outcomes=None, targets=None):
        captured["rows"] = list(rows)
        return {"groups": {}, "excluded": [], "off_target": [],
                "usable": len(captured["rows"]), "total": len(captured["rows"])}
    monkeypatch.setattr("research_agent.meta.pooling.build_analysis", fake_build)
    analysis = build_verified_analysis(
        [{"verification_record_id": "r1", "label": "A"}],
        _verified_state(),
    )
    assert captured["rows"] == [{"verification_record_id": "r1", "label": "A"}]
    assert analysis["verification_gate"]["verified_rows"] == 1


def test_verified_analysis_refuses_before_pooling(monkeypatch):
    called = {"value": False}
    def fake_build(rows, outcomes=None, targets=None):
        called["value"] = True
        return {}
    monkeypatch.setattr("research_agent.meta.pooling.build_analysis", fake_build)
    with pytest.raises(UnverifiedRecordError):
        build_verified_analysis(
            [{"verification_record_id": "missing", "label": "B"}],
            _verified_state(),
        )
    assert called["value"] is False


def test_decision_preserves_old_value_and_invalidation_drops_approval(tmp_path):
    store = VerificationStore(str(tmp_path / "audit.json"))
    store.register_record("r1", {
        "document_hash": "old", "outcome_type": "continuous",
        "required_fields": ["intervention_mean"],
    })
    store.record_comparison("r1", {
        "field": "intervention_mean", "value_a": 1.0, "value_b": 1.0,
        "comparison": "mismatch", "rule": "test", "field_status": "unresolved",
    })
    store.add_evidence("r1", [{
        "evidence_id": "ev:1", "field": "intervention_mean",
        "table_id": "md:1", "row_label": "Posttreatment",
        "column_label": "Intervention", "raw_cell": "2.0 (0.5)",
    }])
    store.set_status("r1", "cross_checked", "test")
    store.set_status("r1", "pending_review", "test")
    store.apply_decision("r1", "intervention_mean", "correct", value=2.0,
                         reviewer="Pruefer A", note="Quelle", evidence_id="ev:1")
    record = store.record("r1")
    assert record["fields"]["intervention_mean"]["final_value"] == 2.0
    decision = record["decisions"][-1]
    assert decision["old"]["final_value"] == 1.0
    store.set_status("r1", "verified", "test", basis="human_review")
    assert invalidate_on_source_change(store, "r1", "new") is True
    assert store.record("r1")["status"] == "pending_review"
    assert store.record("r1")["fields"]["intervention_mean"]["status"] == "cross_checked"


def test_audit_chain_detects_tampering(tmp_path):
    path = tmp_path / "audit.json"
    store = VerificationStore(str(path))
    store.register_record("r1", {"document_hash": "x", "outcome_type": "binary",
                                 "required_fields": []})
    store.set_status("r1", "cross_checked", "x")
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["events"][0]["payload"]["document_hash"] = "manipulated"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        VerificationStore(str(path))


def test_review_requires_reviewer_and_reason_for_not_reported(tmp_path):
    store = VerificationStore(str(tmp_path / "audit.json"))
    store.register_record("r1", {"document_hash": "x", "outcome_type": "continuous",
                                 "required_fields": ["intervention_sd"]})
    store.record_comparison("r1", {
        "field": "intervention_sd", "value_a": 1.0, "value_b": 1.0,
        "comparison": "mismatch", "rule": "test", "field_status": "unresolved",
    })
    with pytest.raises(ValueError):
        store.apply_decision("r1", "intervention_sd", "confirm", reviewer="")
    with pytest.raises(ValueError):
        store.apply_decision("r1", "intervention_sd", "not_reported",
                             reviewer="A", note="")


def test_confirm_without_evidence_leaves_field_open(tmp_path):
    store = _review_store(tmp_path)
    store.apply_decision("r1", "intervention_mean", "confirm",
                         reviewer="Pruefer A")
    record = store.record("r1")
    field = record["fields"]["intervention_mean"]
    assert field["status"] == "unresolved"
    assert field["final_value"] == 1.0
    assert record["status"] == "pending_review"
    assert record["decisions"][-1]["action"] == "confirm"


def test_confirm_both_missing_leaves_field_open(tmp_path):
    store = _review_store(tmp_path, comparison="both_missing",
                          value_a=None, value_b=None)
    store.add_evidence("r1", [{
        "evidence_id": "ev:both-missing", "field": "intervention_mean",
        "table_id": "md:1", "row_label": "Posttreatment",
        "column_label": "Intervention", "raw_cell": "-",
    }])
    store.apply_decision("r1", "intervention_mean", "confirm",
                         reviewer="Pruefer A", evidence_id="ev:both-missing")
    field = store.record("r1")["fields"]["intervention_mean"]
    assert field["status"] == "unresolved"
    assert field["final_value"] is None
    assert field["evidence_id"] == ""


def test_correct_without_value_leaves_field_open(tmp_path):
    store = _review_store(tmp_path)
    store.add_evidence("r1", [{
        "evidence_id": "ev:value", "field": "intervention_mean",
        "table_id": "md:1", "row_label": "Posttreatment",
        "column_label": "Intervention", "raw_cell": "2.0 (0.5)",
    }])
    store.apply_decision("r1", "intervention_mean", "correct", value=None,
                         reviewer="Pruefer A", evidence_id="ev:value")
    field = store.record("r1")["fields"]["intervention_mean"]
    assert field["status"] == "unresolved"
    assert field["final_value"] is None


def test_confirm_with_stored_evidence_can_verify(tmp_path):
    store = _review_store(tmp_path)
    store.add_evidence("r1", [{
        "evidence_id": "ev:value", "field": "intervention_mean",
        "table_id": "md:1", "row_label": "Posttreatment",
        "column_label": "Intervention", "raw_cell": "1.0 (0.5)",
    }])
    store.apply_decision("r1", "intervention_mean", "confirm",
                         reviewer="Pruefer A", evidence_id="ev:value")
    assert finalize_after_review(store, "r1", "Pruefer A") == "verified"
    assert store.record("r1")["status"] == "verified"


def test_correction_with_unknown_evidence_stays_open(tmp_path):
    store = _review_store(tmp_path)
    store.apply_decision("r1", "intervention_mean", "correct", value=2.0,
                         reviewer="Pruefer A", evidence_id="ev:not-stored")
    field = store.record("r1")["fields"]["intervention_mean"]
    assert field["status"] == "unresolved"


def test_correction_with_unrelated_evidence_stays_open(tmp_path):
    store = _review_store(tmp_path)
    store.add_evidence("r1", [{
        "evidence_id": "ev:wrong-value", "field": "intervention_mean",
        "table_id": "md:1", "row_label": "Posttreatment",
        "column_label": "Intervention", "raw_cell": "9.9 (0.5)",
    }])
    store.apply_decision("r1", "intervention_mean", "correct", value=2.0,
                         reviewer="Pruefer A", evidence_id="ev:wrong-value")
    field = store.record("r1")["fields"]["intervention_mean"]
    assert field["status"] == "unresolved"


def test_finalize_keeps_unresolved_context_field_open(tmp_path):
    store = _review_store(tmp_path)
    store.record_comparison("r1", {
        "field": "outcome", "value_a": "Pain", "value_b": "Pain",
        "comparison": "mismatch", "rule": "test",
        "field_status": "unresolved",
    })
    store.add_evidence("r1", [{
        "evidence_id": "ev:value", "field": "intervention_mean",
        "table_id": "md:1", "row_label": "Posttreatment",
        "column_label": "Intervention", "raw_cell": "1.0 (0.5)",
    }])
    store.apply_decision("r1", "intervention_mean", "confirm",
                         reviewer="Pruefer A", evidence_id="ev:value")
    assert finalize_after_review(store, "r1", "Pruefer A") == "pending_review"
