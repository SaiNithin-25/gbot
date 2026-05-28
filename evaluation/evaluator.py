"""evaluation/evaluator.py — Post-execution workflow evaluation."""
import logging
log = logging.getLogger("evaluation")

class WorkflowEvaluator:
    def evaluate(self, workflow, world_model) -> dict:
        report = {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status,
            "structure_count": len(world_model.all_structures()),
            "passed": workflow.status == "complete",
        }
        log.info(f"Eval: {report}")
        return report
