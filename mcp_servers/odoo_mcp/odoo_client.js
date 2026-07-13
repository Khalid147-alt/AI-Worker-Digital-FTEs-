
const fetch = require('node-fetch');

class OdooClient {
    constructor(url, db, username, password) {
        this.url = url.replace(/\/+$/, ''); // Remove trailing slashes
        this.db = db;
        this.username = username;
        this.password = password;
        this.uid = null;
    }

    async authenticate() {
        if (this.uid) return this.uid;

        const endpoint = `${this.url}/jsonrpc`;
        const payload = {
            jsonrpc: '2.0',
            method: 'call',
            params: {
                service: 'common',
                method: 'login',
                args: [this.db, this.username, this.password],
            },
            id: Math.floor(Math.random() * 1000000),
        };

        console.error(`Authenticating to ${this.url} DB: ${this.db} User: ${this.username}`);

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(`Odoo Error: ${JSON.stringify(data.error)}`);
            }

            this.uid = data.result;
            if (!this.uid) {
                throw new Error("Authentication failed: Invalid credentials or database.");
            }

            console.error(`Authenticated successfully. UID: ${this.uid}`);
            return this.uid;
        } catch (error) {
            console.error("Authentication failed:", error);
            throw error;
        }
    }

    async execute_kw(model, method, args = [], kwargs = {}) {
        await this.authenticate();

        const endpoint = `${this.url}/jsonrpc`;
        const payload = {
            jsonrpc: '2.0',
            method: 'call',
            params: {
                service: 'object',
                method: 'execute_kw',
                args: [this.db, this.uid, this.password, model, method, args, kwargs],
            },
            id: Math.floor(Math.random() * 1000000),
        };

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(`Odoo Error in ${model}.${method}: ${JSON.stringify(data.error)}`);
            }

            return data.result;
        } catch (error) {
            console.error(`Error executing ${model}.${method}:`, error);
            throw error;
        }
    }
}

module.exports = OdooClient;
