# Progress Indicators Implementation Guide

## 🎯 **Quick Start**

### **Basic Usage**
```python
from sources.weebcentral_optimized import ProgressCallback

# Create progress callback
progress = ProgressCallback()

# Use in search
results = search(page, query, progress)

# Use in details
details = get_details(page, manga_id, progress)

# Use in images
images = get_chapter_images(page, chapter_url, progress)
```

## 🔄 **Progress Callback System**

### **Core Methods**
```python
class ProgressCallback:
    def add_step(self, step: str)           # Add new step to track
    def update(self, step: str, progress: float, message: str = "")  # Update progress
    def complete_step(self, step: str, message: str = "")           # Mark step complete
```

### **Custom Callback Example**
```python
class CustomProgressCallback(ProgressCallback):
    def update(self, step: str, progress: float, message: str = ""):
        # Your custom progress handling
        print(f"Step: {step}, Progress: {progress:.1%}, Message: {message}")
        super().update(step, progress, message)
```

## 🎨 **Visual Progress Indicators**

### **Console Progress Bar**
```python
class ConsoleProgressCallback(ProgressCallback):
    def update(self, step: str, progress: float, message: str = ""):
        # Create progress bar
        bar_length = 20
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Color coding
        if progress < 0.3:
            color = "🔴"  # Red for early stages
        elif progress < 0.7:
            color = "🟡"  # Yellow for middle stages
        else:
            color = "🟢"  # Green for completion
        
        print(f"{color} {step.upper():<10} [{bar}] {progress:>6.1%} - {message}")
```

### **Web UI Progress Bar**
```javascript
// React component example
const ProgressBar = ({ step, progress, message }) => {
    const getColor = (progress) => {
        if (progress < 0.3) return '#ef4444';  // Red
        if (progress < 0.7) return '#f59e0b';  // Yellow
        return '#10b981';  // Green
    };
    
    return (
        <div className="progress-container">
            <div className="progress-header">
                <span className="step-name">{step}</span>
                <span className="progress-percent">{Math.round(progress * 100)}%</span>
            </div>
            <div className="progress-bar">
                <div 
                    className="progress-fill"
                    style={{
                        width: `${progress * 100}%`,
                        backgroundColor: getColor(progress)
                    }}
                />
            </div>
            <div className="progress-message">{message}</div>
        </div>
    );
};
```

## 📊 **Progress Steps**

### **Search Process**
```python
# 0% - Starting search
progress.update("search", 0.0, "Starting search...")

# 20% - Navigating
progress.update("search", 0.2, "Navigating to search page...")

# 40% - Waiting for content
progress.update("search", 0.4, "Waiting for content to load...")

# 60% - Extracting results
progress.update("search", 0.6, "Extracting search results...")

# 80% - Processing results
progress.update("search", 0.8, f"Processing {len(results)} results...")

# 100% - Complete
progress.complete_step("search", f"Found {len(results)} results in {time:.2f}s")
```

### **Details Process**
```python
# 0% - Starting details
progress.update("details", 0.0, "Starting details extraction...")

# 10% - Navigating
progress.update("details", 0.1, "Navigating to manga page...")

# 30% - Waiting for content
progress.update("details", 0.3, "Waiting for content to load...")

# 40% - Extracting title
progress.update("details", 0.4, "Extracting title...")

# 50% - Extracting image
progress.update("details", 0.5, "Extracting image...")

# 60% - Extracting description
progress.update("details", 0.6, "Extracting description...")

# 70% - Extracting metadata
progress.update("details", 0.7, "Extracting author and status...")

# 80% - Extracting chapters
progress.update("details", 0.8, "Extracting chapters...")

# 90-100% - Processing chapters
for i, chapter in enumerate(chapters):
    chapter_progress = 0.9 + (0.1 * (i / len(chapters)))
    progress.update("details", chapter_progress, f"Processed {i+1}/{len(chapters)} chapters")
```

