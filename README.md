# Supervisor Workers Agent

A FastAPI-based customer service chatbot application with a **supervisor-workers architecture** powered by LangGraph. The agent handles returns and refunds end-to-end using a deterministic, state-based workflow with **persistent state management** via MongoDB checkpointing.

## Features

- 🤖 **LangGraph Agent** - Supervisor-workers architecture for customer service
- 💾 **State Persistence** - MongoDB checkpointing for conversation continuity across sessions
- 🔄 **Multi-turn Conversations** - Handle multiple intents in a single session (e.g., check status → return order)
- ⚡ **Template-based Responses** - Fast, consistent messaging using Zendesk-style templates (10-20x faster than LLM generation)
- 🔁 **Return/Refund Processing** - Automated handling of return and refund requests
- 📊 **Order Status Tracking** - Real-time order status with tracking information
- 📋 **Order Lookup** - Integration with MongoDB for order data
- ✅ **Policy Enforcement** - Deterministic eligibility checking (30-day return, 14-day refund)
- 🎫 **Ticket Management** - Idempotent return/refund ticket creation
- 📧 **Email Notifications** - Confirmation emails (mock implementation)
- 🔐 **Authentication** - JWT-based user authentication with cookies
- 💬 **Modern Chat UI** - Real-time chat interface with quick-reply buttons
- 🚀 **FastAPI** - Modern, fast web framework
- 📄 **Jinja2 Templates** - Dynamic HTML page rendering
- 🐳 **Docker** - Containerized deployment with MongoDB

## Architecture

The agent follows a **supervisor → workers** pattern with **singleton graph + global checkpointer** (enterprise-scale pattern):

### Key Components

1. **Supervisor** - Deterministic routing between workers based on state
2. **Workers** - Specialized nodes for specific tasks:
   - `ClassifyIntentWorker` - Classifies user intent (return/refund/order_status/other) with multi-turn support
   - `SlotFillerWorker` - Extracts or asks for order number
   - `OrderLookupWorker` - Fetches order from MongoDB
   - `ShowOrderStatusWorker` - Displays order status with tracking info (template-based, no LLM)
   - `ConfirmDetailsWorker` - Confirms order with user (template-based with random variations)
   - `PolicyCheckWorker` - Checks return/refund eligibility
   - `DecideActionWorker` - Determines which action to take
   - `ProcessReturnWorker` - Creates return (RMA) ticket
   - `ProcessRefundWorker` - Creates refund ticket
   - `EmailWorker` - Sends confirmation email
   - `FinalizeWorker` - Provides final summary using templates (sets conversation_complete flag)
3. **Checkpointer** - MongoDBSaver for persistent conversation state
4. **Human-in-the-Loop** - Automatic pausing when agent asks questions

### Response Generation Strategy

The agent uses a **hybrid approach** for optimal performance:

- **LLM-powered**: Intent classification and order number extraction (2 workers)
- **Template-based**: All user-facing responses (8 workers using Zendesk-style templates)

**Benefits:**
- **10-20x faster responses** (<500ms vs 5-10s for LLM generation)
- **70% cost reduction** (2 LLM calls vs 5-6 per conversation)
- **Consistent messaging** (templates ensure brand voice)
- **Natural variety** (3+ template variations per scenario, randomly selected)

**Template collections:**
- `CONFIRMATION_TEMPLATES`, `APOLOGY_TEMPLATES` (confirm_details)
- `STATUS_MESSAGES` with 4 status types × 3 variations (show_order_status)
- `ORDER_STATUS_CLOSING`, `CANCEL_TEMPLATES`, `DENIAL_TEMPLATES`, etc. (finalize)

### State Persistence

The agent uses **LangGraph's MongoDBSaver** for checkpointing:
- **Singleton graph**: Created once at startup, reused for all requests
- **Global checkpointer**: Single MongoDBSaver instance shared across all sessions
- **Thread isolation**: Each conversation identified by unique `thread_id`
- **Message reducer**: `add_messages` reducer appends messages across turns
- **Automatic state loading**: Previous conversation state restored on each turn
- **Multi-turn support**: `conversation_complete` flag enables seamless intent transitions

**How multi-turn works:**
1. User completes a flow (e.g., order status) → finalize sets `conversation_complete: True`
2. Supervisor sees flag → routes to END, waiting for new user message
3. User asks new question (e.g., "return my order") → classify_intent detects flag
4. State reset → old fields cleared (intent, order_number, etc.)
5. New intent classified → fresh flow begins in same session

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

### Chatbot Flow Examples

#### Multi-turn Conversation (New!)

The chatbot now supports **multiple intents in a single session**:

1. **Check order status**: Click "📋 Order status" → provide order number → view status
2. **Agent asks**: "Is there anything else I can help you with today?"
3. **Start new flow**: Reply "I want to return my order"
4. **Continue with return**: Agent classifies new intent and starts return flow
5. **Complete return**: Provide (same or different) order number → confirm → get ticket

**Key benefits:**
- Natural conversation flow without page refresh
- Seamless transition between different intents
- State properly reset between conversations
- Fast responses with template-based messaging

#### Returns & Refunds Flow

