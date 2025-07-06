# Dude Manga

A modern web application for searching and discovering manga from WeebCentral. Built with React frontend, Flask proxy, and Playwright web scraping.

## Features

- 🔍 Search manga by title
- 📱 Responsive dark mode UI
- 🎨 Beautiful card-based layout
- 📖 Detailed manga information
- 🚀 Fast and efficient web scraping

## Architecture

- **Frontend**: React (Port 3005) - Modern UI with dark mode
- **Proxy**: Flask (Port 3006) - API gateway and request handling
- **Scraper**: Playwright (Port 5000) - Web scraping from WeebCentral

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DUDE-MANGA-RE
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**
   ```bash
   playwright install chromium
   ```

4. **Install Node.js dependencies**
   ```bash
   npm install
   ```

5. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your Firecrawl API key:
   ```
   FIRECRAWL_API_KEY=your_firecrawl_api_key_here
   FLASK_PORT=3006
   PLAYWRIGHT_PORT=5000
   REACT_PORT=3005
   ```

## Running the Application

### Option 1: Start all services at once
```bash
python start_services.py
```

### Option 2: Start services individually

1. **Start Playwright service** (Terminal 1)
   ```bash
   cd playwright_service
   python app.py
   ```

2. **Start Flask proxy** (Terminal 2)
   ```bash
   cd proxy
   python app.py
   ```

3. **Start React frontend** (Terminal 3)
   ```bash
   npm start
   ```

## Usage

1. Open your browser and navigate to `http://localhost:3005`
2. Use the search bar to find manga by title
3. Click on any manga card to view detailed information
4. Navigate back to search results using the "Back to Search" button

## API Endpoints

### Flask Proxy (Port 3006)
- `GET /api/search?q=<query>` - Search for manga
- `GET /api/manga/<id>` - Get manga details
- `GET /api/health` - Health check

### Playwright Service (Port 5000)
- `GET /search?q=<query>` - Search WeebCentral
- `GET /manga/<id>` - Get manga details from WeebCentral
- `GET /health` - Health check

## Project Structure

```
DUDE-MANGA-RE/
├── src/                    # React frontend source
│   ├── components/         # React components
│   ├── App.js             # Main app component
│   ├── App.css            # Main styles
│   └── index.js           # App entry point
├── proxy/                  # Flask proxy service
│   └── app.py             # Proxy server
├── playwright_service/     # Playwright scraping service
│   └── app.py             # Scraping server
├── public/                 # Static files
├── package.json           # Node.js dependencies
├── requirements.txt       # Python dependencies
├── start_services.py      # Service startup script
└── README.md              # This file
```

## Development

### Frontend Development
- The React app uses modern hooks and functional components
- Styled with CSS custom properties for easy theming
- Responsive design with mobile-first approach

### Backend Development
- Flask proxy handles CORS and request forwarding
- Playwright service manages web scraping with headless browser
- Error handling and logging throughout the stack

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Check if ports 3005, 3006, or 5000 are already occupied
   - Kill existing processes or change ports in `.env`

2. **Playwright browser issues**
   - Run `playwright install chromium` to ensure browser is installed
   - Check if you have sufficient system resources

3. **API connection errors**
   - Ensure all services are running
   - Check firewall settings
   - Verify environment variables are set correctly

### Debug Mode

To run services in debug mode, set the `DEBUG` environment variable:
```bash
export DEBUG=1
python start_services.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Please respect WeebCentral's terms of service and robots.txt when scraping their content.

## Support

For issues and questions, please open an issue on the repository. 


## HOW TO ENTER PYTHON ENV

venv\Scripts\Activate.ps1 