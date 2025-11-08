"""
MCP Client for Sales API
Connects to MCP server to retrieve pre-built pitch templates, success stories, and sales tools
"""

import logging
from typing import Dict, Any, List, Optional
import httpx

from config import settings

logger = logging.getLogger(__name__)


class MCPClient:
    """
    Client for Model Context Protocol server
    Provides access to:
    - Pitch templates
    - Success stories
    - Feature descriptions
    - Objection handlers
    - Value calculators
    """
    
    def __init__(self):
        self.base_url = settings.MCP_SERVER_URL
        self.timeout = settings.MCP_SERVER_TIMEOUT
        self.client = httpx.AsyncClient(timeout=self.timeout)
    
    async def get_pitch_template(
        self,
        industry: Optional[str] = None,
        company_size: Optional[str] = None,
        pain_points: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve personalized pitch template based on prospect profile
        
        Args:
            industry: Industry/sector
            company_size: Size of company
            pain_points: List of identified pain points
        
        Returns:
            {
                "template": str,
                "key_points": List[str],
                "call_to_action": str
            }
        """
        
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/pitch_template_retriever",
                json={
                    "industry": industry,
                    "company_size": company_size,
                    "pain_points": pain_points or []
                }
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error fetching pitch template: {e}")
            return {
                "template": "Generic pitch template",
                "key_points": [],
                "call_to_action": "Ready to learn more?"
            }
    
    async def find_success_stories(
        self,
        industry: Optional[str] = None,
        pain_points: Optional[List[str]] = None,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find relevant success stories/case studies
        
        Returns:
            List of success stories with:
            {
                "company": str,
                "industry": str,
                "challenge": str,
                "solution": str,
                "results": str
            }
        """
        
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/success_story_finder",
                json={
                    "industry": industry,
                    "pain_points": pain_points or [],
                    "limit": limit
                }
            )
            response.raise_for_status()
            return response.json().get("stories", [])
        
        except Exception as e:
            logger.error(f"Error fetching success stories: {e}")
            return []
    
    async def match_features(
        self,
        pain_points: List[str],
        goals: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Match platform features to user needs
        
        Returns:
            List of matched features:
            {
                "feature": str,
                "description": str,
                "benefit": str,
                "relevance_score": float
            }
        """
        
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/feature_matcher",
                json={
                    "pain_points": pain_points,
                    "goals": goals
                }
            )
            response.raise_for_status()
            return response.json().get("features", [])
        
        except Exception as e:
            logger.error(f"Error matching features: {e}")
            return []
    
    async def handle_objection(self, objection: str) -> Dict[str, str]:
        """
        Get response to common objections
        
        Returns:
            {
                "response": str,
                "follow_up": str
            }
        """
        
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/objection_handler",
                json={"objection": objection}
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error handling objection: {e}")
            return {
                "response": "That's a great question. Let me address that...",
                "follow_up": "Does that help clarify things?"
            }
    
    async def calculate_value(
        self,
        company_size: Optional[str] = None,
        pain_points: Optional[List[str]] = None,
        current_solution: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate estimated value/ROI for prospect
        
        Returns:
            {
                "time_saved": str,
                "cost_savings": str,
                "efficiency_gain": str,
                "roi_estimate": str
            }
        """
        
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/value_calculator",
                json={
                    "company_size": company_size,
                    "pain_points": pain_points or [],
                    "current_solution": current_solution
                }
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error calculating value: {e}")
            return {
                "time_saved": "10+ hours per week",
                "cost_savings": "Significant",
                "efficiency_gain": "40%+",
                "roi_estimate": "Positive within 3 months"
            }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
