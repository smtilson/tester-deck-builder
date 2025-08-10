# Test Suite Documentation

This document describes the testing architecture, patterns, and principles for the `fast_backend` application. Our test suite is organized into multiple layers to ensure comprehensive coverage and maintainability.

## Testing Architecture Overview

### Test Organization Structure

```
test_fast_backend/
├── conftest.py              # Global fixtures and configuration
├── base_class.py           # Base test data class for inheritance
├── models/                 # Unit tests for Tortoise ORM models
├── crud/                   # Unit tests for CRUD operations
├── services/               # Unit tests for business logic services
├── auth/                   # Authentication and authorization tests
├── endpoints/              # Integration tests for API endpoints
└── utils/                  # Test utilities and helpers
```

## Testing Stages and Layers

### 1. Unit Tests
**Purpose**: Test individual components in isolation with mocked dependencies.

**Scope**:
- **Models** (`models/`): Test model validation, relationships, and and not business logic (will we even do this?)
- **CRUD Operations** (`crud/`): Test database operations with mocked database
- **Services** (`services/`): Test business logic with mocked external dependencies
- **Utilities**: Test helper functions and utilities

**Characteristics**:
- Fast execution (< 1s per test)
- No external dependencies (database, network, filesystem)
- Heavy use of mocks and fixtures
- Focus on single responsibility testing

### 2. Integration Tests
**Purpose**: Test interactions between components with real or near-real dependencies.

**Scope**:
- **API Endpoints** (`endpoints/`): Test full request/response cycles
- **Authentication Flow** (`auth/`): Test end-to-end auth processes
- **Database Integration**: Test with real test database
- **Service Integration**: Test service interactions

**Characteristics**:
- Moderate execution time (1-5s per test)
- Uses test database and real service instances
- Tests component interactions
- Validates data flow between layers

### 3. End-to-End Tests
**Purpose**: Test complete user workflows from API to database.

**Scope**:
- Complete user registration and authentication flows
- Full CRUD operations through API endpoints
- Cross-service data consistency
- Error handling and edge cases

**Characteristics**:
- Slower execution (5-30s per test)
- Uses full application stack
- Real database with test data
- Simulates actual user interactions

## Testing Principles

### 1. Test Isolation
- Each test should be independent and not rely on other tests
- Use fresh test data for each test
- Clean up resources after each test
- No shared mutable state between tests

### 2. Descriptive Test Names
```python
# Good
def test_create_deck_with_valid_owner_returns_deck_with_correct_attributes():
    pass

# Bad  
def test_create_deck():
    pass
```

### 3. Arrange-Act-Assert (AAA) Pattern
```python
def test_example():
    # Arrange: Set up test data and mocks
    user_data = test_data.get_user_by_username("testuser1")
    
    # Act: Execute the function under test
    result = create_user(user_data)
    
    # Assert: Verify the expected outcome
    assert result.username == user_data["username"]
    assert isinstance(result.id, uuid.UUID)
```

### 4. Mock External Dependencies
- Mock third-party services (email, external APIs)
- Mock database in unit tests
- Use real database only in integration tests
- Mock file system operations

### 5. Test Data Management
- Use `BaseTestData` class for consistent test data
- Create minimal test data for each test
- Use factories for complex object creation
- Keep test data separate from production data

## Pytest Patterns and Conventions

### Class-Based Test Organization
```python
class TestCardCRUD:
    """Tests for card CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_card_success(self):
        pass
    
    @pytest.mark.asyncio 
    async def test_create_card_duplicate_name_fails(self):
        pass
```

### Fixture Usage
```python
# conftest.py
@pytest.fixture
async def test_user():
    """Create a test user for testing."""
    user_data = BaseTestData().get_user_by_username("testuser1")
    user = await User.create(**user_data)
    yield user
    await user.delete()

# test file
class TestUserOperations:
    @pytest.mark.asyncio
    async def test_user_creation(self, test_user):
        assert test_user.username == "testuser1"
```

### Async Test Patterns
```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```

### Parametrized Tests
```python
@pytest.mark.parametrize("input_data,expected", [
    ({"name": "Test Card"}, "Test Card"),
    ({"name": "Another Card"}, "Another Card"),
])
def test_card_name_validation(input_data, expected):
    card = Card(**input_data)
    assert card.name == expected
```

## Test Class Organization

