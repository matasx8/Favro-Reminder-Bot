import requests


class favroAPI():
    @staticmethod
    def get_json(headers, email, token, params):
        """
        gets all cards from favro

        Args:

            headers (dict): header for GET request
            email (str): email auth
            token (str): token auth
            params (tuple): parameters for GET request

        Returns:

            dict: json dictionary of card data
        """
        response = requests.get("https://favro.com/api/v1/cards", headers=headers, params=params, auth=(
            email, token))
        if not response.ok:
            return "Response was not ok, try again later"
        recursive = False
        try:
            json = response.json()
        except Exception:
            return "Response was empty, check if get_json parameters are correct"
        else:
            # recursion to concat all pages of cards
            # could be more than 100 cards
            if json["pages"] > 1 and json["page"] != json["pages"] - 1:
                recursive_response_json = favroAPI.get_json(headers, email, token, params + (
                    "requestId", json["requestId"]) + ("page", json["page"] + 1))
                recursive = True
            if recursive:  # concating entities if there was a recursion
                json["entities"] = json["entities"] + \
                    recursive_response_json["entities"]
            return json

    @staticmethod
    def get_users_json(headers, email, token, params=()):
        """
        gets all users from favro

        Args:

            headers (dict): header for GET request
            email (str): email auth
            token (str): token auth
            params (tuple): parameters for GET request

        Returns:

            dict: json dictionary of user data
        """
        response = requests.get("https://favro.com/api/v1/users",
                                headers=headers, params=params, auth=(email, token))
        if not response.ok:
            return "Response was not ok, try again later"
        try:
            json = response.json()
        except Exception:
            return "Response was empty, check if get_users_json parameters are correct"
        else:
            return response.json()

    @staticmethod
    def get_all_columns(headers, email, token, params):
        """
        gets all columns from favro

        Args:

            headers (dict): header for GET request
            email (str): email auth
            token (str): token auth
            params (tuple): parameters for GET request

        Returns:

            dict: json dictionary of column data
        """
        response = requests.get("https://favro.com/api/v1/columns",
                                headers=headers, params=params, auth=(email, token))
        if not response.ok:
            return "Response was not ok, try again later"
        try:
            json = response.json()
        except Exception:
            return "Response was empty, check if get_all_columns parameters are correct"
        else:
            return response.json()
