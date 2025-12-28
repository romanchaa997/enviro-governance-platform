# AI Agent Development Guide

## Overview

Guide for developing biological and computational agents for environmental remediation within the Enviro-Governance Platform.

## Agent Architecture

### Base Agent Class

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any
import asyncio

class AgentType(str, Enum):
    FUNGAL = "fungal"
    BACTERIAL = "bacterial"
    CRISPR = "crispr"
    ANALYTICAL = "analytical"

class BaseAgent(ABC):
    """Abstract base class for all remediation agents"""
    
    def __init__(self, agent_id: str, name: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.effectiveness = 0.0
        self.status = "idle"
        self.execution_history = []
    
    @abstractmethod
    async def analyze(self, contamination_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze contamination and propose remediation strategy"""
        pass
    
    @abstractmethod
    async def execute(self, proposal_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute remediation strategy"""
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "effectiveness": self.effectiveness,
            "executions": len(self.execution_history)
        }
```

## Biological Agents

### Fungal Bioremediation Agent

```python
class FungalBioremediationAgent(BaseAgent):
    """Agent using fungal species for heavy metal and organic pollutant removal"""
    
    EFFECTIVE_SPECIES = {
        "Pestalotipora_microspora": {"effectiveness": 0.85, "timeframe": "6-12 months"},
        "Aspergillus_niger": {"effectiveness": 0.78, "timeframe": "8-14 months"},
        "Phanerochaete_chrysosporium": {"effectiveness": 0.82, "timeframe": "4-10 months"}
    }
    
    def __init__(self):
        super().__init__(
            agent_id="agent_fungal_01",
            name="Fungal Bioremediation Agent",
            agent_type=AgentType.FUNGAL
        )
    
    async def analyze(self, contamination_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze contamination profile and recommend fungal species"""
        contaminants = contamination_data.get("contaminants", [])
        site_ph = contamination_data.get("soil_ph", 7.0)
        temperature = contamination_data.get("temperature", 25)
        
        recommendations = []
        for species, props in self.EFFECTIVE_SPECIES.items():
            score = self._calculate_compatibility_score(
                species, contaminants, site_ph, temperature
            )
            recommendations.append({
                "species": species,
                "effectiveness": score,
                "timeframe": props["timeframe"],
                "cost_estimate": "$500K-$750K"
            })
        
        return {
            "analysis_complete": True,
            "recommendations": sorted(
                recommendations, 
                key=lambda x: x["effectiveness"],
                reverse=True
            ),
            "confidence": 0.87
        }
    
    async def execute(self, proposal_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy fungal consortium for remediation"""
        self.status = "processing"
        species = parameters.get("species", "Pestalotipora_microspora")
        site_area = parameters.get("site_area", 1000)
        
        try:
            # Simulate remediation process
            execution_result = {
                "proposal_id": proposal_id,
                "species_deployed": species,
                "site_area_m2": site_area,
                "deployment_status": "in_progress",
                "expected_completion": "6-12 months",
                "monitoring_points": site_area // 100
            }
            
            self.execution_history.append(execution_result)
            self.effectiveness = self.EFFECTIVE_SPECIES[species]["effectiveness"]
            self.status = "active"
            
            return execution_result
        except Exception as e:
            self.status = "error"
            return {"error": str(e)}
    
    def _calculate_compatibility_score(self, species: str, contaminants: List[str],
                                      ph: float, temp: float) -> float:
        """Calculate how well species matches site conditions"""
        # Simplified scoring logic
        score = 0.8
        
        # Adjust for heavy metals
        if "heavy_metals" in contaminants:
            score += 0.1
        
        # Adjust for pH (optimal 5-7)
        if 5 <= ph <= 7:
            score += 0.05
        
        # Adjust for temperature (optimal 20-30°C)
        if 20 <= temp <= 30:
            score += 0.05
        
        return min(score, 1.0)
```

### Bacterial Consortium Agent

```python
class BacterialConsortiumAgent(BaseAgent):
    """Agent using engineered bacterial strains for organic pollutant degradation"""
    
    def __init__(self):
        super().__init__(
            agent_id="agent_bacterial_01",
            name="Bacterial Consortium Agent",
            agent_type=AgentType.BACTERIAL
        )
    
    async def analyze(self, contamination_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze organic contaminants and design consortium"""
        contaminants = contamination_data.get("contaminants", [])
        
        consortium_design = {
            "primary_degraders": ["Pseudomonas_aeruginosa", "Bacillus_subtilis"],
            "secondary_degraders": ["Arthrobacter_globiformis"],
            "effectiveness": 0.75,
            "timeframe": "12-18 months",
            "cost_estimate": "$300K-$450K"
        }
        
        return {
            "analysis_complete": True,
            "consortium_design": consortium_design,
            "confidence": 0.82
        }
    
    async def execute(self, proposal_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy bacterial consortium"""
        self.status = "processing"
        
        execution_result = {
            "proposal_id": proposal_id,
            "consortium_deployed": True,
            "strains_count": 3,
            "deployment_status": "in_progress",
            "monitoring_interval": "monthly"
        }
        
        self.execution_history.append(execution_result)
        self.effectiveness = 0.75
        self.status = "active"
        
        return execution_result
```

## Agent Development Workflow

### Step 1: Define Agent Specifications

```python
# Define what your agent will do
agent_spec = {
    "name": "Novel Bioremediation Agent",
    "type": "fungal",
    "capabilities": ["heavy_metal_removal", "organic_degradation"],
    "effectiveness_range": [0.70, 0.90],
    "timeframe": "6-12 months",
    "cost_range": "$500K-$750K"
}
```

### Step 2: Implement Agent Class

```python
from app.agents.base import BaseAgent, AgentType

class NovelBioremediationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="agent_novel_01",
            name="Novel Bioremediation Agent",
            agent_type=AgentType.FUNGAL
        )
    
    async def analyze(self, contamination_data):
        # Implement analysis logic
        pass
    
    async def execute(self, proposal_id, parameters):
        # Implement execution logic
        pass
```

### Step 3: Register Agent

```python
# In app/agents/__init__.py
from .novel_agent import NovelBioremediationAgent

AVAILABLE_AGENTS = {
    "agent_novel_01": NovelBioremediationAgent()
}
```

### Step 4: Test Agent

```python
import pytest
from app.agents import NovelBioremediationAgent

@pytest.mark.asyncio
async def test_agent_analysis():
    agent = NovelBioremediationAgent()
    
    contamination_data = {
        "contaminants": ["heavy_metals", "organic"],
        "soil_ph": 6.5,
        "temperature": 25
    }
    
    result = await agent.analyze(contamination_data)
    
    assert result["analysis_complete"] is True
    assert "recommendations" in result
    assert result["confidence"] > 0.7

@pytest.mark.asyncio
async def test_agent_execution():
    agent = NovelBioremediationAgent()
    
    result = await agent.execute(
        proposal_id="prop_123",
        parameters={"site_area": 5000}
    )
    
    assert result["deployment_status"] == "in_progress"
```

## Agent Configuration

### Configuration File Format

```yaml
# backend/config/agents.yml
agents:
  - id: agent_fungal_01
    name: Fungal Bioremediation Agent
    type: fungal
    enabled: true
    parameters:
      effectiveness_min: 0.70
      effectiveness_max: 0.90
      timeframe_min_months: 6
      timeframe_max_months: 12
      cost_min: 500000
      cost_max: 750000
  
  - id: agent_bacterial_01
    name: Bacterial Consortium Agent
    type: bacterial
    enabled: true
    parameters:
      effectiveness_min: 0.65
      effectiveness_max: 0.85
      timeframe_min_months: 12
      timeframe_max_months: 18
      cost_min: 300000
      cost_max: 450000
```

## Agent Integration with Governance Engine

```python
from app.agents import AVAILABLE_AGENTS
from app.services.governance import GovernanceService

class AgentIntegration:
    @staticmethod
    async def get_remediation_suggestions(proposal_id: str):
        """Get all agent recommendations for a proposal"""
        suggestions = []
        
        for agent_id, agent in AVAILABLE_AGENTS.items():
            if agent.status != "active":
                suggestion = await agent.analyze(proposal_data)
                suggestions.append({
                    "agent_id": agent_id,
                    "recommendation": suggestion
                })
        
        return suggestions
    
    @staticmethod
    async def execute_agent_task(agent_id: str, proposal_id: str,
                                parameters: Dict[str, Any]):
        """Execute specific agent task"""
        agent = AVAILABLE_AGENTS.get(agent_id)
        
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        result = await agent.execute(proposal_id, parameters)
        
        # Log execution
        await GovernanceService.log_agent_execution(
            agent_id=agent_id,
            proposal_id=proposal_id,
            result=result
        )
        
        return result
```

## Best Practices

1. **Asynchronous Operations**: Always use `async/await` for long-running tasks
2. **Error Handling**: Implement comprehensive error handling and logging
3. **State Management**: Track agent status and execution history
4. **Validation**: Validate input parameters before execution
5. **Testing**: Write unit tests for all agent methods
6. **Documentation**: Document agent capabilities and limitations
7. **Monitoring**: Implement monitoring and alerting for agent health

## Future Agent Types

- CRISPR-based genetic engineering agents
- Chemical remediation agents
- Phytoremediation agents
- Hybrid multi-strategy agents
- Machine learning-based optimization agents

## Support

For agent development support:
- **Repository**: https://github.com/romanchaa997/enviro-governance-platform
- **Issues**: File issues with agent development questions
- **Documentation**: See API_REFERENCE.md for agent endpoints
