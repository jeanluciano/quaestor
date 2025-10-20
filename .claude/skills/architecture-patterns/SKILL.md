---
name: Architecture Patterns
description: Common architecture patterns including MVC, DDD, Microservices, Clean Architecture, and more. Use when designing system architecture or choosing architectural approaches.
---

# Architecture Patterns

## Purpose
Provides comprehensive guide to common architecture patterns, their use cases, and implementation strategies.

## When to Use
- Designing new system architecture
- Evaluating architectural approaches
- Refactoring existing architecture
- Understanding design trade-offs
- Making architectural decisions
- Documenting system design

## Pattern Overview

### When to Use Each Pattern

```yaml
pattern_selection:
  MVC:
    use_when: "Building web applications with clear UI separation"
    complexity: "Low to Medium"
    team_size: "Small to Medium"

  Domain-Driven Design:
    use_when: "Complex business logic, large enterprise systems"
    complexity: "High"
    team_size: "Medium to Large"

  Microservices:
    use_when: "Need independent scaling, large distributed teams"
    complexity: "Very High"
    team_size: "Large"

  Clean Architecture:
    use_when: "Long-term maintainability is critical"
    complexity: "Medium to High"
    team_size: "Any"

  Monolithic:
    use_when: "Starting new project, small team, simple requirements"
    complexity: "Low to Medium"
    team_size: "Small to Medium"
```

## 1. Model-View-Controller (MVC)

### Description
Separates application into three interconnected components: Model (data), View (presentation), Controller (logic).

### Structure
```yaml
mvc:
  Model:
    responsibility: "Data and business logic"
    files:
      - "models/user.py"
      - "models/product.py"
    concerns:
      - Database schema
      - Business rules
      - Data validation

  View:
    responsibility: "User interface and presentation"
    files:
      - "templates/user_list.html"
      - "templates/product_detail.html"
    concerns:
      - HTML/UI rendering
      - User interaction
      - Display logic

  Controller:
    responsibility: "Handle requests and coordinate"
    files:
      - "controllers/user_controller.py"
      - "controllers/product_controller.py"
    concerns:
      - Request routing
      - Business logic orchestration
      - Response formatting
```

### Pros & Cons
```yaml
pros:
  - Simple to understand
  - Clear separation of concerns
  - Easy to test
  - Good for web applications

cons:
  - Can become tightly coupled
  - Controllers can grow large
  - Not ideal for complex business logic
  - Views may contain logic
```

### Use Cases
- Web applications
- Admin dashboards
- CRUD applications
- Content management systems

## 2. Domain-Driven Design (DDD)

### Description
Focuses on modeling complex business domains with rich domain models and ubiquitous language.

### Layered Architecture
```yaml
ddd_layers:
  Domain Layer:
    path: "/domain"
    description: "Pure business logic, no external dependencies"
    components:
      Entities:
        description: "Objects with identity and lifecycle"
        example: "User, Order, Product"

      Value Objects:
        description: "Immutable objects defined by values"
        example: "Money, Address, Email"

      Aggregates:
        description: "Cluster of entities treated as unit"
        example: "Order (contains OrderItems)"

      Domain Services:
        description: "Business logic spanning multiple entities"
        example: "PricingService, ShippingCalculator"

      Domain Events:
        description: "Something that happened in domain"
        example: "OrderPlaced, PaymentReceived"

  Application Layer:
    path: "/application"
    description: "Use case orchestration"
    components:
      Application Services:
        description: "Coordinate domain objects"
        example: "PlaceOrderService"

      DTOs:
        description: "Data transfer objects"
        example: "OrderDTO, UserDTO"

      Command Handlers:
        description: "Handle commands from outside"
        example: "CreateOrderHandler"

  Infrastructure Layer:
    path: "/infrastructure"
    description: "Technical implementations"
    components:
      Repositories:
        description: "Database access"
        example: "UserRepository"

      External Services:
        description: "Third-party integrations"
        example: "PaymentGateway"

      Adapters:
        description: "Interface implementations"
        example: "EmailAdapter"

  Presentation Layer:
    path: "/presentation"
    description: "API/UI layer"
    components:
      Controllers:
        description: "Handle HTTP requests"
        example: "OrderController"

      Views:
        description: "UI templates"
        example: "order_form.html"
```

### DDD Building Blocks
```yaml
tactical_patterns:
  Entity:
    definition: "Object with unique identity"
    example: |
      class User:
          def __init__(self, user_id, email):
              self.id = user_id
              self.email = email

  Value Object:
    definition: "Immutable object defined by values"
    example: |
      @dataclass(frozen=True)
      class Money:
          amount: Decimal
          currency: str

  Aggregate:
    definition: "Consistency boundary, transaction scope"
    example: |
      class Order:  # Aggregate Root
          def __init__(self):
              self.items = []  # Internal entities

          def add_item(self, product, quantity):
              self.items.append(OrderItem(product, quantity))

  Repository:
    definition: "Abstraction for data access"
    example: |
      class UserRepository(ABC):
          @abstractmethod
          def find_by_id(self, user_id: UserId) -> User:
              pass

  Domain Service:
    definition: "Stateless operations on domain objects"
    example: |
      class PricingService:
          def calculate_order_total(self, order: Order) -> Money:
              pass
```

### Pros & Cons
```yaml
pros:
  - Handles complex business logic well
  - Clear domain boundaries
  - Promotes ubiquitous language
  - Highly testable
  - Good for large systems

cons:
  - High learning curve
  - Can be overkill for simple apps
  - Requires domain expertise
  - More boilerplate code
  - Needs buy-in from team
```

### Use Cases
- Complex business systems
- Enterprise applications
- Long-lived projects
- Systems with evolving requirements

## 3. Microservices Architecture

