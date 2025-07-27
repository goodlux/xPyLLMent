"""
AI Agent Framework for xPyLLMent

Base classes and interfaces for AI agents that operate as Pixeltable computed columns.
Each agent specializes in a specific aspect of the research process.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
import json
from datetime import datetime

import pixeltable as pxt
from loguru import logger
from anthropic import Anthropic
import openai

from ..config import Config, LLMConfig


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = Anthropic(api_key=config.api_key)
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Claude"""
        
        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                temperature=kwargs.get('temperature', self.config.temperature),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


class OpenAIProvider(LLMProvider):
    """OpenAI GPT API provider"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = openai.OpenAI(api_key=config.api_key)
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using GPT"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                temperature=kwargs.get('temperature', self.config.temperature),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


def create_llm_provider(config: LLMConfig) -> LLMProvider:
    """Factory function to create LLM provider"""
    
    if config.provider.lower() == "anthropic":
        return AnthropicProvider(config)
    elif config.provider.lower() == "openai":
        return OpenAIProvider(config)
    else:
        raise ValueError(f"Unsupported LLM provider: {config.provider}")


class BaseAgent(ABC):
    """
    Base class for all AI agents in the research system
    
    Agents are designed to work as Pixeltable computed columns,
    processing data and generating insights automatically.
    """
    
    def __init__(self, config: Config, name: str):
        self.config = config
        self.name = name
        self.llm = create_llm_provider(config.llm)
        
        logger.info(f"Initialized {self.__class__.__name__}: {name}")
    
    @abstractmethod
    def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process inputs and return outputs
        
        Args:
            inputs: Input data for processing
            
        Returns:
            Processed outputs
        """
        pass
    
    def _create_prompt(self, template: str, **kwargs) -> str:
        """Create prompt from template with variable substitution"""
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            raise
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        
        try:
            # Clean up response (remove markdown, etc.)
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            return json.loads(cleaned.strip())
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response was: {response}")
            raise
    
    def _safe_llm_call(self, prompt: str, **kwargs) -> Optional[str]:
        """Make LLM call with error handling"""
        
        try:
            return self.llm.generate(prompt, **kwargs)
        except Exception as e:
            logger.error(f"LLM call failed for {self.name}: {e}")
            return None


class ResearcherAgent(BaseAgent):
    """
    Researcher Agent: Proposes novel architectures
    
    Takes historical experiment data and cognition insights,
    generates new architecture proposals with motivation.
    """
    
    def __init__(self, config: Config):
        super().__init__(config, "researcher")
    
    def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate new architecture proposal"""
        
        historical_experiments = inputs.get('historical_experiments', [])
        cognition_insights = inputs.get('cognition_insights', {})
        parent_config = inputs.get('parent_config', {})
        
        # Create proposal prompt
        prompt = self._create_proposal_prompt(
            historical_experiments, cognition_insights, parent_config
        )
        
        # Generate proposal
        response = self._safe_llm_call(prompt)
        
        if not response:
            return {'error': 'Failed to generate proposal'}
        
        try:
            proposal = self._parse_json_response(response)
            
            # Validate proposal structure
            required_fields = ['name', 'motivation', 'proposed_changes', 'expected_improvements']
            if not all(field in proposal for field in required_fields):
                return {'error': 'Invalid proposal structure'}
            
            # Add metadata
            proposal['generated_at'] = datetime.now().isoformat()
            proposal['agent'] = self.name
            
            return proposal
            
        except Exception as e:
            logger.error(f"Failed to process proposal: {e}")
            return {'error': str(e)}
    
    def _create_proposal_prompt(
        self, 
        historical_experiments: List[Dict],
        cognition_insights: Dict,
        parent_config: Dict
    ) -> str:
        """Create architecture proposal prompt"""
        
        # Analyze successful patterns
        successful_patterns = []
        for exp in historical_experiments[-10:]:  # Last 10 experiments
            if exp.get('fitness_score', 0) > 0.6:
                successful_patterns.append({
                    'name': exp.get('name', 'Unknown'),
                    'fitness': exp.get('fitness_score', 0),
                    'key_features': exp.get('architecture_spec', {}).get('proposed_changes', [])
                })
        
        # Extract key insights
        key_insights = cognition_insights.get('design_insights', [])[:5]
        algorithmic_patterns = cognition_insights.get('algorithmic_patterns', [])[:5]
        
        prompt = f"""
You are an expert AI researcher specializing in neural architecture discovery. 
Your task is to propose a novel neural architecture based on historical experiments and research insights.

SUCCESSFUL PATTERNS FROM RECENT EXPERIMENTS:
{json.dumps(successful_patterns, indent=2)}

RESEARCH INSIGHTS FROM PAPERS:
Design Insights: {key_insights}
Algorithmic Patterns: {algorithmic_patterns}

PARENT ARCHITECTURE CONFIG:
{json.dumps(parent_config, indent=2)}

REQUIREMENTS:
1. Propose a novel architecture that builds on successful patterns
2. Ensure the architecture maintains sub-quadratic complexity O(n log n)
3. Focus on linear attention mechanisms and efficient transformers
4. Consider improvements for reasoning, language understanding, and efficiency

OUTPUT FORMAT (valid JSON):
{{
    "name": "descriptive_architecture_name",
    "motivation": "clear explanation of why this architecture should work",
    "base_architecture": "starting point (e.g., DeltaNet, LinearAttention)",
    "proposed_changes": [
        "specific architectural modification 1",
        "specific architectural modification 2",
        "specific architectural modification 3"
    ],
    "expected_improvements": [
        "expected capability improvement 1", 
        "expected capability improvement 2",
        "expected capability improvement 3"
    ],
    "theoretical_justification": "mathematical or computational reasoning for the approach",
    "implementation_notes": "key considerations for implementation"
}}

