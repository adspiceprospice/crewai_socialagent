from typing import List
from crewai import Agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
import logging
import os
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("content_strategy_agent")

class ContentStrategyAgent(Agent):
    def __init__(self, llm: ChatOpenAI = None, tools: List[Tool] = None):
        logger.info("Initializing ContentStrategyAgent")
        try:
            super().__init__(
                name="Content Strategy Agent",
                role="Content Strategist",
                goal="Create effective content strategies for social media platforms",
                backstory="""You are an expert content strategist with years of experience in 
                social media marketing. You understand different industries, target audiences, 
                and how to achieve various business goals through content.""",
                tools=tools or [],
                llm=llm,
                verbose=True
            )
            # Initialize direct OpenAI client
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            logger.info("ContentStrategyAgent initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ContentStrategyAgent: {str(e)}")
            raise

    def create_content_strategy(self, industry: str, target_audience: str, goals: List[str]) -> str:
        """
        Create a content strategy based on the industry, target audience, and goals.
        
        Args:
            industry (str): The industry or business domain
            target_audience (str): Description of the target audience
            goals (List[str]): List of goals to achieve with the content strategy
            
        Returns:
            str: A detailed content strategy
        """
        logger.info(f"Creating content strategy for industry: {industry}, target_audience: {target_audience}")
        try:
            # Format the goals into a readable string
            if isinstance(goals, list):
                goals_str = "\n- ".join(goals)
            else:
                goals_str = goals  # In case goals is already a string
            
            # Create a direct prompt for the LLM
            prompt = f"""
            Create a comprehensive content strategy for:
            Industry: {industry}
            Target Audience: {target_audience}
            Goals:
            - {goals_str}
            
            The strategy should include:
            1. Content themes and topics
            2. Content types and formats
            3. Posting frequency and timing
            4. Platform-specific recommendations
            5. Engagement strategies
            6. Success metrics and KPIs
            
            Please provide a detailed, actionable strategy that aligns with the industry, 
            resonates with the target audience, and helps achieve the specified goals.
            """
            
            # Use OpenAI client directly
            logger.info("Creating content strategy using OpenAI directly")
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert content strategist specializing in social media marketing."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract the content from response
            result = response.choices[0].message.content
            
            logger.info("Content strategy created successfully")
            return result
        except Exception as e:
            logger.error(f"Error creating content strategy: {str(e)}")
            return f"Error creating content strategy: {str(e)}" 