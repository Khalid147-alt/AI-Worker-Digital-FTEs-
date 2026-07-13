# Skill: Auto-Post Business Updates to LinkedIn

## Purpose
Generate and queue LinkedIn posts about business activities, services, or insights to maintain visibility and generate leads.

## Trigger
- Manual: When user creates a file in /Social_Media/LinkedIn_Queue/TOPIC.md
- Scheduled: Every Monday & Thursday at 9 AM

## Instructions

1. **Read Business_Goals.md** to understand:
   - Current services offered
   - Target audience
   - Key messaging themes

2. **Check recent activity** in /Done folder:
   - Completed projects (last 7 days)
   - Client wins
   - New capabilities added

3. **Generate post** using this framework:
   ```markdown
   [HOOK - Start with a problem or insight]
   
   [CONTEXT - Brief story or example]
   
   [VALUE - What you learned / what you offer]
   
   [CTA - Invitation to connect or learn more]
   
   #hashtag1 #hashtag2 #hashtag3
   ```

4. **Post Guidelines:**
   - Length: 100-200 words
   - Tone: Professional but conversational
   - Include 3-5 relevant hashtags
   - Avoid hard sales pitches
   - Focus on value/insights

5. **Create draft** in /Social_Media/LinkedIn_Queue/:
   ```markdown
   ---
   type: linkedin_post
   topic: <topic>
   created: <timestamp>
   scheduled_for: <date and time>
   status: draft
   ---
   
   ## Post Content
   
   [Your drafted post here]
   
   ## Hashtags
   #webdevelopment #freelance #techpakistan
   
   ## Image Suggestion (optional)
   [Describe what kind of image would work]
   ```

6. **If auto-posting is enabled:**
   - Create approval request in /Pending_Approval/POST_LINKEDIN_xxx.md
   - Wait for human to move to /Approved
   - Then use LinkedIn MCP to post

7. **Log** the post in /Logs/YYYY-MM-DD.md and /Social_Media/Posted/

## Success Criteria
- Post is engaging and on-brand
- Provides value (not just promotion)
- Scheduled appropriately
- Logged for tracking
