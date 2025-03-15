@main.route('/schedule-content', methods=['GET', 'POST'])
def schedule_content_route():
    """Render the content scheduling page and handle form submission."""
    result = None
    scheduled_posts = []
    
    # Get all scheduled posts
    if scheduler_tool:
        posts_result = scheduler_tool.get_scheduled_posts()
        if posts_result.get('success', False):
            scheduled_posts = posts_result.get('scheduled_posts', [])
            # Sort by schedule time
            scheduled_posts.sort(key=lambda x: x.get('schedule_time', ''))
    
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
                
                # Refresh the scheduled posts list
                if scheduler_tool:
                    posts_result = scheduler_tool.get_scheduled_posts()
                    if posts_result.get('success', False):
                        scheduled_posts = posts_result.get('scheduled_posts', [])
                        # Sort by schedule time
                        scheduled_posts.sort(key=lambda x: x.get('schedule_time', ''))
                
                flash('Content scheduled successfully!', 'success')
        except Exception as e:
            logger.error(f"Error in schedule content route: {str(e)}")
            flash(f'Error scheduling content: {str(e)}', 'danger')
    
    return render_template('schedule_content.html', result=result, scheduled_posts=scheduled_posts)