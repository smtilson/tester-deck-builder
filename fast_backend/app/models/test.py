from beanie import Document

class TestDocument(Document):
    """A simple test document to verify database connection."""
    value: str

    class Settings:
        name = "test_documents"