### By Functionality
```python
class TestUserAuthentication:
    """Tests for user authentication flows."""
    pass

class TestUserCRUDOperations:  
    """Tests for user CRUD operations."""
    pass

class TestUserPermissions:
    """Tests for user permission checking."""
    pass
```

### By HTTP Method (for endpoints)
```python
class TestCardEndpointsGET:
    """Tests for GET /cards/* endpoints."""
    pass

class TestCardEndpointsPOST:
    """Tests for POST /cards/* endpoints."""
    pass
```

### By Success/Failure Scenarios
```python
class TestDeckCreationSuccess:
    """Tests for successful deck creation scenarios."""
    pass

class TestDeckCreationFailure:
    """Tests for deck creation failure scenarios."""
    pass
```

## Test Data Strategy

### Base Test Data
- Use `BaseTestData` class from `base_class.py`
- Provides consistent test data across all tests
- Includes users, cards, decks, and deck_cards
- Helper methods for finding specific test objects

### Test Data Inheritance
```python
from test_fast_backend.base_class import BaseTestData

class TestDeckOperations(BaseTestData):
    def setUp(self):
        super().setup_test_data()
        # Additional test-specific setup
    
    def test_deck_creation(self):
        deck_data = self.get_deck_by_name("Red Burn Deck")
        # Use deck_data in test
```

## Database Testing Strategy

### Unit Tests
- Use mocked database operations
- Focus on business logic validation
- Fast execution without database overhead

### Integration Tests  
- Use real test database
- Test actual database constraints and relationships
- Verify data persistence and retrieval

### Database Fixtures
```python
@pytest.fixture(scope="function")
async def clean_db():
    """Ensure clean database state for each test."""
    await clear_test_database()
    yield
    await clear_test_database()
```

## Error Testing Patterns

### Exception Testing
```python
@pytest.mark.asyncio
async def test_create_user_duplicate_username_raises_error():
    user_data = test_data.get_user_by_username("testuser1")
    await User.create(**user_data)
    
    with pytest.raises(IntegrityError):
        await User.create(**user_data)
```

### Validation Testing
```python
def test_deck_invalid_name_validation():
    with pytest.raises(ValidationError):
        DeckCreate(name="", description="Test")
```

## Mock Patterns

### Service Mocking
```python
@pytest.fixture
def mock_email_service():
    with patch('fast_backend.app.services.email.send_email') as mock:
        mock.return_value = True
        yield mock
```

### Database Mocking (for unit tests)
```python
@pytest.fixture
def mock_user_db():
    with patch('fast_backend.app.crud.users.get_user') as mock:
        mock.return_value = test_user_data
        yield mock
```

## Running Tests

### All Tests
```bash
pytest test_fast_backend/
```

### By Category
```bash
# Unit tests only
pytest test_fast_backend/models/ test_fast_backend/crud/ test_fast_backend/services/

# Integration tests only  
pytest test_fast_backend/endpoints/ test_fast_backend/auth/

# Specific test file
pytest test_fast_backend/models/test_users.py
```

### With Coverage
```bash
pytest --cov=fast_backend test_fast_backend/
```

## Test Markers

### Custom Markers
```python
# pytest.ini or conftest.py
pytest_plugins = [
    "pytest_asyncio",
]

# Usage
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration  
@pytest.mark.asyncio
async def test_integration_function():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

### Running by Markers
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Future Considerations

### Test Performance
- Monitor test execution time
- Identify and optimize slow tests
- Consider parallel test execution for large test suites

### Test Coverage Goals
- Aim for >90% code coverage
- Focus on critical business logic paths
- Ensure edge cases are covered

### Continuous Integration
- All tests must pass before merge
- Run different test suites in parallel
- Generate coverage reports
- Fail builds on coverage regression

## Best Practices Summary

1. **Keep tests simple and focused** - One concept per test
2. **Use descriptive test names** - Clearly indicate what is being tested
3. **Follow AAA pattern** - Arrange, Act, Assert
4. **Mock external dependencies** - Keep tests isolated and fast
5. **Use fixtures for setup** - Avoid code duplication
6. **Organize tests logically** - Group related tests in classes
7. **Test edge cases** - Don't just test the happy path
8. **Keep test data minimal** - Only create what's needed for the test
9. **Clean up after tests** - Ensure tests don't affect each other
10. **Document complex test logic** - Help future maintainers understand

This testing strategy ensures comprehensive coverage while maintaining fast, reliable, and maintainable tests that support confident development and deployment of the fast_backend application.
