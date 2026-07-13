const fetch = require('node-fetch');

async function listDbs() {
    console.log("Fetching database list from https://neuros.odoo.com/jsonrpc...");
    try {
        const response = await fetch("https://neuros.odoo.com/jsonrpc", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    service: 'db',
                    method: 'list',
                    args: [],
                },
                id: 1,
            }),
        });
        const data = await response.json();
        console.log("Response:", data);
    } catch (e) {
        console.error("Error:", e);
    }
}
listDbs();
