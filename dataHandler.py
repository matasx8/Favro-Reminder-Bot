class dataHandler():
    @staticmethod
    def extract_cards_from_json(json, hour_limit):
        """
        Extracts cards from a given column json

        Args:

            json (dict): json dictionary of a column

        Returns:

            dict: json card dictionary
        """
        new_json = dict()
        timelimit = 3600000 * hour_limit + 1  # ms in an hour * hours in 3 days
        for entity in json["entities"]:
            time_on_column = entity["timeOnColumns"]["eabf7b078e3586e75de71d98"]
            if time_on_column < timelimit:
                continue
            card_name = entity["name"]
            card_id = entity["cardId"]
            # assignments can be multiple
            user_ids = list()
            for assignment in entity["assignments"]:
                user_ids.append(assignment["userId"])
            new_json[card_name] = {
                "card_id": card_id, "time_on_column": time_on_column, "user_ids": user_ids}
        return new_json

    @staticmethod
    def extract_users_from_json(json, list_of_assigned_users):
        """
        Gets user data that match given list of users by their user id

        Args:

            json (dict): json dictionary of user data
            list_of_assigned_users (list): list of user ids that have tasks assigned

        Returns:

            dict: json dictionary of assigned users with their corresponding data
        """
        new_json = dict()
        for entity in json["entities"]:
            user_id = entity["userId"]
            for user in list_of_assigned_users:
                if user_id == user:
                    # new_json[user_id] = {
                    #   "name": entity["name"], "email": "YOUREMAIL@gmail.com", "tasks": []}
                    new_json[user_id] = {
                        "name": entity["name"], "email": entity["email"], "tasks": []}  # WARNING WILL SEND EMAILS TO THIS ADRESS
        return new_json

    @staticmethod
    def extract_unique_assigned_users_from_json(json):
        """
        Extracts unique users from json

        Args:

            json (dict): json dictionary of user ids

        Returns:

            list: list of unique user ids
        """
        list_all = []
        for users in json.values():
            for user in users["user_ids"]:
                list_all.append(user)
        return list(set(list_all))

    @staticmethod
    def merge_user_data_and_cards(data, cards):
        """
        merge json of user data and card data for email sender

        Args:

            data (dict): json dictionary of user data
            cards (dict): json dictionary of card data

        Returns:

            dict: json dictionary of assigned users with their corresponding data
        """
        for card, card_name in zip(cards.values(), cards):
            for cards_user_id in card["user_ids"]:
                for user_id in data:
                    if cards_user_id == user_id:
                        # for each user id the must be a list with their task names
                        data[user_id]["tasks"].append(card_name)
                        break
        return data

    @staticmethod
    def extract_desired_column_id(json, column_name):
        """
        extracts desired column id by colum name
        Args:

            json (dict): json dictionary of colum data
            column name (str): desired column name

        Returns:

            str: desired column id
        """
        for entity in json["entities"]:
            if entity["name"] == column_name:
                if entity["cardCount"] < 1:
                    # no cards, end everything
                    return
                return entity["columnId"]
