import aiohttp
import typing

class AmariError(Exception):
    """
    Base class for exceptions raised with the Amari API."""
    
class HTTPException(AmariError):
    """Base Exception for HTTP errors."""
    def __init__(self, response: aiohttp.ClientResponse.status, message: typing.Optional[str] = None):
        self.response: aiohttp.ClientResponse = response
        message = f"({response}): {message}" if message else f"({self.status})"
        super().__init__(message)

class NotFoundError(AmariError):
    """
    An exception raised when the Amari API returns a 404 status code
    indicating the object requested was not found."""
    def __init__(self, response: aiohttp.ClientResponse.status, message: typing.Optional[str] = "Requested Guild/User was not found"):
        super().__init__(response, message)
    
class RatelimitedError(AmariError):
    """
    An exception raised when the API returns a 429 status code
    indicating that the user is currently ratelimited."""
    def __init__(self, response: aiohttp.ClientResponse.status, message: typing.Optional[str] = "You are being ratelimited by the API. Please try again later."):
        super().__init__(response, message)
    
class APIError(AmariError):
    """
    An exception raised when the Amari API returns a 500 status code
    indicating that theres an issue with the API due to which the request could not be completed."""
    def __init__(self, response: aiohttp.ClientResponse.status, message: typing.Optional[str] = "The request couldn't be resolved due to an error with the Amari API. Try again later."):
        super().__init__(response, message)