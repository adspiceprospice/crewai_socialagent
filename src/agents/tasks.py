from crewai import Task
from typing import List, Optional, Dict, Any
from src.agents.social_media_agent import SocialMediaAgent

class SocialMediaTasks:
    """
    Tasks for the social media agent.
    """
    
    @staticmethod
    def create_content_strategy_task(agent: SocialMediaAgent, industry: str, target_audience: str, goals: List[str]) -> Task:
        """
        Create a task for creating a content strategy.
        
        Args:
            agent: The social media agent
            industry: The industry the content is for
            target_audience: The target audience for the content
            goals: The goals of the content strategy
            
        Returns:
            A task for creating a content strategy
        """
        return Task(
            description=f"""
            Create a comprehensive social media content strategy for a business in the {industry} industry.
            
            Target Audience:
            {target_audience}
            
            Goals:
            {', '.join(goals)}
            
            Your strategy should include:
            1. Content themes and topics
            2. Content types (e.g., posts, articles, videos)
            3. Posting frequency and schedule
            4. Platform-specific strategies for LinkedIn and Twitter
            5. Engagement tactics
            6. Success metrics
            
            Be specific and provide actionable recommendations.
            """,
            agent=agent.get_agent(),
            expected_output="A comprehensive social media content strategy document"
        )
        
    @staticmethod
    def generate_content_task(agent: SocialMediaAgent, topic: str, platform: str, content_type: str) -> Task:
        """
        Create a task for generating content.
        
        Args:
            agent: The social media agent
            topic: The topic to generate content for
            platform: The platform to generate content for
            content_type: The type of content to generate
            
        Returns:
            A task for generating content
        """
        platform_specific_instructions = ""
        if platform.lower() == "linkedin":
            platform_specific_instructions = """
            For LinkedIn:
            - Keep it professional but conversational
            - Include relevant hashtags (3-5)
            - Consider adding a call to action
            - Optimal length is 1,200-1,600 characters
            """
        elif platform.lower() in ["twitter", "x"]:
            platform_specific_instructions = """
            For Twitter/X:
            - Keep it concise (max 280 characters)
            - Include relevant hashtags (1-2)
            - Consider adding a call to action
            - Make it engaging and shareable
            """
            
        content_type_instructions = ""
        if content_type.lower() == "post":
            content_type_instructions = """
            For a regular post:
            - Make it engaging and informative
            - Include a hook to grab attention
            - End with a question or call to action
            """
        elif content_type.lower() == "article":
            content_type_instructions = """
            For an article:
            - Create a compelling headline
            - Structure with clear sections
            - Include actionable insights
            - End with a conclusion and call to action
            """
        elif content_type.lower() == "thread":
            content_type_instructions = """
            For a thread:
            - Create a compelling opening tweet
            - Structure the thread logically
            - Make each tweet valuable on its own
            - End with a conclusion and call to action
            """
            
        return Task(
            description=f"""
            Generate {content_type} content about {topic} for {platform}.
            
            {platform_specific_instructions}
            
            {content_type_instructions}
            
            Make the content engaging, informative, and aligned with best practices for {platform}.
            """,
            agent=agent.get_agent(),
            expected_output=f"A {content_type} for {platform} about {topic}"
        )
        
    @staticmethod
    def generate_image_task(agent: SocialMediaAgent, prompt: str, reference_image_path: Optional[str] = None) -> Task:
        """
        Create a task for generating an image.
        
        Args:
            agent: The social media agent
            prompt: The prompt to generate an image from
            reference_image_path: Optional path to a reference image
            
        Returns:
            A task for generating an image
        """
        reference_instructions = ""
        if reference_image_path:
            reference_instructions = f"""
            Use the reference image at {reference_image_path} as inspiration.
            """
            
        return Task(
            description=f"""
            Generate an image based on the following prompt:
            
            "{prompt}"
            
            {reference_instructions}
            
            The image should be high-quality and suitable for social media.
            """,
            agent=agent.get_agent(),
            expected_output="Path to the generated image"
        )
        
    @staticmethod
    def schedule_content_task(
        agent: SocialMediaAgent, 
        content: str, 
        platform: str, 
        schedule_time: str, 
        image_path: Optional[str] = None
    ) -> Task:
        """
        Create a task for scheduling content.
        
        Args:
            agent: The social media agent
            content: The content to schedule
            platform: The platform to schedule the content for
            schedule_time: The time to schedule the content for
            image_path: Optional path to an image to include
            
        Returns:
            A task for scheduling content
        """
        image_instructions = ""
        if image_path:
            image_instructions = f"""
            Include the image at {image_path} in the post.
            """
            
        return Task(
            description=f"""
            Schedule the following content for posting on {platform} at {schedule_time}:
            
            "{content}"
            
            {image_instructions}
            
            Ensure the content is properly formatted for {platform} and scheduled correctly.
            """,
            agent=agent.get_agent(),
            expected_output="Confirmation of scheduled post"
        )
        
    @staticmethod
    def post_content_task(
        agent: SocialMediaAgent, 
        content: str, 
        platform: str, 
        image_path: Optional[str] = None
    ) -> Task:
        """
        Create a task for posting content immediately.
        
        Args:
            agent: The social media agent
            content: The content to post
            platform: The platform to post the content to
            image_path: Optional path to an image to include
            
        Returns:
            A task for posting content
        """
        image_instructions = ""
        if image_path:
            image_instructions = f"""
            Include the image at {image_path} in the post.
            """
            
        return Task(
            description=f"""
            Post the following content to {platform} immediately:
            
            "{content}"
            
            {image_instructions}
            
            Ensure the content is properly formatted for {platform} and posted successfully.
            """,
            agent=agent.get_agent(),
            expected_output="Confirmation of posted content"
        )
        
    @staticmethod
    def check_engagement_task(agent: SocialMediaAgent, platform: str, post_id: str) -> Task:
        """
        Create a task for checking engagement on a post.
        
        Args:
            agent: The social media agent
            platform: The platform to check engagement on
            post_id: The ID of the post to check engagement on
            
        Returns:
            A task for checking engagement
        """
        return Task(
            description=f"""
            Check the engagement on the {platform} post with ID {post_id}.
            
            Analyze the following metrics:
            1. Number of likes/reactions
            2. Number of comments
            3. Number of shares/retweets
            4. Overall engagement rate
            
            Provide insights on the post's performance and recommendations for improvement.
            """,
            agent=agent.get_agent(),
            expected_output="Engagement metrics and analysis"
        )
        
    @staticmethod
    def respond_to_comments_task(agent: SocialMediaAgent, platform: str, post_id: str, comments: List[Dict[str, Any]]) -> Task:
        """
        Create a task for responding to comments on a post.
        
        Args:
            agent: The social media agent
            platform: The platform the comments are on
            post_id: The ID of the post the comments are on
            comments: A list of comments to respond to
            
        Returns:
            A task for responding to comments
        """
        comments_str = "\n".join([f"- {comment.get('author', 'User')}: {comment.get('text', '')}" for comment in comments])
        
        return Task(
            description=f"""
            Generate responses to the following comments on a {platform} post (ID: {post_id}):
            
            {comments_str}
            
            For each comment:
            1. Acknowledge the commenter
            2. Provide a thoughtful, helpful response
            3. Maintain a consistent brand voice
            4. Include a call to action where appropriate
            
            Ensure responses are appropriate for {platform} and follow best practices for engagement.
            """,
            agent=agent.get_agent(),
            expected_output="Responses to each comment"
        ) 