### Description
Application as suite of small, independent services communicating over network.

### Structure
```yaml
microservices:
  service_characteristics:
    - Independent deployment
    - Own database per service
    - Loose coupling
    - Technology diversity
    - Business capability focus

  services:
    - name: "User Service"
      responsibility: "User management"
      database: "users_db"
      api: "users-api.example.com"

    - name: "Order Service"
      responsibility: "Order processing"
      database: "orders_db"
      api: "orders-api.example.com"

    - name: "Payment Service"
      responsibility: "Payment processing"
      database: "payments_db"
      api: "payments-api.example.com"

  communication:
    synchronous:
      - "REST APIs"
      - "gRPC"

    asynchronous:
      - "Message queues (RabbitMQ, Kafka)"
      - "Event bus"

  infrastructure:
    - "API Gateway"
    - "Service Discovery (Consul, Eureka)"
    - "Load Balancers"
    - "Circuit Breakers"
    - "Distributed Tracing"
```

### Pros & Cons
```yaml
pros:
  - Independent scaling
  - Technology flexibility
  - Isolated failures
  - Easy to understand individual services
  - Parallel development

cons:
  - Operational complexity
  - Network overhead
  - Distributed system challenges
  - Data consistency issues
  - More difficult testing
  - Requires DevOps expertise
```

### Use Cases
- Large-scale applications
- Teams needing independence
- Different scaling requirements
- Polyglot systems

## 4. Clean Architecture

### Description
Dependency rule: dependencies point inward. Business logic independent of frameworks and external concerns.

### Layers
```yaml
clean_architecture:
  Entities (Center):
    description: "Enterprise business rules"
    depends_on: "Nothing"
    example: "User, Order (pure business objects)"

  Use Cases:
    description: "Application business rules"
    depends_on: "Entities"
    example: "PlaceOrder, RegisterUser"

  Interface Adapters:
    description: "Convert data between use cases and external"
    depends_on: "Use Cases"
    example: "Controllers, Presenters, Gateways"

  Frameworks & Drivers:
    description: "External tools and frameworks"
    depends_on: "Interface Adapters"
    example: "Web framework, Database, UI"
```

### Dependency Rule
```
┌─────────────────────────────┐
│   Frameworks & Drivers      │
│  ┌───────────────────────┐  │
│  │  Interface Adapters   │  │
│  │  ┌─────────────────┐  │  │
│  │  │   Use Cases     │  │  │
│  │  │  ┌───────────┐  │  │  │
│  │  │  │ Entities  │  │  │  │
│  │  │  └───────────┘  │  │  │
│  │  └─────────────────┘  │  │
│  └───────────────────────┘  │
└─────────────────────────────┘

Dependencies always point INWARD
```

### Pros & Cons
```yaml
pros:
  - Framework independent
  - Highly testable
  - Database independent
  - UI independent
  - Clean separation of concerns

cons:
  - More files and interfaces
  - Steeper learning curve
  - Can feel over-engineered for simple apps
  - More boilerplate
```

### Use Cases
- Long-term projects
- Complex business logic
- Need to switch frameworks/databases
- High testability requirements

## 5. Layered Architecture

### Description
Traditional three-tier architecture with presentation, business, and data layers.

### Structure
```yaml
layers:
  Presentation:
    description: "UI and user interaction"
    components:
      - Web pages
      - API controllers
      - Mobile app UI

  Business Logic:
    description: "Core application logic"
    components:
      - Services
      - Business rules
      - Workflows

  Data Access:
    description: "Database and external data"
    components:
      - Repositories
      - ORM models
      - Database queries

  Cross-Cutting:
    description: "Shared concerns"
    components:
      - Logging
      - Security
      - Caching
      - Error handling
```

### Pros & Cons
```yaml
pros:
  - Simple and well-understood
  - Easy to implement
  - Clear separation
  - Good for standard applications

cons:
  - Can become tightly coupled
  - Changes ripple through layers
  - Not ideal for complex domains
  - Can lead to anemic models
```

## 6. Event-Driven Architecture

### Description
Components communicate through events, promoting loose coupling and scalability.

### Structure
```yaml
event_driven:
  components:
    Event Producers:
      - Publish events
      - Don't know about consumers

    Event Bus:
      - Message broker (Kafka, RabbitMQ)
      - Routes events to consumers

    Event Consumers:
      - Subscribe to events
      - React to events independently

  patterns:
    Event Notification:
      description: "Notify when something happened"
      example: "UserRegistered"

    Event-Carried State Transfer:
      description: "Event contains full state"
      example: "OrderCompleted with all order data"

    Event Sourcing:
      description: "Store all changes as events"
      example: "All order state changes stored"

    CQRS:
      description: "Separate read and write models"
      example: "Write via commands, read via queries"
```

### Pros & Cons
```yaml
pros:
  - Loose coupling
  - Scalable
  - Event history/audit trail
  - Asynchronous processing
  - Easy to add new consumers

cons:
  - Eventual consistency
  - Complex debugging
  - Event versioning challenges
  - Requires message infrastructure
```

## Decision Matrix

```yaml
choose_pattern_based_on:
  project_size:
    small: "Monolithic, MVC"
    medium: "Layered, Clean Architecture"
    large: "DDD, Microservices"

  team_size:
    small: "Monolithic, Layered"
    medium: "Clean Architecture, DDD"
    large: "Microservices, DDD"

  business_complexity:
    low: "MVC, Layered"
    medium: "Clean Architecture"
    high: "DDD"

  scalability_needs:
    low: "Monolithic"
    medium: "Layered, Clean"
    high: "Microservices, Event-Driven"

  deployment_frequency:
    low: "Monolithic"
    medium: "Modular Monolith"
    high: "Microservices"
```

---
*Use this skill when making architectural decisions or designing system structure*
