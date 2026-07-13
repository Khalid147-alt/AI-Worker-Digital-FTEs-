---
name: social_media_poster
description: Generate and publish social media content.
---

# Social Media Poster Skill

## 1. Purpose
Creates engaging content for LinkedIn, Twitter, etc., and schedules it for publication.

## 2. Trigger
-   Schedule (e.g., Mon/Thu).
-   Task: "Post about our new feature".

## 3. Input
-   **Topic**: Provided in task or derived from `Business_Goals.md`.
-   **Platform**: LinkedIn, Twitter, Facebook, Instagram.

## 4. Steps
1.  **Draft**: Use `Social_Post_Template.md` to format the content.
2.  **Optimize**: Adjust length/tone for specific platform (e.g., Hashtags for Twitter).
3.  **Review**: Save to `/Pending_Approval/Social/`.
4.  **Publish**:
    -   If `immediate: true` (and trusted), call Social MCP `post_to_xyz`.
    -   Else, wait for approval file to be moved to `/Approved`.

## 5. Output
-   File: `/Pending_Approval/Social/DRAFT_{Platform}_{Date}.md`.
-   Live Post (if automated).

## 6. Approval Required
-   **YES** (Default).
-   **NO** (If `immediate: true` flag is set by Orchestrator for trusted routine posts).

## 7. Error Handling
-   API Failure: Log to `ERROR_PLAYBOOK` logic (Retry -> Alert).
-   Content Filter: If AI detects sensitive topics, flag for human review.
