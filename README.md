# CrewAI Social Media Agent

A powerful, AI-driven social media management solution built with CrewAI that automates content strategy, creation, scheduling, and engagement across LinkedIn and X.com (Twitter).

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/CrewAI-0.28.0+-orange.svg" alt="CrewAI 0.28.0+">
</div>

## 🚀 Features

- **🧠 Content Strategy Generation**: Create comprehensive, data-driven social media strategies tailored to your industry, audience, and business goals.
- **✍️ Content Creation**: Generate engaging posts, articles, and threads optimized for LinkedIn and X.com with AI-powered content creation.
- **🖼️ Image Generation**: Create compelling visual content using Google's Gemini 2.0 Flash model to accompany your posts.
- **📅 Intelligent Scheduling**: Schedule posts for optimal engagement times with automated publishing.
- **📊 Engagement Monitoring**: Track post performance and audience interaction across platforms.
- **💬 Automated Responses**: Generate contextually relevant responses to comments, increasing engagement and building community.
- **🧠 Memory System**: Leverage CrewAI's memory capabilities to learn from past interactions and improve over time.

## 📋 Prerequisites

- Python 3.8+
- API keys for:
  - OpenAI (for CrewAI)
  - Google Gemini (for image generation)
  - LinkedIn API (client ID, client secret, access token)
  - Twitter API (API key, API secret, access token, access token secret)

## 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/crewai_socialagent.git
   cd crewai_socialagent
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory with the following variables:
   ```
   # API Keys
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_gemini_api_key

   # LinkedIn API Configuration
   LINKEDIN_CLIENT_ID=your_client_id
   LINKEDIN_CLIENT_SECRET=your_client_secret
   LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

   # Twitter API Configuration
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

   # Memory Configuration
   CREWAI_STORAGE_DIR=./memory_storage
   
   # Flask Configuration (for Web UI)
   FLASK_SECRET_KEY=your_secure_random_string
   ```

5. **Verify your setup**:
   ```bash
   python verify_setup.py
   ```

## 🔑 API Authentication

### LinkedIn Authentication

To set up LinkedIn API access:

1. Go to https://www.linkedin.com/developers/apps
2. Click "Create app" and fill in the required information
3. Under "Auth" settings:
   - Add `http://localhost:8000/callback` to the "Authorized redirect URLs"
   - Note your Client ID and Client Secret
4. Add the credentials to your `.env` file:
   ```
   LINKEDIN_CLIENT_ID=your_client_id
   LINKEDIN_CLIENT_SECRET=your_client_secret
   ```
5. Run the LinkedIn OAuth helper script:
   ```bash
   python linkedin_auth.py
   ```
6. Follow the browser prompts to authorize your application
7. The access token will be automatically saved to your `.env` file

### Twitter (X) Authentication

To set up Twitter API access:

1. Go to https://developer.twitter.com/en/portal/projects-and-apps
2. Create a new project and app (or select an existing one)
3. Under "User authentication settings":
   - Enable OAuth 1.0a
   - Set App permissions to "Read and Write"
4. Under "Keys and tokens":
   - Generate "API Key and Secret"
   - Generate "Access Token and Secret"
5. Add the credentials to your `.env` file:
   ```
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
   ```
6. Verify your Twitter credentials:
   ```bash
   python twitter_auth.py
   ```

If you encounter any authentication issues, the helper scripts will provide detailed guidance on how to resolve them.

## 💻 Usage

### Command Line Interface

#### Creating a Content Strategy

```bash
python -m src.main strategy --industry "technology" --audience "software developers" --goals "increase brand awareness" "drive engagement" "generate leads"
```

#### Generating Content

```bash
python -m src.main content --topic "artificial intelligence" --platform "linkedin" --type "post"
```

#### Generating an Image

```bash
python -m src.main image --prompt "A futuristic city with flying cars and tall skyscrapers"
```

#### Scheduling a Post

```bash
python -m src.main schedule --content "Check out our latest blog post on AI advancements!" --platform "linkedin" --time "2023-12-31T12:00:00Z" --image "path/to/image.jpg"
```

