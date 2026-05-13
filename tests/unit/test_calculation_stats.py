from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from app.services.calculation_stats import summarize_calcs


@dataclass
class CalcStub:
    type: str
    inputs: List[float]
    result: Optional[float]
    created_at: datetime


def test_sum_calc_empty_hist():
    s = summarize_calcs([])

    assert s["total_calculations"] == 0
    assert s["average_inputs_per_calculation"] == 0.0
    assert s["average_result"] is None
    assert s["most_used_operation"] is None
    assert s["latest_calculation_at"] is None
    assert s["operation_counts"] == {
        "addition": 0,
        "subtraction": 0,
        "multiplication": 0,
        "division": 0,
    }


def test_sum_calc_metrics():
    calcs = [
        CalcStub("addition", [1, 2, 3], 6, datetime(2026, 1, 1, 9, 0, 0)),
        CalcStub("addition", [10, 5], 15, datetime(2026, 1, 2, 9, 0, 0)),
        CalcStub("division", [20, 2], 10, datetime(2026, 1, 3, 9, 0, 0)),
    ]

    s = summarize_calcs(calcs)

    assert s["total_calculations"] == 3
    assert s["average_inputs_per_calculation"] == 2.33
    assert s["average_result"] == 10.33
    assert s["operation_counts"]["addition"] == 2
    assert s["operation_counts"]["division"] == 1
    assert s["operation_counts"]["subtraction"] == 0
    assert s["operation_counts"]["multiplication"] == 0
    assert s["most_used_operation"] == "addition"
    assert s["latest_calculation_at"] == datetime(2026, 1, 3, 9, 0, 0)
