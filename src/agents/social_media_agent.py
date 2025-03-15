from crewai import Agent
from crewai.tools import BaseTool
from typing import List, Optional
from src.tools.gemini_image_tool import GeminiImageTool
from src.tools.linkedin_tool import LinkedInTool
from src.tools.twitter_tool import TwitterTool
from src.tools.scheduler_tool import SchedulerTool

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
        extra_tools: Optional[List[BaseTool]] = None
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
        """
        # Default tools
        self.default_tools = [
            GeminiImageTool(),
            LinkedInTool(),
            TwitterTool(),
            SchedulerTool()
        ]
        
        # Add extra tools if provided
        self.tools = self.default_tools
        if extra_tools:
            self.tools.extend(extra_tools)
            
        # Create the agent
        self.agent = Agent(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=verbose,
            allow_delegation=allow_delegation,
            tools=self.tools
        )
        
    def get_agent(self) -> Agent:
        """Get the CrewAI agent instance."""
        return self.agent
        
    def create_content_strategy(self, industry: str, target_audience: str, goals: List[str]) -> str:
        """
        Create a content strategy for the specified industry, target audience, and goals.
        
        Args:
            industry: The industry the content is for
            target_audience: The target audience for the content
            goals: The goals of the content strategy
            
        Returns:
            A string containing the content strategy
        """
        # This will be implemented as a task for the agent
        pass
        
    def generate_content(self, topic: str, platform: str, content_type: str) -> dict:
        """
        Generate content for the specified topic, platform, and content type.
        
        Args:
            topic: The topic to generate content for
            platform: The platform to generate content for (e.g., "linkedin", "twitter")
            content_type: The type of content to generate (e.g., "post", "article", "thread")
            
        Returns:
            A dictionary containing the generated content
        """
        # This will be implemented as a task for the agent
        pass
        
    def schedule_content(self, content: str, platform: str, schedule_time: str, image_path: Optional[str] = None) -> dict:
        """
        Schedule content for posting.
        
        Args:
            content: The content to post
            platform: The platform to post to (e.g., "linkedin", "twitter")
            schedule_time: The time to schedule the post for (ISO-8601 format)
            image_path: Optional path to an image to include in the post
            
        Returns:
            A dictionary containing the result of the scheduling operation
        """
        # This will be implemented as a task for the agent
        pass
        
    def post_content(self, content: str, platform: str, image_path: Optional[str] = None) -> dict:
        """
        Post content immediately.
        
        Args:
            content: The content to post
            platform: The platform to post to (e.g., "linkedin", "twitter")
            image_path: Optional path to an image to include in the post
            
        Returns:
            A dictionary containing the result of the posting operation
        """
        # This will be implemented as a task for the agent
        pass
        
    def generate_image(self, prompt: str, reference_image_path: Optional[str] = None) -> dict:
        """
        Generate an image based on the provided prompt.
        
        Args:
            prompt: The prompt to generate an image from
            reference_image_path: Optional path to a reference image
            
        Returns:
            A dictionary containing the path to the generated image
        """
        # This will be implemented as a task for the agent
        pass
        
    def check_engagement(self, platform: str, post_id: str) -> dict:
        """
        Check engagement on a post.
        
        Args:
            platform: The platform to check engagement on (e.g., "linkedin", "twitter")
            post_id: The ID of the post to check engagement on
            
        Returns:
            A dictionary containing engagement metrics
        """
        # This will be implemented as a task for the agent
        pass
        
    def respond_to_comments(self, platform: str, post_id: str, comments: List[dict]) -> List[dict]:
        """
        Generate responses to comments on a post.
        
        Args:
            platform: The platform the comments are on (e.g., "linkedin", "twitter")
            post_id: The ID of the post the comments are on
            comments: A list of comments to respond to
            
        Returns:
            A list of dictionaries containing the responses
        """
        # This will be implemented as a task for the agent
        pass 