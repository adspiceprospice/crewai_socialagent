# CrewAI Social Media Agent

A powerful, AI-driven social media management solution built with CrewAI that automates content strategy, creation, scheduling, and engagement across LinkedIn and X.com (Twitter).

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/CrewAI-0.28.0+-orange.svg" alt="CrewAI 0.28.0+">
</div>

## 🚀 Features

- **🧠 Content Strategy Generation**: Create comprehensive, data-driven social media strategies tailored to your industry, audience, and business goals.
- **📝 Content Plan Creation**: Generate multi-platform content plans with multiple posts scheduled over days, weeks, or months based on your strategy.
- **✍️ Content Creation**: Generate engaging posts, articles, and threads optimized for LinkedIn and X.com with AI-powered content creation.
- **🖼️ Image Generation**: Create compelling visual content using Google's Gemini 2.0 Flash model to accompany your posts.
- **📅 Intelligent Scheduling**: Schedule posts for optimal engagement times with automated publishing.
- **📊 Engagement Monitoring**: Track post performance and audience interaction across platforms.
- **💬 Automated Responses**: Generate contextually relevant responses to comments, increasing engagement and building community.
- **🧠 Memory System**: Leverage CrewAI's memory capabilities to learn from past interactions and improve over time.

## 📋 Prerequisites

- Python 3.9+
- API keys for:
  - OpenAI (for CrewAI and direct content generation)
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
   python src/utils/linkedin_auth.py
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
   python src/utils/twitter_auth.py
   ```

If you encounter any authentication issues, the helper scripts will provide detailed guidance on how to resolve them.

## 💻 Usage

### Web UI (Recommended)

The project includes a modern, responsive web-based user interface for easier interaction with the social media agent. To start the web UI:

```bash
python web_ui.py
```

Then open your browser and navigate to `http://localhost:5001` to access the interface.

The web UI provides the following features:
- Content strategy generation
- Content plan creation and scheduling
- Individual content creation
- Image generation
- Post scheduling
- Immediate posting
- Engagement monitoring
- Comment response generation
- Running the scheduler and monitor

### Content Planning Workflow

The system offers a streamlined workflow for content creation:

1. **Generate a Content Strategy**:
   - Enter your industry, target audience, and goals
   - The system generates a comprehensive content strategy with themes, content types, posting schedules, and more

2. **Create a Content Plan**:
   - From the strategy page, click "Generate Content Plan"
   - Select your desired time period (1 week, 2 weeks, 1 month, 3 months)
   - Choose how many content pieces to generate
   - Select which platforms to generate content for (LinkedIn, Twitter/X)
   - The system creates a complete content calendar with multiple posts distributed over time

3. **Review and Schedule**:
   - Review all generated content pieces in a table
   - Edit any individual content pieces as needed
   - Schedule individual posts or all posts at once

This approach enables you to quickly go from strategy to a complete content calendar with minimal effort.

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

This is the recommended way to run the system in development or production mode.

## 📋 Project Vision

### Core Mission

The CrewAI Social Media Agent aims to democratize access to professional social media management by providing an AI-powered solution that handles the entire content lifecycle - from strategy to engagement. The system is designed to help businesses, entrepreneurs, and content creators maintain a consistent and engaging social media presence without the need for dedicated social media teams or expensive agency services.

### Long-Term Goals

1. **Autonomous Social Media Management**: Create a fully autonomous system that can operate with minimal human supervision, making intelligent decisions about content strategy, creation, and engagement.

2. **Multi-Platform Support**: Expand beyond LinkedIn and Twitter to support all major social media platforms including Instagram, Facebook, TikTok, and emerging platforms.

3. **Advanced Analytics**: Develop comprehensive analytics capabilities that provide actionable insights into social media performance and ROI.

4. **Content Personalization**: Implement advanced personalization algorithms that target specific audience segments based on user behavior and engagement patterns.

5. **Ecosystem Integration**: Create integrations with other marketing tools including CRM systems, email marketing platforms, and web analytics solutions.

### Development Philosophy

The project follows these guiding principles:

- **User-Centric Design**: All features are developed with the end user in mind, prioritizing ease of use and accessibility.
- **Modular Architecture**: The system is built with a modular design to allow for easy extension and customization.
- **Ethical AI Use**: The AI components prioritize ethical content generation, avoiding manipulative tactics and promoting authentic engagement.
- **Performance Optimization**: All components are designed for optimal performance, minimizing resource usage while maximizing capabilities.
- **Continuous Improvement**: The system is designed to learn and improve over time based on user feedback and performance data.

## 🏗️ Project Architecture

### System Overview

The CrewAI Social Media Agent is built on a modular architecture that separates concerns and allows for independent development and scaling of different components. The system consists of three main layers:

1. **Interface Layer**: Web UI and command-line interfaces that allow users to interact with the system.
2. **Application Layer**: Core business logic including agent behaviors, content generation, and scheduling.
3. **Integration Layer**: Tools and connectors for external services including social media APIs and AI providers.

### Component Diagram

