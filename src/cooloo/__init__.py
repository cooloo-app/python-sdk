"""cooloo: Python API and launcher for the bundled GUI+CLI client."""
from .client import Client, CoolooError, Message, MessageStream, SendOutcomeUnknown, SentResult

__version__ = "0.1.7"
__all__ = ["Client", "CoolooError", "Message", "MessageStream", "SendOutcomeUnknown", "SentResult"]
