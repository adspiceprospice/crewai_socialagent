import os
import sys
import json
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the main functions
from src.main import (
    create_content_strategy,
    generate_content,
    generate_image,
    schedule_content,
    post_content,
    check_engagement,
    respond_to_comments
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-key-for-testing')
csrf = CSRFProtect(app)

# Create templates directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'), exist_ok=True)

# Create static directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'), exist_ok=True)

# Forms
class ContentStrategyForm(FlaskForm):
    industry = StringField('Industry', validators=[DataRequired()])
    audience = StringField('Target Audience', validators=[DataRequired()])
    goals = TextAreaField('Business Goals', validators=[DataRequired()])
    submit = SubmitField('Generate Strategy')

class ContentGenerationForm(FlaskForm):
    topic = StringField('Topic', validators=[DataRequired()])
    platform = SelectField('Platform', choices=[('linkedin', 'LinkedIn'), ('twitter', 'Twitter')], validators=[DataRequired()])
    submit = SubmitField('Generate Content')

class ImageGenerationForm(FlaskForm):
    prompt = TextAreaField('Image Prompt', validators=[DataRequired()])
    submit = SubmitField('Generate Image')

class ScheduleContentForm(FlaskForm):
    topic = StringField('Topic', validators=[DataRequired()])
    platform = SelectField('Platform', choices=[('linkedin', 'LinkedIn'), ('twitter', 'Twitter')], validators=[DataRequired()])
    schedule_time = StringField('Schedule Time (YYYY-MM-DD HH:MM)', validators=[DataRequired()])
    submit = SubmitField('Schedule Content')

class PostContentForm(FlaskForm):
    topic = StringField('Topic', validators=[DataRequired()])
    platform = SelectField('Platform', choices=[('linkedin', 'LinkedIn'), ('twitter', 'Twitter')], validators=[DataRequired()])
    submit = SubmitField('Post Now')

class CheckEngagementForm(FlaskForm):
    platform = SelectField('Platform', choices=[('linkedin', 'LinkedIn'), ('twitter', 'Twitter')], validators=[DataRequired()])
    submit = SubmitField('Check Engagement')

class RespondCommentsForm(FlaskForm):
    comments_file = StringField('Comments File Path', validators=[DataRequired()])
    submit = SubmitField('Generate Responses')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/content-strategy', methods=['GET', 'POST'])
def content_strategy():
    form = ContentStrategyForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = create_content_strategy(
                industry=form.industry.data,
                audience=form.audience.data,
                goals=form.goals.data
            )
            flash('Content strategy generated successfully!', 'success')
        except Exception as e:
            flash(f'Error generating content strategy: {str(e)}', 'danger')
    
    return render_template('content_strategy.html', form=form, result=result)

@app.route('/generate-content', methods=['GET', 'POST'])
def content_generation():
    form = ContentGenerationForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = generate_content(
                topic=form.topic.data,
                platform=form.platform.data
            )
            flash('Content generated successfully!', 'success')
        except Exception as e:
            flash(f'Error generating content: {str(e)}', 'danger')
    
    return render_template('generate_content.html', form=form, result=result)

@app.route('/generate-image', methods=['GET', 'POST'])
def image_generation():
    form = ImageGenerationForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = generate_image(prompt=form.prompt.data)
            flash('Image generated successfully!', 'success')
        except Exception as e:
            flash(f'Error generating image: {str(e)}', 'danger')
    
    return render_template('generate_image.html', form=form, result=result)

@app.route('/schedule-content', methods=['GET', 'POST'])
def schedule_content_route():
    form = ScheduleContentForm()
    result = None
    
    if form.validate_on_submit():
        try:
            # Parse the schedule time
            schedule_time = datetime.strptime(form.schedule_time.data, '%Y-%m-%d %H:%M')
            
            result = schedule_content(
                topic=form.topic.data,
                platform=form.platform.data,
                time=schedule_time.isoformat()
            )
            flash('Content scheduled successfully!', 'success')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD HH:MM', 'danger')
        except Exception as e:
            flash(f'Error scheduling content: {str(e)}', 'danger')
    
    return render_template('schedule_content.html', form=form, result=result)

@app.route('/post-content', methods=['GET', 'POST'])
def post_content_route():
    form = PostContentForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = post_content(
                topic=form.topic.data,
                platform=form.platform.data
            )
            flash('Content posted successfully!', 'success')
        except Exception as e:
            flash(f'Error posting content: {str(e)}', 'danger')
    
    return render_template('post_content.html', form=form, result=result)

@app.route('/check-engagement', methods=['GET', 'POST'])
def check_engagement_route():
    form = CheckEngagementForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = check_engagement(platform=form.platform.data)
            flash('Engagement checked successfully!', 'success')
        except Exception as e:
            flash(f'Error checking engagement: {str(e)}', 'danger')
    
    return render_template('check_engagement.html', form=form, result=result)

@app.route('/respond-comments', methods=['GET', 'POST'])
def respond_comments_route():
    form = RespondCommentsForm()
    result = None
    
    if form.validate_on_submit():
        try:
            result = respond_to_comments(comments_file=form.comments_file.data)
            flash('Responses generated successfully!', 'success')
        except Exception as e:
            flash(f'Error generating responses: {str(e)}', 'danger')
    
    return render_template('respond_comments.html', form=form, result=result)

@app.route('/run-scheduler')
def run_scheduler():
    try:
        # Run the scheduler in a subprocess
        subprocess.Popen([sys.executable, 'src/scheduler.py'])
        flash('Scheduler started successfully!', 'success')
    except Exception as e:
        flash(f'Error starting scheduler: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/run-monitor')
def run_monitor():
    try:
        # Run the monitor in a subprocess
        subprocess.Popen([sys.executable, 'src/monitor.py'])
        flash('Monitor started successfully!', 'success')
    except Exception as e:
        flash(f'Error starting monitor: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 