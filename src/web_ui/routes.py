@main.route('/respond-to-comments', methods=['GET', 'POST'])
def respond_comments_route():
    """Render the comment response page and handle form submission."""
    result = None
    comments = []
    
    if request.method == 'POST':
        try:
            platform = request.form.get('platform')
            post_id = request.form.get('post_id')
            
            if not all([platform, post_id]):
                flash('Please fill out all required fields', 'danger')
            else:
                # Check for comments first
                if monitor:
                    comments_result = monitor.check_for_comments(platform, post_id)
                    if comments_result.get('success', True):
                        comments = comments_result.get('comments', [])
                        
                        if comments:
                            # Generate responses to the comments
                            result = agent.respond_to_comments(
                                platform=platform,
                                post_id=post_id,
                                comments=comments
                            )
                            flash('Responses generated successfully!', 'success')
                        else:
                            flash('No comments found to respond to.', 'info')
                else:
                    # Fallback to sample comments if monitor is not available
                    sample_comments = [
                        {"id": "comment1", "text": "Great post!"},
                        {"id": "comment2", "text": "I have a question about this."}
                    ]
                    
                    comments = sample_comments
                    result = agent.respond_to_comments(
                        platform=platform,
                        post_id=post_id,
                        comments=sample_comments
                    )
                    flash('Responses generated successfully (using sample comments)!', 'success')
        except Exception as e:
            logger.error(f"Error in respond to comments route: {str(e)}")
            flash(f'Error responding to comments: {str(e)}', 'danger')
    
    return render_template('respond_comments.html', result=result, comments=comments)