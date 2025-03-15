from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, session
from src.agents.social_media_agent import SocialMediaAgent
from langchain_openai import ChatOpenAI
import os
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
        model_name="gpt-4-turbo-preview",
        temperature=0.7,
        api_key=os.getenv('OPENAI_API_KEY')
    )
    agent = SocialMediaAgent(llm=llm)
    logger.info("SocialMediaAgent initialized in routes.py")
except Exception as e:
    logger.error(f"Error initializing agent in routes.py: {str(e)}")
    agent = None

@main.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

@main.route('/content-strategy', methods=['GET', 'POST'])
def content_strategy():
    """Render the content strategy page and handle form submission."""
    result = None
    strategy_json = None
    
    if request.method == 'POST':
        try:
            industry = request.form.get('industry')
            target_audience = request.form.get('target_audience')
            goals = request.form.get('goals', '').split(',')
            
            if not all([industry, target_audience, goals]):
                flash('Please fill out all required fields', 'danger')
            else:
                # Get structured content strategy
                strategy_json = agent.create_content_strategy(
                    industry=industry,
                    target_audience=target_audience,
                    goals=goals
                )
                
                if 'error' in strategy_json:
                    flash(f'Error generating content strategy: {strategy_json["error"]}', 'danger')
                else:
                    # Get the formatted text version for rendering
                    result = strategy_json.get('text_version', '')
                    
                    # Store the strategy in session for use in other routes
                    session['content_strategy'] = strategy_json
                    
                    flash('Content strategy generated successfully!', 'success')
        except Exception as e:
            logger.error(f"Error in content strategy route: {str(e)}")
            flash(f'Error generating content strategy: {str(e)}', 'danger')
    
    return render_template('content_strategy.html', result=result, strategy_json=strategy_json)

@main.route('/execute-content-plan', methods=['GET', 'POST'])
def execute_content_plan():
    """Render the content plan execution page and handle form submission."""
    result = None
    
    # Get the content strategy from the session or form
    strategy_json = None
    if 'strategy_json' in request.form:
        try:
            strategy_json = json.loads(request.form.get('strategy_json'))
        except:
            pass
    
    if not strategy_json and 'content_strategy' in session:
        strategy_json = session.get('content_strategy')
    
    if request.method == 'POST':
        try:
            # Get form data
            time_period = request.form.get('time_period')  # e.g., '1 week', '1 month', '3 months'
            content_count = int(request.form.get('content_count', 10))
            platforms = request.form.getlist('platforms')  # Multiple select for platforms
            
            if not all([time_period, content_count, platforms]):
                flash('Please fill out all required fields', 'danger')
            else:
                if not strategy_json:
                    flash('Content strategy not found. Please generate a strategy first.', 'danger')
                    return redirect(url_for('main.content_strategy'))
                
                # Generate content based on the strategy
                result = agent.execute_content_plan(
                    strategy=strategy_json,
                    time_period=time_period,
                    content_count=content_count,
                    platforms=platforms
                )
                
                # Store the generated content in the session
                session['generated_content'] = result
                
                flash('Content plan executed successfully!', 'success')
        except Exception as e:
            logger.error(f"Error in execute content plan route: {str(e)}")
            flash(f'Error executing content plan: {str(e)}', 'danger')
    elif request.method == 'GET' and 'generated_content' in session:
        # If we have previously generated content, display it
        result = session.get('generated_content')
    
    return render_template('execute_content_plan.html', strategy=strategy_json, result=result)

