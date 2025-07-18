# SkyQuest Tracker - Troubleshooting Guide

## Common Issues and Solutions

### 1. Python Not Found
**Problem**: `python` command not recognized
**Solution**: 
- Install Python 3.7+ from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation
- Restart your terminal/command prompt after installation

### 2. Flask Not Installed
**Problem**: `ModuleNotFoundError: No module named 'flask'`
**Solution**:
```bash
pip install -r web_requirements.txt
```

### 3. Port Already in Use
**Problem**: `Address already in use` error
**Solution**:
- Check if another application is using port 5001
- Kill the process using the port:
  ```bash
  # Windows
  netstat -ano | findstr :5001
  taskkill /PID <PID> /F
  
  # Linux/Mac
  lsof -i :5001
  kill -9 <PID>
  ```

### 4. Backend API Not Available
**Problem**: Web app shows "API not available" message
**Solution**:
- The web app will run in standalone mode with sample data
- To enable full functionality, start the backend API:
  ```bash
  python enhanced_app.py
  ```

### 5. Template Files Not Found
**Problem**: `TemplateNotFound` error
**Solution**:
- Make sure you're running the web app from the project root directory
- Check that `templates/` and `static/` folders exist
- Verify file permissions

### 6. CSS/JS Files Not Loading
**Problem**: Styles or JavaScript not working
**Solution**:
- Check browser console for 404 errors
- Verify `static/css/style.css` and `static/js/` files exist
- Clear browser cache (Ctrl+F5)

## Quick Start Guide

### Option 1: Web App Only (Recommended for testing)
```bash
# Windows
start_web_only.bat

# Linux/Mac
chmod +x start_web_only.sh
./start_web_only.sh
```

### Option 2: Full Application (API + Web App)
```bash
# Windows
start_multi_page.bat

# Linux/Mac
chmod +x start_multi_page.sh
./start_multi_page.sh
```

### Option 3: Manual Start
```bash
# Install dependencies
pip install -r web_requirements.txt

# Start web app
python web_app.py

# In another terminal, start API (optional)
python enhanced_app.py
```

## Accessing the Application

Once started, the web app will be available at:
- **Landing Page**: http://localhost:5001
- **Recommendations**: http://localhost:5001/recommendations
- **Events**: http://localhost:5001/events
- **About**: http://localhost:5001/about
- **Health Check**: http://localhost:5001/health

## File Structure
```
SkyQuest Tracker/
├── web_app.py              # Main web application
├── enhanced_app.py         # Backend API
├── templates/              # HTML templates
│   ├── landing.html
│   ├── recommendations.html
│   ├── events.html
│   ├── about.html
│   ├── 404.html
│   └── 500.html
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── landing.js
│       ├── recommendations.js
│       ├── events.js
│       └── about.js
├── web_requirements.txt    # Python dependencies
├── start_web_only.bat      # Windows startup (web only)
├── start_web_only.sh       # Linux/Mac startup (web only)
├── start_multi_page.bat    # Windows startup (full app)
└── start_multi_page.sh     # Linux/Mac startup (full app)
```

## System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Browser**: Chrome, Firefox, Safari, or Edge (latest versions)
- **Memory**: 512MB RAM minimum
- **Storage**: 100MB free space

## Performance Tips

1. **Use the web-only mode** for faster startup if you don't need the full API
2. **Clear browser cache** if you experience styling issues
3. **Disable browser extensions** that might interfere with the app
4. **Use a modern browser** for best performance and features

## Getting Help

If you're still experiencing issues:

1. Check the console output for error messages
2. Verify all files are in the correct locations
3. Ensure Python and pip are properly installed
4. Try running the web app in standalone mode first
5. Check the health endpoint: http://localhost:5001/health

## Development Mode

For development, the web app runs with debug mode enabled:
- Automatic reloading on file changes
- Detailed error messages
- Debug console output

To disable debug mode, edit `web_app.py` and change:
```python
app.run(host='0.0.0.0', port=5001, debug=False)
``` 