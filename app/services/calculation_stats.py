"""Calc report helpers."""

from datetime import datetime
from typing import Any, Dict, Iterable, Optional

from app.schemas.calculation import CalculationType


def summarize_calcs(calcs: Iterable[Any]) -> Dict[str, Any]:
    """Build calc report stats."""
    op_order = [op.value for op in CalculationType]
    op_counts = {op: 0 for op in op_order}
    total_calcs = 0
    input_ct = 0
    result_sum = 0.0
    result_ct = 0
    latest_at: Optional[datetime] = None

    for calc in calcs:
        total_calcs += 1

        calc_type = str(getattr(calc, "type", "")).lower()
        op_counts[calc_type] = op_counts.get(calc_type, 0) + 1

        nums = getattr(calc, "inputs", [])
        if isinstance(nums, list):
            input_ct += len(nums)

        result = getattr(calc, "result", None)
        if result is not None:
            result_sum += float(result)
            result_ct += 1

        created_at = getattr(calc, "created_at", None)
        if created_at and (latest_at is None or created_at > latest_at):
            latest_at = created_at

    avg_inputs = (
        round(input_ct / total_calcs, 2)
        if total_calcs
        else 0.0
    )
    avg_result = (
        round(result_sum / result_ct, 2)
        if result_ct
        else None
    )
    used_ops = [
        (op, ct)
        for op, ct in op_counts.items()
        if ct > 0
    ]

    def op_rank(item):
        op, ct = item
        idx = op_order.index(op) if op in op_order else 0
        return ct, -idx

    top_op = (
        max(used_ops, key=op_rank)[0]
        if used_ops
        else None
    )

    return {
        "total_calculations": total_calcs,
        "average_inputs_per_calculation": avg_inputs,
        "average_result": avg_result,
        "operation_counts": op_counts,
        "most_used_operation": top_op,
        "latest_calculation_at": latest_at,
    }
