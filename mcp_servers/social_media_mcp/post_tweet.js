require('dotenv').config({ path: '../../.env' });
const { TwitterApi } = require("twitter-api-v2");

const client = new TwitterApi({
    appKey: process.env.TWITTER_API_KEY,
    appSecret: process.env.TWITTER_API_SECRET,
    accessToken: process.env.TWITTER_ACCESS_TOKEN,
    accessSecret: process.env.TWITTER_ACCESS_SECRET,
});

async function post() {
    try {
        const content = `🚀 Meet your new Digital FTE (Full-Time Employee)! 🤖💼\n\nWe're thrilled to announce an artificial intelligence designed to autonomously handle your busy work. From drafting emails and making social posts to keeping your entire team organized—your Digital FTE never sleeps so you don't have to stress. \n\nSay goodbye to the grind and hello to the future of productivity! ✨\n\n#DigitalFTE #AI #FutureOfWork #HackathonGold`;
        console.log("Posting to Twitter using v2...");
        // Try v2 which is required for Free tier API keys for text posts
        const data = await client.v2.tweet(content);
        console.log(`Tweet posted successfully! ID: ${data.data.id}`);
    } catch (e) {
        console.error("Error posting to Twitter:", e?.data || e.message || e);
    }
}
post();
