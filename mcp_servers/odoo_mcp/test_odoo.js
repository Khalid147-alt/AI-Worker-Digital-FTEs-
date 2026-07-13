require('dotenv').config({ path: '../../.env' });
const OdooClient = require('./odoo_client');

const ODOO_URL = process.env.ODOO_URL || "http://localhost:8069";
const ODOO_DB = process.env.ODOO_DB || "odoo";
const ODOO_USER = process.env.ODOO_USER || "admin";
const ODOO_PASSWORD = process.env.ODOO_PASSWORD || "admin";

async function testOdoo() {
    console.log(`Connecting to Odoo: ${ODOO_URL}, DB: ${ODOO_DB}, User: ${ODOO_USER}`);
    try {
        const client = new OdooClient(ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD);

        // Try a simple search_read to test connection
        console.log("Testing connection by fetching 1 partner...");
        const partners = await client.execute_kw("res.partner", "search_read", [[]], {
            fields: ["id", "name"],
            limit: 1
        });

        console.log("Success! Found partner:", partners[0].name);
    } catch (err) {
        console.error("Odoo connection failed:", err.message || err);
    }
}

testOdoo();
