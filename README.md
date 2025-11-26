# 🧬 NEXUS AI - Multi-User Chatbot with LangGraph

A production-ready AI chatbot application with multi-user authentication, persistent conversation history, and a futuristic cyberpunk UI. Built with Streamlit, LangGraph, and SQLite.

## ✨ Features

- **🔐 Multi-User Authentication**: Secure login and registration system with password hashing
- **💬 Persistent Chat History**: Conversations are saved and linked to user accounts
- **🔄 Session Persistence**: Stay logged in even after page refresh
- **🗑️ Chat Management**: Create, view, and delete conversation threads
- **🎨 Futuristic UI**: Cyberpunk-themed interface with glassmorphism effects
- **⚡ Real-time Streaming**: AI responses stream in real-time for better UX
- **🧠 LangGraph Integration**: Advanced conversation state management

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- An OpenRouter API key (for LLM access)

### Installation

1. **Clone the repository** (or navigate to your project directory):
   ```bash
   cd "d:\ChatBot 2"
   ```

2. **Activate the virtual environment**:
   ```powershell
   # Windows PowerShell
   .\myenv\Scripts\Activate.ps1
   
   # Windows CMD
   myenv\Scripts\activate.bat
   
   # Linux/Mac
   source myenv/bin/activate
   ```

3. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your environment**:
   - Create a `.env` file in the root directory
   - Add your OpenRouter API key:
     ```
     OPENROUTER_API_KEY=your_api_key_here
     ```

### Running the Application

Run the Streamlit app from the project root:

```bash
streamlit run src/app.py
```

The application will open in your default browser at `http://localhost:8501`

## 👤 Demo Credentials

A test user account is pre-configured for quick testing:

- **Username**: `testuser`
- **Password**: `password123`

You can also create your own account using the registration form.

## 📁 Project Structure

```
ChatBot 2/
├── src/
│   ├── app.py                 # Main Streamlit application
│   ├── backend/
│   │   └── chatbot.py         # LangGraph chatbot logic
│   ├── utils/
│   │   └── database.py        # Database utilities & auth
│   └── styles/
│       └── main.css           # Custom CSS styling
├── chatbot.db                 # SQLite database (auto-created)
├── chatbot.db-shm             # SQLite WAL mode file (auto-generated)
├── chatbot.db-wal             # SQLite WAL mode file (auto-generated)
├── .env                       # Environment variables (create this)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: LangGraph, LangChain
- **Database**: SQLite
- **LLM Provider**: OpenRouter (OpenAI compatible)
- **Authentication**: Custom implementation with SHA-256 hashing
- **Styling**: Custom CSS with cyberpunk theme

## 📖 Usage Guide

### Creating an Account

1. Launch the app and navigate to the **REGISTER** tab
2. Enter a unique username and password
3. Click **REGISTER OPERATOR**
4. Switch to the **LOGIN** tab to sign in

### Starting a Conversation

1. After logging in, click **NEW CHAT** in the sidebar
2. Type your message in the input box at the bottom
3. AI responses will stream in real-time

### Managing Chats

- **View Chats**: All your conversations appear in the sidebar
- **Switch Chats**: Click any chat ID to load that conversation
- **Delete Chats**: Click the **✖** button next to any chat to remove it
- **Logout**: Click **TERMINATE SESSION** to log out

## 🔧 Configuration

### Database Path

The application uses `chatbot.db` in the root directory. This is automatically created on first run.

### Environment Variables

Create a `.env` file with:

```env
OPENROUTER_API_KEY=your_api_key_here
```

### LLM Model

The default model is `gpt-4o-mini` via OpenRouter. To change it, edit `src/backend/chatbot.py`:

```python
llm = ChatOpenAI(
    model="gpt-4o-mini",  # Change this to any OpenRouter model
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)
```

## 🎨 UI Customization

The UI theme can be customized in `src/styles/main.css`. Key variables:

```css
:root {
    --bg-color: #020617;           /* Background */
    --accent-color: #06b6d4;       /* Primary accent (cyan) */
    --secondary-accent: #8b5cf6;   /* Secondary accent (violet) */
    --text-primary: #f1f5f9;       /* Text color */
    --glass-bg: rgba(15, 23, 42, 0.6);  /* Glass effect */
}
```

## 🐛 Troubleshooting

### "Module not found" errors
Make sure your virtual environment is activated and all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Database errors
If you encounter database issues, delete `chatbot.db` and restart the app. The database will be recreated automatically.

### API errors
Verify your `.env` file exists and contains a valid `OPENROUTER_API_KEY`.

### CSS not loading
Ensure you're running the app from the root directory (`d:\ChatBot 2`), not from the `src` folder.

## 🔒 Security Notes

**⚠️ WARNING**: This is a development project. For production use:

1. Replace SHA-256 password hashing with bcrypt or argon2
2. Implement session expiration and refresh tokens
3. Add HTTPS/SSL encryption
4. Implement rate limiting
5. Add CSRF protection
6. Use environment-based configuration
7. Add comprehensive input validation

See `PROJECT_ANALYSIS.md` for a detailed security audit.

## 📝 License

This project is provided as-is for educational and portfolio purposes.

## 🤝 Contributing

This is a personal portfolio project, but suggestions are welcome! Feel free to open issues or submit pull requests.

## 📧 Support

For issues or questions, please check the troubleshooting section or create an issue in the repository.

---

**Developed with** ⚡ **by** Shubh Agrawal

**Built using**: Streamlit • LangGraph • LangChain • SQLite • OpenRouter
