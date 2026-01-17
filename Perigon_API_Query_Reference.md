# Perigon API Query Reference

## Core Endpoints

**Articles** (`/v1/all`) - Individual news articles with full metadata
**Stories** (`/v1/stories`) - Articles clustered into events with AI summaries and aggregated entities

---

## Query Building Blocks

### Boolean Operators
Must be UPPERCASE or they're treated as keywords. Terms are case-insensitive.

| Operator | Function | Example |
|----------|----------|---------|
| `AND` | Both required | `Tesla AND "Elon Musk"` |
| `OR` | Either works (default) | `AI OR "machine learning"` |
| `NOT` | Exclude term | `"blockchain" NOT bitcoin` |
| `" "` | Exact phrase | `"self-driving cars"` |
| `*` | 0+ characters wildcard | `immuni*` → immunity, immunization |
| `?` | 1 character wildcard | `wom?n` → woman, women |
| `( )` | Group expressions | `(Google OR Amazon) AND NOT Android` |
| `^n` | Boost relevance | `"machine learning"^2 OR AI` |

**Evaluation order** (without parentheses): NOT → AND → OR

---

## Search Parameters

### Content Search (Articles)
| Parameter | Searches | Boolean | Wildcards |
|-----------|----------|---------|-----------|
| `q` | Title, description, content | ✓ | ✓ |
| `title` | Headlines only | ✓ | ✓ |
| `desc` | Description field | ✓ | ✓ |
| `content` | Full article body | ✓ | ✓ |
| `url` | Article URLs | ✓ | ✓ |
| `linkTo` | URLs linked within articles | ✓ | ✓ |

### Content Search (Stories)
| Parameter | Searches | Boolean | Wildcards |
|-----------|----------|---------|-----------|
| `q` | Name, summary, key points | ✓ | ✓ |
| `name` | Story names | ✓ | ✓ |

---

## Date & Time Filters

**Format:** ISO 8601 UTC (`2025-01-01` or `2025-01-01T00:00:00`)
**Note:** `to` is exclusive - set to next day/hour to capture full range

### Articles
- `from` / `to` - Publication date
- `addDateFrom` / `addDateTo` - When added to Perigon
- `refreshDateFrom` / `refreshDateTo` - When updated in Perigon

### Stories
- `from` / `to` - Story creation date
- `initializedFrom` / `initializedTo` - Alternative creation date filter
- `updatedFrom` / `updatedTo` - When new articles were added to story

---

## Entity Filters

**Multiple includes = OR logic | Multiple excludes = AND logic**

### People
**Articles:**
- `personWikidataId` / `excludePersonWikidataId` - Wikidata Q-IDs
- `personName` / `excludePersonName` - Exact names

**Stories:**
- `personWikidataId` - Filter by topPeople Q-IDs
- `personName` - Filter by topPeople names

### Companies
**Articles:**
- `companyId` / `excludeCompanyId` - Company UUIDs
- `companyName` - Company full name (single value)
- `companyDomain` / `excludeCompanyDomain` - Web domains (e.g., apple.com)
- `companySymbol` / `excludeCompanySymbol` - Stock tickers (e.g., AAPL)

**Stories:**
- `companyId` - Filter by topCompanies UUIDs
- `companyName` - Filter by topCompanies names
- `companyDomain` - Filter by company domains
- `companySymbol` - Filter by tickers

### Authors & Journalists
**Articles only:**
- `author` / `excludeAuthor` - Author name
- `journalistId` / `excludeJournalistId` - Journalist UUID

---

## Topics & Categories

**Multiple includes = OR logic | Multiple excludes = AND logic**

### Categories (Broad themes)
Politics, Tech, Sports, Business, Finance, Entertainment, Health, Weather, Lifestyle, Auto, Science, Travel, Environment, World, General

**Parameters:** `category` / `excludeCategory` (Articles), `category` (Stories)

### Topics (Fine-grained)
Examples: Markets, Crime, Cryptocurrency, College Sports, Security Breach, 2025 Elections

**Access full list:** `/v1/topics` endpoint

**Parameters:** `topic` / `excludeTopic` (Articles), `topic` (Stories)

### Taxonomies (Google Content Categories)
Hierarchical paths like `/Finance/Banking/Other`

