# Social Media Auth Guide

To enable the Social Media MCP server, you need to obtain API credentials and add them to your `.env` file or `mcp.json` environment variables.

## 1. Twitter / X API (v2)
1.  Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard).
2.  Sign up for a **Free** account (write-only access is limited, you might need Basic tier for full features).
3.  Create a Project and App.
4.  Navigate to **Keys and Tokens**.
5.  Generate:
    -   `API Key` & `API Secret`
    -   `Access Token` & `Access Token Secret` (Ensure you enable **Read and Write** permissions in App Settings first!)
6.  Add to `.env`:
    ```env
    TWITTER_API_KEY=your_key
    TWITTER_API_SECRET=your_secret
    TWITTER_ACCESS_TOKEN=your_token
    TWITTER_ACCESS_SECRET=your_token_secret
    ```

## 2. Facebook & Instagram (Graph API)
1.  Go to [Meta for Developers](https://developers.facebook.com/).
2.  Create an App (Select "Business" type).
3.  **Facebook Page**:
    -   Add "Facebook Login for Business" product.
    -   Generate a Long-Lived Page Access Token via Graph API Explorer.
    -   Permissions needed: `pages_manage_posts`, `pages_read_engagement`.
    -   Find your `Page ID` (in About section of your page).
4.  **Instagram Business**:
    -   Connect your Instagram Professional account to your Facebook Page.
    -   Use the same Access Token (if scopes include `instagram_basic`, `instagram_content_publish`).
    -   Find `IG_USER_ID` via API: `GET /me?fields=instagram_business_account`.

5.  Add to `.env`:
    ```env
    FB_PAGE_TOKEN=your_long_lived_token
    FB_PAGE_ID=your_page_id
    IG_USER_ID=your_instagram_business_id
    ```

## 3. Storage
Save these in `d:/Hackathon0/mcp_servers/social_media_mcp/.env`.
