"""
MCP Sales Server Client - Calls MCP tools for sales actions
"""

import httpx
import os
import logging
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

# MCP Server URL from environment
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")

if not MCP_SERVER_URL:
    logger.warning("MCP_SERVER_URL not set - MCP tools will not be available")


async def call_mcp_tool(tool_name: str, params: Dict[str, Any]) -> Optional[Dict]:
    """
    Call MCP tool
    
    Args:
        tool_name: Tool name (pitch_template_retriever, objection_handler, etc)
        params: Tool parameters
    
    Returns:
        Tool response or None if failed
    """
    if not MCP_SERVER_URL:
        logger.warning(f"MCP tool {tool_name} called but MCP_SERVER_URL not configured")
        return None
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{MCP_SERVER_URL}/tools/{tool_name}",
                json=params
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"MCP tool {tool_name} succeeded")
                return data
            else:
                logger.error(f"MCP tool {tool_name} error: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"MCP tool {tool_name} failed: {type(e).__name__}: {e}")
        return None


async def get_pitch_template(industry: str, pain_points: List[str], company_size: str = None) -> Optional[Dict]:
    """Get industry-specific pitch template"""
    return await call_mcp_tool("pitch_template_retriever", {
        "industry": industry,
        "pain_points": pain_points,
        "company_size": company_size
    })


async def find_success_story(industry: str, company_size: str = None, pain_points: List[str] = None) -> Optional[Dict]:
    """Find relevant success story"""
    return await call_mcp_tool("success_story_finder", {
        "industry": industry,
        "company_size": company_size,
        "pain_points": pain_points
    })


async def match_features(pain_points: List[str], goals: List[str]) -> Optional[Dict]:
    """Match platform features to pain points"""
    return await call_mcp_tool("feature_matcher", {
        "pain_points": pain_points,
        "goals": goals
    })


async def handle_objection(objection_type: str, context: Dict[str, Any]) -> Optional[Dict]:
    """Handle sales objection"""
    return await call_mcp_tool("objection_handler", {
        "objection_type": objection_type,
        "context": context
    })


async def calculate_value(company_size: str, industry: str, current_process: str = None) -> Optional[Dict]:
    """Calculate ROI and value proposition"""
    return await call_mcp_tool("value_calculator", {
        "company_size": company_size,
        "industry": industry,
        "current_process": current_process
    })


async def draft_email(prospect_name: str, company: str, pain_points: List[str], template_type: str) -> Optional[Dict]:
    """Draft sales email"""
    return await call_mcp_tool("draft_email", {
        "prospect_name": prospect_name,
        "company": company,
        "pain_points": pain_points,
        "template_type": template_type
    })


async def schedule_meeting(prospect_email: str, meeting_type: str, timezone: str, preferred_times: List[str]) -> Optional[Dict]:
    """Schedule meeting"""
    return await call_mcp_tool("schedule_meeting", {
        "prospect_email": prospect_email,
        "meeting_type": meeting_type,
        "timezone": timezone,
        "preferred_times": preferred_times
    })