Generate a novel, theoretically sound architecture proposal:
"""
        
        return prompt


class EngineerAgent(BaseAgent):
    """
    Engineer Agent: Converts proposals to executable code
    
    Takes architecture specifications and generates clean,
    working PyTorch implementations.
    """
    
    def __init__(self, config: Config):
        super().__init__(config, "engineer")
    
    def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executable code from architecture specification"""
        
        architecture_spec = inputs.get('architecture_spec', {})
        base_code = inputs.get('base_code', '')
        
        if not architecture_spec:
            return {'error': 'No architecture specification provided'}
        
        # Create code generation prompt
        prompt = self._create_code_prompt(architecture_spec, base_code)
        
        # Generate code
        response = self._safe_llm_call(prompt, max_tokens=6000)
        
        if not response:
            return {'error': 'Failed to generate code'}
        
        try:
            # Extract code from response
            code = self._extract_code(response)
            
            # Basic validation
            if not self._validate_code(code):
                return {'error': 'Generated code failed validation'}
            
            return {
                'code': code,
                'generated_at': datetime.now().isoformat(),
                'agent': self.name,
                'architecture_name': architecture_spec.get('name', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"Failed to process code generation: {e}")
            return {'error': str(e)}
    
    def _create_code_prompt(self, architecture_spec: Dict, base_code: str) -> str:
        """Create code generation prompt"""
        
        prompt = f"""
You are an expert PyTorch developer implementing neural architectures.
Generate clean, working PyTorch code for the following architecture specification.

ARCHITECTURE SPECIFICATION:
{json.dumps(architecture_spec, indent=2)}

BASE CODE REFERENCE:
{base_code[:2000] if base_code else "No base code provided"}

REQUIREMENTS:
1. Generate complete, working PyTorch code
2. Use modern PyTorch patterns and best practices
3. Ensure sub-quadratic complexity O(n log n) or better
4. Include proper error handling and input validation
5. Use clear variable names and add comments
6. Maintain compatibility with the DeltaNet interface

CODE STRUCTURE:
- Main class should be named 'DeltaNet' for compatibility
- Include proper __init__ and forward methods
- Use chunked processing for efficiency
- Implement causal masking correctly
- Add @torch.compile decorators for performance

Generate the complete implementation:
"""
        
        return prompt
    
    def _extract_code(self, response: str) -> str:
        """Extract Python code from LLM response"""
        
        # Look for code blocks
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            if end != -1:
                return response[start:end].strip()
        
        # If no code blocks, return the whole response
        return response.strip()
    
    def _validate_code(self, code: str) -> bool:
        """Basic code validation"""
        
        try:
            # Check for required elements
            required_elements = [
                "class DeltaNet",
                "def __init__",
                "def forward",
                "import torch"
            ]
            
            for element in required_elements:
                if element not in code:
                    logger.warning(f"Missing required element: {element}")
                    return False
            
            # Basic syntax check
            compile(code, '<string>', 'exec')
            
            return True
            
        except SyntaxError as e:
            logger.error(f"Code syntax error: {e}")
            return False
        except Exception as e:
            logger.error(f"Code validation error: {e}")
            return False


# TODO: Implement remaining agents
class TrainingAgent(BaseAgent):
    """Training Agent: Orchestrates model training and evaluation"""
    
    def __init__(self, config: Config):
        super().__init__(config, "training")
    
    def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute training pipeline"""
        
        # TODO: Implement training orchestration
        # This will be a major component that handles:
        # - Model instantiation from generated code
        # - Training loop execution
        # - Evaluation on benchmarks
        # - Resource monitoring
        # - Error handling and recovery
        
        return {
            'status': 'not_implemented',
            'message': 'Training agent implementation pending'
        }


class AnalystAgent(BaseAgent):
    """Analyst Agent: Analyzes results and generates insights"""
    
    def __init__(self, config: Config):
        super().__init__(config, "analyst")
    
    def process(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis and insights from experimental results"""
        
        # TODO: Implement result analysis
        # This will analyze:
        # - Performance patterns across benchmarks
        # - Comparison with parent/sibling architectures
        # - Failure mode analysis
        # - Recommendations for future directions
        
        return {
            'status': 'not_implemented',
            'message': 'Analyst agent implementation pending'
        }


# Pixeltable UDF decorators for computed columns
def create_researcher_udf(config: Config):
    """Create Pixeltable UDF for researcher agent"""
    
    agent = ResearcherAgent(config)
    
    @pxt.udf
    def researcher_agent_udf(
        historical_experiments: pxt.Json,
        cognition_insights: pxt.Json,
        parent_config: pxt.Json
    ) -> pxt.Json:
        """Pixeltable UDF for architecture proposal generation"""
        
        inputs = {
            'historical_experiments': historical_experiments or [],
            'cognition_insights': cognition_insights or {},
            'parent_config': parent_config or {}
        }
        
        return agent.process(inputs)
    
    return researcher_agent_udf


def create_engineer_udf(config: Config):
    """Create Pixeltable UDF for engineer agent"""
    
    agent = EngineerAgent(config)
    
    @pxt.udf
    def engineer_agent_udf(
        architecture_spec: pxt.Json,
        base_code: pxt.String
    ) -> pxt.Json:
        """Pixeltable UDF for code generation"""
        
        inputs = {
            'architecture_spec': architecture_spec or {},
            'base_code': base_code or ''
        }
        
        return agent.process(inputs)
    
    return engineer_agent_udf


# Export for easy imports
__all__ = [
    "BaseAgent",
    "ResearcherAgent", 
    "EngineerAgent",
    "TrainingAgent",
    "AnalystAgent",
    "create_researcher_udf",
    "create_engineer_udf",
    "LLMProvider",
    "create_llm_provider",
]