**Parameters:**
- `taxonomy` - Full GCC paths (comma-separated)
- `prefixTaxonomy` - Match all nested under prefix (e.g., `/Science` → Astronomy, Chemistry...)

### Medium
- `Article` - Written long-form
- `Video` - Video as primary medium

**Parameter:** `medium`

### Labels (Editorial style/provenance)
Non-news, Opinion, Paid News, Pop Culture, Fact Check, Roundup, Press Release, Low Content, Synthetic

**Parameters:** `label` / `excludeLabel`

---

## Sources & Source Groups

### Individual Sources
**Parameters:**
- `source` - Include domains (supports wildcards: `*.cnn.com`, `us?.nytimes.com`)
- `excludeSource` - Exclude domains (Articles only)

**Logic:** Multiple `source=` = OR | Multiple `excludeSource=` = AND

### Source Groups (Curated bundles)
**Parameters:**
- `sourceGroup` - Include groups
- `excludeSourceGroup` - Exclude groups (Articles only)

**Available groups:**
- `top10`, `top100`, `top500English`
- `top25crypto`, `top25finance`, `top50tech`, `top100sports`
- `top100leftUS`, `top100rightUS`, `top100centerUS`

**Preview group contents:** `/v1/sources?sourceGroup=top100`

---

## Geography

**Code formats:** 2-char ISO (country: `us`, state: `TX`)

### Articles
**Content location:**
- `city` / `excludeCity`
- `area` / `excludeArea` - Borough/district/neighborhood
- `state` / `excludeState`
- `county` / `excludeCounty`
- `locationsCountry` or `country` / `excludeLocationsCountry`
- `lat`, `lon`, `maxDistance` - Radius in km (all 3 required)

**Publisher location:**
- `sourceCity`, `sourceCounty`, `sourceState`, `sourceCountry`
- `sourceLat`, `sourceLon`, `sourceMaxDistance` - Radius search (all 3 required)

### Stories
- `city`, `area`, `state`, `country` - Local story clusters only
- `excludeCity`, `excludeArea`, `excludeState`

**Note:** Any geo parameter on Stories limits to local clusters only

---

## Sentiment

AI-scored emotional tone: positive, negative, neutral (sum = 1.0)

**Parameters (Articles & Stories):**
- `positiveSentimentFrom` / `positiveSentimentTo`
- `negativeSentimentFrom` / `negativeSentimentTo`
- `neutralSentimentFrom` / `neutralSentimentTo`

**Example:** `positiveSentimentFrom=0.7` for highly positive content

---

## Response Fields (Key examples)

### Articles
- `title`, `description`, `content`
- `pubDate`, `imageUrl`, `url`
- `sentiment` object (positive, negative, neutral scores)
- `locations` array (city, state, country)
- `source` object (domain, name, location)
- `links` array (embedded URLs in content)

### Stories
- `name`, `summary`, `description`
- `topPeople`, `topCompanies`, `topTopics`
- Aggregated entities from clustered articles

---

## Query Construction Examples

**Entity with context:**
```
personName=Satya%20Nadella&q=AI&from=2025-01-01
```

**Boolean with exclusions:**
```
q=(Tesla OR SpaceX) AND NOT bitcoin&excludeLabel=Opinion
```

**Source group + category:**
```
sourceGroup=top25finance&category=Finance&topic=Markets
```

**Geo + sentiment:**
```
city=Austin&positiveSentimentFrom=0.6&category=Tech
```

**Wildcard search:**
```
q=crypto*&excludeSource=buzzfeed.com
```

---

## Implementation Guide

### Authentication
API key is stored in environment variable: `PERIGON_API_KEY`

### Making Requests

**Stories Endpoint (Recommended for context gathering):**
```python
import os
import requests

PERIGON_KEY = os.environ.get('PERIGON_API_KEY')

params = {
    'apiKey': PERIGON_KEY,
    'q': '(Trump AND Greenland AND tariff*)',
    'from': '2026-01-10',
    'to': '2026-01-18',
    'sortBy': 'relevance',
    'category': 'Politics,Business,World',
    'size': 10,
    'minUniqueSources': 2,
    'showReprints': False
}

response = requests.get('https://api.goperigon.com/v1/stories/all',
                       params=params,
                       timeout=15)
data = response.json()
```