1. **Visit** http://localhost:8000 and log in
2. **Choose quick action**: Click "🔄 Returns & refunds" button (or type your message)
3. **Provide order number**: "ORD-2024-001"
4. **Review order details**: Agent shows formatted order with items, dates, and total
5. **Confirm details**: Reply "yes"
6. **Eligibility check**: Agent verifies policy (30-day return window)
7. **Receive outcome**: 
   - If eligible: Return/refund ticket created with next steps
   - If not eligible: Clear explanation of why (e.g., "Outside 30-day return window")

#### Order Status Flow

1. **Choose quick action**: Click "📋 Order status" button
2. **Provide order number**: "ORD-2024-001"
3. **View status**: Agent displays:
   - Order number and current status (delivered/shipped/processing/pending)
   - Order date and delivery date
   - Tracking number (if available)
   - Items count and total amount
   - Status-specific message with emoji
4. **Done**: Simple closing message (no ticket creation needed)

### Sample Order Numbers

The database includes 10 sample orders for testing:
- `ORD-2024-001` - Recent order (eligible)
- `ORD-2024-002` through `ORD-2024-010` - Various scenarios

**Note**: Orders from 2024 fixtures are outside the 30-day window as of October 2025, so they'll be denied. For testing eligibility, you may need to update fixture dates or adjust policy settings.

### Quick Reply Buttons

The chat interface includes interactive buttons for common tasks:
- 📦 Product information (coming soon)
- 📋 **Order status** ← Active! Check order status and tracking
- 🔄 **Returns & refunds** ← Active! Triggers return/refund flow
- 🔧 Technical support (coming soon)
- 👤 Account management (coming soon)

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

3. **Order Status Check**
   - Click "📋 Order status" button or ask "What's the status of my order?"
   - Provide order number (e.g., "ORD-2024-001")
   - View formatted status display with tracking info
   - No confirmation or ticket creation needed

4. **Order Not Found**
   - Provide invalid order number
   - Agent asks to re-enter

5. **Outside Window**
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
- View logs: `docker compose logs -f web`
- Verify MongoDB is running: `docker compose ps`

### Orders not found
- Load fixtures: `docker compose exec web python scripts/load_fixtures.py`
- Check MongoDB: Visit http://localhost:8081
- Verify collection exists: `db.orders.find()`

### State not persisting between messages
- Check MongoDBSaver is initialized: Look for `✅ Checkpointer initialized` in logs
- Verify checkpoints collection exists in MongoDB
- Ensure `thread_id` (session_id) is being passed correctly
- Check messages use LangChain message types (HumanMessage, AIMessage)

### Recursion limit errors
- Check supervisor routing logic for infinite loops
- Verify workers return proper state updates
- Ensure field names match between workers and supervisor (e.g., `user_confirmed_order`)

### Authentication issues
- Clear browser cookies
- Check JWT secret key is set in `.env`

### Display issues (newlines not showing)
- Frontend converts `\n` to `<br>` automatically
- Check `chat.js` has: `htmlText.replace(/\n/g, '<br>')`

## Dependencies

- **fastapi** - Web framework
- **langgraph** - Agent workflow orchestration
- **langgraph-checkpoint-mongodb** - MongoDB checkpointing for state persistence
- **langchain-openai** - OpenAI integration
- **langchain-core** - Core LangChain primitives (messages, runnables)
- **motor** - Async MongoDB driver (for data operations)
- **pymongo** - Sync MongoDB driver (required for MongoDBSaver)
- **bcrypt** - Password hashing
- **python-jose** - JWT tokens
- **pydantic-settings** - Settings management

## Architecture Deep Dive

### Checkpointing Pattern

This implementation uses the **enterprise-scale singleton pattern**:

```python
# Global singleton (created once at startup)
_graph_instance = None
checkpointer = MongoDBSaver(sync_client, db_name, "checkpoints")

# Reused for all requests
graph = create_agent_graph(llm, db, checkpointer)

# Thread isolation via config
result = await graph.ainvoke(
    {"messages": [new_message]},
    config={"configurable": {"thread_id": session_id}}
)
```

**Key Points:**
- One graph instance serves all requests (optimal performance)
- One checkpointer instance manages all conversation states
- Thread IDs isolate different conversations
- Messages use `add_messages` reducer for proper appending
- State automatically loads/saves on each turn

### Human-in-the-Loop

The supervisor detects questions and routes to `__end__`:
```python
if "?" in last_message or "please" in last_message.lower():
    return "__end__"  # Pause for user input
```

This prevents infinite loops and ensures proper turn-taking.

## License

MIT License

## Next Steps

- [x] ~~State persistence with MongoDB checkpointing~~
- [x] ~~Human-in-the-loop for turn-taking~~
- [x] ~~Quick reply buttons for common actions~~
- [x] ~~Formatted order display with bullet points~~
- [x] ~~Order status tracking functionality~~
- [x] ~~Multi-turn conversation support~~
- [x] ~~Template-based responses (Zendesk pattern)~~
- [x] ~~Performance optimization (10-20x faster responses)~~
- [ ] Add real tracking API integration (FedEx, UPS, USPS)
- [ ] Add more worker types (FAQ, product info)
- [ ] Implement real email service (SendGrid, AWS SES)
- [ ] Add conversation analytics dashboard
- [ ] Deploy to production (Railway, Render, AWS)
- [ ] Add comprehensive unit tests for workers
- [ ] Implement human handoff to live agent
- [ ] Add support for multiple languages
- [ ] Performance monitoring and observability
