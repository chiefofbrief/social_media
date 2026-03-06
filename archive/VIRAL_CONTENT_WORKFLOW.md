# Viral Content Workflow

**Goal**: Transform seed excerpts into viral posts for Reddit and X/Threads.

---

## Core Reference Files

**Always have these loaded before starting:**
1. `General_Characteristics_of_Viral_Content.md` - Foundation for all analysis
2. `Perigon_API_Query_Reference.md` - API integration guide

**Load during drafting:**
3. `Characteristics_of_Viral_Content_Reddit_Posts` - When drafting Reddit posts
4. `Characteristics_of_Viral_Content_Reddit_Comments` - When crafting Reddit comments (optional)
5. `Characteristics_of_Viral_Content_X_and_Threads` - When drafting X/Threads posts

---

## Workflow Steps

### Step 1: Seed Input
**User provides**: Excerpt(s) from news, newsletters, social media, or other sources.

**Your task**: Acknowledge receipt and prepare for research.

---

### Step 2a: Context Gathering

**Objective**: Use Perigon API to gather context about the seed topic.

**Process**:

1. **Analyze the seed** to extract:
   - Key entities (people, companies, specific terms)
   - Topic/category
   - Timing cues (breaking news vs evergreen)

2. **Construct Perigon query**:
   - **Default**: Use Stories endpoint with Boolean query
   - Reference `Perigon_API_Query_Reference.md` for syntax
   - Build query using entities and wildcards
   - Set date range: 7 days for breaking news, 30 days for evergreen
   - Include `category` if obvious
   - Always use: `minUniqueSources=2`, `showReprints=False`

3. **Execute query**:
   - Use Python with requests library
   - Include retry logic for rate limits/errors
   - Request 5-10 stories

4. **Extract key data**:
   - `uniqueCount` - article coverage
   - `sentiment` - emotion scores
   - `keyPoints` - specific claims, quotes, facts
   - `topPeople`/`topCompanies` - key players
   - `topics` - subject areas
   - `summary` - AI overview

**When to use Vector Search instead**:
- Seed is thematic/conceptual with no clear entities
- Topic might be described in varying ways

**Output**: Present raw Perigon data to user (formatted clearly).

---

### Step 2b: Viral Analysis

**Objective**: Map Perigon data to viral characteristics and identify potential angles.

**Process**:

1. **Reference `General_Characteristics_of_Viral_Content.md`** explicitly

2. **Map to viral framework**:
   - **Value drivers**: Does this serve Practical, Personal, or Social value?
   - **Emotion**: What high-arousal emotion is present? (anger, awe, surprise, humor, fear, anxiety)
   - **Timing**: Does this meet people at an emotional moment?
   - **Shareability**: What makes this spreadable?

3. **Extract angles from keyPoints**:
   - Contrarian narratives (debunking, insider dissent)
   - Specific impacts (who's affected, how)
   - Reactions (protests, pushback, quotes)
   - Cross-topic connections (links to other trending issues)

4. **Note small account advantages**:
   - What's the risk-averse angle larger accounts won't touch?
   - What authentic/specific observation can be made?

**Output**:
- Brief viral analysis summary
- 2-3 potential angles with explanation of why each could work
- Reference specific keyPoints or data supporting each angle

**Checkpoint**: User reviews and selects/refines angle.

---

### Step 2c: Angle Confirmation

**User action**: Choose angle or provide direction.

**Your task**: Confirm the selected angle and prepare to draft posts.

---

### Step 3: Reddit Post Draft

**Objective**: Create viral Reddit post using the confirmed angle.

**Process**:

1. **Load and reference**: `Characteristics_of_Viral_Content_Reddit`

2. **Apply Reddit formula**:
   - **Provocative simplicity** - concrete details, specific examples
   - **Shared truth articulation** - say what people think but haven't stated
   - **Defensible controversy** - strong stance with logic
   - **Question-based engagement** - invite discussion
   - **Wit/irony** where appropriate

3. **Draft the post**:
   - Keep it focused and punchy
   - Include concrete details from Perigon data
   - Design for comment engagement

4. **Consider visual needs**:
   - Does this post benefit from an accompanying image/chart?
   - If yes, suggest what visual would strengthen it

**Output**: Reddit post draft

**Checkpoint**: User reviews Reddit post.

---

### Step 4: X/Threads Post Draft

**Objective**: Create viral X/Threads posts using the confirmed angle.

**Process**:

1. **Load and reference**: `Characteristics_of_Viral_Content_X_and_Threads`

2. **Apply X formula** (use for both X and Threads):
   - **Broadcast & React** approach
   - **Screenshot-worthy** - immediate impact
   - **Punchy statements** with emotional hooks in first words
   - **Strong opinionated language**

3. **Draft the post**:
   - Short, impactful
   - Lead with the hook
   - Design for sharing/remixing

4. **Consider visual needs**:
   - X posts are 87.5% visual - does this need an image?
   - If yes, provide image prompt for generation

**Output**: X/Threads post draft(s)

**Checkpoint**: User reviews X/Threads posts.

---

## Execution Guidelines

**Do**:
- Reference the viral characteristics files explicitly during analysis
- Extract and cite specific data from Perigon responses
- Present options at checkpoints
- Keep explanations focused on the data and frameworks

**Don't**:
- Add arbitrary thresholds or metrics not in the source materials
- Over-engineer or add unnecessary complexity
- Skip checkpoints - always give user chance to review/redirect
- Make assumptions about user preferences without asking

**Tone**:
- Direct and actionable
- Grounded in the frameworks and data
- Collaborative (this is iterative work)

---

## Notes

- Each seed is different - adapt the query and analysis accordingly
- The "wrong" angle might emerge during drafting - be flexible
- User may iterate on posts multiple times - that's expected
- Some seeds won't have viral potential - that's okay to surface
