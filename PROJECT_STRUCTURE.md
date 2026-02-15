Now act as a performance and scalability engineer.

Upgrade the project for high-load production usage.

Add:

* caching layer
* broadcast queue worker
* rate limit middleware
* logging and analytics system
* optimized database queries
* anti-spam protection

Explain WHY each optimization is necessary.
Ensure the bot can handle 50,000+ concurrent users.
# Project Structure

```
app/
├── bot/                 # Presentation Layer (Telegram)
│   ├── handlers/        # Thin handlers (No business logic)
│   ├── middlewares/     # Infrastructure (Session management)
│   ├── keyboards/       # UI components
│   └── main.py          # Bot entry point
├── services/            # Service Layer (Business Logic)
│   └── media_service.py # Core logic for Media domain
├── infrastructure/      # Data Access Layer
│   ├── database/        # DB configuration & Models
│   └── repositories/    # Repository Pattern implementation
├── core/                # Configuration & Settings
└── web/                 # Presentation Layer (Admin API)
```
