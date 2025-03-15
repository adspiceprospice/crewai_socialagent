# CrewAI Social Media Agent

A social media agent built with CrewAI that can generate content, schedule posts, and interact with users on LinkedIn and X.com (Twitter).

## Features

- **Content Strategy**: Generate comprehensive social media content strategies based on industry, target audience, and goals.
- **Content Generation**: Create engaging posts, articles, and threads for LinkedIn and X.com.
- **Image Generation**: Generate images using Google's Gemini 2.0 Flash model.
- **Post Scheduling**: Schedule posts for future publication.
- **Engagement Monitoring**: Monitor posts for comments and engagement.
- **Automated Responses**: Generate responses to comments on posts.
- **Memory**: Remember past actions and interactions using CrewAI's memory system.

## Prerequisites

- Python 3.8+
- API keys for:
  - OpenAI (for CrewAI)
  - Google Gemini (for image generation)
  - LinkedIn API
  - Twitter API

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/crewai_socialagent.git
   cd crewai_socialagent
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your API keys and configuration:
     ```
     # API Keys
     OPENAI_API_KEY=your_openai_api_key
     GEMINI_API_KEY=your_gemini_api_key

     # Social Media API Keys
     LINKEDIN_CLIENT_ID=your_linkedin_client_id
     LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
     LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

     TWITTER_API_KEY=your_twitter_api_key
     TWITTER_API_SECRET=your_twitter_api_secret
     TWITTER_ACCESS_TOKEN=your_twitter_access_token
     TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

     # Memory Configuration
     CREWAI_STORAGE_DIR=./memory_storage
     ```

## Usage

### Creating a Content Strategy

```bash
python -m src.main strategy --industry "technology" --audience "software developers" --goals "increase brand awareness" "drive engagement" "generate leads"
```

### Generating Content

```bash
python -m src.main content --topic "artificial intelligence" --platform "linkedin" --type "post"
```

### Generating an Image

```bash
python -m src.main image --prompt "A futuristic city with flying cars and tall skyscrapers"
```

### Scheduling a Post

```bash
python -m src.main schedule --content "Check out our latest blog post on AI advancements!" --platform "linkedin" --time "2023-12-31T12:00:00Z" --image "path/to/image.jpg"
```

### Posting Content Immediately

```bash
python -m src.main post --content "Excited to announce our new product launch!" --platform "twitter" --image "path/to/image.jpg"
```

### Checking Engagement

```bash
python -m src.main engagement --platform "linkedin" --post-id "123456789"
```

### Responding to Comments

```bash
python -m src.main respond --platform "linkedin" --post-id "123456789" --comments-file "path/to/comments.json"
```

## Running the Scheduler

To run the scheduler that will automatically post scheduled content:

```bash
python -m src.scheduler
```

## Running the Monitor

To run the monitor that will check for comments on posts and generate responses:

```bash
python -m src.monitor
```

## Project Structure

```
crewai_socialagent/
├── .env                    # Environment variables
├── README.md               # Project documentation
├── requirements.txt        # Project dependencies
├── src/                    # Source code
│   ├── __init__.py
│   ├── main.py             # Main application
│   ├── scheduler.py        # Scheduler for running scheduled posts
│   ├── monitor.py          # Monitor for checking comments
│   ├── agents/             # Agent definitions
│   │   ├── __init__.py
│   │   ├── social_media_agent.py
│   │   └── tasks.py
│   ├── tools/              # Custom tools
│   │   ├── __init__.py
│   │   ├── gemini_image_tool.py
│   │   ├── linkedin_tool.py
│   │   ├── twitter_tool.py
│   │   └── scheduler_tool.py
│   ├── utils/              # Utility functions
│   │   └── __init__.py
│   └── config/             # Configuration
│       ├── __init__.py
│       └── config.py
├── memory_storage/         # Memory storage directory
├── generated_images/       # Generated images directory
├── comments/               # Comments directory
└── responses/              # Responses directory
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [CrewAI](https://github.com/crewAIInc/crewAI) - Framework for orchestrating role-playing, autonomous AI agents
- [CrewAI Tools](https://github.com/crewAIInc/crewAI-tools) - Tools for CrewAI
- [Google Gemini](https://ai.google.dev/gemini-api) - Multimodal AI model for image generation