import os
import argparse
from datetime import datetime, timedelta
from crewai import Crew, Process
from src.agents.social_media_agent import SocialMediaAgent
from src.agents.tasks import SocialMediaTasks

def create_content_strategy(industry: str, target_audience: str, goals: list):
    """Create a content strategy for the specified industry, target audience, and goals."""
    # Create the social media agent
    agent = SocialMediaAgent(
        name="Content Strategist",
        role="Social Media Content Strategist",
        goal="Create comprehensive and effective social media content strategies",
        backstory="I am an experienced social media strategist with expertise in developing content strategies that drive engagement and achieve business goals.",
        verbose=True
    )
    
    # Create the content strategy task
    task = SocialMediaTasks.create_content_strategy_task(agent, industry, target_audience, goals)
    
    # Create the crew with memory enabled
    crew = Crew(
        agents=[agent.get_agent()],
        tasks=[task],
        verbose=True,
        process=Process.sequential,
        memory=True  # Enable memory
    )
    
    # Run the crew
    result = crew.kickoff()
    
    return result

def generate_content(topic: str, platform: str, content_type: str):
    """Generate content for the specified topic, platform, and content type."""
    # Create the social media agent
    agent = SocialMediaAgent(
        name="Content Creator",
        role="Social Media Content Creator",
        goal="Create engaging and effective social media content",
        backstory="I am a creative content creator with expertise in crafting engaging social media posts that resonate with audiences.",
        verbose=True
    )
    
    # Create the content generation task
    task = SocialMediaTasks.generate_content_task(agent, topic, platform, content_type)
    
    # Create the crew with memory enabled
    crew = Crew(
        agents=[agent.get_agent()],
        tasks=[task],
        verbose=True,
        process=Process.sequential,
        memory=True  # Enable memory
    )
    
    # Run the crew
    result = crew.kickoff()
    
    return result

def generate_image(prompt: str, reference_image_path=None):
    """Generate an image based on the provided prompt."""
    # Create the social media agent
    agent = SocialMediaAgent(
        name="Image Creator",
        role="Social Media Image Creator",
        goal="Create visually appealing images for social media",
        backstory="I am a skilled image creator with expertise in generating high-quality images that enhance social media content.",
        verbose=True
    )
    
    # Create the image generation task
    task = SocialMediaTasks.generate_image_task(agent, prompt, reference_image_path)
    
    # Create the crew with memory enabled
    crew = Crew(
        agents=[agent.get_agent()],
        tasks=[task],
        verbose=True,
        process=Process.sequential,
        memory=True  # Enable memory
    )
    
    # Run the crew
    result = crew.kickoff()
    
    return result

def schedule_content(content: str, platform: str, schedule_time: str, image_path=None):
    """Schedule content for posting."""
    # Create the social media agent
    agent = SocialMediaAgent(
        name="Content Scheduler",
        role="Social Media Content Scheduler",
        goal="Schedule social media content for optimal engagement",
        backstory="I am an expert in scheduling social media content to maximize reach and engagement.",
        verbose=True
    )
    
    # Create the content scheduling task
    task = SocialMediaTasks.schedule_content_task(agent, content, platform, schedule_time, image_path)
    
    # Create the crew with memory enabled
    crew = Crew(
        agents=[agent.get_agent()],
        tasks=[task],
        verbose=True,
        process=Process.sequential,
        memory=True  # Enable memory
    )
    
    # Run the crew
    result = crew.kickoff()
    
    return result

def post_content(content: str, platform: str, image_path=None):
    """Post content immediately."""
    # Create the social media agent
    agent = SocialMediaAgent(
        name="Content Poster",
        role="Social Media Content Poster",
        goal="Post engaging social media content",
        backstory="I am an expert in posting social media content that drives engagement and achieves business goals.",
        verbose=True
    )
    
    # Create the content posting task
    task = SocialMediaTasks.post_content_task(agent, content, platform, image_path)
    
    # Create the crew with memory enabled
    crew = Crew(
        agents=[agent.get_agent()],
        tasks=[task],
        verbose=True,
        process=Process.sequential,
        memory=True  # Enable memory
    )
    
    # Run the crew
    result = crew.kickoff()
    
    return result

def check_engagement(platform: str, post_id: str):
    """Check engagement on a post."""
    # Create the social media agent
    agent = SocialMediaAgent(
        name="Engagement Analyst",
        role="Social Media Engagement Analyst",
        goal="Analyze social media engagement and provide insights",
        backstory="I am an expert in analyzing social media engagement metrics and providing actionable insights to improve performance.",
        verbose=True
    )
    
    # Create the engagement checking task
    task = SocialMediaTasks.check_engagement_task(agent, platform, post_id)
    
    # Create the crew with memory enabled
    crew = Crew(
        agents=[agent.get_agent()],
        tasks=[task],
        verbose=True,
        process=Process.sequential,
        memory=True  # Enable memory
    )
    
    # Run the crew
    result = crew.kickoff()
    
    return result

