# Manga Metadata Comparison

## Overview

This document compares the metadata we extract from different manga sources during search, pagination, and detailed manga information gathering.

## AsuraScans Metadata

### Search/Pagination Results (Basic Info)
```json
{
  "id": "manga-slug-id",
  "title": "Manga Title",
  "status": "", // Empty in search results
  "chapter": "62", // Latest chapter number
  "image": "https://asuracomic.net/images/cover.jpg",
  "details_url": "series/manga-slug-id",
  "source": "asurascans"
}
```

### Detailed Manga Information
```json
{
  "id": "manga-slug-id",
  "title": "Manga Title",
  "image": "https://asuracomic.net/images/cover.jpg",
  "description": "Full manga description...",
  "author": "Author Name",
  "status": "Ongoing/Completed",
  "url": "https://asuracomic.net/series/manga-slug-id",
  "source": "asurascans",
  "chapters": [
    {
      "title": "Chapter 1",
      "url": "https://asuracomic.net/series/manga-slug-id/chapter/1",
      "date": "2024-01-01"
    }
  ]
}
```

## WeebCentral Metadata

### Search Results (Enhanced Basic Info)
```json
{
  "id": "manga-slug-id",
  "title": "Manga Title",
  "status": "Ongoing/Completed",
  "chapter": "Chapter 62",
  "image": "https://weebcentral.com/images/cover.webp",
  "details_url": "/series/manga-slug-id/",
  "source": "weebcentral",
  "authors": ["Author Name"],
  "tags": ["Action", "Adventure", "Fantasy"],
  "year": "2024"
}
```

### Detailed Manga Information (Comprehensive)
```json
{
  "id": "manga-slug-id",
  "title": "Manga Title",
  "image": "https://weebcentral.com/images/cover.webp",
  "description": "Full manga description...",
  "author": "Author Name",
  "status": "Ongoing/Completed",
  "tags": ["Action", "Adventure", "Fantasy"],
  "type": "Manhwa/Manhua/Manga",
  "released": "2024",
  "official_translation": "Yes/No",
  "anime_adaptation": "Yes/No",
  "adult_content": "Yes/No",
  "url": "https://weebcentral.com/series/manga-slug-id/",
  "source": "weebcentral",
  "chapters": [
    {
      "title": "Chapter 1",
      "url": "https://weebcentral.com/series/manga-slug-id/chapter/1"
    }
  ]
}
```

## MangaDex Metadata

### Search Results (API-based)
```json
{
  "id": "manga-uuid",
  "title": "Manga Title",
  "status": "ongoing/completed",
  "chapter": "Chapter 62",
  "image": "https://uploads.mangadex.org/covers/manga-uuid.jpg",
  "details_url": "/title/manga-uuid",
  "source": "mangadex",
  "authors": ["Author Name"],
  "tags": ["action", "adventure", "fantasy"],
  "year": "2024"
}
```

### Detailed Manga Information (API-based)
```json
{
  "id": "manga-uuid",
  "title": "Manga Title",
  "image": "https://uploads.mangadex.org/covers/manga-uuid.jpg",
  "description": "Full manga description...",
  "author": "Author Name",
  "status": "ongoing/completed",
  "tags": ["action", "adventure", "fantasy"],
  "type": "manga/manhwa/manhua",
  "released": "2024",
  "official_translation": "Yes/No",
  "anime_adaptation": "Yes/No",
  "adult_content": "Yes/No",
  "url": "https://mangadex.org/title/manga-uuid",
  "source": "mangadex",
  "chapters": [
    {
      "title": "Chapter 1",
      "url": "https://mangadex.org/chapter/chapter-uuid"
    }
  ]
}
```

## Metadata Comparison Table

