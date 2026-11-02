#!/usr/bin/env python3

import requests
import time
from concurrent.futures import ThreadPoolExecutor

# World Bank API URL
COUNTRY_URL = "https://api.worldbank.org/v2/country"

def get_countries():

    response = requests.get(
        COUNTRY_URL,
        params={"format": "json", "per_page": 300},
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    # the second element contains the actual country records
    countries = data[1]
    
    return countries

def extract_country_info(country):
    return {
        "name": country["name"],
        "code": country["id"],
    }

def is_valid_country(country):
    return country["region"]["value"] != "Aggregates"

def get_population_data():

    url = (
        "https://api.worldbank.org/v2/country/all/"
        "indicator/SP.POP.TOTL"
    )

    response = requests.get(
        url,
        params={
            "format": "json",
            "mrnev": 1,
            "per_page": 300
        },
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    if len(data) < 2 or data[1] is None:
        return []

    return data[1]


def main():
    times = []
    for workers in [1,2]:
        with ThreadPoolExecutor(max_workers=workers) as e:
        
            start = time.perf_counter()

            country_future = e.submit(get_countries)
            population_future = e.submit(get_population_data)

            country_data = country_future.result()
            population_data = population_future.result()

        # remove regional aggregates
        countries = list(filter(is_valid_country, country_data))

        # extract country information
        countries = list(map(extract_country_info, countries))

        # create a dictionary connecting country codes to populations
        population_by_code = {
            item["countryiso3code"]: {
                "population": item["value"],
            }
            for item in population_data if item["value"] is not None
        }

        # add population information to each country
        def add_population(country):
            population = population_by_code.get(country["code"])

            if population is None:
                return None
    
            country["population"] = population["population"]
    
            return country

        countries = list(map(add_population, countries))

        # remove countries without population data
        countries = list(filter(None, countries))

        # find the five highest and lowest populations
        highest = sorted(
            countries,
            key=lambda country: country["population"],
            reverse=True
        )[:5]

        lowest = sorted(
            countries,
            key=lambda country: country["population"]
        )[:5]

        elapsed = time.perf_counter() - start
        times.append(elapsed)

        print("------------------------------------")
        print(f"Countries analyzed: {len(countries)}")
        
        print("\nTop Five Most Populated Countries:")

        for country in highest:
            print(
                f"{country['name']:25} "
                f"{country['population']:,} "
            )

        print("\nTop Five Least Populated Countries:")

        for country in lowest:
            print(
                f"{country['name']:25} "
                f"{country['population']:,} "
            )

        print(f"\nTime: {elapsed:.3f} sec")
        print(f"Workers: {workers}")

        print("------------------------------------")

    print(f"\nSpeedup with two workers: {times[0]/times[1]:.2f}x\n")

if __name__ == "__main__":
    main()
