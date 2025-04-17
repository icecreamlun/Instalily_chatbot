"""
This module implements a Chain of Thought based repair diagnosis system.
It provides structured analysis and solutions for refrigerator and dishwasher repair issues.
"""

from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
from enum import Enum

class ProblemType(Enum):
    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"
    SOFTWARE = "software"
    PLUMBING = "plumbing"
    GENERAL = "general"

@dataclass
class DiagnosisStep:
    step_number: int
    description: str
    possible_causes: List[str]
    verification_method: str
    solution: str
    safety_notes: Optional[str] = None

class RepairChain:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.problem_types = {
            ProblemType.ELECTRICAL: self._analyze_electrical,
            ProblemType.MECHANICAL: self._analyze_mechanical,
            ProblemType.SOFTWARE: self._analyze_software,
            ProblemType.PLUMBING: self._analyze_plumbing,
            ProblemType.GENERAL: self._analyze_general
        }
        self.supported_appliances = ["refrigerator", "dishwasher"]

    def diagnose(self, appliance_type: str, problem_description: str) -> Dict:
        """
        Perform a chain of thought diagnosis for an appliance problem.
        If the problem is repair-related, search the database for relevant information.
        Only supports refrigerator and dishwasher repairs.
        
        Args:
            appliance_type: Type of appliance
            problem_description: Description of the problem
            
        Returns:
            Dictionary containing the diagnosis steps and recommendations
        """
        try:
            # Check if appliance type is supported
            if appliance_type.lower() not in self.supported_appliances:
                return {
                    "error": "unsupported_appliance",
                    "message": f"Currently only support repairs for: {', '.join(self.supported_appliances)}"
                }
            
            # Check if the problem is repair-related
            repair_keywords = [
                "repair", "fix", "broken", "not working", "malfunction",
                "issue", "problem", "fault", "error", "trouble"
            ]
            
            if not any(keyword in problem_description.lower() for keyword in repair_keywords):
                return {
                    "error": "not_repair_related",
                    "message": "This appears to be a non-repair related issue. Please describe the repair problem."
                }
            
            # Step 1: Problem Analysis
            problem_type = self._determine_problem_type(problem_description)
            self.logger.info(f"Problem type determined: {problem_type.value}")
            
            # Step 2: Initial Assessment
            initial_assessment = self._create_initial_assessment(appliance_type, problem_description)
            
            # Step 3: Detailed Analysis using Chain of Thought
            analysis_method = self.problem_types.get(problem_type, self._analyze_general)
            diagnosis_steps = analysis_method(appliance_type, problem_description)
            
            # Step 4: Compile Results
            result = {
                "problem_type": problem_type.value,
                "initial_assessment": initial_assessment,
                "diagnosis_steps": [step.__dict__ for step in diagnosis_steps],
                "preventive_measures": self._get_preventive_measures(appliance_type, problem_type),
                "safety_notes": self._get_safety_notes(appliance_type, problem_type),
                "chain_of_thought": self._generate_chain_of_thought(appliance_type, problem_description, problem_type)
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in diagnosis: {str(e)}")
            return {
                "error": "diagnosis_error",
                "message": "Unable to complete diagnosis due to an unexpected error"
            }

    def _determine_problem_type(self, problem_description: str) -> ProblemType:
        """Determine the type of problem based on description."""
        problem_lower = problem_description.lower()
        
        # Refrigerator specific checks
        if "refrigerator" in problem_lower:
            if any(word in problem_lower for word in ["not cooling", "temperature", "warm", "hot"]):
                return ProblemType.MECHANICAL
            elif any(word in problem_lower for word in ["leak", "water", "ice"]):
                return ProblemType.PLUMBING
            elif any(word in problem_lower for word in ["noise", "sound", "grinding"]):
                return ProblemType.MECHANICAL
            elif any(word in problem_lower for word in ["display", "error", "code"]):
                return ProblemType.SOFTWARE
            elif any(word in problem_lower for word in ["power", "electric", "circuit"]):
                return ProblemType.ELECTRICAL
        
        # Dishwasher specific checks
        elif "dishwasher" in problem_lower:
            if any(word in problem_lower for word in ["not draining", "water", "leak"]):
                return ProblemType.PLUMBING
            elif any(word in problem_lower for word in ["not starting", "power", "electric"]):
                return ProblemType.ELECTRICAL
            elif any(word in problem_lower for word in ["error", "code", "display"]):
                return ProblemType.SOFTWARE
            elif any(word in problem_lower for word in ["noise", "sound", "grinding"]):
                return ProblemType.MECHANICAL
        
        # General checks
        if any(word in problem_lower for word in ["power", "electric", "circuit", "voltage"]):
            return ProblemType.ELECTRICAL
        elif any(word in problem_lower for word in ["leak", "water", "drain", "pipe"]):
            return ProblemType.PLUMBING
        elif any(word in problem_lower for word in ["error", "code", "display", "program"]):
            return ProblemType.SOFTWARE
        elif any(word in problem_lower for word in ["noise", "vibration", "movement", "part"]):
            return ProblemType.MECHANICAL
        else:
            return ProblemType.GENERAL

    def _create_initial_assessment(self, appliance_type: str, problem_description: str) -> Dict:
        """Create initial assessment of the problem."""
        return {
            "appliance": appliance_type,
            "problem": problem_description,
            "complexity": self._assess_complexity(problem_description),
            "urgency": self._assess_urgency(problem_description),
            "tools_needed": self._get_initial_tools(appliance_type, self._determine_problem_type(problem_description))
        }

    def _analyze_electrical(self, appliance_type: str, problem_description: str) -> List[DiagnosisStep]:
        """Analyze electrical problems."""
        steps = []
        
        # Step 1: Power Supply Check
        steps.append(DiagnosisStep(
            step_number=1,
            description="Check power supply and connections",
            possible_causes=["Power cord issue", "Outlet problem", "Circuit breaker tripped"],
            verification_method="Use multimeter to check voltage",
            solution="Verify power source and connections",
            safety_notes="Always disconnect power before inspection"
        ))
        
        # Step 2: Internal Wiring
        steps.append(DiagnosisStep(
            step_number=2,
            description="Inspect internal wiring and connections",
            possible_causes=["Loose connections", "Damaged wires", "Faulty components"],
            verification_method="Visual inspection and continuity test",
            solution="Repair or replace damaged components",
            safety_notes="Ensure proper insulation and grounding"
        ))
        
        return steps

    def _analyze_mechanical(self, appliance_type: str, problem_description: str) -> List[DiagnosisStep]:
        """Analyze mechanical problems."""
        steps = []
        
        # Step 1: Visual Inspection
        steps.append(DiagnosisStep(
            step_number=1,
            description="Perform visual inspection of moving parts",
            possible_causes=["Worn components", "Obstructions", "Misalignment"],
            verification_method="Visual and physical inspection",
            solution="Clean, lubricate, or replace components",
            safety_notes="Ensure appliance is unplugged"
        ))
        
        # Step 2: Component Testing
        steps.append(DiagnosisStep(
            step_number=2,
            description="Test individual mechanical components",
            possible_causes=["Motor failure", "Belt issues", "Bearing problems"],
            verification_method="Manual testing and observation",
            solution="Replace or repair faulty components",
            safety_notes="Follow manufacturer's guidelines"
        ))
        
        return steps

    def _analyze_software(self, appliance_type: str, problem_description: str) -> List[DiagnosisStep]:
        """Analyze software/control problems."""
        steps = []
        
        # Step 1: Error Code Analysis
        steps.append(DiagnosisStep(
            step_number=1,
            description="Check for error codes and diagnostics",
            possible_causes=["Software glitch", "Sensor failure", "Control board issue"],
            verification_method="Check display and error codes",
            solution="Reset or update software",
            safety_notes="Backup settings if possible"
        ))
        
        # Step 2: Control System Check
        steps.append(DiagnosisStep(
            step_number=2,
            description="Inspect control system components",
            possible_causes=["Faulty sensors", "Control board failure", "Programming error"],
            verification_method="Diagnostic mode and testing",
            solution="Replace or reprogram control system",
            safety_notes="Handle electronic components carefully"
        ))
        
        return steps

    def _analyze_plumbing(self, appliance_type: str, problem_description: str) -> List[DiagnosisStep]:
        """Analyze plumbing-related problems."""
        steps = []
        
        # Step 1: Leak Detection
        steps.append(DiagnosisStep(
            step_number=1,
            description="Locate and identify leaks",
            possible_causes=["Pipe damage", "Seal failure", "Connection issues"],
            verification_method="Visual inspection and pressure test",
            solution="Repair or replace damaged components",
            safety_notes="Turn off water supply before inspection"
        ))
        
        # Step 2: Flow Analysis
        steps.append(DiagnosisStep(
            step_number=2,
            description="Check water flow and drainage",
            possible_causes=["Clogged pipes", "Pump failure", "Valve issues"],
            verification_method="Flow test and inspection",
            solution="Clear obstructions or replace components",
            safety_notes="Ensure proper drainage"
        ))
        
        return steps

    def _analyze_general(self, appliance_type: str, problem_description: str) -> List[DiagnosisStep]:
        """General analysis for undefined problems."""
        steps = []
        
        # Step 1: Basic Troubleshooting
        steps.append(DiagnosisStep(
            step_number=1,
            description="Perform basic troubleshooting",
            possible_causes=["General malfunction", "Multiple issues", "Unknown cause"],
            verification_method="Systematic testing",
            solution="Follow manufacturer's troubleshooting guide",
            safety_notes="Proceed with caution"
        ))
        
        return steps

    def _assess_complexity(self, problem_description: str) -> str:
        """Assess the complexity of the problem."""
        complexity_keywords = {
            "simple": [
                "reset", "clean", "basic", "unplug", "plug in",
                "filter", "drain", "clear", "blockage"
            ],
            "moderate": [
                "replace", "repair", "adjust", "sensor", "thermostat",
                "valve", "pump", "motor", "fan", "coil"
            ],
            "complex": [
                "circuit", "board", "compressor", "seal", "refrigerant",
                "leak", "pressure", "control", "system", "wiring"
            ]
        }
        
        problem_lower = problem_description.lower()
        
        # Count matches for each complexity level
        matches = {level: sum(1 for keyword in keywords if keyword in problem_lower)
                  for level, keywords in complexity_keywords.items()}
        
        # Determine complexity based on matches
        if matches["complex"] > 0:
            return "complex"
        elif matches["moderate"] > 0:
            return "moderate"
        elif matches["simple"] > 0:
            return "simple"
        else:
            return "unknown"

    def _assess_urgency(self, problem_description: str) -> str:
        """Assess the urgency of the problem."""
        urgency_keywords = {
            "high": ["leak", "smoke", "fire", "spark"],
            "medium": ["not working", "broken", "faulty"],
            "low": ["noise", "slow", "minor"]
        }
        
        problem_lower = problem_description.lower()
        for level, keywords in urgency_keywords.items():
            if any(keyword in problem_lower for keyword in keywords):
                return level
        return "unknown"

    def _get_initial_tools(self, appliance_type: str, problem_type: ProblemType) -> List[str]:
        """Get initial tools needed based on appliance type and problem type."""
        base_tools = {
            "refrigerator": ["multimeter", "thermometer", "screwdriver set"],
            "dishwasher": ["multimeter", "screwdriver set", "pliers"]
        }
        
        problem_specific_tools = {
            ProblemType.ELECTRICAL: ["voltage tester", "continuity tester"],
            ProblemType.MECHANICAL: ["wrench set", "lubricant"],
            ProblemType.PLUMBING: ["plunger", "drain snake", "bucket"],
            ProblemType.SOFTWARE: ["user manual", "reset tool"],
            ProblemType.GENERAL: ["flashlight", "gloves"]
        }
        
        tools = base_tools.get(appliance_type.lower(), [])
        tools.extend(problem_specific_tools.get(problem_type, []))
        
        return list(set(tools))  # Remove duplicates

    def _get_preventive_measures(self, appliance_type: str, problem_type: ProblemType) -> List[str]:
        """Get preventive measures based on appliance and problem type."""
        measures = []
        
        # General measures
        measures.extend([
            "Regular maintenance and cleaning",
            "Follow manufacturer's usage guidelines",
            "Monitor for unusual sounds or behaviors"
        ])
        
        # Type-specific measures
        if problem_type == ProblemType.ELECTRICAL:
            measures.extend([
                "Check power cords regularly",
                "Use surge protectors",
                "Avoid overloading circuits"
            ])
        elif problem_type == ProblemType.MECHANICAL:
            measures.extend([
                "Regular lubrication of moving parts",
                "Check for wear and tear",
                "Keep moving parts clean"
            ])
        elif problem_type == ProblemType.PLUMBING:
            measures.extend([
                "Regular inspection of hoses and connections",
                "Clean filters and drains",
                "Monitor water pressure"
            ])
            
        return measures

    def _get_safety_notes(self, appliance_type: str, problem_type: ProblemType) -> List[str]:
        """Get safety notes based on appliance and problem type."""
        notes = []
        
        # General safety notes
        notes.extend([
            "Always unplug appliance before inspection",
            "Wear appropriate safety gear",
            "Work in a well-ventilated area"
        ])
        
        # Type-specific notes
        if problem_type == ProblemType.ELECTRICAL:
            notes.extend([
                "Use insulated tools",
                "Check for live wires",
                "Avoid water contact"
            ])
        elif problem_type == ProblemType.MECHANICAL:
            notes.extend([
                "Ensure moving parts are stopped",
                "Use proper lifting techniques",
                "Secure loose components"
            ])
        elif problem_type == ProblemType.PLUMBING:
            notes.extend([
                "Turn off water supply",
                "Have towels ready for spills",
                "Check for water damage"
            ])
            
        return notes

    def _generate_chain_of_thought(self, appliance_type: str, problem_description: str, problem_type: ProblemType) -> List[str]:
        """Generate a chain of thought analysis for the problem."""
        chain = []
        
        # Initial observation
        chain.append(f"Observing that the {appliance_type} has the following issue: {problem_description}")
        
        # Problem categorization
        chain.append(f"Based on the description, this appears to be a {problem_type.value} problem")
        
        # Potential causes
        if problem_type == ProblemType.ELECTRICAL:
            chain.append("Common electrical issues include:")
            chain.append("- Power supply problems")
            chain.append("- Circuit board malfunctions")
            chain.append("- Wiring issues")
        elif problem_type == ProblemType.MECHANICAL:
            chain.append("Common mechanical issues include:")
            chain.append("- Worn or damaged components")
            chain.append("- Motor or fan problems")
            chain.append("- Mechanical obstructions")
        elif problem_type == ProblemType.PLUMBING:
            chain.append("Common plumbing issues include:")
            chain.append("- Clogged drains or pipes")
            chain.append("- Leaking connections")
            chain.append("- Water pressure problems")
        elif problem_type == ProblemType.SOFTWARE:
            chain.append("Common software/control issues include:")
            chain.append("- Error codes or display problems")
            chain.append("- Control board malfunctions")
            chain.append("- Sensor calibration issues")
        
        # Diagnostic approach
        chain.append("\nRecommended diagnostic approach:")
        chain.append("1. Start with basic checks (power, connections, visible damage)")
        chain.append("2. Use appropriate tools to verify the issue")
        chain.append("3. Follow systematic troubleshooting steps")
        chain.append("4. Document findings and test results")
        
        # Safety considerations
        chain.append("\nImportant safety considerations:")
        chain.append("- Always disconnect power before inspection")
        chain.append("- Use appropriate personal protective equipment")
        chain.append("- Follow manufacturer's safety guidelines")
        
        return chain 