**Vector Search Endpoint (Semantic queries):**
```python
payload = {
    'prompt': 'Trump threatens tariffs on European countries to pressure Denmark',
    'size': 10,
    'pubDateFrom': '2026-01-10',
    'pubDateTo': '2026-01-18',
    'showReprints': False
}

response = requests.post(
    'https://api.goperigon.com/v1/vector/news/all',
    json=payload,
    headers={
        'x-api-key': PERIGON_KEY,  # Note: header auth, not query param
        'Content-Type': 'application/json'
    },
    timeout=15
)
data = response.json()

# Vector response structure: results contain score + data objects
for result in data.get('results', []):
    article = result['data']
    score = result['score']  # Semantic relevance score (0-1)
    title = article.get('title')
```

### Retry Logic Pattern

```python
import time

MAX_RETRIES = 3
RETRY_STATUS_CODES = [429, 403, 500, 502, 503]
RETRY_BASE_WAIT = 5

def make_request_with_retry(request_func):
    for attempt in range(MAX_RETRIES):
        try:
            response = request_func()
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in RETRY_STATUS_CODES:
                wait_time = (2 ** attempt) * RETRY_BASE_WAIT
                print(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
                if attempt == MAX_RETRIES - 1:
                    return {'error': str(e), 'results': []}
            else:
                return {'error': str(e), 'results': []}
    return {'results': []}
```

---

## Working Example: Trump Greenland Tariffs

### Seed Excerpt
"Trump to Hit European Nations with 10% Tariffs in Bid for Greenland Deal. President says the levies will go into effect Feb. 1 to pressure the countries into approving the acquisition."

### Seed Analysis
- **Entities**: Trump, Denmark, Greenland, EU countries
- **Topic**: Tariffs, geopolitical leverage, territorial acquisition
- **Categories**: Politics, Business, World
- **Emotion**: High-arousal (anger, surprise, controversy)
- **Timing**: Breaking news (Jan 17, 2026)

### Boolean Query Construction
```
q=(Trump AND Greenland AND tariff*)
```

**Why this query:**
- `Trump` + `Greenland` - Core entities
- `tariff*` - Wildcard catches tariff, tariffs, tariffing
- Parentheses group the AND logic
- No exclusions needed (story is specific enough)

### Full Request
```python
params = {
    'apiKey': PERIGON_KEY,
    'q': '(Trump AND Greenland AND tariff*)',
    'from': '2026-01-10',      # 7 days back for breaking news
    'to': '2026-01-18',
    'sortBy': 'relevance',
    'category': 'Politics,Business,World',
    'size': 10,
    'minUniqueSources': 2,
    'showReprints': False
}

response = requests.get('https://api.goperigon.com/v1/stories/all',
                       params=params, timeout=15)
```

### Sample Response
```json
{
  "numResults": 8,
  "stories": [
    {
      "name": "Trump Imposes Tariffs, Presses to Buy Greenland",
      "summary": "On Jan. 17, President Donald Trump announced that the United States will impose a 10% tariff on goods from Denmark, Norway, Sweden, France, Germany, the United Kingdom, the Netherlands and Finland...",
      "sentiment": {
        "positive": 0.092,
        "negative": 0.606,
        "neutral": 0.303
      },
      "uniqueCount": 185,
      "topPeople": ["Donald Trump"],
      "topics": [
        {"name": "US Politics", "count": 5},
        {"name": "Markets", "count": 15},
        {"name": "Congress", "count": 3}
      ]
    }
  ]
}
```

### Key Insights from Response
- **185 unique articles** clustered into this story - major coverage
- **Negative sentiment (0.606)** - high-arousal emotion confirmed
- **Topics**: US Politics, Markets, Congress - cross-category viral potential
- **Multiple follow-on stories** - protests, EU response, Congressional pushback

---

### Vector Search Comparison (Same Seed)

**Semantic Prompt:**
```
prompt: "Trump threatens tariffs on European countries to pressure Denmark into selling Greenland"
```

**Why Vector:**
- Natural language query instead of Boolean operators
- Semantic matching finds conceptually related articles
- Good for exploratory research when exact keywords might vary

**Full Request:**
```python
payload = {
    'prompt': 'Trump threatens tariffs on European countries to pressure Denmark into selling Greenland',
    'size': 10,
    'pubDateFrom': '2026-01-10',
    'pubDateTo': '2026-01-18',
    'showReprints': False
}

response = requests.post(
    'https://api.goperigon.com/v1/vector/news/all',
    json=payload,
    headers={
        'x-api-key': PERIGON_KEY,
        'Content-Type': 'application/json'
    },
    timeout=15
)
```

