from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, session
from src.agents.social_media_agent import SocialMediaAgent
from src.tools.scheduler_tool import SchedulerTool
from src.monitor import SocialMediaMonitor
from langchain_openai import ChatOpenAI
from src.web_ui.publish_helpers import publish_scheduled_post
from src.config.api_helper import normalize_post_response
import os
import subprocess
import signal
import threading
import time
from datetime import datetime
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("web_ui_routes")

bp = Blueprint('api', __name__, url_prefix='/api')
main = Blueprint('main', __name__)

# Initialize the language model and agent
try:
    llm = ChatOpenAI(
        model_name="gpt-4o",
        temperature=0.7,
        api_key=os.getenv('OPENAI_API_KEY')
    )
    agent = SocialMediaAgent(llm=llm)
    scheduler_tool = SchedulerTool()
    monitor = SocialMediaMonitor()
    logger.info("SocialMediaAgent initialized in routes.py")
except Exception as e:
    logger.error(f"Error initializing agent in routes.py: {str(e)}")
    agent = None
    scheduler_tool = None
    monitor = None

# Global variables for the monitor and scheduler threads
monitor_thread = None
scheduler_process = None