# SAP OData Middleware - Test Suite

## 📋 Overview

This test suite validates the core functionality of the SAP OData Middleware API, including request execution, URL generation, parsing, navigation properties, error handling, and response processing.

## 🏗️ Test Structure

### Core Test Files

- **`test_middleware_core.py`** - Core functionality tests
- **`test_navigation_property.py`** - Navigation property handling
- **`test_error_handling.py`** - Error scenarios and edge cases
- **`test_response_processing.py`** - Response format processing
- **`test_integration_scenarios.py`** - End-to-end workflows
- **`test_debug.py`** - Debug utilities for troubleshooting

### Test Configuration

- **`conftest.py`** - Global test configuration and fixtures
- **`__init__.py`** - Package initialization

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Install test dependencies
pip install pytest pytest-mock pytest-cov
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_middleware_core.py

# Run specific test
pytest tests/test_middleware_core.py::TestCoreMiddlewareFunctionality::test_execute_odata_request_success
```

## 🧪 Test Data

### Real SAP Entity Used

All tests use the **SAP Business Partner** entity with the following configuration:

- **Base URL**: `https://intds4.test.apimanagement.us10.hana.ondemand.com`
- **Service**: `API_BUSINESS_PARTNER_QAS_220`
- **Entity**: `A_BusinessPartner`
- **Test Key**: `234277`

### Example Test URL

```
https://intds4.test.apimanagement.us10.hana.ondemand.com/API_BUSINESS_PARTNER_QAS_220/A_BusinessPartner?$select=BusinessPartner,BusinessPartnerFullName,BusinessPartnerName,PersonFullName,SearchTerm2,to_Supplier,BusinessPartnerGrouping,to_BusinessPartnerBank&$filter=SearchTerm2 eq '234277'
```

## 🔧 Test Configuration

### Global Authentication Mocking

The test suite automatically mocks SAP authentication for all tests using a global fixture:

```python
@pytest.fixture(autouse=True)
def patch_sap_auth():
    """Mock global de sap_auth para todos los tests"""
    with patch('app.bussiness_logic.post_business_logic.sap_auth') as mock_auth:
        mock_auth.get_basic_auth_headers.return_value = {
            "Authorization": "Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ=",
            "sap-client": "100",
            "sap-language": "EN",
            "Content-Type": "application/json"
        }
        # ... more mock configuration
        yield mock_auth
```

### Environment Variables

Test environment variables are automatically configured:

```python
os.environ['SAP_USERNAME'] = 'test_user'
os.environ['SAP_PASSWORD'] = 'test_password'
os.environ['SAP_CLIENT'] = '100'
os.environ['SAP_LANGUAGE'] = 'EN'
```

## 📊 Test Coverage

### Core Functionality Tests

| Test                                 | Description                                  | Status |
| ------------------------------------ | -------------------------------------------- | ------ |
| `test_execute_odata_request_success` | Validates successful OData request execution | ✅     |
| `test_url_generation_functionality`  | Tests URL generation from parameters         | ✅     |
| `test_url_parsing_functionality`     | Tests URL parsing and validation             | ✅     |
| `test_health_check_endpoint`         | Validates health check endpoint              | ✅     |

### Navigation Property Tests

| Test                                        | Description                           | Status |
| ------------------------------------------- | ------------------------------------- | ------ |
| `test_execute_request_with_json_navigation` | Tests JSON navigation property format | ✅     |
| `test_legacy_string_navigation`             | Tests legacy string navigation format | ✅     |
| `test_url_generation_with_navigation`       | Tests URL generation with navigation  | ✅     |

### Error Handling Tests

| Test                               | Description                         | Status |
| ---------------------------------- | ----------------------------------- | ------ |
| `test_sap_connection_error`        | Tests SAP connection error handling | ✅     |
| `test_malformed_odata_url_parsing` | Tests malformed URL parsing         | ✅     |

### Response Processing Tests

| Test                             | Description                    | Status |
| -------------------------------- | ------------------------------ | ------ |
| `test_json_response_processing`  | Tests JSON response processing | ✅     |
| `test_xml_response_processing`   | Tests XML response processing  | ✅     |
| `test_error_response_processing` | Tests error response handling  | ✅     |

### Integration Tests

| Test                                       | Description                               | Status |
| ------------------------------------------ | ----------------------------------------- | ------ |
| `test_complete_sales_order_workflow`       | Tests complete business partner workflow  | ✅     |
| `test_url_generation_and_parsing_workflow` | Tests URL generation and parsing workflow | ✅     |

## 🔍 Debugging Tests

### Debug Test File

Use `test_debug.py` for troubleshooting specific issues:

```bash
# Run debug test with output
pytest tests/test_debug.py::test_debug_validation_error -v -s
```

### Common Issues

1. **422 Unprocessable Entity**: Usually indicates validation errors in request data
2. **Authentication Errors**: Check that the global mock is working correctly
3. **Import Errors**: Ensure all dependencies are installed

## 📝 Test Data Examples

### Request Data Structure

```json
{
  "http_method": "GET",
  "base_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com",
  "service_name": "API_BUSINESS_PARTNER_QAS_220",
  "source_entity": "A_BusinessPartner",
  "source_key": "234277",
  "select": "BusinessPartner,BusinessPartnerFullName,BusinessPartnerName",
  "filter": "SearchTerm2 eq '234277'"
}
```

### Navigation Property Examples

```json
{
  "navigation_property": [
    {
      "entity": "to_BusinessPartnerBank",
      "key": "10"
    }
  ]
}
```

### Expected Response Structure

```json
{
    "data": {
        "status_code": 200,
        "parsed_response": {...},
        "raw_response": {...}
    },
    "metadata": {
        "responseId": "...",
        "timestamp": "..."
    }
}
```

## 🚀 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.12
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-mock pytest-cov
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## 📚 Additional Resources

- [SAP OData Documentation](https://help.sap.com/doc/odp_1903_apiref/en-US/index.html)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest Documentation](https://docs.pytest.org/)

## 🤝 Contributing

When adding new tests:

1. Follow the existing naming conventions
2. Use the real SAP Business Partner entity for consistency
3. Include proper error handling tests
4. Update this README with new test descriptions
5. Ensure all tests pass before submitting

## 📞 Support

For test-related issues:

1. Check the debug test output
2. Review the test configuration in `conftest.py`
3. Verify environment variables are set correctly
4. Ensure all dependencies are installed
