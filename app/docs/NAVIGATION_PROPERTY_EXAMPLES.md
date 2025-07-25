# Navigation Property - Nuevo Formato JSON

## 📋 Resumen

La API ahora soporta `navigation_property` en formato JSON para navegaciones complejas y múltiples niveles, manteniendo compatibilidad con el formato string original.

## 🔄 Formato Anterior vs Nuevo

### **Formato Anterior (String)**

```json
{
  "navigation_property": "to_Items/to_Product"
}
```

### **Nuevo Formato (JSON Array)**

```json
{
  "navigation_property": [
    { "entity": "to_Items", "key": "10" },
    { "entity": "to_Product", "filter": "Category eq 'ELECTRONICS'" }
  ]
}
```

## 🎯 Ejemplos de Uso

### 1. **Navegación Simple**

```json
{
  "http_method": "GET",
  "base_url": "https://sap-server.com",
  "service_name": "API_SALES_ORDER_SRV",
  "source_entity": "A_SalesOrder",
  "source_key": "5001",
  "navigation_property": [{ "entity": "to_Items" }]
}
```

**URL Generada:** `A_SalesOrder('5001')/to_Items`

### 2. **Navegación con Clave**

```json
{
  "http_method": "GET",
  "base_url": "https://sap-server.com",
  "service_name": "API_SALES_ORDER_SRV",
  "source_entity": "A_SalesOrder",
  "source_key": "5001",
  "navigation_property": [{ "entity": "to_Items", "key": "10" }]
}
```

**URL Generada:** `A_SalesOrder('5001')/to_Items('10')`

### 3. **Navegación Múltiple**

```json
{
  "http_method": "GET",
  "base_url": "https://sap-server.com",
  "service_name": "API_SALES_ORDER_SRV",
  "source_entity": "A_SalesOrder",
  "source_key": "5001",
  "navigation_property": [
    { "entity": "to_Items", "key": "10" },
    { "entity": "to_Product" }
  ]
}
```

**URL Generada:** `A_SalesOrder('5001')/to_Items('10')/to_Product`

### 4. **Navegación con Filtros**

```json
{
  "http_method": "GET",
  "base_url": "https://sap-server.com",
  "service_name": "API_SALES_ORDER_SRV",
  "source_entity": "A_SalesOrder",
  "source_key": "5001",
  "navigation_property": [
    { "entity": "to_Items", "filter": "Status eq 'ACTIVE'" },
    { "entity": "to_Product", "filter": "Category eq 'ELECTRONICS'" }
  ]
}
```

**URL Generada:** `A_SalesOrder('5001')/to_Items?$filter=Status eq 'ACTIVE'/to_Product?$filter=Category eq 'ELECTRONICS'`

### 5. **Claves Compuestas**

```json
{
  "http_method": "GET",
  "base_url": "https://sap-server.com",
  "service_name": "API_BUSINESS_PARTNER",
  "source_entity": "A_BusinessPartner",
  "source_key": "12345",
  "navigation_property": [
    {
      "entity": "to_Supplier",
      "key": { "BusinessPartner": "12345", "Supplier": "12345" }
    }
  ]
}
```

**URL Generada:** `A_BusinessPartner('12345')/to_Supplier(BusinessPartner='12345',Supplier='12345')`

## 🔧 Casos de Uso Reales

### **Caso 1: Obtener Items de una Orden**

```python
import requests

request_body = {
    "http_method": "GET",
    "base_url": "https://sap-server.com",
    "service_name": "API_SALES_ORDER_SRV",
    "source_entity": "A_SalesOrder",
    "source_key": "5001",
    "navigation_property": [
        {"entity": "to_Items"}
    ]
}

response = requests.post(
    "http://localhost:8000/api/v1/execute-odata",
    json=request_body,
    params={"auth_type": "basic", "parse_response": "true"}
)
```

### **Caso 2: Obtener Producto de un Item Específico**

```python
request_body = {
    "http_method": "GET",
    "base_url": "https://sap-server.com",
    "service_name": "API_SALES_ORDER_SRV",
    "source_entity": "A_SalesOrder",
    "source_key": "5001",
    "navigation_property": [
        {"entity": "to_Items", "key": "10"},
        {"entity": "to_Product"}
    ]
}
```

### **Caso 3: Actualizar Supplier de Business Partner**

```python
request_body = {
    "http_method": "PUT",
    "base_url": "https://sap-server.com",
    "service_name": "API_BUSINESS_PARTNER",
    "source_entity": "A_BusinessPartner",
    "source_key": "12345",
    "navigation_property": [
        {
            "entity": "to_Supplier",
            "key": {"BusinessPartner": "12345", "Supplier": "12345"}
        }
    ],
    "payload": {
        "SupplierName": "Updated Supplier Name",
        "SupplierType": "VENDOR"
    }
}
```

## 📊 Comparación de Formatos

| Característica        | Formato String  | Formato JSON   |
| --------------------- | --------------- | -------------- |
| **Simplicidad**       | ✅ Simple       | ⚠️ Más verboso |
| **Claves**            | ❌ No soportado | ✅ Soportado   |
| **Filtros**           | ❌ No soportado | ✅ Soportado   |
| **Múltiples niveles** | ✅ Básico       | ✅ Avanzado    |
| **Validación**        | ❌ Limitada     | ✅ Completa    |
| **Legibilidad**       | ⚠️ Media        | ✅ Alta        |

## 🔄 Migración

### **Antes:**

```json
{
  "navigation_property": "to_Items/to_Product"
}
```

### **Después (Opcional):**

```json
{
  "navigation_property": [{ "entity": "to_Items" }, { "entity": "to_Product" }]
}
```

**Nota:** El formato string sigue siendo compatible para casos simples.

## ⚠️ Consideraciones

1. **Compatibilidad:** El formato string original sigue funcionando
2. **Validación:** El formato JSON tiene validación automática
3. **Rendimiento:** Ambos formatos tienen el mismo rendimiento
4. **Documentación:** El formato JSON es más autodocumentado

## 🧪 Testing

### **Test con Postman:**

```json
{
  "http_method": "GET",
  "base_url": "{{SAP_SERVER}}",
  "service_name": "API_SALES_ORDER_SRV",
  "source_entity": "A_SalesOrder",
  "source_key": "{{LAST_SALES_ORDER_ID}}",
  "navigation_property": [
    { "entity": "to_Items", "key": "10" },
    { "entity": "to_Product" }
  ]
}
```

### **Test de Validación:**

```javascript
pm.test("Navigation property is processed correctly", function () {
  const response = pm.response.json();
  pm.expect(response.status_code).to.equal(200);
  pm.expect(response.response.success).to.be.true;
});
```

## 📚 Referencias

- [OData Navigation Properties](https://www.odata.org/getting-started/basic-tutorial/#NavigationProperties)
- [SAP OData Navigation](https://help.sap.com/doc/saphelp_gateway20sp12/2.0/en-US/76/bf7c506aa8134e8aa745b0a08f9d16/content.htm)
