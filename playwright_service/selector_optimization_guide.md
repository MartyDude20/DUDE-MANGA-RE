# Fast Selector Optimization Guide

## Selector Performance Hierarchy (Fastest to Slowest)

### 1. **ID Selectors** (Fastest)
```javascript
// ⚡ FASTEST - Direct ID lookup
page.query_selector('#manga-title')
page.query_selector('#chapter-list')
```

### 2. **Class Selectors** (Very Fast)
```javascript
// 🚀 Very Fast - Direct class lookup
page.query_selector('.manga-card')
page.query_selector('.chapter-item')
```

### 3. **Tag Selectors** (Fast)
```javascript
// ⚡ Fast - Direct tag lookup
page.query_selector('h1')
page.query_selector('img')
page.query_selector('a')
```

### 4. **Attribute Selectors** (Moderate)
```javascript
// 🟡 Moderate - Attribute filtering
page.query_selector('[data-testid="title"]')
page.query_selector('a[href*="/chapter"]')
page.query_selector('img[alt*="cover"]')
```

### 5. **Descendant Selectors** (Slower)
```javascript
// 🟠 Slower - DOM traversal
page.query_selector('.container .manga-item')
page.query_selector('section .title')
```

### 6. **Complex Selectors** (Slowest)
```javascript
// 🔴 Slowest - Complex traversal
page.query_selector('div.container > section > div.manga-item > h3.title')
page.query_selector('main:has(.manga-list) .manga-item:first-child')
```

## Optimization Strategies

### 1. **Use Specific, Direct Selectors**
```javascript
// ❌ Bad - Complex traversal
page.query_selector('main > div > section > div.manga-item > a')

// ✅ Good - Direct selector
page.query_selector('.manga-item a')
// or even better
page.query_selector('[data-testid="manga-link"]')
```

### 2. **Avoid Deep Nesting**
```javascript
// ❌ Bad - Deep nesting
page.query_selector('body > main > div.container > section > div.manga-list > div.manga-item')

// ✅ Good - Shallow, specific
page.query_selector('.manga-item')
```

### 3. **Use Data Attributes**
```javascript
// ✅ Best - Semantic and fast
page.query_selector('[data-testid="manga-title"]')
page.query_selector('[data-manga-id]')
page.query_selector('[data-chapter-number]')
```

### 4. **Combine Multiple Fast Selectors**
```javascript
// ✅ Good - Multiple fast selectors
selectors = [
    '[data-testid="title"]',
    '.manga-title',
    'h1',
    '[data-title]'
]

for selector in selectors:
    element = page.query_selector(selector)
    if element:
        return element
```

### 5. **Use query_selector_all Efficiently**
```javascript
// ✅ Good - Get all at once, then process
manga_items = page.query_selector_all('.manga-item')
for item in manga_items:
    title = item.query_selector('.title')
    link = item.query_selector('a')
```

## Optimized Selector Patterns

### For Manga Titles
```javascript
// Priority order (fastest first)
title_selectors = [
    '[data-testid="manga-title"]',     // Semantic data attribute
    '#manga-title',                     // ID selector
    '.manga-title',                     // Class selector
    'h1[data-title]',                   // Tag + attribute
    'h1',                               // Simple tag
    '[data-title]',                     // Generic data attribute
    '.title'                            // Generic class
]
```

### For Manga Images
```javascript
// Priority order (fastest first)
image_selectors = [
    '[data-testid="manga-cover"]',      // Semantic data attribute
    '.manga-cover img',                 // Class + tag
    'img[alt*="cover"]',                // Tag + attribute
    'img[src*="cover"]',                // Tag + attribute
    'picture img',                      // Tag + tag
    'img'                               // Simple tag
]
```

### For Chapter Links
```javascript
// Priority order (fastest first)
chapter_selectors = [
    '[data-testid="chapter-link"]',     // Semantic data attribute
    'a[href*="/chapter"]',              // Tag + attribute
    '.chapter-link',                    // Class selector
    'a[href*="read"]',                  // Tag + attribute
    'a'                                 // Simple tag
]
```

## Performance Testing Selectors

### Test Selector Speed
```javascript
async function testSelectorSpeed(page, selectors, iterations = 1000) {
    const results = {};
    
    for (const selector of selectors) {
        const start = performance.now();
        
        for (let i = 0; i < iterations; i++) {
            await page.query_selector(selector);
        }
        
        const end = performance.now();
        results[selector] = (end - start) / iterations;
    }
    
    return results;
}

// Usage
const selectors = [
    '#title',
    '.title',
    '[data-testid="title"]',
    'h1',
    'div > h1'
];

const speeds = await testSelectorSpeed(page, selectors);
console.log('Selector speeds (ms):', speeds);
```

## Real-World Optimization Examples

### Before (Slow)
```javascript
// ❌ Slow - Complex traversal
def get_manga_title(page):
    title_elem = page.query_selector('body > main > div.container > section > div.manga-details > h1.title')
    return title_elem.inner_text() if title_elem else None
```

### After (Fast)
```javascript
// ✅ Fast - Direct selectors with fallbacks
def get_manga_title(page):
    title_selectors = [
        '[data-testid="manga-title"]',
        '#manga-title',
        '.manga-title',
        'h1',
        '[data-title]'
    ]
    
    for selector in title_selectors:
        title_elem = page.query_selector(selector)
        if title_elem:
            return title_elem.inner_text().strip()
    
    return None
```

### Before (Slow)
```javascript
// ❌ Slow - Multiple DOM traversals
def get_manga_list(page):
    manga_items = page.query_selector_all('main > div > section > div.manga-list > div.manga-item')
    results = []
    
    for item in manga_items:
        title = item.query_selector('div > h3 > a').inner_text()
        link = item.query_selector('div > h3 > a').get_attribute('href')
        image = item.query_selector('div > div > img').get_attribute('src')
        results.append({'title': title, 'link': link, 'image': image})
    
    return results
```

### After (Fast)
```javascript
// ✅ Fast - Efficient selectors and batch processing
def get_manga_list(page):
    manga_items = page.query_selector_all('.manga-item')
    results = []
    
    for item in manga_items:
        # Use direct selectors within each item
        title_elem = item.query_selector('.title, h3, [data-testid="title"]')
        link_elem = item.query_selector('a[href*="/series"]')
        image_elem = item.query_selector('img')
        
        if title_elem and link_elem:
            results.append({
                'title': title_elem.inner_text().strip(),
                'link': link_elem.get_attribute('href'),
                'image': image_elem.get_attribute('src') if image_elem else None
            })
    
    return results
```

## Best Practices Summary

1. **Use IDs when available** - Fastest possible selector
2. **Prefer classes over complex selectors** - Good balance of speed and flexibility
3. **Use data attributes** - Semantic and fast
4. **Avoid deep nesting** - Keep selectors shallow
5. **Test selector performance** - Measure before optimizing
6. **Use fallback chains** - Multiple fast selectors in order of preference
7. **Batch operations** - Use query_selector_all when possible
8. **Cache selectors** - Store frequently used selectors as constants

## Performance Impact

| Selector Type | Relative Speed | Use Case |
|---------------|----------------|----------|
| ID (#id) | 100% | When you know the exact ID |
| Class (.class) | 95% | Most common use case |
| Tag (tag) | 90% | Simple element selection |
| Attribute ([attr]) | 80% | When you need attribute filtering |
| Descendant (.a .b) | 60% | When you need parent-child relationship |
| Complex (.a > .b + .c) | 40% | Avoid when possible |

Remember: The difference between a fast and slow selector can be 10-100x in performance, especially when scraping many elements! 