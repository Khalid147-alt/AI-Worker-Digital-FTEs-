
const { McpServer } = require("@modelcontextprotocol/sdk/server/mcp.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const { z } = require("zod");
const dotenv = require("dotenv");
const OdooClient = require("./odoo_client");

dotenv.config();

const ODOO_URL = process.env.ODOO_URL || "http://localhost:8069";
const ODOO_DB = process.env.ODOO_DB || "odoo";
const ODOO_USER = process.env.ODOO_USER || "admin";
const ODOO_PASSWORD = process.env.ODOO_PASSWORD || "admin";
const DRY_RUN = process.env.DRY_RUN !== 'false'; // Default to true for safety

const client = new OdooClient(ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD);

// Initialize MCP Server
const server = new McpServer({
    name: "odoo-server",
    version: "1.0.0",
});

// Helper to format currency
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
};


// Tool: get_invoices
server.tool(
    "get_invoices",
    "Retrieve a list of invoices based on status and date range.",
    {
        status: z.enum(["draft", "posted", "cancel"]).optional().describe("Invoice status (draft, posted, cancel). Defaults to all."),
        date_from: z.string().optional().describe("Start date (YYYY-MM-DD)."),
        date_to: z.string().optional().describe("End date (YYYY-MM-DD)."),
        limit: z.number().optional().default(10).describe("Max number of records to return."),
    },
    async ({ status, date_from, date_to, limit }) => {
        try {
            const domain = [["move_type", "=", "out_invoice"]]; // Customer Invoices
            if (status) domain.push(["state", "=", status]);
            if (date_from) domain.push(["invoice_date", ">=", date_from]);
            if (date_to) domain.push(["invoice_date", "<=", date_to]);

            const fields = ["name", "partner_id", "invoice_date", "amount_total", "state", "payment_state"];

            const invoices = await client.execute_kw("account.move", "search_read", [domain], {
                fields: fields,
                limit: limit,
                order: "invoice_date desc"
            });

            return {
                content: [{
                    type: "text",
                    text: JSON.stringify(invoices, null, 2)
                }]
            };
        } catch (error) {
            return {
                content: [{ type: "text", text: `Error fetching invoices: ${error.message}` }],
                isError: true,
            };
        }
    }
);


// Tool: create_invoice
server.tool(
    "create_invoice",
    "Create a new customer invoice (Draft).",
    {
        partner_name: z.string().describe("Name of the customer/partner."),
        amount: z.number().describe("Total amount (will be added as a line item 'Service')."),
        description: z.string().describe("Description for the invoice line."),
        due_date: z.string().optional().describe("Due date (YYYY-MM-DD)."),
    },
    async ({ partner_name, amount, description, due_date }) => {
        if (DRY_RUN) {
            return {
                content: [{
                    type: "text",
                    text: `[DRY RUN] Would create invoice for '${partner_name}' amount ${amount} - '${description}'.`
                }]
            };
        }

        try {
            // 1. Find Partner
            const partners = await client.execute_kw("res.partner", "search_read", [[["name", "ilike", partner_name]]], {
                fields: ["id", "name"],
                limit: 1
            });

            if (!partners || partners.length === 0) {
                throw new Error(`Partner '${partner_name}' not found.`);
            }
            const partner_id = partners[0].id;

            // 2. Create Invoice
            const invoice_vals = {
                partner_id: partner_id,
                move_type: 'out_invoice',
                invoice_date: new Date().toISOString().split('T')[0],
                invoice_date_due: due_date || undefined,
                invoice_line_ids: [
                    [0, 0, {
                        name: description,
                        quantity: 1,
                        price_unit: amount,
                    }]
                ]
            };

            const invoice_id = await client.execute_kw("account.move", "create", [invoice_vals]);

            return {
                content: [{
                    type: "text",
                    text: `Successfully created draft invoice ID: ${invoice_id}`
                }]
            };

        } catch (error) {
            return {
                content: [{ type: "text", text: `Error creating invoice: ${error.message}` }],
                isError: true,
            };
        }
    }
);

// Tool: get_transactions
server.tool(
    "get_transactions",
    "Get all account moves (journal entries) for a specific month.",
    {
        month: z.number().min(1).max(12).describe("Month (1-12)"),
        year: z.number().describe("Year (e.g. 2026)")
    },
    async ({ month, year }) => {
        try {
            const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
            // Calculate end date (first day of next month)
            const nextMonth = month === 12 ? 1 : month + 1;
            const nextYear = month === 12 ? year + 1 : year;
            const endDate = `${nextYear}-${String(nextMonth).padStart(2, '0')}-01`;

            const domain = [
                ["date", ">=", startDate],
                ["date", "<", endDate],
                ["state", "=", "posted"]
            ];

            const moves = await client.execute_kw("account.move", "search_read", [domain], {
                fields: ["name", "date", "journal_id", "amount_total", "ref"],
                limit: 50
            });

            return {
                content: [{
                    type: "text",
                    text: JSON.stringify(moves, null, 2)
                }]
            };

        } catch (error) {
            return {
                content: [{ type: "text", text: `Error fetching transactions: ${error.message}` }],
                isError: true,
            };
        }
    }
);

// Tool: get_revenue_summary
server.tool(
    "get_revenue_summary",
    "Calculate total revenue for a specific month.",
    {
        month: z.number().min(1).max(12).describe("Month (1-12)"),
        year: z.number().describe("Year (e.g. 2026)")
    },
    async ({ month, year }) => {
        try {
            // Basic implementation using search_read on account.move where type is out_invoice and state is posted
            const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
            const nextMonth = month === 12 ? 1 : month + 1;
            const nextYear = month === 12 ? year + 1 : year;
            const endDate = `${nextYear}-${String(nextMonth).padStart(2, '0')}-01`;

            const domain = [
                ["move_type", "=", "out_invoice"],
                ["state", "=", "posted"],
                ["invoice_date", ">=", startDate],
                ["invoice_date", "<", endDate]
            ];

            const invoices = await client.execute_kw("account.move", "search_read", [domain], {
                fields: ["amount_untaxed", "amount_total"]
            });

            let total_revenue = 0;
            invoices.forEach(inv => total_revenue += inv.amount_untaxed);

            return {
                content: [{
                    type: "text",
                    text: `Total Revenue for ${month}/${year}: ${formatCurrency(total_revenue)} (from ${invoices.length} invoices)`
                }]
            };

        } catch (error) {
            return {
                content: [{ type: "text", text: `Error calculating revenue: ${error.message}` }],
                isError: true,
            };
        }
    }
);

// Tool: flat_subscription
server.tool(
    "flag_subscription",
    "Flag a vendor bill as a recurring subscription for tracking.",
    {
        vendor_name: z.string().describe("Name of the vendor."),
        reason: z.string().describe("Why this is a subscription (e.g. 'Monthly SaaS').")
    },
    async ({ vendor_name, reason }) => {
        if (DRY_RUN) {
            return {
                content: [{
                    type: "text",
                    text: `[DRY RUN] Would flag vendor '${vendor_name}' as subscription. Reason: ${reason}`
                }]
            };
        }
        // In a real implementation, this might add a tag to the partner or create a recurring entry model
        return {
            content: [{
                type: "text",
                text: `Capability 'flag_subscription' is not fully implemented in Odoo schema yet. Simulating success for '${vendor_name}'.`
            }]
        };
    }
);


const transport = new StdioServerTransport();
server.connect(transport);
