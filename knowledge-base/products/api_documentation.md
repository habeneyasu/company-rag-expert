# API Documentation

## Overview

Our platform provides comprehensive RESTful APIs for integrating with our products and services. All APIs follow REST principles and return JSON responses.

## Base URL

```
Production: https://api.company.com/v1
Sandbox: https://api-sandbox.company.com/v1
```

## Authentication

### API Keys
All API requests require authentication using API keys.

```http
Authorization: Bearer YOUR_API_KEY
```

### Getting API Keys
1. Log in to your account
2. Navigate to Settings > API Keys
3. Generate a new API key
4. Store securely (keys are only shown once)

### Rate Limits
- **Free Tier**: 100 requests per minute
- **Professional**: 1,000 requests per minute
- **Enterprise**: 10,000 requests per minute

## Common Endpoints

### Health Check
Check API status and availability.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2024.1",
  "timestamp": "2024-01-20T10:00:00Z"
}
```

## CRM API

### Get Contacts
Retrieve a list of contacts.

```http
GET /crm/contacts
```

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `limit` (integer): Results per page (default: 20, max: 100)
- `search` (string): Search term
- `filter` (object): Filter criteria

**Response:**
```json
{
  "data": [
    {
      "id": "123",
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0123",
      "company": "Acme Corp",
      "created_at": "2024-01-15T08:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

### Create Contact
Create a new contact.

```http
POST /crm/contacts
```

**Request Body:**
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+1-555-0456",
  "company": "Tech Solutions",
  "tags": ["prospect", "enterprise"]
}
```

**Response:**
```json
{
  "id": "124",
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+1-555-0456",
  "company": "Tech Solutions",
  "created_at": "2024-01-20T10:00:00Z"
}
```

### Update Contact
Update an existing contact.

```http
PUT /crm/contacts/{id}
```

### Delete Contact
Delete a contact.

```http
DELETE /crm/contacts/{id}
```

## ERP API

### Get Products
Retrieve product inventory.

```http
GET /erp/products
```

**Query Parameters:**
- `category` (string): Filter by category
- `status` (string): Filter by status (active, inactive)
- `page`, `limit`: Pagination

**Response:**
```json
{
  "data": [
    {
      "id": "PROD-001",
      "name": "Widget A",
      "sku": "WID-A-001",
      "price": 99.99,
      "quantity": 150,
      "category": "Electronics",
      "status": "active"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45
  }
}
```

### Create Order
Create a new sales order.

```http
POST /erp/orders
```

**Request Body:**
```json
{
  "customer_id": "CUST-123",
  "items": [
    {
      "product_id": "PROD-001",
      "quantity": 5,
      "price": 99.99
    }
  ],
  "shipping_address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "zip": "94102",
    "country": "USA"
  }
}
```

## Analytics API

### Get Reports
Retrieve analytics reports.

```http
GET /analytics/reports
```

### Create Custom Report
Generate a custom analytics report.

```http
POST /analytics/reports/custom
```

**Request Body:**
```json
{
  "name": "Sales Report Q1",
  "metrics": ["revenue", "orders", "customers"],
  "dimensions": ["date", "region", "product"],
  "filters": {
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-03-31"
    }
  }
}
```

## Error Handling

### Error Response Format
All errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {},
    "timestamp": "2024-01-20T10:00:00Z"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

### Example Error Response
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Contact with ID '123' not found",
    "details": {
      "resource": "contact",
      "id": "123"
    },
    "timestamp": "2024-01-20T10:00:00Z"
  }
}
```

## Webhooks

### Setting Up Webhooks
Configure webhooks to receive real-time notifications.

```http
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://your-server.com/webhook",
  "events": ["contact.created", "order.updated"],
  "secret": "your_webhook_secret"
}
```

### Webhook Payload
```json
{
  "event": "contact.created",
  "timestamp": "2024-01-20T10:00:00Z",
  "data": {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

## SDKs and Libraries

### Official SDKs
- **Python**: `pip install company-api-python`
- **JavaScript/Node.js**: `npm install @company/api-client`
- **Java**: Available via Maven Central
- **PHP**: Available via Composer

### Example Usage (Python)
```python
from company_api import Client

client = Client(api_key='YOUR_API_KEY')

# Get contacts
contacts = client.crm.contacts.list(limit=10)

# Create contact
new_contact = client.crm.contacts.create(
    name="John Doe",
    email="john@example.com"
)
```

## Best Practices

### Rate Limiting
- Implement exponential backoff for retries
- Monitor rate limit headers
- Use webhooks instead of polling when possible

### Security
- Never commit API keys to version control
- Use environment variables for API keys
- Rotate API keys regularly
- Use HTTPS for all requests

### Performance
- Use pagination for large datasets
- Implement caching where appropriate
- Use field selection to reduce payload size
- Batch operations when possible

## Support

### API Support
- **Documentation**: https://docs.company.com/api
- **Status Page**: https://status.company.com
- **Support Email**: api-support@company.com
- **Community Forum**: https://community.company.com

---

**Document Owner**: Engineering Team  
**Last Updated**: 2024-01-20  
**Version**: 2.3
