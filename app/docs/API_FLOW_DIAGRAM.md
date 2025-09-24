# SAP OData Middleware - Diagrama de Flujo Básico

## 📊 Flujo General del API

```mermaid
flowchart TD
    A[Cliente] --> B[FastAPI App]
    B --> C{Endpoint?}

    C -->|GET /healthcheck| D[Health Check]
    C -->|POST /execute-odata| E[Execute OData]
    C -->|POST /execute-odata-is| E2[Execute OData IS]
    C -->|POST /generate-odata-url| F[Generate URL]
    C -->|GET /parse-odata-url| G[Parse URL]

    D --> D1[Return Service Status]
    D1 --> Z[Response]

    E --> E1[Process Request]
    E1 --> E2[Call SAP]
    E2 --> E3[Process Response]
    E3 --> Z

    E2 --> E2A[Process IS Request]
    E2A --> E2B[Call Integration Suite]
    E2B --> E2C[Process IS Response]
    E2C --> Z

    F --> F1[Build URL]
    F1 --> Z

    G --> G1[Parse URL]
    G1 --> Z

    Z --> H[Client]
```

## 🔄 Flujo Detallado por Endpoint

### 1. Health Check (`GET /healthcheck`)

```mermaid
flowchart LR
    A[Client Request] --> B[Health Check]
    B --> C[Return Status]
    C --> D[Service Info]
    D --> E[Response to Client]
```

**Funcionalidad:**

- Verifica que el servicio esté activo
- Retorna información del estado del sistema
- No requiere parámetros
- Respuesta inmediata

### 2. Execute OData (`POST /execute-odata`)

```mermaid
flowchart TD
    A[Client Request] --> B{Request Type?}

    B -->|ExecuteODataRequest| C[Direct URL]
    B -->|ODataRequest| D[Structured Request]

    C --> E[Build Request URL]
    D --> F[Build OData URL]
    F --> E

    E --> G[Get SAP Headers]
    G --> H[Execute HTTP Request]
    H --> I[SAP System]
    I --> J[Process Response]
    J --> K[Return Response]
    K --> L[Client]
```

**Funcionalidad:**

- Ejecuta peticiones OData a SAP
- Soporta requests estructurados y URLs directas
- Maneja autenticación automática
- Procesa respuestas JSON/XML
- Maneja errores de SAP

### 3. Execute OData Integration Suite (`POST /execute-odata-is`)

```mermaid
flowchart TD
    A[Client Request] --> B{Request Type?}

    B -->|ExecuteODataRequest| C[Direct URL]
    B -->|ODataRequest| D[Structured Request]

    C --> E[Build Request URL]
    D --> F[Build OData URL]
    F --> E

    E --> G[Get API Key Headers]
    G --> H[Execute HTTP Request]
    H --> I[Integration Suite]
    I --> J[Process Response]
    J --> K[Return Response]
    K --> L[Client]
```

**Funcionalidad:**

- Ejecuta peticiones OData a través de SAP Integration Suite
- Usa autenticación por API Key en lugar de Basic Auth
- Optimizado para entornos de Integration Suite
- Filtra automáticamente headers de API Key
- Procesa respuestas con identificador "is"

### 4. Generate OData URL (`POST /generate-odata-url`)

```mermaid
flowchart LR
    A[Structured Parameters] --> B[Build URL Components]
    B --> C[Combine URL Parts]
    C --> D[Generate Full URL]
    D --> E[Return URL]
    E --> F[Client]
```

**Funcionalidad:**

- Convierte parámetros estructurados en URL OData
- Maneja navegación simple y compleja
- Incluye todos los parámetros de consulta
- Retorna URL lista para usar

### 4. Parse OData URL (`GET /parse-odata-url`)

```mermaid
flowchart LR
    A[OData URL] --> B[Parse Components]
    B --> C[Extract Service Info]
    C --> D[Map Query Parameters]
    D --> E[Return Structure]
    E --> F[Client]
```

**Funcionalidad:**

- Analiza URLs OData completas
- Extrae componentes individuales
- Valida estructura de la URL
- Retorna información estructurada

