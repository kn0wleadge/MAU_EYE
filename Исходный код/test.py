[
    {
        "firstname": "Ivan",
        "hashed_pwd": "mama",
        "lastname": "Ivanov",
        "login": "testikus",
        "number": "1",
        "role": "department_worker"
    },
    {
        "firstname": "string",
        "hashed_pwd": "string",
        "lastname": "string",
        "login": "string",
        "number": "2",
        "role": "department_worker"
    }
]
new_list = []
for item in list:
    new_item = {"number" : item["number"],
                "full_name": f"{item['firstname']+ " " + item['lastname']}"}
    new_list.append(new_item)