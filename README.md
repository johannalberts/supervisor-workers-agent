# Supervisor Workers Agent

A FastAPI-based customer service chatbot application with a **supervisor-workers architecture** powered by LangGraph. The agent handles returns and refunds end-to-end using a deterministic, state-based workflow.

## Features

- 🤖 **LangGraph Agent** - Supervisor-workers architecture for customer service
- 🔄 **Return/Refund Processing** - Automated handling of return and refund requests
- 📋 **Order Lookup** - Integration with MongoDB for order data
- ✅ **Policy Enforcement** - Deterministic eligibility checking
- 🎫 **Ticket Management** - Idempotent return/refund ticket creation
- 📧 **Email Notifications** - Confirmation emails (mock implementation)
- 🔐 **Authentication** - JWT-based user authentication with cookies
- 💬 **Modern Chat UI** - Real-time chat interface
- 🚀 **FastAPI** - Modern, fast web framework
- 📄 **Jinja2 Templates** - Dynamic HTML page rendering
- 🐳 **Docker** - Containerized deployment with MongoDB

## Architecture

The agent follows a **supervisor → workers** pattern:

1. **Supervisor** - Routes between workers based on state
2. **Workers** - Specialized nodes for specific tasks:
   - `ClassifyIntentWorker` - Classifies user intent (return/refund/other)
   - `SlotFillerWorker` - Extracts or asks for order number
   - `OrderLookupWorker` - Fetches order from MongoDB
   - `ConfirmDetailsWorker` - Confirms order with user
   - `PolicyCheckWorker` - Checks return/refund eligibility
   - `DecideActionWorker` - Determines which action to take
   - `ProcessReturnWorker` - Creates return (RMA) ticket
   - `ProcessRefundWorker` - Creates refund ticket
   - `EmailWorker` - Sends confirmation email
   - `FinalizeWorker` - Provides final summary

See [AGENT-INFO.md](AGENT-INFO.md) for detailed specifications.

## Project Structure

```
supervisor-workers-agent/
├── app/
│   ├── agent/              # LangGraph agent implementation
│   │   ├── models.py       # State schema and Pydantic models
│   │   ├── policy.py       # Pure policy functions
│   │   ├── supervisor.py   # Routing logic
│   │   ├── graph.py        # LangGraph workflow
│   │   └── workers/        # Worker nodes
│   ├── core/               # Core functionality
│   │   ├── config.py       # Settings
│   │   ├── database.py     # MongoDB connection
│   │   └── auth.py         # Authentication
│   ├── routers/            # API routes
│   │   ├── api.py          # JSON API endpoints
│   │   ├── pages.py        # HTML pages
│   │   └── auth.py         # Auth endpoints
│   ├── services/           # Business logic
│   │   └── agent_service.py # Agent orchestration
│   └── models/             # Data models
├── templates/              # Jinja2 templates
├── static/                 # CSS, JS, images
├── scripts/                # Utility scripts
└── docker-compose.yml      # Docker configuration
```

## Installation

### Prerequisites

- Python 3.12 or higher
- Docker & Docker Compose
- OpenAI API key
- uv (recommended) or pip

### Setup

1. **Clone the repository**

2. **Copy environment file and add your OpenAI API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Start with Docker (recommended):**
   ```bash
   docker compose up -d --build
   ```

   This starts:
   - **Web App**: http://localhost:8000
   - **MongoDB**: localhost:27017
   - **Mongo Express**: http://localhost:8081

4. **Load sample order data:**
   ```bash
   # The fixtures are loaded automatically on first run
   # Or manually load them:
   docker compose exec web python scripts/load_fixtures.py
   ```

### Local Development (without Docker)

```bash
# Install dependencies
uv sync

# Start MongoDB locally or update MONGODB_URL in .env

# Run the application
python run.py
```

## Usage

### Chatbot Flow Example

1. **Visit** http://localhost:8000 and log in
2. **Start conversation**: "I want to return my order"
3. **Provide order number**: "ORD-20241001-001"
4. **Confirm details**: "Yes"
5. **Receive ticket**: The agent creates a return ticket and provides next steps

### Sample Order Numbers

The database includes 10 sample orders:
- `ORD-20241001-001` through `ORD-20241001-010`

Try them to test different eligibility scenarios!

### API Endpoints

#### Chat Endpoint
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "I want to return my order",
  "session_id": "optional-session-id"
}
```

#### Get Conversation History
```bash
GET /api/session/{session_id}/history
```

## Configuration

Key settings in `.env`:

```bash
# OpenAI (Required)
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o-mini

# MongoDB
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB_NAME=chatbot

# JWT Authentication
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Policy Configuration

Edit `app/agent/policy.py` to customize:

- `DEFAULT_RETURN_WINDOW_DAYS` - Default return window (30 days)
- `DEFAULT_REFUND_WINDOW_DAYS` - Default refund window (14 days)
- `CATEGORY_OVERRIDES` - Category-specific windows

## Testing

### Test Scenarios

1. **Happy Path (Return)**
   - "I want to return my order"
   - Provide order number within 30-day window
   - Confirm details
   - Receive return ticket

2. **Refund Request**
   - "Can I get a refund?"
   - Provide order number within 14-day window
   - Complete refund flow

3. **Order Not Found**
   - Provide invalid order number
   - Agent asks to re-enter

4. **Outside Window**
   - Use old order (>30 days)
   - Agent explains ineligibility

## Development

### Adding New Workers

1. Create worker file in `app/agent/workers/`
2. Implement async function: `async def your_worker(state: AgentState) -> Dict[str, Any]`
3. Add to `app/agent/graph.py`
4. Update supervisor routing in `app/agent/supervisor.py`

### Modifying Policy

Edit `app/agent/policy.py` - all policy logic is pure functions (easy to test).

## Monitoring

### View Logs
```bash
docker compose logs -f web
```

### Access MongoDB
- **Mongo Express UI**: http://localhost:8081 (admin/admin123)
- **Direct connection**: `mongodb://localhost:27017`

### Inspect Sessions
```bash
# View conversation sessions
docker compose exec mongodb mongosh chatbot --eval "db.conversation_sessions.find().pretty()"

# View action tickets
docker compose exec mongodb mongosh chatbot --eval "db.action_tickets.find().pretty()"
```

## Deployment

See [DOCKER.md](DOCKER.md) for production deployment guide.

## Troubleshooting

### Agent not responding
- Check OpenAI API key is set correctly in `.env`
- View logs: `docker compose logs web`
- Verify MongoDB is running: `docker compose ps`

### Orders not found
- Load fixtures: `docker compose exec web python scripts/load_fixtures.py`
- Check MongoDB: Visit http://localhost:8081

### Authentication issues
- Clear browser cookies
- Check JWT secret key is set in `.env`

## Dependencies

- **fastapi** - Web framework
- **langgraph** - Agent workflow orchestration
- **langchain-openai** - OpenAI integration
- **motor** - Async MongoDB driver
- **pymongo** - MongoDB driver
- **bcrypt** - Password hashing
- **python-jose** - JWT tokens

## License

MIT License

## Next Steps

- [ ] Add more worker types (FAQ, product info)
- [ ] Implement real email service
- [ ] Add conversation analytics
- [ ] Deploy to production
- [ ] Add unit tests for workers
- [ ] Implement human handoff