@bp.route('/content-strategy', methods=['POST'])
def create_content_strategy():
    """API endpoint to create a content strategy."""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        industry = data.get('industry')
        target_audience = data.get('target_audience')
        goals = data.get('goals', [])
        
        if not all([industry, target_audience, goals]):
            return jsonify({"error": "Missing required parameters: industry, target_audience, goals"}), 400
        
        result = agent.create_content_strategy(
            industry=industry,
            target_audience=target_audience,
            goals=goals
        )
        
        return jsonify({"success": True, "result": result})
    except Exception as e:
        logger.error(f"API error in create_content_strategy: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/schedule-content-item', methods=['POST'])
def schedule_content_item():
    """API endpoint to schedule a single content item."""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        content_item = data.get('content_item')
        
        if not content_item:
            return jsonify({"error": "Missing content item data"}), 400
        
        # Schedule the content
        result = agent.schedule_content(
            content=content_item.get('content'),
            platform=content_item.get('platform'),
            schedule_time=datetime.fromisoformat(content_item.get('scheduled_time').replace(' ', 'T')),
            image_path=content_item.get('image_path')
        )
        
        return jsonify({"success": True, "result": result})
    except Exception as e:
        logger.error(f"API error in schedule_content_item: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/schedule-all-content', methods=['POST'])
def schedule_all_content():
    """API endpoint to schedule multiple content items at once."""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        content_items = data.get('content_items', [])
        
        if not content_items:
            return jsonify({"error": "No content items provided"}), 400
        
        # Schedule all content items
        result = agent.schedule_multiple_content(content_items)
        
        return jsonify({"success": True, "result": result})
    except Exception as e:
        logger.error(f"API error in schedule_all_content: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/generate-content', methods=['POST'])
def generate_content():
    """API endpoint to generate content."""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        topic = data.get('topic')
        platform = data.get('platform')
        content_type = data.get('content_type')
        
        if not all([topic, platform, content_type]):
            return jsonify({"error": "Missing required parameters: topic, platform, content_type"}), 400
        
        result = agent.generate_content(
            topic=topic,
            platform=platform,
            content_type=content_type
        )
        
        return jsonify({"success": True, "result": result})
    except Exception as e:
        logger.error(f"API error in generate_content: {str(e)}")
        return jsonify({"error": str(e)}), 500

@main.route('/content-generation', methods=['GET', 'POST'])
def content_generation():
    """Render the content generation page and handle form submission."""
    result = None
    
    if request.method == 'POST':
        try:
            topic = request.form.get('topic')
            platform = request.form.get('platform')
            content_type = request.form.get('content_type')
            
            if not all([topic, platform, content_type]):
                flash('Please fill out all required fields', 'danger')
            else:
                result = agent.generate_content(
                    topic=topic,
                    platform=platform,
                    content_type=content_type
                )
                flash('Content generated successfully!', 'success')
        except Exception as e:
            logger.error(f"Error in content generation route: {str(e)}")
            flash(f'Error generating content: {str(e)}', 'danger')
    
    return render_template('content_generation.html', result=result)

@main.route('/image-generation', methods=['GET', 'POST'])
def image_generation():
    """Render the image generation page and handle form submission."""
    result = None
    
    if request.method == 'POST':
        try:
            prompt = request.form.get('prompt')
            reference_image = request.files.get('reference_image')
            
            reference_path = None
            if reference_image and reference_image.filename:
                # Save the reference image temporarily
                reference_path = os.path.join('uploads', reference_image.filename)
                os.makedirs('uploads', exist_ok=True)
                reference_image.save(reference_path)
            
            if not prompt:
                flash('Please provide a prompt for the image', 'danger')
            else:
                result = agent.generate_image(
                    prompt=prompt,
                    reference_image_path=reference_path
                )
                flash('Image generated successfully!', 'success')
        except Exception as e:
            logger.error(f"Error in image generation route: {str(e)}")
            flash(f'Error generating image: {str(e)}', 'danger')
    
    return render_template('image_generation.html', result=result)

@main.route('/schedule-content', methods=['GET', 'POST'])
def schedule_content_route():
    """Render the content scheduling page and handle form submission."""
    result = None
    
    if request.method == 'POST':
        try:
            content = request.form.get('content')
            platform = request.form.get('platform')
            schedule_time = request.form.get('schedule_time')
            image = request.files.get('image')
            
            image_path = None
            if image and image.filename:
                # Save the image temporarily
                image_path = os.path.join('uploads', image.filename)
                os.makedirs('uploads', exist_ok=True)
                image.save(image_path)
            
            if not all([content, platform, schedule_time]):
                flash('Please fill out all required fields', 'danger')
            else:
                # Convert schedule_time to datetime
                schedule_datetime = datetime.fromisoformat(schedule_time.replace('Z', '+00:00'))
                
                result = agent.schedule_content(
                    content=content,
                    platform=platform,
                    schedule_time=schedule_datetime,
                    image_path=image_path
                )
                flash('Content scheduled successfully!', 'success')
        except Exception as e:
            logger.error(f"Error in schedule content route: {str(e)}")
            flash(f'Error scheduling content: {str(e)}', 'danger')
    
    return render_template('schedule_content.html', result=result)

@main.route('/post-content', methods=['GET', 'POST'])
def post_content_route():
    """Render the content posting page and handle form submission."""
    result = None
    
    if request.method == 'POST':
        try:
            content = request.form.get('content')
            platform = request.form.get('platform')
            image = request.files.get('image')
            
            image_path = None
            if image and image.filename:
                # Save the image temporarily
                image_path = os.path.join('uploads', image.filename)
                os.makedirs('uploads', exist_ok=True)
                image.save(image_path)
            
            if not all([content, platform]):
                flash('Please fill out all required fields', 'danger')
            else:
                result = agent.post_content(
                    content=content,
                    platform=platform,
                    image_path=image_path
                )
                flash('Content posted successfully!', 'success')
        except Exception as e:
            logger.error(f"Error in post content route: {str(e)}")
            flash(f'Error posting content: {str(e)}', 'danger')
    
    return render_template('post_content.html', result=result)

@main.route('/check-engagement', methods=['GET', 'POST'])
def check_engagement_route():
    """Render the engagement checking page and handle form submission."""
    result = None
    
    if request.method == 'POST':
        try:
            platform = request.form.get('platform')
            post_id = request.form.get('post_id')
            
            if not all([platform, post_id]):
                flash('Please fill out all required fields', 'danger')
            else:
                result = agent.check_engagement(
                    platform=platform,
                    post_id=post_id
                )
                flash('Engagement data retrieved successfully!', 'success')
        except Exception as e:
            logger.error(f"Error in check engagement route: {str(e)}")
            flash(f'Error checking engagement: {str(e)}', 'danger')
    
    return render_template('check_engagement.html', result=result)

@main.route('/respond-to-comments', methods=['GET', 'POST'])
def respond_comments_route():
    """Render the comment response page and handle form submission."""
    result = None
    
    if request.method == 'POST':
        try:
            platform = request.form.get('platform')
            post_id = request.form.get('post_id')
            
            if not all([platform, post_id]):
                flash('Please fill out all required fields', 'danger')
            else:
                # Here we would typically retrieve comments and then respond
                # For now, let's use a simplified approach with sample comments
                sample_comments = [
                    {"id": "comment1", "text": "Great post!"},
                    {"id": "comment2", "text": "I have a question about this."}
                ]
                
                result = agent.respond_to_comments(
                    platform=platform,
                    post_id=post_id,
                    comments=sample_comments
                )
                flash('Responses generated successfully!', 'success')
        except Exception as e:
            logger.error(f"Error in respond to comments route: {str(e)}")
            flash(f'Error responding to comments: {str(e)}', 'danger')
    
    return render_template('respond_comments.html', result=result)

@main.route('/run-scheduler')
def run_scheduler():
    """Endpoint to manually trigger the scheduler."""
    try:
        # Here we would typically trigger the scheduler to run
        # For now, we'll just show a message
        flash('Scheduler triggered successfully!', 'success')
    except Exception as e:
        logger.error(f"Error triggering scheduler: {str(e)}")
        flash(f'Error triggering scheduler: {str(e)}', 'danger')
    
    return redirect(url_for('main.index'))

@main.route('/run-monitor')
def run_monitor():
    """Endpoint to manually trigger the monitor."""
    try:
        # Here we would typically trigger the monitor to run
        # For now, we'll just show a message
        flash('Monitor triggered successfully!', 'success')
    except Exception as e:
        logger.error(f"Error triggering monitor: {str(e)}")
        flash(f'Error triggering monitor: {str(e)}', 'danger')
    
    return redirect(url_for('main.index'))