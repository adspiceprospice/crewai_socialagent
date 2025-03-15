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

@main.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

# Function to run the monitor in a separate thread
def run_monitor_thread():
    """Function to run the monitor in a separate thread."""
    try:
        logger.info("Starting monitor thread")
        global monitor
        if monitor:
            monitor.run()
    except Exception as e:
        logger.error(f"Error in monitor thread: {str(e)}")

# Scheduler process
scheduler_process = None

@main.route('/run-scheduler')
def run_scheduler():
    """Endpoint to manually trigger the scheduler."""
    global scheduler_process
    
    try:
        if scheduler_process is None or scheduler_process.poll() is not None:
            # Start the scheduler process
            scheduler_process = subprocess.Popen(
                ["python", "-m", "src.scheduler"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            flash('Scheduler started successfully!', 'success')
        else:
            flash('Scheduler is already running', 'info')
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        flash(f'Error starting scheduler: {str(e)}', 'danger')
    
    return redirect(url_for('main.schedule_content_route'))

@main.route('/stop-scheduler')
def stop_scheduler():
    """Endpoint to stop the scheduler."""
    global scheduler_process
    
    try:
        if scheduler_process is not None and scheduler_process.poll() is None:
            # Terminate the scheduler process
            scheduler_process.terminate()
            scheduler_process.wait(timeout=5)
            scheduler_process = None
            flash('Scheduler stopped successfully!', 'success')
        else:
            flash('Scheduler is not running', 'info')
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
        flash(f'Error stopping scheduler: {str(e)}', 'danger')
    
    return redirect(url_for('main.schedule_content_route'))

# Monitor thread
monitor_thread = None

@main.route('/run-monitor')
def run_monitor():
    """Endpoint to manually trigger the monitor."""
    global monitor_thread
    global monitor
    
    try:
        if monitor_thread is None or not monitor_thread.is_alive():
            # Start the monitor in a thread instead of a separate process
            if monitor:
                monitor_thread = threading.Thread(target=run_monitor_thread)
                monitor_thread.daemon = True
                monitor.is_running = True
                monitor_thread.start()
                flash('Monitor started successfully!', 'success')
            else:
                # Fallback to subprocess method if monitor isn't available
                monitor_process = subprocess.Popen(
                    ["python", "-m", "src.monitor"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                flash('Monitor started successfully (using subprocess)!', 'info')
        else:
            flash('Monitor is already running', 'info')
    except Exception as e:
        logger.error(f"Error starting monitor: {str(e)}")
        flash(f'Error starting monitor: {str(e)}', 'danger')
    
    return redirect(url_for('main.respond_comments_route'))

@main.route('/stop-monitor')
def stop_monitor():
    """Endpoint to stop the monitor."""
    global monitor_thread
    global monitor
    
    try:
        if monitor and monitor_thread and monitor_thread.is_alive():
            # Signal the monitor to stop
            monitor.is_running = False
            # Wait for the thread to finish
            monitor_thread.join(timeout=5)
            flash('Monitor stopped successfully!', 'success')
        else:
            # Fallback to killing any monitor processes
            try:
                # Find and kill monitor processes
                subprocess.run(["pkill", "-f", "src.monitor"], check=False)
                flash('Monitor stopped successfully!', 'success')
            except:
                flash('Monitor is not running', 'info')
    except Exception as e:
        logger.error(f"Error stopping monitor: {str(e)}")
        flash(f'Error stopping monitor: {str(e)}', 'danger')
    
    return redirect(url_for('main.respond_comments_route'))

@main.route('/publish-post/<post_id>')
def publish_post(post_id):
    """Endpoint to publish a scheduled post immediately."""
    try:
        # Call the helper function to publish the post
        result = publish_scheduled_post(post_id, agent, scheduler_tool)
        
        if result.get('success', False):
            if result.get('warning'):
                flash(f"Post published with warning: {result['warning']}", 'warning')
            else:
                flash('Post published successfully!', 'success')
        else:
            flash(f"Error publishing post: {result.get('error', 'Unknown error')}", 'danger')
    except Exception as e:
        logger.error(f"Error publishing post immediately: {str(e)}")
        flash(f'Error publishing post: {str(e)}', 'danger')
    
    return redirect(url_for('main.schedule_content_route'))

@main.route('/view-comments/<platform>/<post_id>')
def view_comments(platform, post_id):
    """Endpoint to view comments for a specific post."""
    comments = []
    responses = []
    
    try:
        if monitor:
            # Check for comments
            comments_result = monitor.check_for_comments(platform, post_id)
            if comments_result.get('success', True):
                comments = comments_result.get('comments', [])
                
                # Also load any saved responses
                try:
                    responses_file = os.path.join(monitor.responses_dir, f"{post_id}_responses.json")
                    if os.path.exists(responses_file):
                        with open(responses_file, "r") as f:
                            responses = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading responses: {str(e)}")
        else:
            flash('Monitor not available', 'danger')
    except Exception as e:
        logger.error(f"Error viewing comments: {str(e)}")
        flash(f'Error viewing comments: {str(e)}', 'danger')
    
    return render_template('view_comments.html', platform=platform, post_id=post_id, comments=comments, responses=responses)

@main.route('/manual-check-comments', methods=['GET', 'POST'])
def manual_check_comments():
    """Render the manual comment checking page and handle form submission."""
    comments = []
    
    if request.method == 'POST':
        try:
            platform = request.form.get('platform')
            post_id = request.form.get('post_id')
            
            if not all([platform, post_id]):
                flash('Please fill out all required fields', 'danger')
            else:
                # Check for comments
                if monitor:
                    comments_result = monitor.check_for_comments(platform, post_id)
                    if comments_result.get('success', True):
                        comments = comments_result.get('comments', [])
                        
                        if comments:
                            flash(f'Found {len(comments)} comments!', 'success')
                        else:
                            flash('No comments found.', 'info')
                else:
                   flash('Monitor not available', 'danger')
        except Exception as e:
            logger.error(f"Error in manual check comments route: {str(e)}")
            flash(f'Error checking comments: {str(e)}', 'danger')
    
    return render_template('manual_check_comments.html', comments=comments)