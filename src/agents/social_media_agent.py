import logging
from crewai import Agent
from crewai.tools import BaseTool
from typing import List, Optional, Dict, Any
from src.tools.gemini_image_tool import GeminiImageTool
from src.tools.linkedin_tool import LinkedInTool
from src.tools.twitter_tool import TwitterTool
from src.tools.scheduler_tool import SchedulerTool
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from .content_strategy_agent import ContentStrategyAgent
import os
from openai import OpenAI
import json
import uuid

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
            # Initialize OpenAI client directly for backup
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            logger.info("OpenAI client initialized")
            
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

    def create_content_strategy(self, industry: str, target_audience: str, goals: List[str]) -> Dict[str, Any]:
        """
        Create a structured content strategy.
        
        Args:
            industry (str): The industry or business domain
            target_audience (str): Description of the target audience
            goals (List[str]): List of goals to achieve with the content strategy
            
        Returns:
            Dict[str, Any]: A structured content strategy with sections
        """
        logger.info(f"Creating content strategy for {industry}, target audience: {target_audience}")
        try:
            # Format the goals into a readable string
            if isinstance(goals, str):
                # If goals is a string, split it into a list
                goals_list = [goal.strip() for goal in goals.split(',') if goal.strip()]
            else:
                goals_list = goals
            
            goals_str = "\n- " + "\n- ".join(goals_list)
            
            # Create a direct prompt for OpenAI that requests structured output
            prompt = f"""
            Create a comprehensive content strategy for:
            Industry: {industry}
            Target Audience: {target_audience}
            Goals:
            - {goals_str}
            
            Return your response in a structured JSON format with the following sections:
            
            1. "executive_summary": A brief overview of the strategy
            2. "target_audience_analysis": Details about the target audience and their needs
            3. "content_themes": A list of key themes and topics to focus on
            4. "content_types": Types of content to create (posts, articles, threads, etc.)
            5. "platform_recommendations": Platform-specific strategies for LinkedIn and Twitter
            6. "posting_schedule": Recommended posting frequency and timings
            7. "engagement_strategies": Tactics for increasing engagement
            8. "success_metrics": KPIs to track performance
            9. "action_plan": Specific next steps to implement the strategy
            
            Ensure each section has detailed, actionable information.
            Format your response as a valid JSON object with these exact keys.
            """
            
            # Use OpenAI client directly with JSON response format
            logger.info("Creating structured content strategy using OpenAI directly")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert content strategist specializing in social media marketing. Return your response in a structured JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4500,
                response_format={"type": "json_object"}
            )
            
            # Extract the content from response and parse as JSON
            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)
            
            # Also store original text version for rendering
            result_json["text_version"] = self._generate_text_version(result_json)
            
            logger.info("Structured content strategy created successfully")
            return result_json
        except Exception as e:
            logger.error(f"Error creating content strategy: {str(e)}")
            return {
                "error": f"Error creating content strategy: {str(e)}",
                "text_version": f"Error: {str(e)}"
            }
    
    def _generate_text_version(self, strategy_json: Dict[str, Any]) -> str:
        """Generate a readable text version of the JSON strategy."""
        try:
            text = "# Content Strategy\n\n"
            
            # Executive Summary
            text += "## Executive Summary\n\n"
            text += f"{strategy_json.get('executive_summary', 'No summary provided.')}\n\n"
            
            # Target Audience Analysis
            text += "## Target Audience Analysis\n\n"
            text += f"{strategy_json.get('target_audience_analysis', 'No audience analysis provided.')}\n\n"
            
            # Content Themes
            text += "## Content Themes\n\n"
            themes = strategy_json.get('content_themes', [])
            if isinstance(themes, list):
                for theme in themes:
                    text += f"- {theme}\n"
            else:
                text += themes
            text += "\n\n"
            
            # Content Types
            text += "## Content Types\n\n"
            content_types = strategy_json.get('content_types', {})
            if isinstance(content_types, dict):
                for platform, types in content_types.items():
                    text += f"### {platform}\n"
                    if isinstance(types, list):
                        for t in types:
                            text += f"- {t}\n"
                    else:
                        text += f"{types}\n"
            else:
                text += str(content_types)
            text += "\n"
            
            # Platform Recommendations
            text += "## Platform Recommendations\n\n"
            platforms = strategy_json.get('platform_recommendations', {})
            if isinstance(platforms, dict):
                for platform, recommendation in platforms.items():
                    text += f"### {platform}\n"
                    text += f"{recommendation}\n\n"
            else:
                text += str(platforms)
            text += "\n"
            
            # Posting Schedule
            text += "## Posting Schedule\n\n"
            text += f"{strategy_json.get('posting_schedule', 'No posting schedule provided.')}\n\n"
            
            # Engagement Strategies
            text += "## Engagement Strategies\n\n"
            text += f"{strategy_json.get('engagement_strategies', 'No engagement strategies provided.')}\n\n"
            
            # Success Metrics
            text += "## Success Metrics\n\n"
            metrics = strategy_json.get('success_metrics', [])
            if isinstance(metrics, list):
                for metric in metrics:
                    text += f"- {metric}\n"
            else:
                text += str(metrics)
            text += "\n\n"
            
            # Action Plan
            text += "## Action Plan\n\n"
            action_plan = strategy_json.get('action_plan', [])
            if isinstance(action_plan, list):
                for i, action in enumerate(action_plan, 1):
                    text += f"{i}. {action}\n"
            else:
                text += str(action_plan)
                
            return text
        except Exception as e:
            logger.error(f"Error generating text version: {str(e)}")
            return "Error generating text version of the strategy. Please refer to the JSON data."

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
            # Create prompt for OpenAI
            prompt = f"""
            Generate {content_type} content for {platform} about the topic: {topic}.
            
            Make it engaging, relevant to the platform, and optimized for user engagement.
            For LinkedIn, maintain a professional tone. For Twitter, keep it concise and to the point.
            
            Include relevant hashtags for the platform at the end if appropriate.
            """
            
            # Use OpenAI client directly
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an experienced social media content creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract the content
            content = response.choices[0].message.content
            
            return {
                "content": content,
                "platform": platform,
                "type": content_type,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return {
                "error": f"Error generating content: {str(e)}"
            }

    def execute_content_plan(self, strategy: dict, time_period: str, content_count: int, platforms: list) -> dict:
        """
        Generate a comprehensive content plan based on a content strategy.
        
        Args:
            strategy (dict): The content strategy to base the plan on
            time_period (str): Time period to generate content for (e.g., '1 week', '1 month')
            content_count (int): Number of content pieces to generate
            platforms (list): Platforms to generate content for
            
        Returns:
            dict: Generated content plan with scheduled items
        """
        logger.info(f"Executing content plan for {time_period}, {content_count} items")
        try:
            # Handle the case where strategy might be a string (from JSON serialization/deserialization)
            if isinstance(strategy, str):
                strategy = json.loads(strategy)
                
            # Extract key information from the strategy
            industry = "Unknown"
            audience = "Unknown"
            themes_str = "General content"
            
            # Safely extract target audience analysis
            if isinstance(strategy.get('target_audience_analysis'), dict):
                demographics = strategy.get('target_audience_analysis').get('demographics', {})
                if isinstance(demographics, dict):
                    industry = demographics.get('industry', 'Unknown')
                    roles = demographics.get('roles', ['Unknown'])
                    if isinstance(roles, list):
                        audience = ', '.join(roles)
                    else:
                        audience = str(roles)
            
            # Safely extract content themes
            content_themes = strategy.get('content_themes', [])
            if isinstance(content_themes, list):
                themes_str = '\n- ' + '\n- '.join(content_themes)
            else:
                themes_str = str(content_themes)
                
            # Parse time period to determine date range
            start_date = datetime.now()
            
            if time_period == '1 week':
                end_date = start_date + timedelta(days=7)
            elif time_period == '2 weeks':
                end_date = start_date + timedelta(days=14)
            elif time_period == '3 months':
                end_date = start_date + timedelta(days=90)
            else:  # Default to 1 month
                end_date = start_date + timedelta(days=30)
                
            # Create a prompt for OpenAI to generate the content plan
            prompt = f"""
            Create a detailed content plan for a business in the {industry} industry targeting {audience}.
            
            The content plan should cover the period from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}.
            
            Generate {content_count} content pieces distributed appropriately across the following platforms: {', '.join(platforms)}.
            
            Content should be based on these themes:
            {themes_str}
            
            For each content piece, provide:
            1. Scheduled date and time (within the specified period)
            2. Platform ({', '.join(platforms)})
            3. Content type (post, article, thread, etc.)
            4. Actual content (ready to post)
            5. Relevant hashtags
            
            Format your response as a valid JSON object with the following structure:
            {{
                "plan_overview": {{
                    "industry": "...",
                    "start_date": "YYYY-MM-DD",
                    "end_date": "YYYY-MM-DD",
                    "platform_distribution": {{ "platform_name": count, ... }}
                }},
                "content_items": [
                    {{
                        "id": "unique_id",
                        "scheduled_time": "YYYY-MM-DD HH:MM",
                        "platform": "platform_name",
                        "content_type": "content_type",
                        "content": "full content text",
                        "hashtags": ["tag1", "tag2", ...],
                        "theme": "content theme"
                    }},
                    ...
                ]
            }}
            
            Ensure the content is engaging, relevant to the audience, and follows best practices for each platform.
            Distribute the content evenly across the time period and consider optimal posting times for each platform.
            Make each piece of content unique, creative, and directly usable without requiring further editing.
            """
            
            # Use OpenAI client directly with JSON response format
            logger.info("Creating content plan using OpenAI")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert social media content planner. Return your response in a structured JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            # Extract the content from response and parse as JSON
            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)
            
            # Ensure each item has a unique ID
            for item in result_json.get('content_items', []):
                if 'id' not in item or not item['id']:
                    item['id'] = str(uuid.uuid4())
            
            logger.info(f"Content plan created successfully with {len(result_json.get('content_items', []))} items")
            return result_json
        except Exception as e:
            logger.error(f"Error executing content plan: {str(e)}")
            return {
                "error": f"Error executing content plan: {str(e)}",
                "content_items": []
            }

    def schedule_multiple_content(self, content_items: list) -> dict:
        """
        Schedule multiple content items at once.
        
        Args:
            content_items (list): List of content items to schedule
            
        Returns:
            dict: Results of scheduling operations
        """
        logger.info(f"Scheduling {len(content_items)} content items")
        results = {
            "success": [],
            "failed": []
        }
        
        try:
            # Find the scheduler tool
            scheduler_tool = next((tool for tool in self.tools if isinstance(tool, SchedulerTool)), None)
            
            if not scheduler_tool:
                logger.error("Scheduler tool not found")
                return {"error": "Scheduler tool not found"}
            
            # Schedule each content item
            for item in content_items:
                try:
                    # Parse the scheduled time
                    scheduled_time = datetime.fromisoformat(item.get("scheduled_time").replace(' ', 'T'))
                    
                    # Schedule the content
                    result = scheduler_tool._run(
                        content=item.get("content"),
                        platform=item.get("platform"),
                        schedule_time=scheduled_time.isoformat(),
                        image_path=item.get("image_path")
                    )
                    
                    # Add to results
                    results["success"].append({
                        "id": item.get("id"),
                        "message": result
                    })
                    
                except Exception as item_error:
                    logger.error(f"Error scheduling content item {item.get('id')}: {str(item_error)}")
                    results["failed"].append({
                        "id": item.get("id"),
                        "error": str(item_error)
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error scheduling multiple content: {str(e)}")
            return {"error": f"Error scheduling multiple content: {str(e)}"}

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
            responses = []
            
            for comment in comments:
                # Create a prompt for responding to the comment
                comment_text = comment.get('text', '')
                prompt = f"""
                Generate a friendly, authentic response to this comment on a {platform} post:
                
                Comment: "{comment_text}"
                
                Make your response sound human, personable, and on-brand. Avoid generic responses.
                Keep it fairly brief and conversational.
                """
                
                # Use OpenAI to generate a response
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are a friendly social media manager responding to comments."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=150
                )
                
                # Add the response to our list
                responses.append({
                    "comment_id": comment.get("id"),
                    "response": response.choices[0].message.content.strip(),
                    "timestamp": datetime.now().isoformat()
                })
                
            return responses
        except Exception as e:
            logger.error(f"Error responding to comments: {str(e)}")
            return [{"error": f"Error responding to comments: {str(e)}"}]