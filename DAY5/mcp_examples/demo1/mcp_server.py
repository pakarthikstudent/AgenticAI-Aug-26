from mcp.server.fastmcp import FastMCP


# Create MCP Server
mcp = FastMCP("CustomerTools")


@mcp.tool()
def get_customer(customer_id: int):
    """Get customer details using customer ID."""

    customers = {
        101: {
            "name": "John",
            "city": "Bangalore",
            "status": "Active"
        },
        102: {
            "name": "Alice",
            "city": "Mumbai",
            "status": "Inactive"
        }
    }

    return customers.get(
        customer_id,
        {"error": "Customer not found"}
    )


@mcp.tool()
def get_orders(customer_id: int):
    """Get orders for a customer."""

    orders = {
        101: [
            {
                "order_id": 5001,
                "product": "Laptop",
                "status": "Delivered"
            },
            {
                "order_id": 5002,
                "product": "Mobile",
                "status": "Shipped"
            }
        ],
        102: [
            {
                "order_id": 5003,
                "product": "Headphones",
                "status": "Delivered"
            }
        ]
    }

    return orders.get(customer_id, [])


if __name__ == "__main__":
    mcp.run()