```
╔════════════════════════════════════════╗
║              Interface Layer            ║
╠════════════════════════════════════════╣
║                                         ║
║    ┌──────────┐         ┌──────────┐   ║
║    │  Web UI  │         │    CLI   │   ║
║    └────┬─────┘         └────┬─────┘   ║
║         │                    │         ║
╚═════════│════════════════════│═════════╝
          │                    │
          ▼                    ▼
╔═════════════════════════════════════════╗
║             Application Layer            ║
╠═════════════════════════════════════════╣
║                                          ║
║    ┌─────────────────────────────────┐  ║
║    │       Social Media Agent         │  ║
║    └───────────────┬─────────────────┘  ║
║                    │                    ║
║    ┌───────────────┼───────────────┐    ║
║    │               │               │    ║
║    ▼               ▼               ▼    ║
║ ┌─────────┐  ┌──────────┐  ┌──────────┐ ║
║ │Scheduler│  │ Monitor  │  │ Strategy │ ║
║ └─────────┘  └──────────┘  └──────────┘ ║
║                                          ║
╚══════════════════│════════════════════════╝
                   │
                   ▼
╔═════════════════════════════════════════╗
║             Integration Layer            ║
╠═════════════════════════════════════════╣
║                                          ║
║  ┌──────────┐ ┌──────────┐ ┌──────────┐ ║
║  │ LinkedIn │ │ Twitter  │ │ OpenAI   │ ║
║  │  Tool    │ │  Tool    │ │  Client  │ ║
║  └──────────┘ └──────────┘ └──────────┘ ║
║                                          ║
║  ┌──────────┐ ┌──────────┐ ┌──────────┐ ║
║  │ Gemini   │ │ Scheduler│ │ Storage  │ ║
║  │ Tool     │ │  Tool    │ │  Client  │ ║
║  └──────────┘ └──────────┘ └──────────┘ ║
║                                          ║
╚══════════════════════════════════════════╝
```

### Key Components

1. **Social Media Agent**:
   - Serves as the core orchestrator for all social media operations
   - Manages tool selection and execution based on user requirements
   - Implements direct OpenAI integration for content generation

2. **Tools Layer**:
   - **LinkedIn Tool**: Handles all LinkedIn API interactions
   - **Twitter Tool**: Manages all Twitter/X.com API operations
   - **Gemini Image Tool**: Generates images using Google's Gemini model
   - **Scheduler Tool**: Manages scheduling and execution of timed posts

3. **Web UI**:
   - Modern, responsive interface built with Flask and Tailwind CSS
   - Provides form-based interfaces for all system capabilities
   - Implements real-time feedback for user operations

4. **Schedulers and Monitors**:
   - Background processes that handle scheduled tasks
   - Monitor engagement and trigger responses
   - Implement fault tolerance and recovery mechanisms

### Data Flow

1. **Content Strategy Creation**:
   - User inputs industry, target audience, and goals
   - OpenAI generates comprehensive content strategy
   - Strategy is rendered on web UI or returned via CLI

2. **Content Plan Creation**:
   - User selects time period, content count, and platforms
   - System generates multiple content pieces distributed over time
   - Content is displayed in a table for review and scheduling

3. **Content Generation**:
   - User provides topic, platform, and content type
   - OpenAI creates optimized content for the specified platform
   - Content is stored and optionally scheduled or posted immediately

4. **Engagement Monitoring**:
   - Monitor periodically checks posts for new engagements
   - When new comments are detected, they're processed for response
   - AI generates contextually appropriate responses

## 📁 Project Structure

```
crewai_socialagent/
├── .env                    # Environment variables
├── README.md               # Project documentation
├── requirements.txt        # Project dependencies
├── run.py                  # System launcher script
├── verify_setup.py         # Setup verification script
├── web_ui.py               # Web UI launcher
├── src/                    # Source code
│   ├── __init__.py
│   ├── main.py             # CLI entrypoint
│   ├── scheduler.py        # Scheduled posts service
│   ├── monitor.py          # Engagement monitor service
│   ├── agents/             # Agent definitions
│   │   ├── __init__.py
│   │   ├── social_media_agent.py
│   │   └── content_strategy_agent.py
│   ├── tools/              # Custom tools
│   │   ├── __init__.py
│   │   ├── linkedin_tool.py
│   │   ├── twitter_tool.py
│   │   ├── gemini_image_tool.py
│   │   └── scheduler_tool.py
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   ├── linkedin_auth.py
│   │   └── twitter_auth.py
│   ├── web_ui/             # Web interface
│       ├── __init__.py
│       ├── routes.py
│       └── templates/
│           ├── base.html
│           ├── index.html
│           ├── content_strategy.html
│           ├── execute_content_plan.html
│           └── ...
└── memory_storage/         # CrewAI memory storage
```

## 🧩 Extensibility

The CrewAI Social Media Agent is designed to be easily extensible. To add support for new platforms or features:

1. **Adding New Social Media Platforms**:
   - Create a new tool class in `src/tools/` that implements the required API interactions
   - Add the tool to the `SocialMediaAgent` initialization in `social_media_agent.py`
   - Update the web UI to include the new platform options

2. **Adding New Content Types**:
   - Extend the content generation prompts in the `SocialMediaAgent` class
   - Update the web UI to include the new content type options

3. **Adding New Capabilities**:
   - Implement new methods in the `SocialMediaAgent` class
   - Add corresponding routes in the web UI
   - Update the CLI to expose the new capabilities

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Created by Adrian Tamplaru (ad1x.com) with assistance from Claude Sonnet 3.7*