| Field | AsuraScans | WeebCentral | MangaDex |
|-------|------------|-------------|----------|
| **Basic Info** | | | |
| ID | ✅ | ✅ | ✅ |
| Title | ✅ | ✅ | ✅ |
| Status | ✅ (details only) | ✅ | ✅ |
| Chapter | ✅ | ✅ | ✅ |
| Image | ✅ | ✅ | ✅ |
| URL | ✅ | ✅ | ✅ |
| Source | ✅ | ✅ | ✅ |
| **Enhanced Info** | | | |
| Description | ✅ | ✅ | ✅ |
| Author | ✅ | ✅ | ✅ |
| Authors (array) | ❌ | ✅ | ✅ |
| Tags | ❌ | ✅ | ✅ |
| Type | ❌ | ✅ | ✅ |
| Release Year | ❌ | ✅ | ✅ |
| Official Translation | ❌ | ✅ | ✅ |
| Anime Adaptation | ❌ | ✅ | ✅ |
| Adult Content | ❌ | ✅ | ✅ |
| **Chapter Info** | | | |
| Chapter List | ✅ | ✅ | ✅ |
| Chapter Dates | ✅ | ❌ | ✅ |
| Chapter URLs | ✅ | ✅ | ✅ |
| **Image Info** | | | |
| Chapter Images | ✅ | ✅ | ✅ |
| Cover Quality | Medium | High (WebP) | High |

## Metadata Quality Assessment

### AsuraScans
- **Strengths**: Simple, reliable, good chapter dates
- **Weaknesses**: Limited metadata, no tags, no type info
- **Best for**: Basic manga discovery, chapter reading

### WeebCentral
- **Strengths**: Comprehensive metadata, rich tags, multiple authors
- **Weaknesses**: Complex scraping, no chapter dates
- **Best for**: Detailed manga information, filtering, discovery

### MangaDex
- **Strengths**: API-based, consistent, comprehensive
- **Weaknesses**: Rate limits, API dependencies
- **Best for**: Reliable data, consistent format

## Recommendations for Enhancement

### 1. Standardize Metadata Fields
```python
# Proposed standard metadata structure
{
  "id": "unique_id",
  "title": "Manga Title",
  "status": "ongoing/completed/hiatus",
  "type": "manga/manhwa/manhua",
  "authors": ["Author 1", "Author 2"],
  "tags": ["tag1", "tag2"],
  "year": "2024",
  "description": "Description",
  "image": "cover_url",
  "chapters": [...],
  "metadata": {
    "official_translation": true,
    "anime_adaptation": false,
    "adult_content": false,
    "rating": "PG-13",
    "genres": ["action", "adventure"]
  }
}
```

### 2. Enhance AsuraScans Metadata
- Add tag extraction from manga details page
- Extract type information (manhwa/manhua/manga)
- Add release year detection
- Include rating/adult content flags

### 3. Improve WeebCentral Metadata
- Add chapter date extraction
- Standardize status values
- Add rating information
- Include more detailed genre classification

### 4. Cross-Source Metadata Merging
- Merge metadata from multiple sources
- Use MangaDex as authoritative source for basic info
- Supplement with source-specific details
- Create unified manga database

## Current Implementation Status

### ✅ Implemented
- Basic metadata extraction from all sources
- Pagination-based crawling (AsuraScans)
- Search-based crawling (WeebCentral, MangaDex)
- Chapter image extraction
- Caching system

### 🔄 In Progress
- Metadata standardization
- Cross-source data merging
- Enhanced filtering capabilities

### 📋 Planned
- Rating system integration
- Genre classification
- User preferences
- Advanced search filters
- Metadata validation

## Usage Examples

### Get All Available Metadata
```python
# Get comprehensive manga info
manga_details = cache_manager.get_manga_details(manga_id, source)

# Access specific metadata
title = manga_details['title']
authors = manga_details.get('authors', [manga_details.get('author', 'Unknown')])
tags = manga_details.get('tags', [])
status = manga_details.get('status', 'Unknown')
```

### Filter by Metadata
```python
# Filter by tags
action_manga = [m for m in all_manga if 'action' in m.get('tags', [])]

# Filter by status
ongoing_manga = [m for m in all_manga if m.get('status', '').lower() == 'ongoing']

# Filter by year
recent_manga = [m for m in all_manga if m.get('year', '0') >= '2020']
```

This metadata system provides a solid foundation for manga discovery, filtering, and user experience enhancement across all supported sources. 