## 🎯 Casos de Uso Principales

```mermaid
flowchart TD
    A[Cliente] --> B{Use Case?}

    B -->|Query Data| C[Execute OData GET]
    B -->|Create Data| D[Execute OData POST]
    B -->|Update Data| E[Execute OData PATCH/PUT]
    B -->|Delete Data| F[Execute OData DELETE]
    B -->|Build URL| G[Generate OData URL]
    B -->|Analyze URL| H[Parse OData URL]
    B -->|Check Status| I[Health Check]

    C --> J[SAP Response]
    D --> K[Created Entity]
    E --> L[Updated Entity]
    F --> M[Deletion Status]
    G --> N[Generated URL]
    H --> O[Parsed Structure]
    I --> P[Service Status]

    J --> Q[Client]
    K --> Q
    L --> Q
    M --> Q
    N --> Q
    O --> Q
    P --> Q
```

## 🔐 Autenticación y Seguridad

```mermaid
flowchart TD
    A[Request] --> B{Auth Type?}

    B -->|basic| C[Basic Auth]
    B -->|auto| D[Auto Auth]

    C --> E[Username/Password]
    D --> F[Auto Credentials]

    E --> G[SAP Headers]
    F --> G

    G --> H[SAP Request]
```

## 📊 Procesamiento de Respuestas

```mermaid
flowchart TD
    A[SAP Response] --> B{Response Type?}

    B -->|Success| C[Parse Response]
    B -->|Error| D[Handle Error]

    C --> E{Format?}
    E -->|JSON| F[Parse JSON]
    E -->|XML| G[Parse XML]

    F --> H[Extract Data]
    G --> H

    H --> I[Format Response]
    I --> J[Return to Client]

    D --> K[Error Response]
    K --> J
```

## 🚨 Manejo de Errores

```mermaid
flowchart TD
    A[Request] --> B{Validation?}

    B -->|Pass| C[Continue]
    B -->|Fail| D[422 Error]

    C --> E{Execution?}
    E -->|Success| F[Return Success]
    E -->|Fail| G{Error Type?}

    G -->|401| H[Auth Error]
    G -->|403| I[Permission Error]
    G -->|404| J[Not Found]
    G -->|500+| K[Server Error]

    D --> L[Client]
    H --> L
    I --> L
    J --> L
    K --> L
    F --> L
```

## 📋 Resumen de Endpoints

| Endpoint              | Método | Función                            | Entrada                    | Salida                  |
| --------------------- | ------ | ---------------------------------- | -------------------------- | ----------------------- |
| `/helpcheck`          | GET    | Health Check                       | Ninguna                    | Estado del servicio     |
| `/execute-odata`      | POST   | Ejecutar OData (SAP Directo)       | Request estructurado o URL | Respuesta de SAP        |
| `/execute-odata-is`   | POST   | Ejecutar OData (Integration Suite) | Request estructurado o URL | Respuesta de SAP via IS |
| `/generate-odata-url` | POST   | Generar URL                        | Parámetros estructurados   | URL OData completa      |
| `/parse-odata-url`    | GET    | Parsear URL                        | URL OData                  | Estructura parseada     |

## 🔄 Flujo de Datos General

```mermaid
flowchart LR
    A[Cliente] --> B[FastAPI]
    B --> C[Business Logic]
    C --> D[SAP System]
    D --> E[Response Parser]
    E --> F[Formatted Response]
    F --> A
```

## 🎯 Beneficios del Middleware

- **Simplificación**: Convierte requests complejos en simples
- **Estandarización**: Respuestas consistentes
- **Autenticación**: Manejo automático de credenciales SAP
- **Flexibilidad**: Soporta múltiples formatos de entrada
- **Validación**: Verificación automática de parámetros
- **Error Handling**: Manejo consistente de errores

---

## 📝 Notas

- Todos los endpoints retornan respuestas en formato JSON/XML estándar
- La autenticación se maneja automáticamente
- Los errores se formatean de manera consistente
- El middleware actúa como puente entre clientes y SAP
- Soporta operaciones CRUD completas
- Maneja navegación simple y compleja en OData
