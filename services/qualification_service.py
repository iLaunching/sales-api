"""
Lead Qualification Service
Calculates qualification scores and engagement metrics
"""

from typing import Dict, Any
import logging

from models.sales_conversation import SalesConversation
from config import settings

logger = logging.getLogger(__name__)


class QualificationService:
    """
    Calculates lead quality scores based on:
    - Pain points discovered
    - Budget signals
    - Urgency level
    - Decision authority
    - Engagement metrics
    """
    
    def calculate_score(self, conversation: SalesConversation) -> Dict[str, Any]:
        """
        Calculate qualification score (0-100)
        
        Returns:
            {
                "score": float,
                "tier": str,  # "high", "medium", "low"
                "breakdown": dict  # Score components
            }
        """
        
        score = 0.0
        breakdown = {}
        
        # Pain points (max 25 points)
        pain_count = len(conversation.pain_points or [])
        pain_score = min(pain_count * 8, 25)
        score += pain_score
        breakdown["pain_points"] = pain_score
        
        # Goals identified (max 20 points)
        goal_count = len(conversation.goals or [])
        goal_score = min(goal_count * 7, 20)
        score += goal_score
        breakdown["goals"] = goal_score
        
        # Budget signals (max 20 points)
        budget_count = len(conversation.budget_signals or [])
        budget_score = min(budget_count * 10, 20)
        score += budget_score
        breakdown["budget_signals"] = budget_score
        
        # Urgency level (max 15 points)
        urgency_scores = {
            "high": 15,
            "medium": 10,
            "low": 5
        }
        urgency_score = urgency_scores.get(conversation.urgency_level, 0)
        score += urgency_score
        breakdown["urgency"] = urgency_score
        
        # Decision authority (max 15 points)
        authority_scores = {
            "decision_maker": 15,
            "influencer": 10,
            "researcher": 5
        }
        authority_score = authority_scores.get(conversation.decision_authority, 0)
        score += authority_score
        breakdown["authority"] = authority_score
        
        # Company info completeness (max 5 points)
        info_score = 0
        if conversation.company:
            info_score += 1
        if conversation.industry:
            info_score += 2
        if conversation.company_size:
            info_score += 2
        score += info_score
        breakdown["company_info"] = info_score
        
        # Determine tier
        if score >= settings.HIGH_QUALITY_SCORE_THRESHOLD:
            tier = "high"
        elif score >= settings.MEDIUM_QUALITY_SCORE_THRESHOLD:
            tier = "medium"
        else:
            tier = "low"
        
        return {
            "score": round(score, 2),
            "tier": tier,
            "breakdown": breakdown
        }
    
    def calculate_engagement(self, conversation: SalesConversation) -> float:
        """
        Calculate engagement score based on conversation metrics
        Higher score = more engaged prospect
        
        Returns:
            float: Engagement score (0-100)
        """
        
        score = 0.0
        
        # Message count (max 30 points)
        message_score = min(conversation.total_messages * 3, 30)
        score += message_score
        
        # Conversation duration (max 25 points)
        if conversation.conversation_duration:
            # 1 point per minute, max 25
            duration_minutes = conversation.conversation_duration / 60
            duration_score = min(duration_minutes, 25)
            score += duration_score
        
        # Stage progression (max 25 points)
        stage_scores = {
            "greeting": 5,
            "discovery": 10,
            "qualification": 15,
            "pitch": 20,
            "handoff": 25
        }
        stage_score = stage_scores.get(conversation.current_stage, 0)
        score += stage_score
        
        # Response quality indicators (max 20 points)
        # Longer messages = more engaged
        avg_message_length = 0
        user_messages = [m for m in (conversation.messages or []) if m.get("role") == "user"]
        if user_messages:
            total_length = sum(len(m.get("content", "")) for m in user_messages)
            avg_message_length = total_length / len(user_messages)
        
        if avg_message_length > 100:
            score += 20
        elif avg_message_length > 50:
            score += 15
        elif avg_message_length > 20:
            score += 10
        else:
            score += 5
        
        return round(min(score, 100), 2)
    
    def should_handoff_to_auth(self, conversation: SalesConversation) -> bool:
        """
        Determine if conversation is ready to handoff to auth signup
        
        Criteria:
        - Qualification score above threshold
        - Has email
        - In pitch or handoff stage
        - Not already converted
        """
        
        return (
            conversation.qualification_score >= settings.HIGH_QUALITY_SCORE_THRESHOLD and
            conversation.email is not None and
            conversation.current_stage in ["pitch", "handoff"] and
            not conversation.converted
        )
    
    def get_next_questions(self, conversation: SalesConversation) -> list:
        """
        Suggest next questions based on missing qualification data
        
        Returns:
            list: Suggested questions to ask
        """
        
        questions = []
        
        # Check what's missing
        if not conversation.industry:
            questions.append("What industry or sector is your business in?")
        
        if not conversation.pain_points or len(conversation.pain_points) < 2:
            questions.append("What are your biggest challenges right now?")
        
        if not conversation.goals or len(conversation.goals) < 2:
            questions.append("What are you hoping to achieve in the next 3-6 months?")
        
        if not conversation.company_size:
            questions.append("How large is your team or company?")
        
        if not conversation.urgency_level:
            questions.append("What's your timeline for addressing these challenges?")
        
        if not conversation.decision_authority:
            questions.append("Are you the primary decision-maker for this type of solution?")
        
        return questions[:2]  # Return max 2 questions to avoid overwhelming
