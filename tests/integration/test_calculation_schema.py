import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime
from app.schemas.calculation import (
    CalculationCreate,
    CalculationUpdate,
    CalculationResponse,
    CalculationStatsResponse
)

def test_calc_create_ok():
    """Valid CalculationCreate schema."""
    d = {
        "type": "addition",
        "inputs": [10.5, 3.0],
        "user_id": uuid4()
    }
    calc = CalculationCreate(**d)
    assert calc.type == "addition"
    assert calc.inputs == [10.5, 3.0]
    assert calc.user_id is not None

def test_calc_create_no_type():
    """Missing type fails."""
    d = {
        "inputs": [10.5, 3.0],
        "user_id": uuid4()
    }
    with pytest.raises(ValidationError) as exc:
        CalculationCreate(**d)
    assert "required" in str(exc.value).lower()

def test_calc_create_no_inputs():
    """Missing inputs fails."""
    d = {
        "type": "multiplication",
        "user_id": uuid4()
    }
    with pytest.raises(ValidationError) as exc:
        CalculationCreate(**d)
    assert "required" in str(exc.value).lower()

def test_calc_create_bad_inputs():
    """Non-list inputs fail."""
    d = {
        "type": "division",
        "inputs": "not-a-list",
        "user_id": uuid4()
    }
    with pytest.raises(ValidationError) as exc:
        CalculationCreate(**d)
    msg = str(exc.value)
    assert "input should be a valid list" in msg.lower(), msg

def test_calc_create_bad_type():
    """Unsupported type fails."""
    d = {
        "type": "square_root",  # Unsupported type
        "inputs": [25],
        "user_id": uuid4()
    }
    with pytest.raises(ValidationError) as exc:
        CalculationCreate(**d)
    msg = str(exc.value).lower()
    assert "one of" in msg or "not a valid" in msg

def test_calc_update_ok():
    """Valid partial update."""
    d = {
        "inputs": [42.0, 7.0]
    }
    upd = CalculationUpdate(**d)
    assert upd.inputs == [42.0, 7.0]

def test_calc_update_empty_ok():
    """Empty update is allowed."""
    upd = CalculationUpdate()
    assert upd.inputs is None

def test_calc_resp_ok():
    """Valid CalculationResponse schema."""
    d = {
        "id": uuid4(),
        "user_id": uuid4(),
        "type": "subtraction",
        "inputs": [20, 5],
        "result": 15.5,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    res = CalculationResponse(**d)
    assert res.id is not None
    assert res.user_id is not None
    assert res.type == "subtraction"
    assert res.inputs == [20, 5]
    assert res.result == 15.5


def test_calc_stat_resp_ok():
    """Valid CalculationStatsResponse schema."""
    s = CalculationStatsResponse(
        total_calculations=3,
        average_inputs_per_calculation=2.33,
        average_result=10.33,
        operation_counts={
            "addition": 2,
            "subtraction": 0,
            "multiplication": 0,
            "division": 1,
        },
        most_used_operation="addition",
        latest_calculation_at=datetime.utcnow(),
    )

    assert s.total_calculations == 3
    assert s.average_inputs_per_calculation == 2.33
    assert s.average_result == 10.33
    assert s.operation_counts["addition"] == 2
