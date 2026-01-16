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
