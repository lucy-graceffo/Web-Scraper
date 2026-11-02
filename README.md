World Bank Country Population Scraper

This project analyzes data from the World Bank API and outputs the five largest and five smallest countries by population, as well as data about concurrency.

To run it:

chmod +x webscraper.py
./webscraper.py

you will need python3 and requests

Functional Programming:

I use map(), filter(), and sorted() in this program.

countries = list(filter(is_valid_country, country_data))
countries = list(map(extract_country_info, countries))
highest = sorted(
            countries,
            key=lambda country: country["population"],
            reverse=True
        )[:5]

These functions make the data-processing steps more organized and readable.

Concurrent Programming:

I use ThreadPoolExecutor from concurrent.futures to retrieve country information and population data.

with ThreadPoolExecutor(max_workers=workers) as e:
    country_future = e.submit(get_countries)
    population_future = e.submit(get_population_data)

Because these requests are independent, they can run concurrently when two workers are being used, but only sequentially when there is one worker.

Performance Analysis:

I use python's time library to measure the difference between using one or two workers. At the end of the program, I output the speedup ratio between the one-worker and two-worker executions. This ratio is usually around two, which makes sense as there are twice as many workers, and each only have to do half as much as the solo worker does.