### **Images Process**
```python
# 0% - Starting images
progress.update("images", 0.0, "Starting image extraction...")

# 20% - Navigating
progress.update("images", 0.2, "Navigating to chapter page...")

# 40% - Waiting for images
progress.update("images", 0.4, "Waiting for images to load...")

# 60% - Extracting URLs
progress.update("images", 0.6, "Extracting image URLs...")

# 80-100% - Processing images
for i, img in enumerate(images):
    image_progress = 0.8 + (0.2 * (i / len(images)))
    progress.update("images", image_progress, f"Processed {i+1}/{len(images)} images")
```

## 🎯 **Integration Examples**

### **Frontend Integration**
```javascript
// React hook for progress
const useProgress = () => {
    const [progress, setProgress] = useState({});
    const [messages, setMessages] = useState({});
    
    const updateProgress = (step, progress, message) => {
        setProgress(prev => ({ ...prev, [step]: progress }));
        setMessages(prev => ({ ...prev, [step]: message }));
    };
    
    return { progress, messages, updateProgress };
};

// Usage in component
const { progress, messages, updateProgress } = useProgress();

// Send to backend
const searchManga = async (query) => {
    const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, progressCallback: true })
    });
    
    // Handle SSE for real-time updates
    const eventSource = new EventSource('/api/search/progress');
    eventSource.onmessage = (event) => {
        const { step, progress, message } = JSON.parse(event.data);
        updateProgress(step, progress, message);
    };
};
```

### **Backend Integration**
```python
# Flask SSE endpoint
@app.route('/api/search/progress')
def search_progress():
    def generate():
        while True:
            # Get progress from queue/cache
            progress_data = get_progress_data()
            if progress_data:
                yield f"data: {json.dumps(progress_data)}\n\n"
            time.sleep(0.1)
    
    return Response(generate(), mimetype='text/event-stream')

# Custom progress callback for web
class WebProgressCallback(ProgressCallback):
    def __init__(self, session_id):
        super().__init__()
        self.session_id = session_id
    
    def update(self, step: str, progress: float, message: str = ""):
        # Store progress in cache/queue for SSE
        store_progress(self.session_id, step, progress, message)
        super().update(step, progress, message)
```

## 🎨 **Styling Examples**

### **CSS for Progress Bars**
```css
.progress-container {
    margin: 10px 0;
    padding: 10px;
    border-radius: 8px;
    background: #f8f9fa;
    border: 1px solid #e9ecef;
}

.progress-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    font-weight: 600;
}

.progress-bar {
    height: 8px;
    background: #e9ecef;
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    transition: width 0.3s ease, background-color 0.3s ease;
}

.progress-message {
    margin-top: 4px;
    font-size: 12px;
    color: #6c757d;
}
```

### **Tailwind CSS Classes**
```html
<div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
    <div class="flex justify-between mb-2 font-semibold">
        <span class="text-gray-700">{{ step }}</span>
        <span class="text-gray-600">{{ progress }}%</span>
    </div>
    <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
            class="h-full transition-all duration-300 ease-out"
            :class="progressColor"
            :style="{ width: progress + '%' }"
        ></div>
    </div>
    <div class="mt-1 text-xs text-gray-500">{{ message }}</div>
</div>
```

## 🚀 **Performance Tips**

### **Optimization Strategies**
1. **Batch updates**: Update progress every 5-10% instead of every 1%
2. **Debounce updates**: Limit update frequency to prevent UI lag
3. **Async updates**: Use `setTimeout` for non-blocking updates
4. **Memory management**: Clear old progress data to prevent memory leaks

### **Best Practices**
1. **Consistent naming**: Use clear, consistent step names
2. **Meaningful messages**: Provide helpful status descriptions
3. **Error handling**: Show progress even during errors
4. **Completion feedback**: Always show completion status

## 🎉 **Benefits**

### **User Experience**
- **Real-time feedback**: Users know what's happening
- **Reduced anxiety**: Clear progress reduces waiting stress
- **Better expectations**: Users can estimate completion time
- **Error awareness**: Users know when something goes wrong

### **Developer Experience**
- **Debugging**: Easy to track operation progress
- **Performance monitoring**: Real-time performance metrics
- **User feedback**: Better understanding of user experience
- **Maintenance**: Easier to identify bottlenecks

The progress indicator system provides **excellent user experience** with **comprehensive feedback** for all manga scraping operations! 🎯 