def respond_to_comments(platform: str, post_id: str, comments: list):
    """Generate responses to comments on a post."""
    # Create the social media agent
    agent = SocialMediaAgent(
        name="Engagement Manager",
        role="Social Media Engagement Manager",
        goal="Respond to social media comments in a way that builds relationships and drives engagement",
        backstory="I am an expert in managing social media engagement and crafting thoughtful responses that build community.",
        verbose=True
    )
    
    # Create the comment response task
    task = SocialMediaTasks.respond_to_comments_task(agent, platform, post_id, comments)
    
    # Create the crew with memory enabled
    crew = Crew(
        agents=[agent.get_agent()],
        tasks=[task],
        verbose=True,
        process=Process.sequential,
        memory=True  # Enable memory
    )
    
    # Run the crew
    result = crew.kickoff()
    
    return result

def main():
    """Main function to run the application."""
    parser = argparse.ArgumentParser(description="Social Media Agent CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create content strategy command
    strategy_parser = subparsers.add_parser("strategy", help="Create a content strategy")
    strategy_parser.add_argument("--industry", required=True, help="Industry the content is for")
    strategy_parser.add_argument("--audience", required=True, help="Target audience for the content")
    strategy_parser.add_argument("--goals", required=True, nargs="+", help="Goals of the content strategy")
    
    # Generate content command
    content_parser = subparsers.add_parser("content", help="Generate content")
    content_parser.add_argument("--topic", required=True, help="Topic to generate content for")
    content_parser.add_argument("--platform", required=True, choices=["linkedin", "twitter", "x"], help="Platform to generate content for")
    content_parser.add_argument("--type", required=True, choices=["post", "article", "thread"], help="Type of content to generate")
    
    # Generate image command
    image_parser = subparsers.add_parser("image", help="Generate an image")
    image_parser.add_argument("--prompt", required=True, help="Prompt to generate an image from")
    image_parser.add_argument("--reference", help="Path to a reference image")
    
    # Schedule content command
    schedule_parser = subparsers.add_parser("schedule", help="Schedule content for posting")
    schedule_parser.add_argument("--content", required=True, help="Content to post")
    schedule_parser.add_argument("--platform", required=True, choices=["linkedin", "twitter", "x"], help="Platform to post to")
    schedule_parser.add_argument("--time", required=True, help="Time to schedule the post for (ISO-8601 format)")
    schedule_parser.add_argument("--image", help="Path to an image to include in the post")
    
    # Post content command
    post_parser = subparsers.add_parser("post", help="Post content immediately")
    post_parser.add_argument("--content", required=True, help="Content to post")
    post_parser.add_argument("--platform", required=True, choices=["linkedin", "twitter", "x"], help="Platform to post to")
    post_parser.add_argument("--image", help="Path to an image to include in the post")
    
    # Check engagement command
    engagement_parser = subparsers.add_parser("engagement", help="Check engagement on a post")
    engagement_parser.add_argument("--platform", required=True, choices=["linkedin", "twitter", "x"], help="Platform to check engagement on")
    engagement_parser.add_argument("--post-id", required=True, help="ID of the post to check engagement on")
    
    # Respond to comments command
    respond_parser = subparsers.add_parser("respond", help="Respond to comments on a post")
    respond_parser.add_argument("--platform", required=True, choices=["linkedin", "twitter", "x"], help="Platform the comments are on")
    respond_parser.add_argument("--post-id", required=True, help="ID of the post the comments are on")
    respond_parser.add_argument("--comments-file", required=True, help="Path to a JSON file containing comments")
    
    args = parser.parse_args()
    
    if args.command == "strategy":
        result = create_content_strategy(args.industry, args.audience, args.goals)
        print(result)
    elif args.command == "content":
        result = generate_content(args.topic, args.platform, args.type)
        print(result)
    elif args.command == "image":
        result = generate_image(args.prompt, args.reference)
        print(result)
    elif args.command == "schedule":
        result = schedule_content(args.content, args.platform, args.time, args.image)
        print(result)
    elif args.command == "post":
        result = post_content(args.content, args.platform, args.image)
        print(result)
    elif args.command == "engagement":
        result = check_engagement(args.platform, args.post_id)
        print(result)
    elif args.command == "respond":
        import json
        with open(args.comments_file, "r") as f:
            comments = json.load(f)
        result = respond_to_comments(args.platform, args.post_id, comments)
        print(result)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 