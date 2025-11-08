"""
AI Sales Agent
Handles conversational sales discovery, personalization, and response generation
"""

import logging
from typing import Dict, Any, Optional
import openai
from anthropic import Anthropic

from config import settings
from models.sales_conversation import SalesConversation

logger = logging.getLogger(__name__)


class AISalesAgent:
    """
    AI-powered sales agent for personalized conversations
    Uses LLM to:
    - Ask qualifying questions
    - Extract user needs and pain points
    - Generate personalized pitches
    - Match features to requirements
    """
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.DEFAULT_LLM_MODEL
    
    async def generate_response(
        self,
        conversation: SalesConversation,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Generate AI response based on conversation history and current stage
        
        Returns:
            {
                "message": str,  # AI response
                "stage": str,  # Updated conversation stage
                "extracted_data": dict  # Extracted insights from user message
            }
        """
        
        # Build conversation context
        context = self._build_context(conversation)
        
        # Build system prompt based on stage
        system_prompt = self._build_system_prompt(conversation.current_stage, context)
        
        # Build message history for LLM
        messages = self._build_message_history(conversation, user_message)
        
        try:
            # Call LLM (OpenAI by default)
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
            )
            
            ai_message = response.choices[0].message.content
            
            # Extract insights from user message
            extracted_data = await self._extract_insights(user_message, conversation.current_stage)
            
            # Determine next stage
            next_stage = self._determine_next_stage(conversation, extracted_data)
            
            return {
                "message": ai_message,
                "stage": next_stage,
                "extracted_data": extracted_data
            }
        
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return {
                "message": "I'm having trouble processing that. Could you rephrase?",
                "stage": conversation.current_stage,
                "extracted_data": {}
            }
    
    def _build_context(self, conversation: SalesConversation) -> Dict[str, Any]:
        """Build context summary for the conversation"""
        return {
            "email": conversation.email,
            "name": conversation.name,
            "company": conversation.company,
            "industry": conversation.industry,
            "pain_points": conversation.pain_points or [],
            "goals": conversation.goals or [],
            "qualification_score": conversation.qualification_score
        }
    
    def _build_system_prompt(self, stage: str, context: Dict[str, Any]) -> str:
        """Build stage-specific system prompt"""
        
        base_prompt = """You are an expert sales consultant having a conversation with a potential customer.
Your goal is to understand their needs, identify pain points, and demonstrate how our AI-powered 
business analysis platform can help them succeed.

Be conversational, empathetic, and genuinely curious about their business.
Ask thoughtful follow-up questions. Don't pitch features yet - focus on discovery.

Platform Overview:
- AI-powered business analysis and strategy
- Market research and competitor analysis  
- Social media insights and content generation
- Real-time streaming AI responses
- Personalized recommendations based on business context
"""
        
        stage_prompts = {
            "greeting": """
You're starting a conversation. Be warm and welcoming.
Ask about their business or what brought them here today.
""",
            "discovery": """
You're in discovery mode. Your goal is to understand:
- What industry/business they're in
- Their biggest challenges or pain points
- What they've tried before
- Their goals and timeline

Ask one thoughtful question at a time. Show genuine interest.
""",
            "qualification": """
You now understand their needs. Subtly assess:
- Budget signals (size of company, urgency)
- Decision authority (their role, who else is involved)
- Timeline and urgency

Continue being helpful, but start connecting their pain points to our capabilities.
""",
            "pitch": """
Now personalize the pitch based on what you've learned:
- Address their specific pain points
- Match features to their needs
- Share relevant success stories
- Create urgency around their timeline

Be enthusiastic but not pushy.
""",
            "handoff": """
They're ready to sign up. Guide them smoothly:
- Summarize the value for their specific situation
- Address any final concerns
- Make the signup process feel easy and low-risk
"""
        }
        
        context_str = f"\n\nCurrent context:\n"
        if context.get("name"):
            context_str += f"- Name: {context['name']}\n"
        if context.get("company"):
            context_str += f"- Company: {context['company']}\n"
        if context.get("industry"):
            context_str += f"- Industry: {context['industry']}\n"
        if context.get("pain_points"):
            context_str += f"- Pain points: {', '.join(context['pain_points'])}\n"
        if context.get("goals"):
            context_str += f"- Goals: {', '.join(context['goals'])}\n"
        
        return base_prompt + stage_prompts.get(stage, stage_prompts["discovery"]) + context_str
    
    def _build_message_history(self, conversation: SalesConversation, user_message: str) -> list:
        """Build message history for LLM context"""
        messages = []
        
        # Add last 5 messages from history for context
        recent_messages = conversation.messages[-5:] if conversation.messages else []
        for msg in recent_messages:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    async def _extract_insights(self, user_message: str, stage: str) -> Dict[str, Any]:
        """
        Extract structured insights from user message
        Uses LLM to identify pain points, goals, budget signals, etc.
        """
        
        extraction_prompt = f"""Analyze this user message and extract any relevant information:

User message: "{user_message}"

Extract and return as JSON:
{{
    "pain_points": ["list of problems or challenges mentioned"],
    "goals": ["list of objectives or desired outcomes"],
    "budget_signals": ["any mentions of company size, urgency, budget, etc"],
    "industry": "industry if mentioned, otherwise null",
    "company_size": "size if mentioned (e.g. 'startup', 'small', 'enterprise'), otherwise null",
    "urgency_level": "low/medium/high based on timeline mentions, otherwise null",
    "decision_authority": "decision_maker/influencer/researcher based on role indicators, otherwise null"
}}

Only include fields with actual information. Return empty lists for missing data.
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a data extraction assistant. Return only valid JSON."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            import json
            extracted = json.loads(response.choices[0].message.content)
            return extracted
        
        except Exception as e:
            logger.error(f"Error extracting insights: {e}")
            return {}
    
    def _determine_next_stage(
        self,
        conversation: SalesConversation,
        extracted_data: Dict[str, Any]
    ) -> str:
        """Determine next conversation stage based on gathered information"""
        
        current = conversation.current_stage
        
        # Stage progression logic
        if current == "greeting":
            return "discovery"
        
        elif current == "discovery":
            # Move to qualification if we have basic info
            has_basics = (
                conversation.industry or extracted_data.get("industry") or
                len(conversation.pain_points) >= 2 or
                len(extracted_data.get("pain_points", [])) >= 2
            )
            return "qualification" if has_basics else "discovery"
        
        elif current == "qualification":
            # Move to pitch if qualification score is decent
            if conversation.qualification_score >= 40:
                return "pitch"
            return "qualification"
        
        elif current == "pitch":
            # Move to handoff if they express interest
            interest_signals = ["interested", "sign up", "try it", "get started", "learn more"]
            user_interested = any(signal in extracted_data.get("pain_points", []) for signal in interest_signals)
            return "handoff" if user_interested else "pitch"
        
        return current
