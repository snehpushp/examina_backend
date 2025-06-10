"""
This file will provide necessary and repetitive functions
"""
from typing import List


class HelperFunctions:
    """
    This whole class will contain mostly static methods which can be used to perform some common operations
    Creating class for easier imports
    """

    @staticmethod
    def order_result(result, order, key):
        """
        This function will order the result based on the order provided.
        :param result: List of objects to be ordered
        :param order: List using which it needs to be ordered
        :param key: Key of object based on which it needs to be ordered
        :return: List of objects in the order provided
        """
        # Note that, key is the attribute of the result object based on which it needs to be ordered
        return sorted(result, key=lambda x: order.index(getattr(x, key)))

    @staticmethod
    def order_response(response: List[tuple]):
        """
        This function will order the response based on the order provided.
        :param response: List of tuples to be ordered. 1st is the object, 2nd is the order key
        :return: List of objects in the order provided
        """
        # Note that, key is the attribute of the result object based on which it needs to be ordered
        response = sorted(response, key=lambda x: x[1])
        return [x[0] for x in response]


# This object can be used to access the helper functions
helper_functions = HelperFunctions()
