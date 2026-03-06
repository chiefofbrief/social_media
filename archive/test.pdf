# Viral Content Workflow - Current Status & Next Steps

**Date**: 2026-01-18
**Branch**: `claude/viral-content-workflow-EArew`

---

## ✅ Completed

### 1. Core Framework Files
- `General_Characteristics_of_Viral_Content.md` - Foundation for all viral analysis
- `Characteristics_of_Viral_Content_Reddit` - Reddit-specific guidance
- `Characteristics_of_Viral_Content_X_and_Threads` - X/Threads-specific guidance

### 2. Perigon API Integration
- `Perigon_API_Query_Reference.md` - Complete reference with:
  - Boolean operators and query syntax
  - Stories endpoint (tested, working)
  - Vector Search endpoint (tested, working)
  - Working example: Trump Greenland tariffs query
  - Viral content workflow integration guidance
  - Filtering strategy (minimal filtering, keep Opinion pieces)
  - Key response fields for extraction

**Test Results**:
- Stories: 191 articles, negative sentiment 0.606, rich keyPoints
- Vector: 10 articles, semantic scores 0.84-0.85
- **Conclusion**: Default to Stories for context gathering

### 3. Workflow Guide
- `VIRAL_CONTENT_WORKFLOW.md` - Execution guide with:
  - Step 1: Seed Input
  - Step 2a: Context Gathering (Perigon API)
  - Step 2b: Viral Analysis (map to characteristics)
  - Step 2c: Angle Confirmation
  - Step 3: Reddit Post Draft
  - Step 4: X/Threads Post Draft
  - Checkpoints after each major step

---

## 🔄 In Progress

### Xpoz MCP Integration

**Status**:
- MCP server added to local config (`/home/pyratecru/.claude.json`)
- Command executed successfully: `claude mcp add --transport http --scope user xpoz-mcp https://mcp.xpoz.ai/mcp`
- API Key configured: `K38PnGAezUmMVw4XCgeZPqkMetNhhcEaBlCJhCNp9qTapFYF5fy7Mcp5FCKQjtn8qwWlDsM`

**Issue**:
- Tools not yet available in current web session
- May need new session or local Claude Code session to access tools

**Account Limits**:
- Free plan: 100,000 results/month
- Need to build queries efficiently to stay within limit

**Use Cases**:
1. **Discovery Mode** - Find viral seeds instead of user providing them
2. **Guidance Updates** - Analyze current viral patterns to refresh characteristic files

---

## 📋 Next Steps

### 1. Test Xpoz MCP Availability
**Goal**: Confirm tools are accessible and understand capabilities

**Tasks**:
- [ ] Start fresh Claude Code session (may be needed for MCP to load)
- [ ] List available Xpoz tools to see what's possible
- [ ] Review Xpoz documentation to understand:
  - Available platforms (X, Reddit, Instagram mentioned)
  - Search parameters (keywords, hashtags, users, engagement filters)
  - Response structure and fields
  - Rate limits and best practices

**Questions to answer**:
- What platforms can we search?
- What engagement filters exist? (likes, retweets, comments)
- How do we specify date ranges?
- What fields are returned in responses?
- How to sort/rank results?

### 2. Document Xpoz Integration
**Create**: `Xpoz_API_Reference.md` (similar to Perigon reference)

**Should include**:
- Authentication (already set up via MCP)
- Available platforms and their parameters
- Search syntax and filters
- Response structure
- Example queries for:
  - Finding viral posts by topic
  - Filtering by engagement
  - User/account searches
  - Subreddit searches
- Best practices for staying within 100k/month limit

### 3. Add Discovery Mode to Workflow
**Update**: `VIRAL_CONTENT_WORKFLOW.md`

**Step 1 becomes**:
```
Step 1: Seed Acquisition

OPTION A: User-Provided Seeds
- User provides excerpt(s) from news, newsletters, social media
- Proceed to Step 2a

OPTION B: Discovery Mode (via Xpoz)
- User specifies: [parameters TBD after reviewing Xpoz docs]
- System searches X/Reddit for viral candidates
- Present top results with engagement metrics
- User selects which seed(s) to develop
- Proceed to Step 2a with selected seed
```

**Need to define**:
- How user specifies discovery parameters
- How to present results efficiently
- Selection/confirmation process
- Budget-conscious query strategies

### 4. Test Discovery Workflow
**Run end-to-end test**:
1. Use Xpoz to find a viral seed
2. Run through Steps 2a-2c (Perigon context, analysis, angle)
3. Draft Reddit post (Step 3)
4. Draft X/Threads posts (Step 4)
5. Document what worked, what needs refinement

### 5. Guidance File Updates (Periodic Maintenance)
**Separate from workflow execution** - this is research to refresh frameworks

**Process**:
1. Use Xpoz to gather top viral content samples:
   - Reddit: Top 50 posts with >5k upvotes in key subreddits
   - X: Most viral tweets with >10k likes in relevant topics
2. Analyze patterns against current characteristic files
3. Update files with new insights
4. Note: Do this periodically (monthly?), not during workflow execution

---

## 🔧 Technical Notes

### MCP Setup (Already Done)
```bash
claude mcp add --transport http --scope user xpoz-mcp https://mcp.xpoz.ai/mcp \
  --header "Authorization: Bearer K38PnGAezUmMVw4XCgeZPqkMetNhhcEaBlCJhCNp9qTapFYF5fy7Mcp5FCKQjtn8qwWlDsM"
```

Config location: `/home/pyratecru/.claude.json`

### Perigon API Key (Already Set)
Environment variable: `PERIGON_API_KEY`

### Repository Structure
```
/home/user/social_media/
├── General_Characteristics_of_Viral_Content.md
├── Characteristics_of_Viral_Content_Reddit
├── Characteristics_of_Viral_Content_X_and_Threads
├── Perigon_API_Query_Reference.md
├── VIRAL_CONTENT_WORKFLOW.md
└── [TO ADD] Xpoz_API_Reference.md
```

---

## 🎯 Immediate Actions for New Session

1. **Verify Xpoz MCP tools are available**
   - Check what tools are exposed
   - Test a simple query

2. **Read Xpoz documentation**
   - Understand available parameters
   - Learn response structure
   - Identify best practices

3. **Create Xpoz reference doc**
   - Similar format to Perigon reference
   - Focus on practical examples
   - Include 100k/month budget guidance

4. **Update workflow guide**
   - Add Discovery Mode as Step 1 Option B
   - Include specific Xpoz query examples
   - Define selection/confirmation process

5. **Run test execution**
   - Discovery → Context → Analysis → Draft
   - Document gaps and refinements needed

---

## 📝 Open Questions

1. **Xpoz capabilities**: What exactly can we search and filter?
2. **Engagement thresholds**: How to identify "viral" without prescribing arbitrary numbers?
3. **Result presentation**: Best format for showing discovery candidates to user?
4. **Budget management**: How to track/estimate result usage against 100k limit?
5. **Cross-platform**: Should we search X and Reddit simultaneously or sequentially?

---

## 💡 Design Principles (Maintained Throughout)

- **Grounded in data**: No arbitrary thresholds, reference actual test results
- **Simple but concrete**: Actionable guidance without over-engineering
- **User checkpoints**: Review/confirm at key decision points
- **Framework-driven**: Always map back to viral characteristics
- **Minimal filtering**: Don't exclude Opinion/spicy content during discovery
