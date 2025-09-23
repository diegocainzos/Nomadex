from serpapi import GoogleSearch
import os
from dotenv import load_dotenv


load_dotenv()
SERPI_TOKEN = os.getenv("SERPAPI")


# Update the params to use the environment variable
""""
params = {
    "api_key": SERPI_TOKEN,
    "engine": "google_hotels",
    "q": "madrid",
    "hl": "en",
    "gl": "us",
    "check_in_date": "2025-09-08",
    "check_out_date": "2025-09-14",
    "currency": "EUR",
    "sort_by": "3",
    "adults": "2"
}
"""


def hotel_query(params):
    try:
        params["api_key"] = SERPI_TOKEN
        search = GoogleSearch(params)
        results = search.get_dict()

        if "error" in results:
            return f"An API error occurred: {results['error']}"

        if "properties" not in results:
            return "No hotels were found for the specified search."

        lista_hoteles = results.get("properties", [])

        if not lista_hoteles:
            return "No hotels were found for the specified search."

        # Build the formatted string
        hoteles_encontrados = []
        for hotel in lista_hoteles[:10]:

            info_hotel = {
                "nombre": hotel.get("name"),
                "precio": hotel.get("rate_per_night", {}).get("extracted_lowest"),
                "puntuacion": hotel.get("overall_rating"),
                "total_opiniones": hotel.get("reviews"),
                "descripcion": hotel.get("description"),
                "enlace_google": hotel.get("link"),
                "hotel_class" : hotel.get("hotel_class", "0-star hotel"),
            }

            hoteles_encontrados.append(info_hotel)
        hoteles_encontrados.append({"adults" : params["adults"]})
        hoteles_encontrados.append({"checkin" : params["check_in_date"]})
        hoteles_encontrados.append({"checkout" : params["check_out_date"]})


#add checkin and checkout
        return hoteles_encontrados

    except Exception as e:
        return f"An exception has occurred: {str(e)}"
