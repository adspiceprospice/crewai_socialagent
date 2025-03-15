import logging
from crewai import Agent
from crewai.tools import BaseTool
from typing import List, Optional
from src.tools.gemini_image_tool import GeminiImageTool
from src.tools.linkedin_tool import LinkedInTool
from src.tools.twitter_tool import TwitterTool
from src.tools.scheduler_tool import SchedulerTool
from datetime import datetime
from langchain_openai import ChatOpenAI
from .content_strategy_agent import ContentStrategyAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("social_media_agent")

class SocialMediaAgent:
    """
    A social media agent that can create and manage content for various platforms.
    """
    
    def __init__(
        self,
        name: str = "Social Media Manager",
        role: str = "Social Media Manager",
        goal: str = "Create and manage engaging social media content across platforms",
        backstory: str = "I am an experienced social media manager with expertise in content creation, scheduling, and engagement. I help businesses build their online presence and engage with their audience effectively.",
        verbose: bool = True,
        allow_delegation: bool = False,
        extra_tools: Optional[List[BaseTool]] = None,
        llm: ChatOpenAI = None
    ):
        """
        Initialize the social media agent.
        
        Args:
            name: The name of the agent
            role: The role of the agent
            goal: The goal of the agent
            backstory: The backstory of the agent
            verbose: Whether to enable verbose output
            allow_delegation: Whether to allow the agent to delegate tasks
            extra_tools: Additional tools to provide to the agent
            llm: Language model to use for content strategy generation
        """
        logger.info("Initializing SocialMediaAgent")
        self.llm = llm
        
        try:
            # Initialize content strategy agent
            logger.info("Initializing ContentStrategyAgent")
            self.content_strategy_agent = ContentStrategyAgent(llm=self.llm)
            
            # Initialize tools
            logger.info("Initializing tools")
            self.tools = []
            
            # Add tools with error handling
            try:
                self.tools.append(GeminiImageTool())
                logger.info("GeminiImageTool initialized")
            except Exception as e:
                logger.error(f"Error initializing GeminiImageTool: {str(e)}")
                
            try:
                self.tools.append(LinkedInTool())
                logger.info("LinkedInTool initialized")
            except Exception as e:
                logger.error(f"Error initializing LinkedInTool: {str(e)}")
                
            try:
                self.tools.append(TwitterTool())
                logger.info("TwitterTool initialized")
            except Exception as e:
                logger.error(f"Error initializing TwitterTool: {str(e)}")
                
            try:
                self.tools.append(SchedulerTool())
                logger.info("SchedulerTool initialized")
            except Exception as e:
                logger.error(f"Error initializing SchedulerTool: {str(e)}")
            
            # Add extra tools if provided
            if extra_tools:
                self.tools.extend(extra_tools)
                
            logger.info("SocialMediaAgent initialized successfully")
        except Exception as e:
            logger.error(f"Error during SocialMediaAgent initialization: {str(e)}")
            # Continue with partial initialization to prevent crashes

    def get_agent(self) -> Agent:
        """Get the CrewAI agent instance."""
        return self.agent
        
    def create_content_strategy(self, industry: str, target_audience: str, goals: List[str]) -> str:
        """
        Create a content strategy using the ContentStrategyAgent.
        
        Args:
            industry (str): The industry or business domain
            target_audience (str): Description of the target audience
            goals (List[str]): List of goals to achieve with the content strategy
            
        Returns:
            str: A detailed content strategy
        """
        logger.info(f"Creating content strategy for {industry}, target audience: {target_audience}")
        try:
            if not self.content_strategy_agent:
                logger.error("ContentStrategyAgent not initialized")
                return "Error: Content strategy agent not initialized"
                
            result = self.content_strategy_agent.create_content_strategy(
                industry=industry,
                target_audience=target_audience,
                goals=goals
            )
            logger.info("Content strategy created successfully")
            return result
        except Exception as e:
            logger.error(f"Error creating content strategy: {str(e)}")
            return f"Error creating content strategy: {str(e)}"
        
    def generate_content(self, topic: str, platform: str, content_type: str) -> dict:
        """
        Generate content based on the given parameters.
        
        Args:
            topic (str): The topic to create content about
            platform (str): The target platform (e.g., 'linkedin', 'twitter')
            content_type (str): Type of content to generate (e.g., 'post', 'article', 'thread')
            
        Returns:
            dict: Generated content with metadata
        """
        logger.info(f"Generating content for topic: {topic}, platform: {platform}, type: {content_type}")
        try:
            # For demonstration purposes, return a mock response
            return {
                "content": f"This is a sample {content_type} for {platform} about {topic}.",
                "platform": platform,
                "type": content_type,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return {
                "error": f"Error generating content: {str(e)}"
            }
        
    def schedule_content(self, content: str, platform: str, schedule_time: datetime, image_path: Optional[str] = None) -> dict:
        """
        Schedule content for posting.
        
        Args:
            content (str): The content to schedule
            platform (str): The target platform
            schedule_time (datetime): When to post the content
            image_path (Optional[str]): Path to an image to include with the post
            
        Returns:
            dict: Scheduling confirmation and metadata
        """
        logger.info(f"Scheduling content for {platform} at {schedule_time}")
        try:
            # Find the scheduler tool
            scheduler_tool = next((tool for tool in self.tools if isinstance(tool, SchedulerTool)), None)
            
            if scheduler_tool:
                # Use the scheduler tool to schedule the content
                result = scheduler_tool._run(
                    content=content,
                    platform=platform,
                    schedule_time=schedule_time.isoformat(),
                    image_path=image_path
                )
                return {"success": True, "message": result}
            else:
                logger.error("Scheduler tool not found")
                return {"error": "Scheduler tool not found"}
        except Exception as e:
            logger.error(f"Error scheduling content: {str(e)}")
            return {"error": f"Error scheduling content: {str(e)}"}
        
    def post_content(self, content: str, platform: str, image_path: Optional[str] = None) -> dict:
        """
        Post content immediately.
        
        Args:
            content (str): The content to post
            platform (str): The target platform
            image_path (Optional[str]): Path to an image to include with the post
            
        Returns:
            dict: Posting confirmation and metadata
        """
        logger.info(f"Posting content to {platform}")
        try:
            if platform.lower() == "linkedin":
                tool = next((tool for tool in self.tools if isinstance(tool, LinkedInTool)), None)
            elif platform.lower() in ["twitter", "x"]:
                tool = next((tool for tool in self.tools if isinstance(tool, TwitterTool)), None)
            else:
                logger.error(f"Unsupported platform: {platform}")
                return {"error": f"Unsupported platform: {platform}"}
                
            if tool:
                result = tool._run(
                    text=content,
                    image_path=image_path
                )
                return {"success": True, "message": result}
            else:
                logger.error(f"{platform} tool not found")
                return {"error": f"{platform} tool not found"}
        except Exception as e:
            logger.error(f"Error posting content: {str(e)}")
            return {"error": f"Error posting content: {str(e)}"}
        
    def generate_image(self, prompt: str, reference_image_path: Optional[str] = None) -> str:
        """
        Generate an image based on the prompt.
        
        Args:
            prompt (str): Description of the image to generate
            reference_image_path (Optional[str]): Path to a reference image
            
        Returns:
            str: Path to the generated image
        """
        logger.info(f"Generating image with prompt: {prompt}")
        try:
            # Find the image generation tool
            image_tool = next((tool for tool in self.tools if isinstance(tool, GeminiImageTool)), None)
            
            if image_tool:
                # Use the image tool to generate the image
                result = image_tool._run(
                    prompt=prompt,
                    reference_image_path=reference_image_path
                )
                return result
            else:
                logger.error("Image generation tool not found")
                return "Error: Image generation tool not found"
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return f"Error generating image: {str(e)}"
        
    def check_engagement(self, platform: str, post_id: str) -> dict:
        """
        Check engagement metrics for a post.
        
        Args:
            platform (str): The platform where the post is
            post_id (str): ID of the post to check
            
        Returns:
            dict: Engagement metrics
        """
        logger.info(f"Checking engagement for {platform} post: {post_id}")
        try:
            if platform.lower() == "linkedin":
                tool = next((tool for tool in self.tools if isinstance(tool, LinkedInTool)), None)
                if tool:
                    result = tool.get_post_engagement(post_id)
                    return result
            elif platform.lower() in ["twitter", "x"]:
                tool = next((tool for tool in self.tools if isinstance(tool, TwitterTool)), None)
                if tool:
                    result = tool.get_tweet_metrics(post_id)
                    return result
                    
            logger.error(f"Cannot check engagement for {platform}")
            return {"error": f"Cannot check engagement for {platform}"}
        except Exception as e:
            logger.error(f"Error checking engagement: {str(e)}")
            return {"error": f"Error checking engagement: {str(e)}"}
        
    def respond_to_comments(self, platform: str, post_id: str, comments: List[dict]) -> List[dict]:
        """
        Generate responses to comments on a post.
        
        Args:
            platform (str): The platform where the post is
            post_id (str): ID of the post
            comments (List[dict]): List of comments to respond to
            
        Returns:
            List[dict]: Generated responses
        """
        logger.info(f"Responding to comments for {platform} post: {post_id}")
        try:
            # For demonstration purposes, generate mock responses
            responses = []
            for comment in comments:
                responses.append({
                    "comment_id": comment.get("id"),
                    "response": f"Thank you for your comment: '{comment.get('text')}'",
                    "timestamp": datetime.now().isoformat()
                })
            return responses
        except Exception as e:
            logger.error(f"Error responding to comments: {str(e)}")
            return [{"error": f"Error responding to comments: {str(e)}"}] 