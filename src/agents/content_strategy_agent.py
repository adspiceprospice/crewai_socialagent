from typing import List
from crewai import Agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("content_strategy_agent")

class ContentStrategyAgent(Agent):
    def __init__(self, llm: ChatOpenAI, tools: List[Tool] = None):
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
            goals_str = "\n- ".join(goals)
            
            # Create the task prompt
            task = f"""
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
            
            # Execute the task using the agent's capabilities
            logger.info("Executing content strategy task")
            result = self.execute_task(task)
            logger.info("Content strategy created successfully")
            return result
        except Exception as e:
            logger.error(f"Error creating content strategy: {str(e)}")
            return f"Error creating content strategy: {str(e)}" 