# SkyQuest Tracker - Web Application

A beautiful, modern web application for tracking space events, meteor showers, eclipses, and cosmic phenomena. Built with Flask, featuring a responsive design and interactive user experience.

## 🚀 Quick Start

### Option 1: Web App Only (Recommended)
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

### Option 3: Manual Installation
```bash
# Install dependencies
pip install -r web_requirements.txt

# Start web app
python web_app.py
```

## 🌟 Features

### Multi-Page Application
- **Landing Page**: Beautiful hero section with animated background
- **Recommendations**: AI-powered event recommendations
- **Events**: Browse and filter space events
- **About**: Information about the project and technology stack

### Visual Enhancements
- ✨ Animated particle effects
- 🎥 Video background with meteor shower timelapse
- 🌈 Gradient animations and glow effects
- 📱 Fully responsive design
- 🎨 Modern glassmorphism UI
- ⚡ Smooth page transitions

### Interactive Elements
- 🔍 Real-time event filtering
- 📊 Dynamic statistics counters
- 🎯 Personalized recommendations
- 📅 Event calendar integration
- 🔔 Smart notifications system

## 🛠️ Technology Stack

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Advanced animations and effects
- **JavaScript**: Interactive functionality
- **Bootstrap 5**: Responsive framework
- **Font Awesome**: Icon library
- **Google Fonts**: Typography (Orbitron, Exo 2)

### Backend
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Requests**: HTTP library for API calls

### Design Features
- **Glassmorphism**: Modern glass-like effects
- **Particle System**: Animated background particles
- **Gradient Animations**: Dynamic color transitions
- **Responsive Grid**: Mobile-first design
- **Smooth Scrolling**: Enhanced navigation

## 📁 File Structure

```
web_app/
├── web_app.py              # Main Flask application
├── templates/              # HTML templates
│   ├── landing.html        # Landing page
│   ├── recommendations.html # Recommendations page
│   ├── events.html         # Events page
│   ├── about.html          # About page
│   ├── 404.html           # Error page
│   └── 500.html           # Error page
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   └── js/
│       ├── landing.js     # Landing page scripts
│       ├── recommendations.js # Recommendations scripts
│       ├── events.js      # Events page scripts
│       └── about.js       # About page scripts
├── web_requirements.txt    # Python dependencies
├── start_web_only.bat      # Windows startup (web only)
├── start_web_only.sh       # Linux/Mac startup (web only)
├── start_multi_page.bat    # Windows startup (full app)
├── start_multi_page.sh     # Linux/Mac startup (full app)
└── test_web_app.py        # Test script
```

## 🌐 Access Points

Once started, the application is available at:

- **Landing Page**: http://localhost:5001
- **Recommendations**: http://localhost:5001/recommendations
- **Events**: http://localhost:5001/events
- **About**: http://localhost:5001/about
- **Health Check**: http://localhost:5001/health

## 🎨 Design System

### Color Palette
- **Primary**: `#66fcf1` (Cyan)
- **Secondary**: `#45a29e` (Teal)
- **Dark**: `#1f2833` (Navy)
- **Darker**: `#0b0c10` (Space Black)
- **Accent Purple**: `#7f7fd5`
- **Accent Pink**: `#ff6b9d`

### Typography
- **Headings**: Orbitron (Monospace)
- **Body**: Exo 2 (Sans-serif)
- **Icons**: Font Awesome

### Animations
- **Fade In**: Smooth element appearance
- **Float**: Particle movement
- **Glow**: Interactive hover effects
- **Pulse**: Attention-grabbing elements
- **Slide**: Page transitions

## 🔧 Configuration

### Environment Variables
```bash
# API Base URL (optional)
API_BASE_URL=http://localhost:5000/api/v1
```

### Standalone Mode
The web app can run independently without the backend API, providing sample data for demonstration purposes.

## 🧪 Testing

Run the test script to verify everything is working:

```bash
python test_web_app.py
```

This will test:
- ✅ Health check endpoint
- ✅ All page routes
- ✅ API endpoints (with fallback data)
- ✅ Responsive design
- ✅ JavaScript functionality

## 🐛 Troubleshooting

### Common Issues

1. **Python not found**: Install Python 3.7+ and add to PATH
2. **Flask not installed**: Run `pip install -r web_requirements.txt`
3. **Port in use**: Kill process using port 5001
4. **Template errors**: Check file permissions and paths
5. **CSS not loading**: Clear browser cache (Ctrl+F5)

### Debug Mode
The app runs in debug mode by default. To disable:
```python
app.run(host='0.0.0.0', port=5001, debug=False)
```

## 📱 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 🚀 Performance

- **Lightweight**: Minimal dependencies
- **Fast Loading**: Optimized assets
- **Responsive**: Mobile-first design
- **Accessible**: WCAG compliant
- **SEO Friendly**: Meta tags and structured data

## 🔮 Future Enhancements

- [ ] Real-time notifications
- [ ] User authentication
- [ ] Event calendar integration
- [ ] Social sharing features
- [ ] Dark/light theme toggle
- [ ] Progressive Web App (PWA)
- [ ] Offline functionality
- [ ] Multi-language support

## 📄 License

This project is part of the SkyQuest Tracker application suite.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting guide
2. Review the test script output
3. Verify all dependencies are installed
4. Ensure proper file permissions

---

**SkyQuest Tracker** - Your gateway to the cosmos! 🌌 