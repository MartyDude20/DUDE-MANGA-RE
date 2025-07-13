# DUDE MANGA READER

A modern manga reader application with advanced features for organizing and reading manga from multiple sources.

## Features

### Core Features
- **Multi-Source Support**: Read manga from WeebCentral, Asura Scans, and MangaDex
- **Advanced Search**: Search across all sources with intelligent caching
- **Manga Reader**: High-quality image reader with zoom, navigation, and reading progress tracking
- **User Authentication**: Secure login/register system with password reset functionality
- **Reading Lists**: Create custom reading lists to organize your manga collection
- **Reading Progress**: Track your progress across all manga with detailed statistics
- **Offline Reading**: Download chapters for offline access (coming soon)

### Reading Lists Feature
- **Create Custom Lists**: Organize manga into personalized reading lists
- **Add to Lists**: Easily add manga to reading lists from the manga details page
- **List Management**: Create, edit, and delete reading lists with custom colors and descriptions
- **Quick Access**: View all your reading lists in one place
- **Manga Count**: See how many manga are in each list

### Enhanced Reader Features
- **Zoom Controls**: 0.5x to 3x zoom with smooth transitions
- **Reading Direction**: Toggle between LTR and RTL reading
- **Auto-scroll**: Adjustable speed from 0.5x to 3x
- **Night Mode**: Reduced brightness and contrast for comfortable reading
- **Fullscreen**: Immersive reading mode
- **UI Toggle**: Hide/show reader controls
- **Reading Progress**: Automatic progress tracking and resume functionality

### Performance Features
- **Smart Caching**: Intelligent caching system for faster loading
- **Image Optimization**: Lazy loading and progressive image loading
- **Background Preloading**: Preload chapters for seamless reading
- **Performance Monitoring**: Real-time performance metrics and cache statistics

## Quick Start

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Required Python packages (see requirements.txt)

### Installation
1. Install frontend dependencies:
   ```bash
   npm install
   ```

2. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run database migration:
   ```bash
   cd playwright_service
   python migrate_database.py
   ```

### Starting the Services
Use the provided startup script:
```bash
start_enhanced_services.bat
```

Or start manually:
1. Backend: `cd playwright_service && python app.py`
2. Proxy: `cd proxy && python app.py`
3. Frontend: `npm run dev`

### Access URLs
- **Frontend**: http://localhost:5173
- **Proxy**: http://localhost:3006
- **Backend**: http://localhost:5000

## How to Use Reading Lists

### Adding Manga to Reading Lists
1. Navigate to any manga details page
2. Click the "Add to List" button (green button with plus icon)
3. Select an existing reading list or create a new one
4. The manga will be added to your selected list

### Creating New Reading Lists
1. Click "Add to List" on any manga
2. Click "New List" in the popup
3. Enter a name, description, and choose a color
4. Click "Create List" to save

### Managing Reading Lists
1. Navigate to the Reading Lists page from the main menu
2. View all your created lists
3. Click on any list to view its contents
4. Edit or delete lists as needed

## API Endpoints

### Reading Lists
- `GET /api/reading-lists` - Get user's reading lists
- `POST /api/reading-lists` - Create new reading list
- `POST /api/reading-lists/{id}/manga` - Add manga to list

### Reading Progress
- `GET /api/reading-progress` - Get user's reading progress
- `POST /api/reading-progress` - Update reading progress
- `GET /api/reading-progress/continue` - Get continue reading list

## Architecture

### Frontend
- **React 18** with Vite for fast development
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Axios** for API communication

### Backend
- **Flask** with SQLAlchemy ORM
- **PostgreSQL** database
- **Playwright** for web scraping
- **Redis** for caching (optional)

### Proxy
- **Flask** proxy server for API routing
- **CORS** handling
- **Authentication** forwarding

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.