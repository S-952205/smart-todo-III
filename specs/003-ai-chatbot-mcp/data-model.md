# Data Model: AI Chatbot & MCP Integration

## New Entities

### Conversation Model
- **Entity Name**: Conversation
- **Fields**:
  - id: UUID (primary key, auto-generated)
  - user_id: String (foreign key to User, indexed for performance)
  - title: String (summary of conversation topic, optional)
  - created_at: DateTime (timestamp when conversation started)
  - updated_at: DateTime (timestamp of last message)
- **Validation Rules**:
  - user_id must reference existing user
  - created_at defaults to current timestamp
  - updated_at updates on any conversation activity
- **Relationships**:
  - Belongs to User (many-to-one)
  - Has many Messages (one-to-many)

### Message Model
- **Entity Name**: Message
- **Fields**:
  - id: UUID (primary key, auto-generated)
  - conversation_id: UUID (foreign key to Conversation, indexed)
  - role: String (either "user" or "assistant", required)
  - content: Text (the actual message content, required)
  - timestamp: DateTime (when message was sent)
  - metadata: JSON (optional, for storing tool calls, etc.)
- **Validation Rules**:
  - conversation_id must reference existing conversation
  - role must be either "user" or "assistant"
  - content must not be empty
  - timestamp defaults to current time
- **Relationships**:
  - Belongs to Conversation (many-to-one)
  - Conversation has many Messages (one-to-many)

## Updated Existing Entities

### User Model
- **Additional Relationships**:
  - Has many Conversations (one-to-many)

### Task Model
- **No structural changes required**
- **Additional validation considerations**:
  - Ensure all chat-initiated task operations maintain user isolation
  - Log task operations initiated via chat for audit purposes

## State Transitions

### Conversation States
- Active: New conversation created or recent activity
- Inactive: No activity for extended period (defined by business rule)
- Archived: User requested archive or system cleanup

### Message States
- Pending: Message created but not yet processed by AI
- Processing: AI is currently generating response
- Completed: Both user message and AI response are stored
- Error: Failed to process message (with error details in metadata)

## Database Constraints

### Primary Keys
- All entities use UUID primary keys for consistency
- Auto-generation ensures uniqueness across distributed systems

### Foreign Keys
- conversation_id in Message references Conversation.id
- user_id in Conversation references User.id
- Proper indexing on all foreign key columns for performance

### Indexes
- Index on Conversation.user_id for efficient user-based queries
- Index on Message.conversation_id for efficient conversation-based queries
- Composite index on Message.timestamp + Message.conversation_id for chronological ordering

## Data Integrity Rules

### Referential Integrity
- All foreign key relationships enforced at database level
- Cascade deletion: When Conversation is deleted, all associated Messages are removed
- No orphaned Messages allowed (must belong to existing Conversation)

### User Isolation
- Conversation.user_id must match authenticated user for access
- Message access limited to messages in conversations belonging to user
- All chat operations enforce JWT-based user validation

## Migration Strategy

### Alembic Configuration
- target_metadata = SQLModel.metadata in env.py
- Autogenerate migrations to detect new models
- Preserve existing tables during migration
- Run migration in transaction to ensure atomicity

### Migration Steps
1. Generate migration script for Conversation and Message models
2. Apply migration to create new tables
3. Verify existing tables remain unchanged
4. Update application to use new models