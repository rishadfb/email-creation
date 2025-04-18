# AI Agent Assistants

A flexible multi-assistant framework with AI-powered tools for various tasks. Currently includes an Email Assistant that generates personalized marketing emails using Streamlit, Gemini AI, and Jinja2 templating.

## 🌟 Features

### Framework Features

- **Multi-Assistant Architecture**: Easily add new AI assistants with different capabilities
- **Modular Design**: Each assistant manages its own UI, state, and business logic
- **Consistent User Experience**: Common UI patterns across different assistants
- **Extensible State Management**: Each assistant has its own namespaced state

### Email Assistant Features

- **AI-Powered Content Generation**: Uses Google's Gemini AI to create personalized email content
- **Dynamic Image Generation**: Creates custom images for email templates using Imagen 3.0
- **Smart Template Selection**: Automatically selects the best template based on campaign purpose
- **Contact-Based Personalization**: Tailors content based on contact details and company information
- **Live Preview**: Real-time preview of generated emails with interactive editing
- **Modern Email Templates**: Responsive HTML templates with customizable sections

## 🚀 Getting Started

### Prerequisites

- Python 3.12
- PDM (Python dependency manager)
- Google Gemini API key
- Apollo API key (optional, for contact enrichment)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd ai-agent-assistants
```

2. Install dependencies using PDM:

```bash
pdm install
```

3. Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
APOLLO_API_KEY=your_apollo_api_key_here
```

### Running the Application

1. Activate the virtual environment:

```bash
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

2. Start the Streamlit app:

```bash
pdm run python -m streamlit run app.py
```

## 📝 Usage

1. **Select an Assistant**:

   - Choose from available assistants using the dropdown in the sidebar
   - Each assistant provides different functionality

2. **Upload Contacts** (for Email Assistant):

   - Prepare a JSON file with your contacts in the following format:

   ```json
   {
     "contacts": [
       {
         "first_name": "John",
         "last_name": "Doe",
         "job_title": "Software Engineer",
         "company": "Tech Corp",
         "industry": "Technology"
       }
     ]
   }
   ```

   - Upload the file in the main content area

3. **Create Campaign**:

   - Choose from example prompts or write your own campaign description
   - The AI will select an appropriate template and generate personalized content
   - Preview the email with a selected contact
   - Make adjustments as needed

4. **Export**:

   - Download the generated HTML email
   - Use the HTML in your email marketing platform

## 📁 Project Structure

```
ai-agent-assistants/
├── app.py                # Main Streamlit application
├── utils/
│   ├── assistants/       # Assistant implementations
│   │   ├── base.py      # Base Assistant class
│   │   ├── registry.py  # Assistant registry
│   │   └── email_assistant.py # Email Assistant implementation
│   ├── agents/          # AI agents for specific tasks
│   ├── core/            # Core utilities
│   ├── orchestration/   # Process orchestration
│   ├── services/        # External service integrations
│   └── ui/              # UI components
├── templates/           # Email templates organized by type
│   ├── welcome/
│   ├── announcements/
│   └── newsletters/
├── .env                 # Environment variables
└── README.md           # Documentation
```

## Technologies Used

- **Streamlit**: Web interface and chat UI
- **Google Gemini AI**: Content generation and template selection
- **Imagen 3.0**: Image generation for email templates
- **Jinja2**: HTML template processing
- **Python-dotenv**: Environment variable management
- **BeautifulSoup4**: HTML parsing and manipulation
- **PDM**: Python dependency management
- **Object-Oriented Design**: Modular architecture with inheritance and composition

## Security Notes

- Never commit your `.env` file or API keys to version control
- Always validate and sanitize contact data before processing
- Use environment variables for sensitive configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for natural language processing
- Streamlit for the amazing web framework
- The open-source community for inspiration and tools
