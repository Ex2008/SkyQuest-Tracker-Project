# SkyQuest Tracker - Web Application

A modern, responsive web interface for the SkyQuest Tracker space events recommendation system. This web application provides an intuitive user interface for getting personalized space event recommendations and exploring cosmic events.

## Features

### 🌟 User Interface
- **Modern Design**: Clean, responsive interface with glassmorphism effects
- **Interactive Forms**: Easy-to-use recommendation form with real-time validation
- **Dynamic Content**: Live loading of events and recommendations
- **Mobile Responsive**: Works perfectly on all device sizes

### 🚀 Core Functionality
- **Personalized Recommendations**: Get AI-powered space event suggestions
- **Event Browsing**: Explore all available space events with filtering
- **Real-time Feedback**: Submit feedback to improve recommendations
- **Event Details**: View comprehensive information about each event

### 🎨 Visual Elements
- **Space Theme**: Beautiful space-themed design with cosmic colors
- **Video Background**: Stunning meteor shower timelapse on hero section
- **Smooth Animations**: Elegant transitions and hover effects
- **Loading States**: Professional loading indicators and spinners

## Quick Start

### Prerequisites
- Python 3.8 or higher
- The SkyQuest Tracker API server running (see main README.md)

### Installation

#### Option 1: Using Startup Scripts (Recommended)

**Windows:**
```bash
web_start.bat
```

**Linux/Mac:**
```bash
chmod +x web_start.sh
./web_start.sh
```

#### Option 2: Manual Setup

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

2. **Install dependencies:**
```bash
pip install -r web_requirements.txt
```

3. **Start the web application:**
```bash
python web_app.py
```

4. **Access the application:**
   - Open your browser and go to `http://localhost:8000`
   - The web interface will be available with full functionality

### Docker Deployment

To run both the API and web application together:

```bash
docker-compose -f docker-compose-web.yml up --build
```

This will start:
- API server on `http://localhost:5000`
- Web application on `http://localhost:8000`

## Project Structure

```
├── web_app.py              # Main Flask web application
├── templates/              # HTML templates
│   ├── index.html         # Main landing page
│   ├── 404.html          # 404 error page
│   └── 500.html          # 500 error page
├── static/                # Static assets
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── app.js        # Frontend JavaScript
├── web_requirements.txt   # Python dependencies
├── web_start.bat         # Windows startup script
├── web_start.sh          # Linux/Mac startup script
├── web_test.py           # Test suite
├── Dockerfile.web        # Docker configuration
└── docker-compose-web.yml # Docker Compose configuration
```

## API Integration

The web application integrates with the SkyQuest Tracker API through the following endpoints:

### Core Endpoints
- `GET /api/events` - Get all events with filtering
- `POST /api/recommend` - Get personalized recommendations
- `GET /api/event-types` - Get available event types
- `GET /api/locations` - Get available locations
- `POST /api/feedback` - Submit user feedback
- `GET /api/stats` - Get API statistics

### Error Handling
- Graceful handling of API failures
- User-friendly error messages
- Automatic retry mechanisms
- Fallback content when API is unavailable

## User Interface Components

### 1. Hero Section
- **Video Background**: Perseids meteor shower timelapse
- **Call-to-Action**: Direct link to recommendations
- **Responsive Design**: Adapts to all screen sizes

### 2. Recommendations Form
- **Event Type Selection**: Dropdown with all available event types
- **Location Selection**: Geographic location preferences
- **Time of Day**: Day/night preference selection
- **Real-time Validation**: Form validation with helpful messages

### 3. Events Grid
- **Filtering Options**: Filter by type, location, and time
- **Event Cards**: Beautiful cards with event details
- **Load More**: Pagination for large event lists
- **Interactive Elements**: Hover effects and click actions

### 4. About Section
- **Feature Highlights**: Key benefits and capabilities
- **Technology Stack**: Information about AI and ML features
- **Visual Icons**: Font Awesome icons for visual appeal

## Testing

Run the comprehensive test suite:

```bash
python web_test.py
```

The test suite covers:
- ✅ Health check endpoint
- ✅ Main page loading
- ✅ All API endpoints
- ✅ Error pages (404, 500)
- ✅ Static file serving
- ✅ Form functionality

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_URL` | `http://localhost:5000/api/v1` | API server URL |
| `PORT` | `8000` | Web server port |
| `FLASK_ENV` | `development` | Flask environment |
| `FLASK_DEBUG` | `False` | Debug mode |

### Customization

#### Styling
- Modify `static/css/style.css` for visual changes
- CSS variables for easy color scheme updates
- Responsive breakpoints for mobile optimization

#### JavaScript
- Edit `static/js/app.js` for functionality changes
- Modular class-based architecture
- Easy to extend with new features

#### Templates
- Update HTML templates in `templates/` directory
- Bootstrap 5 framework for consistent styling
- Font Awesome icons for visual elements

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure the API server is running on port 5000
   - Check network connectivity
   - Verify API_BASE_URL environment variable

2. **Static Files Not Loading**
   - Check file permissions
   - Verify static folder structure
   - Clear browser cache

3. **Port Already in Use**
   - Change PORT environment variable
   - Kill existing processes on port 8000
   - Use different port in startup script

4. **Dependencies Installation Failed**
   - Update pip: `python -m pip install --upgrade pip`
   - Check Python version (3.8+ required)
   - Try installing packages individually

### Debug Mode

Enable debug mode for development:

```bash
export FLASK_DEBUG=True  # Linux/Mac
# or
set FLASK_DEBUG=True     # Windows
```

### Logs

Check application logs for detailed error information:
- Console output during startup
- Browser developer tools for frontend errors
- Network tab for API request issues

## Performance Optimization

### Frontend
- **Lazy Loading**: Images load only when needed
- **Minified Assets**: Optimized CSS and JavaScript
- **Caching**: Browser caching for static files
- **CDN**: External libraries loaded from CDN

### Backend
- **Connection Pooling**: Efficient API request handling
- **Error Caching**: Reduced API calls on failures
- **Response Compression**: Faster data transfer
- **Health Checks**: Proactive monitoring

## Security Features

- **CORS Configuration**: Proper cross-origin resource sharing
- **Input Validation**: Server-side and client-side validation
- **Error Handling**: No sensitive information in error messages
- **HTTPS Ready**: Configured for secure deployment

## Deployment

### Production Deployment

1. **Set production environment:**
```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
```

2. **Use production WSGI server:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 web_app:app
```

3. **Configure reverse proxy (nginx):**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Cloud Deployment

#### Heroku
```bash
# Create Procfile
echo "web: gunicorn web_app:app" > Procfile

# Deploy
git push heroku main
```

#### Docker Cloud
```bash
# Build and push
docker build -f Dockerfile.web -t skyquest-web .
docker push your-registry/skyquest-web
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the main README.md for details.

## Support

For support and questions:
- Check the troubleshooting section
- Review the main README.md for API documentation
- Open an issue on GitHub
- Contact the development team

---

**SkyQuest Tracker Web Application** - Your gateway to the cosmos! 🌌 