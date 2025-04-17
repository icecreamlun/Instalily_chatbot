"""
Test module for the repair chain implementation.
Tests focus on refrigerator and dishwasher repair scenarios.
"""

import logging
from repair_chain import RepairChain

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_refrigerator_scenarios():
    """Test various refrigerator repair scenarios."""
    repair_chain = RepairChain()
    
    # Test case 1: Refrigerator not cooling
    logger.info("\nTest Case 1: Refrigerator not cooling")
    result = repair_chain.diagnose(
        appliance_type="refrigerator",
        problem_description="The refrigerator is not cooling properly, temperature is too high"
    )
    print_diagnosis_result(result)
    
    # Test case 2: Refrigerator making noise
    logger.info("\nTest Case 2: Refrigerator making noise")
    result = repair_chain.diagnose(
        appliance_type="refrigerator",
        problem_description="The refrigerator is making a loud grinding noise"
    )
    print_diagnosis_result(result)
    
    # Test case 3: Refrigerator water leak
    logger.info("\nTest Case 3: Refrigerator water leak")
    result = repair_chain.diagnose(
        appliance_type="refrigerator",
        problem_description="Water is leaking from the bottom of the refrigerator"
    )
    print_diagnosis_result(result)

def test_dishwasher_scenarios():
    """Test various dishwasher repair scenarios."""
    repair_chain = RepairChain()
    
    # Test case 1: Dishwasher not draining
    logger.info("\nTest Case 1: Dishwasher not draining")
    result = repair_chain.diagnose(
        appliance_type="dishwasher",
        problem_description="The dishwasher is not draining properly, water remains at the bottom"
    )
    print_diagnosis_result(result)
    
    # Test case 2: Dishwasher not starting
    logger.info("\nTest Case 2: Dishwasher not starting")
    result = repair_chain.diagnose(
        appliance_type="dishwasher",
        problem_description="The dishwasher won't start when I press the start button"
    )
    print_diagnosis_result(result)
    
    # Test case 3: Dishwasher display error
    logger.info("\nTest Case 3: Dishwasher display error")
    result = repair_chain.diagnose(
        appliance_type="dishwasher",
        problem_description="The dishwasher display shows an error code E3"
    )
    print_diagnosis_result(result)

def test_unsupported_appliance():
    """Test handling of unsupported appliance type."""
    repair_chain = RepairChain()
    
    logger.info("\nTest Case: Unsupported Appliance")
    result = repair_chain.diagnose(
        appliance_type="washing machine",
        problem_description="The washing machine is not spinning"
    )
    print_diagnosis_result(result)

def test_non_repair_issue():
    """Test handling of non-repair related issues."""
    repair_chain = RepairChain()
    
    logger.info("\nTest Case: Non-Repair Issue")
    result = repair_chain.diagnose(
        appliance_type="refrigerator",
        problem_description="I want to buy a new refrigerator"
    )
    print_diagnosis_result(result)

def print_diagnosis_result(result: dict):
    """Print the diagnosis result in a formatted way."""
    # Check if this is an error result
    if "error" in result:
        logger.info(f"\nError: {result['error']}")
        logger.info(f"Message: {result['message']}")
        logger.info("\n" + "="*50)
        return
    
    # Print normal diagnosis result
    logger.info(f"\nProblem Type: {result['problem_type']}")
    
    logger.info("\nInitial Assessment:")
    for key, value in result['initial_assessment'].items():
        logger.info(f"{key}: {value}")
    
    logger.info("\nDiagnosis Steps:")
    for step in result['diagnosis_steps']:
        logger.info(f"\nStep {step['step_number']}: {step['description']}")
        logger.info(f"Possible Causes: {', '.join(step['possible_causes'])}")
        logger.info(f"Verification Method: {step['verification_method']}")
        logger.info(f"Solution: {step['solution']}")
        if step['safety_notes']:
            logger.info(f"Safety Notes: {step['safety_notes']}")
    
    logger.info("\nChain of Thought Analysis:")
    for thought in result['chain_of_thought']:
        logger.info(thought)
    
    logger.info("\nPreventive Measures:")
    for measure in result['preventive_measures']:
        logger.info(f"- {measure}")
    
    logger.info("\nSafety Notes:")
    for note in result['safety_notes']:
        logger.info(f"- {note}")
    
    logger.info("\n" + "="*50)

if __name__ == "__main__":
    logger.info("Testing Refrigerator Scenarios...")
    test_refrigerator_scenarios()
    
    logger.info("\nTesting Dishwasher Scenarios...")
    test_dishwasher_scenarios()
    
    logger.info("\nTesting Unsupported Appliance...")
    test_unsupported_appliance()
    
    logger.info("\nTesting Non-Repair Issue...")
    test_non_repair_issue() 