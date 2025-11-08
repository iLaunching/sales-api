"""
MCP (Model Context Protocol) Client for Sales API
Provides access to sales tools and actions via MCP server
"""

import logging
from typing import Dict, Any, List, Optional
import httpx

from config import settings

logger = logging.getLogger(__name__)


class MCPClient:
    """
    Client for Model Context Protocol server
    
    Retrieval Tools:
    - Pitch templates
    - Success stories
    - Feature matching
    - Objection handling
    - Value calculation
    
    Action Tools:
    - Email drafting
    - Meeting scheduling
    """
    
    def __init__(self):
        self.enabled = settings.MCP_ENABLED
        self.base_url = settings.MCP_SERVER_URL if settings.MCP_SERVER_URL else None
        self.timeout = settings.MCP_SERVER_TIMEOUT
        self.client = httpx.AsyncClient(timeout=self.timeout) if self.enabled else None
        
        if not self.enabled:
            logger.info("MCP client running in placeholder mode (MCP_ENABLED=False)")
        else:
            logger.info(f"MCP client connecting to {self.base_url}")
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()
    
    # ============= RETRIEVAL TOOLS =============
    
    async def get_pitch_template(
        self,
        industry: str,
        pain_points: List[str],
        company_size: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve personalized pitch template
        
        Returns:
            {
                "template": {...},  # opener, pain_point_response, value_prop, cta
                "industry": str,
                "confidence": float,
                "suggestions": List[str]
            }
        """
        if not self.enabled or not self.client:
            logger.warning("MCP disabled - returning placeholder pitch")
            return {
                "template": {
                    "opener": f"Based on your work in {industry}, I can see how our platform addresses your challenges.",
                    "value_prop": "We help teams like yours make faster, data-driven decisions.",
                    "cta": "Want to see how this works for your situation?"
                },
                "confidence": 0.5
            }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/pitch_template_retriever",
                json={
                    "industry": industry,
                    "pain_points": pain_points,
                    "company_size": company_size
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching pitch template: {e}")
            return None
    
    async def get_success_story(
        self,
        industry: str,
        company_size: Optional[str] = None,
        pain_points: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find relevant success story
        
        Returns:
            {
                "success_story": {
                    "company": str,
                    "challenge": str,
                    "solution": str,
                    "results": {...}
                },
                "relevance_score": float
            }
        """
        if not self.enabled or not self.client:
            logger.warning("MCP disabled - returning placeholder story")
            return {
                "success_story": {
                    "company": f"Similar {industry} company",
                    "challenge": "Manual analysis taking too long",
                    "results": {"time_saved": "20 hours/week"}
                }
            }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/success_story_finder",
                json={
                    "industry": industry,
                    "company_size": company_size,
                    "pain_points": pain_points or []
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching success story: {e}")
            return None
    
    async def match_features(
        self,
        pain_points: List[str],
        goals: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Match platform features to user needs
        
        Returns:
            List of {
                "name": str,
                "description": str,
                "benefits": List[str],
                "relevance_score": float
            }
        """
        if not self.enabled or not self.client:
            logger.warning("MCP disabled - returning placeholder features")
            return [
                {
                    "name": "AI Market Analysis",
                    "description": "Automated insights",
                    "relevance_score": 0.8
                }
            ]
        
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/feature_matcher",
                json={
                    "pain_points": pain_points,
                    "goals": goals
                }
            )
            response.raise_for_status()
            return response.json().get("matched_features", [])
        except Exception as e:
            logger.error(f"Error matching features: {e}")
            return []
    
    async def handle_objection(
        self,
        objection_type: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get objection handling response
        
        Args:
            objection_type: "price", "timing", "features", "competitors", "trust"
            context: Additional context
        
        Returns:
            {
                "response": str,
                "follow_up_question": str,
                "proof_points": List[str]
            }
        """
        if not self.enabled or not self.client:
            logger.warning("MCP disabled - returning placeholder objection response")
            return {
                "response": "I understand your concern. Let me address that...",
                "follow_up_question": "What would help clarify this for you?"
            }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/objection_handler",
                json={
                    "objection_type": objection_type,
                    "context": context
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error handling objection: {e}")
            return None
    
    async def calculate_value(
        self,
        company_size: str,
        industry: str,
        current_process: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate ROI and value proposition
        
        Returns:
            {
                "time_savings": {...},
                "financial_impact": {...},
                "roi": {...}
            }
        """
        if not self.enabled or not self.client:
            logger.warning("MCP disabled - returning placeholder value calc")
            return {
                "time_savings": {"weekly_hours": 15},
                "financial_impact": {"annual": "$50,000"},
                "roi": {"payback_period": "3 months"}
            }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/value_calculator",
                json={
                    "company_size": company_size,
                    "industry": industry,
                    "current_process": current_process
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error calculating value: {e}")
            return None
    
    # ============= ACTION TOOLS =============
    
    async def draft_email(
        self,
        prospect_name: str,
        company: str,
        pain_points: List[str],
        template_type: str = "follow_up"
    ) -> Optional[Dict[str, Any]]:
        """
        Generate personalized email draft
        
        Args:
            prospect_name: Name of prospect
            company: Company name
            pain_points: Identified pain points
            template_type: "follow_up", "introduction", "demo_invite"
        
        Returns:
            {
                "subject": str,
                "body": str,
                "tone": str,
                "best_send_time": str
            }
        """
        if not self.enabled or not self.client:
            logger.warning("MCP disabled - cannot draft email")
            return None
        
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/draft_email",
                json={
                    "prospect_name": prospect_name,
                    "company": company,
                    "pain_points": pain_points,
                    "template_type": template_type
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error drafting email: {e}")
            return None
    
    async def schedule_meeting(
        self,
        prospect_email: str,
        meeting_type: str,
        timezone: str,
        preferred_times: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate meeting scheduling message
        
        Args:
            prospect_email: Email address
            meeting_type: "discovery", "demo", "closing"
            timezone: Timezone
            preferred_times: List of time options
        
        Returns:
            {
                "meeting_type": str,
                "duration": str,
                "agenda": List[str],
                "scheduling_message": str
            }
        """
        if not self.enabled or not self.client:
            logger.warning("MCP disabled - cannot schedule meeting")
            return None
        
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/schedule_meeting",
                json={
                    "prospect_email": prospect_email,
                    "meeting_type": meeting_type,
                    "timezone": timezone,
                    "preferred_times": preferred_times
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error scheduling meeting: {e}")
            return None

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
