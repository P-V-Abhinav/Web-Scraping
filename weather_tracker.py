import numpy as np
import pandas as pd
from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service


# Disable pandas truncation for display
pd.options.display.max_columns = None
pd.options.display.max_rows = None

# Base Lookup URL
base_lookup_URL = 'https://www.wunderground.com/hourly/{}/date/{}-{}-{}.html'

# Specify locations (e.g., New York City, Los Angeles, Chicago)
locations = {
    "London": "gb/london",
    # "los-angeles": "us/ca/los-angeles",
    # "chicago": "us/il/chicago"
}

df_prep = pd.DataFrame(columns=["Day", "Precipitation"])
# Date range
start_date = date.today() + timedelta(days=1)
end_date = date.today() + timedelta(days=4)

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
#options.add_argument('--headless')  # Run Chrome in headless mode
# driver_path = r"C:\Users\Abhinav P V\Desktop\FPR\chromedriver-win64\chromedriver.exe"
# service = Service(driver_path)
driver = webdriver.Chrome(options=options)

# DataFrame to hold precipitation data
df_prep = pd.DataFrame(columns=["Location", "Day", "Precipitation"])

# Scrape data for each location
for loc_name, loc_path in locations.items():
    print(f"Gathering data for: {loc_name.capitalize()}")
    current_date = start_date
    while current_date != end_date:
        formatted_lookup_URL = base_lookup_URL.format(
            loc_path,
            current_date.year,
            current_date.month,
            current_date.day
        )
        driver.get(formatted_lookup_URL)
        
        try:
            # Wait for precipitation elements to load
            rows = WebDriverWait(driver, 60).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//td[contains(@class, "cdk-column-liquidPrecipitation")]')
                )
            )
            
            # Extract data from rows
            for row in rows:
                try:
                    prep = row.find_element(By.XPATH, './/span[@class="wu-value wu-value-to"]').text
                    # Append data to DataFrame
                    new_row = pd.DataFrame({
                        "Location": [loc_name.capitalize()],
                        "Day": [str(current_date)],
                        "Precipitation": [prep]
                    })
                    df_prep = pd.concat([df_prep, new_row], ignore_index=True)
                except Exception as e:
                    print(f"Error parsing row: {e}")
        except Exception as e:
            print(f"Failed to load data for {current_date} in {loc_name}: {e}")
        
        # Increment date
        current_date += timedelta(days=1)

# Close the driver
driver.quit()
print(df_prep)



# Save to Excel
output_file = "weather_data.xlsx"
df_prep.to_excel(output_file, index=False)
print(f"\nData saved to {output_file}")
