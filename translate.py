
def translate_city(city):
    match city:
        case "תל אביב יפו":
            return "Tel Aviv Jaffa"
        case "ראשון לציון":
            return "Rishon LeZion"
        case "ירושלים":
            return "Jerusalem"
        case "חיפה":
            return "Haifa"
        case "פתח תקווה":
            return "Petah Tikva"
        case "באר שבע":
            return "Beer Sheva"
        case _:
            return city
