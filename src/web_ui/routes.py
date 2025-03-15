
@main.route('/publish-post/<post_id>')
def publish_post(post_id):
    """Endpoint to publish a scheduled post immediately."""
    try:
        # Get the scheduled post
        if scheduler_tool:
            # Get all scheduled posts
            all_posts = scheduler_tool.get_scheduled_posts()
            
            if all_posts.get('success', False):
                # Find the post with the given ID
                post_to_publish = None
                for post in all_posts.get('scheduled_posts', []):
                    if post.get('id') == post_id:
                        post_to_publish = post
                        break
                
                if post_to_publish:
                    # Log post details for debugging
                    logger.info(f"Attempting to publish post: {post_id}, Platform: {post_to_publish.get('platform')}")
                    
                    # Publish the post immediately
                    result = agent.post_content(
                        content=post_to_publish.get('content'),
                        platform=post_to_publish.get('platform'),
                        image_path=post_to_publish.get('image_path')
                    )
                    
                    # Log the result for debugging
                    logger.info(f"Publish result: {result}")
                    
                    if result.get('success', False):
                        # Remove the post from the schedule
                        cancel_result = scheduler_tool.cancel_scheduled_post(post_id)
                        
                        if cancel_result.get('success', False):
                            flash('Post published and removed from schedule successfully!', 'success')
                        else:
                            flash('Post published but could not be removed from schedule.', 'warning')
                    else:
                        flash(f'Error publishing post: {result.get("error", "Unknown error")}', 'danger')
                else:
                    flash(f'Post with ID {post_id} not found', 'danger')
            else:
                flash('Error getting scheduled posts', 'danger')
        else:
            flash('Scheduler tool not available', 'danger')
    except Exception as e:
        logger.error(f"Error publishing post immediately: {str(e)}")
        flash(f'Error publishing post: {str(e)}', 'danger')
    
    return redirect(url_for('main.schedule_content_route'))
