require('dotenv').config({ path: '../../.env' });
const { google } = require('googleapis');

const OAuth2 = google.auth.OAuth2;

async function testOAuth2() {
    console.log("Testing OAuth2 setup with:");
    console.log("Client ID:", process.env.GMAIL_CLIENT_ID ? "Set" : "Missing");
    console.log("Client Secret:", process.env.GMAIL_CLIENT_SECRET ? "Set" : "Missing");
    console.log("Refresh Token:", process.env.GMAIL_REFRESH_TOKEN ? "Set" : "Missing");

    const oauth2Client = new OAuth2(
        process.env.GMAIL_CLIENT_ID,
        process.env.GMAIL_CLIENT_SECRET,
        "https://developers.google.com/oauthplayground"
    );

    if (!process.env.GMAIL_REFRESH_TOKEN) {
        console.log("No Refresh Token provided. Generating auth URL for user to log in:");

        const authUrl = oauth2Client.generateAuthUrl({
            access_type: 'offline',
            scope: ['https://mail.google.com/']
        });

        console.log("\n=================================");
        console.log("ACTION REQUIRED: GO TO THIS URL");
        console.log(authUrl);
        console.log("=================================\n");
        return;
    }

    oauth2Client.setCredentials({
        refresh_token: process.env.GMAIL_REFRESH_TOKEN
    });

    try {
        console.log("Attempting to get Access Token...");
        const res = await oauth2Client.getAccessToken();
        console.log("Access Token retrieved successfully!");
    } catch (e) {
        console.error("Failed to get OAuth2 access token:", e.message);
    }
}

testOAuth2();
