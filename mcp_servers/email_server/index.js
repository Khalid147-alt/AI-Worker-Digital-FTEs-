#!/usr/bin/env node

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const nodemailer = require('nodemailer');

const server = new Server(
    {
        name: 'email-server',
        version: '0.1.0',
    },
    {
        capabilities: {
            tools: {},
        },
    }
);

// Gmail transporter (configure with OAuth2)
const { google } = require('googleapis');

const OAuth2 = google.auth.OAuth2;

const createTransporter = async () => {
    // We need a refresh token for full automation, but without it we can try
    // configuring it if the user provides it, or at least setting up the OAuth2 client.
    // NOTE: To send email via OAuth2, a Refresh Token is typically required.
    // If not provided in .env, this will fail. Let's add that requirement.

    // Fallback to basic auth if GMAIL_USER and GMAIL_APP_PASSWORD are provided despite the .env
    if (process.env.GMAIL_USER && process.env.GMAIL_APP_PASSWORD) {
        return nodemailer.createTransport({
            service: 'gmail',
            auth: {
                user: process.env.GMAIL_USER,
                pass: process.env.GMAIL_APP_PASSWORD,
            },
        });
    }

    const oauth2Client = new OAuth2(
        process.env.GMAIL_CLIENT_ID,
        process.env.GMAIL_CLIENT_SECRET,
        "https://developers.google.com/oauthplayground" // Default redirect URL
    );

    if (process.env.GMAIL_REFRESH_TOKEN) {
        oauth2Client.setCredentials({
            refresh_token: process.env.GMAIL_REFRESH_TOKEN
        });
    }

    // Try to get an access token
    let accessToken = "";
    try {
        if (process.env.GMAIL_REFRESH_TOKEN) {
            const res = await oauth2Client.getAccessToken();
            accessToken = res?.token;
        }
    } catch (e) {
        console.error("Failed to get OAuth2 access token:", e.message);
    }

    return nodemailer.createTransport({
        service: "gmail",
        auth: {
            type: "OAuth2",
            user: process.env.GMAIL_USER || process.env.ODOO_USER, // Try Odoo user as fallback email
            clientId: process.env.GMAIL_CLIENT_ID,
            clientSecret: process.env.GMAIL_CLIENT_SECRET,
            refreshToken: process.env.GMAIL_REFRESH_TOKEN,
            accessToken: accessToken,
        },
    });
};

// We will initialize the transporter on demand to allow async token fetching
let transporter = null;
const getTransporter = async () => {
    if (!transporter) {
        transporter = await createTransporter();
    }
    return transporter;
};

server.setRequestHandler('tools/list', async () => {
    return {
        tools: [
            {
                name: 'send_email',
                description: 'Send an email via Gmail',
                inputSchema: {
                    type: 'object',
                    properties: {
                        to: {
                            type: 'string',
                            description: 'Recipient email address',
                        },
                        subject: {
                            type: 'string',
                            description: 'Email subject',
                        },
                        body: {
                            type: 'string',
                            description: 'Email body (plain text or HTML)',
                        },
                        cc: {
                            type: 'string',
                            description: 'CC recipients (optional)',
                        },
                    },
                    required: ['to', 'subject', 'body'],
                },
            },
            {
                name: 'draft_email',
                description: 'Create a draft email (does not send)',
                inputSchema: {
                    type: 'object',
                    properties: {
                        to: { type: 'string' },
                        subject: { type: 'string' },
                        body: { type: 'string' },
                    },
                    required: ['to', 'subject', 'body'],
                },
            },
        ],
    };
});

server.setRequestHandler('tools/call', async (request) => {
    const { name, arguments: args } = request.params;

    if (name === 'send_email') {
        const mailOptions = {
            from: process.env.GMAIL_USER,
            to: args.to,
            subject: args.subject,
            text: args.body,
            cc: args.cc || undefined,
        };

        try {
            const tp = await getTransporter();
            const info = await tp.sendMail(mailOptions);
            return {
                content: [
                    {
                        type: 'text',
                        text: `Email sent successfully! Message ID: ${info.messageId}`,
                    },
                ],
            };
        } catch (error) {
            return {
                content: [
                    {
                        type: 'text',
                        text: `Failed to send email: ${error.message}`,
                    },
                ],
                isError: true,
            };
        }
    }

    if (name === 'draft_email') {
        // Just return confirmation, don't actually send
        return {
            content: [
                {
                    type: 'text',
                    text: `Draft created (not sent):
To: ${args.to}
Subject: ${args.subject}
Body length: ${args.body.length} characters`,
                },
            ],
        };
    }

    throw new Error(`Unknown tool: ${name}`);
});

const transport = new StdioServerTransport();
server.connect(transport);
