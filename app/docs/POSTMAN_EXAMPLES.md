# SAP OData Middleware - Postman Examples

## 📋 Overview

This document provides comprehensive examples for testing the SAP OData Middleware API using Postman. All examples use the real SAP Business Partner entity for consistency.

## 🔧 Setup

### Environment Variables

Create a Postman environment with the following variables:

| Variable      | Description                | Example Value                                              |
| ------------- | -------------------------- | ---------------------------------------------------------- |
| `BASE_URL`    | Base URL of the middleware | `http://localhost:8000`                                    |
| `SAP_SERVER`  | SAP system URL             | `https://intds4.test.apimanagement.us10.hana.ondemand.com` |
| `SAP_SERVICE` | SAP OData service name     | `API_BUSINESS_PARTNER_QAS_220`                             |
| `SAP_ENTITY`  | SAP entity name            | `A_BusinessPartner`                                        |
| `SAP_KEY`     | Test entity key            | `234277`                                                   |

### Headers

Add these headers to your requests:

```
Content-Type: application/json
Accept: application/json
```

## 🚀 API Endpoints

### 1. Health Check

**Endpoint:** `GET {{BASE_URL}}/api/v1/healthcheck`

**Description:** Verifies that the service is active and responding.

**Response (200 OK):**

```json
{
  "data": {
    "status": "ok",
    "message": "Service is running",
    "service": {
      "name": "OData Middleware",
      "environment": "production",
      "uptime": "healthy"
    }
  },
  "metadata": {
    "responseId": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### 2. Execute OData Request

**Endpoint:** `POST {{BASE_URL}}/api/v1/execute-odata`

**Query Parameters:**

- `auth_type`: `basic` or `auto` (default: `basic`)
- `parse_response`: `true` or `false` (default: `true`)

### 2.1. Execute OData Request via Integration Suite

**Endpoint:** `POST {{BASE_URL}}/api/v1/execute-odata-is`

**Query Parameters:**

- `parse_response`: `true` or `false` (default: `true`)

**Headers Required:**

- `apikey` or `x-api-key` or `api-key`: Integration Suite API Key

#### Example 1: Basic Business Partner Query

**Body:**

```json
{
  "http_method": "GET",
  "base_url": "{{SAP_SERVER}}",
  "service_name": "{{SAP_SERVICE}}",
  "source_entity": "{{SAP_ENTITY}}",
  "source_key": "{{SAP_KEY}}",
  "select": "BusinessPartner,BusinessPartnerFullName,BusinessPartnerName,SearchTerm2",
  "filter": "SearchTerm2 eq '{{SAP_KEY}}'"
}
```

**Response (200 OK):**

```json
{
  "data": {
    "status_code": 200,
    "parsed_response": {
      "results": [
        {
          "BusinessPartner": "234277",
          "BusinessPartnerFullName": "Test Business Partner",
          "BusinessPartnerName": "Test Partner",
          "SearchTerm2": "234277"
        }
      ],
      "count": 1
    },
    "raw_response": {
      "d": {
        "results": [
          {
            "__metadata": {
              "id": "https://intds4.test.apimanagement.us10.hana.ondemand.com/API_BUSINESS_PARTNER_QAS_220/A_BusinessPartner('234277')",
              "type": "API_BUSINESS_PARTNER_QAS_220.A_BusinessPartner"
            },
            "BusinessPartner": "234277",
            "BusinessPartnerFullName": "Test Business Partner",
            "BusinessPartnerName": "Test Partner",
            "SearchTerm2": "234277"
          }
        ]
      }
    },
    "auth_type_used": "basic",
    "content_type": "application/json"
  },
  "metadata": {
    "responseId": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

#### Example 2: Business Partner with Navigation Properties

**Body:**

```json
{
  "http_method": "GET",
  "base_url": "{{SAP_SERVER}}",
  "service_name": "{{SAP_SERVICE}}",
  "source_entity": "{{SAP_ENTITY}}",
  "source_key": "{{SAP_KEY}}",
  "navigation_property": [
    {
      "entity": "to_BusinessPartnerBank",
      "key": "10"
    }
  ],
  "select": "BusinessPartner,BusinessPartnerFullName",
  "expand": "to_BusinessPartnerBank"
}
```

#### Example 3: Direct URL Execution

**Body:**

```json
{
  "odata_url": "{{SAP_SERVER}}/{{SAP_SERVICE}}/{{SAP_ENTITY}}?$select=BusinessPartner,BusinessPartnerFullName&$filter=SearchTerm2 eq '{{SAP_KEY}}'",
  "http_method": "GET"
}
```

#### Example 4: XML Response Format

**Body:**

```json
{
  "http_method": "GET",
  "base_url": "{{SAP_SERVER}}",
  "service_name": "{{SAP_SERVICE}}",
  "source_entity": "{{SAP_ENTITY}}",
  "source_key": "{{SAP_KEY}}",
  "format": "xml"
}
```

#### Integration Suite Examples

##### Example IS-1: Basic Business Partner Query via Integration Suite

**Endpoint:** `POST {{BASE_URL}}/api/v1/execute-odata-is`

**Headers:**

```
Content-Type: application/json
Accept: application/json
apikey: YOUR_INTEGRATION_SUITE_API_KEY
```

**Body:**

```json
{
  "http_method": "GET",
  "base_url": "{{SAP_SERVER}}",
  "service_name": "{{SAP_SERVICE}}",
  "source_entity": "{{SAP_ENTITY}}",
  "source_key": "{{SAP_KEY}}",
  "select": "BusinessPartner,BusinessPartnerFullName,BusinessPartnerName,SearchTerm2",
  "filter": "SearchTerm2 eq '{{SAP_KEY}}'"
}
```

**Response (200 OK):**

```json
{
  "data": {
    "status_code": 200,
    "parsed_response": {
      "results": [
        {
          "BusinessPartner": "234277",
          "BusinessPartnerFullName": "Test Business Partner",
          "BusinessPartnerName": "Test Partner",
          "SearchTerm2": "234277"
        }
      ],
      "count": 1
    },
    "raw_response": {
      "d": {
        "results": [...]
      }
    },
    "auth_type_used": "is",
    "content_type": "application/json"
  },
  "metadata": {
    "responseId": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

##### Example IS-2: Direct URL Execution via Integration Suite

**Body:**

```json
{
  "odata_url": "{{SAP_SERVER}}/{{SAP_SERVICE}}/{{SAP_ENTITY}}?$select=BusinessPartner,BusinessPartnerFullName&$filter=SearchTerm2 eq '{{SAP_KEY}}'",
  "http_method": "GET"
}
```

##### Example IS-3: Create Business Partner via Integration Suite

**Body:**

```json
{
  "http_method": "POST",
  "base_url": "{{SAP_SERVER}}",
  "service_name": "{{SAP_SERVICE}}",
  "source_entity": "{{SAP_ENTITY}}",
  "payload": {
    "BusinessPartnerFullName": "New Test Partner IS",
    "BusinessPartnerName": "Test Partner IS",
    "BusinessPartnerType": "2",
    "SearchTerm1": "TEST_IS",
    "SearchTerm2": "123456"
  }
}
```

### 3. Generate OData URL

**Endpoint:** `POST {{BASE_URL}}/api/v1/generate-odata-url`

#### Example 1: Basic URL Generation

**Body:**

```json
{
  "http_method": "GET",
  "base_url": "{{SAP_SERVER}}",
  "service_name": "{{SAP_SERVICE}}",
  "source_entity": "{{SAP_ENTITY}}",
  "source_key": "{{SAP_KEY}}",
  "select": "BusinessPartner,BusinessPartnerFullName,BusinessPartnerName",
  "filter": "SearchTerm2 eq '{{SAP_KEY}}'"
}
```

**Response (200 OK):**

```json
{
  "data": {
    "http_method": "GET",
    "odata_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com/API_BUSINESS_PARTNER_QAS_220/A_BusinessPartner('234277')?$select=BusinessPartner,BusinessPartnerFullName,BusinessPartnerName&$filter=SearchTerm2 eq '234277'"
  },
  "metadata": {
    "responseId": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

#### Example 2: URL with Navigation Properties

**Body:**

```json
{
  "http_method": "GET",
  "base_url": "{{SAP_SERVER}}",
  "service_name": "{{SAP_SERVICE}}",
  "source_entity": "{{SAP_ENTITY}}",
  "source_key": "{{SAP_KEY}}",
  "navigation_property": [
    {
      "entity": "to_BusinessPartnerBank",
      "key": "10"
    }
  ],
  "select": "BusinessPartner,BusinessPartnerFullName"
}
```

**Response (200 OK):**

```json
{
  "data": {
    "http_method": "GET",
    "odata_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com/API_BUSINESS_PARTNER_QAS_220/A_BusinessPartner('234277')/to_BusinessPartnerBank('10')?$select=BusinessPartner,BusinessPartnerFullName"
  },
  "metadata": {
    "responseId": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### 4. Parse OData URL

**Endpoint:** `GET {{BASE_URL}}/api/v1/parse-odata-url`

#### Example 1: Parse Valid URL

**Query Parameters:**

```
full_url: {{SAP_SERVER}}/{{SAP_SERVICE}}/{{SAP_ENTITY}}?$select=BusinessPartner,BusinessPartnerFullName,BusinessPartnerName,PersonFullName,SearchTerm2,to_Supplier,BusinessPartnerGrouping,to_BusinessPartnerBank&$filter=SearchTerm2 eq '{{SAP_KEY}}'
```

**Response (200 OK):**

```json
{
  "data": {
    "is_valid": true,
    "message": "URL parsed successfully",
    "parsed_structure": {
      "base_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com",
      "sap_api_endpoint": "/API_BUSINESS_PARTNER_QAS_220",
      "source_entity": "A_BusinessPartner",
      "source_key": null,
      "select": "BusinessPartner,BusinessPartnerFullName,BusinessPartnerName,PersonFullName,SearchTerm2,to_Supplier,BusinessPartnerGrouping,to_BusinessPartnerBank",
      "filter": "SearchTerm2 eq '234277'"
    }
  },
  "metadata": {
    "responseId": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

#### Example 2: Parse Invalid URL

**Query Parameters:**

```
full_url: not-a-valid-url
```

**Response (200 OK):**

```json
{
  "data": {
    "is_valid": false,
    "message": "Invalid base URL",
    "parsed_structure": null
  },
  "metadata": {
    "responseId": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## 🔄 Advanced Examples

### 1. Complex Navigation Path

**Body for Execute OData:**

```json
{
  "http_method": "GET",
  "base_url": "{{SAP_SERVER}}",
  "service_name": "{{SAP_SERVICE}}",
  "source_entity": "{{SAP_ENTITY}}",
  "source_key": "{{SAP_KEY}}",
  "navigation_property": [
    {
      "entity": "to_BusinessPartnerBank",
      "key": "10"
    },
    {
      "entity": "to_Bank",
      "filter": "BankCountry eq 'US'"
    }
  ],
  "select": "BusinessPartner,BusinessPartnerFullName",
  "expand": "to_BusinessPartnerBank/to_Bank"
}
```

### 2. Pagination and Filtering

**Body:**

```json
{
  "http_method": "GET",
  "base_url": "{{SAP_SERVER}}",
  "service_name": "{{SAP_SERVICE}}",
  "source_entity": "{{SAP_ENTITY}}",
  "select": "BusinessPartner,BusinessPartnerFullName,BusinessPartnerName",
  "filter": "BusinessPartnerType eq '2'",
  "top": 10,
  "skip": 0,
  "orderby": "BusinessPartnerFullName asc",
  "inlinecount": "allpages"
}
```

### 3. Create Business Partner

**Body:**

```json
{
  "http_method": "POST",
  "base_url": "{{SAP_SERVER}}",
  "service_name": "{{SAP_SERVICE}}",
  "source_entity": "{{SAP_ENTITY}}",
  "payload": {
    "BusinessPartnerFullName": "New Test Partner",
    "BusinessPartnerName": "Test Partner",
    "BusinessPartnerType": "2",
    "SearchTerm1": "TEST",
    "SearchTerm2": "123456"
  }
}
```

### 4. Update Business Partner

**Body:**

```json
{
  "http_method": "PATCH",
  "base_url": "{{SAP_SERVER}}",
  "service_name": "{{SAP_SERVICE}}",
  "source_entity": "{{SAP_ENTITY}}",
  "source_key": "{{SAP_KEY}}",
  "payload": {
    "BusinessPartnerFullName": "Updated Test Partner",
    "SearchTerm1": "UPDATED"
  }
}
```

### 5. Delete Business Partner

**Body:**

```json
{
  "http_method": "DELETE",
  "base_url": "{{SAP_SERVER}}",
  "service_name": "{{SAP_SERVICE}}",
  "source_entity": "{{SAP_ENTITY}}",
  "source_key": "{{SAP_KEY}}"
}
```

## 🚨 Error Examples

### 1. Validation Error (422)

**Invalid Request Body:**

```json
{
  "http_method": "GET",
  "base_url": "invalid-url",
  "source_entity": "{{SAP_ENTITY}}"
}
```

**Response (422 Unprocessable Entity):**

```json
{
  "detail": "Invalid base URL"
}
```

### 2. Authentication Error (401)

**Missing Credentials:**

```json
{
  "detail": "SAP username and password are required"
}
```

### 3. Not Found Error (404)

**Non-existent Entity:**

```json
{
  "http_method": "GET",
  "base_url": "{{SAP_SERVER}}",
  "service_name": "{{SAP_SERVICE}}",
  "source_entity": "{{SAP_ENTITY}}",
  "source_key": "99999"
}
```

## 📊 Testing Workflows

### Workflow 1: URL Generation and Execution

1. **Generate URL:**

   - POST to `/api/v1/generate-odata-url`
   - Use the response URL in the next step

2. **Execute Generated URL:**

   - POST to `/api/v1/execute-odata`
   - Use the generated URL in the request body

3. **Parse the URL:**
   - GET to `/api/v1/parse-odata-url`
   - Use the generated URL as the `full_url` parameter

### Workflow 2: Navigation Property Testing

1. **Test Basic Navigation:**

   - Execute request with simple navigation property

2. **Test Complex Navigation:**

   - Execute request with multiple navigation steps

3. **Test Navigation with Filters:**
   - Execute request with navigation filters

### Workflow 3: Error Handling

1. **Test Invalid URLs:**

   - Try parsing malformed URLs

2. **Test Missing Fields:**

   - Send requests with missing required fields

3. **Test Invalid Authentication:**
   - Test with incorrect credentials

## 🔧 Postman Collection

Import the complete Postman collection from `docs/POSTMAN_COLLECTION_EXAMPLE.json` for all these examples in a ready-to-use format.

## 📝 Notes

- All examples use the SAP Business Partner entity for consistency
- The `source_key` field is required for most operations
- Navigation properties support both string (legacy) and JSON array formats
- Response format includes both `data` and `metadata` sections
- Error responses follow standard HTTP status codes
- Authentication is handled automatically by the middleware