#### Posting Content Immediately

```bash
python -m src.main post --content "Excited to announce our new product launch!" --platform "twitter" --image "path/to/image.jpg"
```

#### Checking Engagement

```bash
python -m src.main engagement --platform "linkedin" --post-id "123456789"
```

#### Responding to Comments

```bash
python -m src.main respond --platform "linkedin" --post-id "123456789" --comments-file "path/to/comments.json"
```

### Running the Scheduler

To run the scheduler that will automatically post scheduled content:

```bash
python -m src.scheduler
```

### Running the Monitor

To run the monitor that will check for comments on posts and generate responses:

```bash
python -m src.monitor
```

## 🌐 Web UI

The project includes a modern, responsive web-based user interface for easier interaction with the social media agent. To start the web UI:

```bash
python web_ui.py
```

Then open your browser and navigate to `http://localhost:5000` to access the interface.

The web UI provides the following features:
- Content strategy generation
- Content creation
- Image generation
- Post scheduling
- Immediate posting
- Engagement monitoring
- Comment response generation
- Running the scheduler and monitor

## 🚀 Running the Entire System

To start all components of the system (web UI, scheduler, and monitor) at once, run:

```bash
python run.py
```

This script will:
1. Verify your setup
2. Start the web UI
3. Start the scheduler
4. Start the monitor
5. Monitor all processes and restart them if they crash
6. Gracefully shut down all components when you press Ctrl+C

This is the recommended way to run the system in development mode.

## 📁 Project Structure

```
crewai_socialagent/
├── .env                    # Environment variables
├── README.md               # Project documentation
├── requirements.txt        # Project dependencies
├── linkedin_auth.py        # LinkedIn OAuth helper script
├── twitter_auth.py         # Twitter verification script
├── web_ui.py               # Web UI launcher
├── verify_setup.py         # Setup verification script
├── run.py                  # System launcher script
├── src/                    # Source code
│   ├── __init__.py
│   ├── main.py             # Main application
│   ├── scheduler.py        # Scheduler for running scheduled posts
│   ├── monitor.py          # Monitor for checking comments
│   ├── web_ui.py           # Web UI implementation
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
│   │   ├── __init__.py
│   │   ├── linkedin_auth.py
│   │   └── twitter_auth.py
│   ├── config/             # Configuration
│   │   ├── __init__.py
│   │   └── config.py
│   └── templates/          # Web UI templates
│       ├── base.html
│       ├── index.html
│       └── content_strategy.html
├── memory_storage/         # Memory storage directory
├── generated_images/       # Generated images directory
├── comments/               # Comments directory
└── responses/              # Responses directory
```

## 🔍 Verifying Your Setup

To verify that your environment is set up correctly, run:

```bash
python verify_setup.py
```

This script will check:
- If all required API keys are set in your `.env` file
- If all required packages are installed
- If the project structure is correct

If any issues are found, the script will provide guidance on how to fix them.

## 🛠️ Extending the System

### Adding New Social Media Platforms

To add support for a new social media platform:

1. Create a new tool in `src/tools/` (e.g., `instagram_tool.py`)
2. Implement the necessary API interactions
3. Update the agent and task classes to support the new platform
4. Add the new platform to the web UI

### Enhancing the AI Capabilities

The system uses CrewAI, which allows for easy enhancement of AI capabilities:

1. Modify the agent roles and goals in `src/agents/social_media_agent.py`
2. Add new tasks in `src/agents/tasks.py`
3. Implement new tools as needed

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [CrewAI](https://github.com/crewAIInc/crewAI) - Framework for orchestrating role-playing, autonomous AI agents
- [CrewAI Tools](https://github.com/crewAIInc/crewAI-tools) - Tools for CrewAI
- [Google Gemini](https://ai.google.dev/gemini-api) - Multimodal AI model for image generation
- [Flask](https://flask.palletsprojects.com/) - Web framework for the UI
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework for the UI

---

<div align="center">
  <p>Made with ❤️ by Adrian Tamplaru - <a href="https://ad1x.com">ad1x.com</a> and Claude Sonnet 3.7</p>
</div>