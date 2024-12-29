"""
This module implements a simple JSON-RPC 2.0 server.

It includes functions to handle basic arithmetic operations such as addition,
subtraction, and summation, as well as error handling for invalid requests.

The 'transport' is assumed to be stdin/stdout, where requests are read from

"""

import sys
import json


class RPCError(Exception):
    """
    Exception raised for errors in the RPC call.

    Attributes:
        code -- error code
        message -- explanation of the error
        id -- id of the request that caused the error
    """

    def __init__(self, code, id=None):
        self.code = code
        self.message = self.get_message()
        self.id = id

    def get_message(self):
        """
        Return the error message based on the error code.
        """
        if self.code == -32600:
            return "Invalid Request"
        elif self.code == -32601:
            return "Method not found"
        elif self.code == -32602:
            return "Invalid parameters"
        elif self.code == -32700:
            return "Parse error"
        else:
            return "Internal error"


def sum_method(params):
    """
    Sum the list of parameters.

    Args:
        params (list): List of numbers to sum.

    Returns:
        int: Sum of the numbers.

    Raises:
        RPCError: If parameters are invalid.
    """
    try:
        if isinstance(params, list):
            return sum(params)
        else:
            raise RPCError(code=-32602)
    except Exception:
        raise RPCError(code=-32602)


def add(params, id=None):
    """
    Add two numbers.

    Args:
        params (list): List containing two numbers.
        id (optional): ID of the request.

    Returns:
        int: Sum of the two numbers.

    Raises:
        RPCError: If parameters are invalid.
    """
    try:
        if isinstance(params, list):
            return params[0] + params[1]
        else:
            raise RPCError(code=-32602, id=id)
    except Exception:
        raise RPCError(code=-32602, id=id)


def subtract(params, id=None):
    """
    Subtract one number from another.

    Args:
        params (dict or list): Dictionary with 'minuend' and 'subtrahend' keys or list containing two numbers.
        id (optional): ID of the request.

    Returns:
        int: Result of the subtraction.

    Raises:
        RPCError: If parameters are invalid.
    """
    try:
        if isinstance(params, dict):
            return params["minuend"] - params["subtrahend"]
        elif isinstance(params, list):
            return params[0] - params[1]
        else:
            raise RPCError(code=-32602, id=id)
    except Exception:
        raise RPCError(code=-32602, id=id)


def handle_request(request):
    """
    Handle an RPC request.

    Args:
        request (str): JSON-RPC request string.

    Returns:
        str: JSON-RPC response string.
    """
    try:
        req = json.loads(request)
        if (
            "jsonrpc" not in req
            or req["jsonrpc"] != "2.0"
            or "method" not in req
            or "id" not in req
        ):
            raise RPCError(code=-32600)

        method = req["method"]
        params = req.get("params", [])
        response = {"jsonrpc": "2.0", "id": req["id"]}

        if method == "add":
            response["result"] = add(params)
        elif method == "sum":
            response["result"] = sum_method(params)
        elif method == "subtract":
            response["result"] = subtract(params, req["id"])
        else:
            response["error"] = {"code": -32601, "message": "Method not found"}

    except json.JSONDecodeError:
        response = {
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"},
            "id": None,
        }
    except RPCError as e:
        response = {
            "jsonrpc": "2.0",
            "error": {"code": e.code, "message": e.message},
            "id": e.id,
        }

    return json.dumps(response)


def main():
    """
    Main function to read requests from stdin and print responses to stdout.
    """
    for line in sys.stdin:
        response = handle_request(line)
        print(response)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