**Sample Response:**
```json
{
  "numResults": 10,
  "articles": [
    {
      "title": "Trump threatens 10% tariffs on eight European nations over Greenland purchase demand",
      "source": "telegraphindia.com",
      "score": 0.842,
      "pubDate": "2026-01-17T22:40:51+05:30",
      "people": ["Chris Coons", "Donald Trump"]
    },
    {
      "title": "Trump says Europe will face tariffs until Denmark gives up Greenland",
      "source": "thecentersquare.com",
      "score": 0.839,
      "pubDate": "2026-01-17T11:11:00-06:00",
      "people": ["Donald Trump"]
    }
  ]
}
```

**Key Differences:**
- **10 individual articles** vs 8 story clusters
- **Relevance scores** (0.84-0.85) show semantic similarity
- **Different sources** than Stories (more diverse, international coverage)
- **No clustering** - each article stands alone

**Boolean (Stories) vs Vector:**
- **Use Boolean** when you have specific entities/keywords and want aggregated context
- **Use Vector** when exploring themes, catching paraphrases, or when keywords might vary

### When to Use Stories vs Articles vs Vector

**Stories** (Recommended for viral content workflow):
- Aggregates coverage across multiple sources
- AI-generated summaries provide quick context
- `uniqueCount` shows story magnitude
- `topPeople`/`topCompanies`/`topTopics` identify key players
- Best for understanding "what's the big story here?"

**Articles**:
- Individual pieces for granular analysis
- Full content access when needed
- More results but potentially redundant
- Better for specific sourcing needs

**Vector Search**:
- Semantic/conceptual queries
- When exact keywords might miss relevant content
- Good for thematic exploration
- "Find articles about X without saying Y"

---

## Viral Content Workflow Integration

### Default Approach: Stories Endpoint

**Why Stories wins for viral content:**
1. **Story magnitude** (`uniqueCount`) = instant virality indicator (191 articles = massive)
2. **keyPoints** = gold mine of contrarian angles, debunking opportunities, insider dissent
3. **Multi-thread narratives** - reveals protests, geopolitical tensions, specific impacts
4. **Emotional hooks** - captures human reactions, protest signs, meme-worthy quotes
5. **Cross-topic virality** - shows connections to other trending topics

**When to use Vector instead:**
- Thematic/conceptual seeds with no clear entities ("AI workplace anxiety")
- Fuzzy topics where keywords might vary significantly
- Exploratory research on abstract concepts

### Filtering Strategy: Less is More

**DO use:**
- Date range (7-30 days depending on topic freshness)
- `category` if obvious (e.g., Tech, Politics)
- `minUniqueSources=2` for Stories (filters out single-source stories)
- `showReprints=False` (avoid duplicates)

**DON'T filter out:**
- Opinion pieces (hot takes = viral gold)
- Paid News (sometimes reveals industry narratives)
- Specific sources (want diverse perspectives for unexpected angles)

**Why minimal filtering:**
- The "wrong" category might have the best viral angle
- Over-filtering = missed contrarian narratives
- We're context gathering, not precision targeting

### Key Response Fields for Viral Analysis

**From Stories response:**
```python
story = {
    'uniqueCount': 191,          # Magnitude indicator
    'sentiment': {
        'negative': 0.606,        # High-arousal emotion
        'positive': 0.092
    },
    'keyPoints': [                # Contrarian angles, specific hooks
        {'point': 'State Dept official calls it "self-evidently bullshit"'},
        {'point': 'Historical claim is FALSE'},
        {'point': 'Pharmaceuticals most affected'}
    ],
    'topPeople': ['Donald Trump'],
    'topics': [                   # Cross-category potential
        {'name': 'US Politics'},
        {'name': 'Markets'},
        {'name': 'Protests'}
    ]
}
```

**What to extract:**
- **uniqueCount**: Number of articles covering this story
- **sentiment**: Scores for positive, negative, neutral (sum = 1.0)
- **keyPoints**: Specific claims, quotes, and facts from coverage
- **topPeople/topCompanies**: Key entities mentioned across articles
- **topics**: Subject areas tagged across the story
