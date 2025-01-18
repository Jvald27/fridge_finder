from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException, StaleElementReferenceException
import os
import re


def convert_to_inches(feet, inches):
    """Convert feet and inches into total inches."""
    return (feet * 12) + inches


def calculate_volume_cubic_feet(length, width, height):
    """Calculate volume in cubic feet from dimensions in inches."""
    volume_cubic_inches = length * width * height
    return volume_cubic_inches / 1728  # 1 cubic foot = 1728 cubic inches


def extract_cubic_feet(description):
    """Extract the cubic feet value from the product description."""
    match = re.search(r"(\d+(\.\d+)?)\s?(cu\. ft\.|cubic feet)", description, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


def main():
    print("Welcome to the Fridge Finder Tool!")

    # Collect user inputs for fridge dimensions in feet and inches
    try:
        print("\nEnter the desired fridge length:")
        length_feet = int(input("  Feet: "))
        length_inches = float(input("  Inches: "))
        length = convert_to_inches(length_feet, length_inches)

        print("\nEnter the desired fridge width:")
        width_feet = int(input("  Feet: "))
        width_inches = float(input("  Inches: "))
        width = convert_to_inches(width_feet, width_inches)

        print("\nEnter the desired fridge height:")
        height_feet = int(input("  Feet: "))
        height_inches = float(input("  Inches: "))
        height = convert_to_inches(height_feet, height_inches)

        if length <= 0 or width <= 0 or height <= 0:
            print("Dimensions should be positive values only.")
            return

    except ValueError:
        print("Invalid input. Please enter whole numbers for feet and numeric values for inches.")
        return

    # Calculate the fridge's total size in cubic feet
    fridge_volume_cubic_feet = calculate_volume_cubic_feet(length, width, height)
    approx_capacity = fridge_volume_cubic_feet * 0.85  # Approximate capacity is ~85% of outer volume

    print(f"\nYour desired fridge size is about {fridge_volume_cubic_feet:.2f} cubic feet.")
    print(f"Approximate internal capacity: {approx_capacity:.2f} cubic feet.\n")

    # Initialize Selenium WebDriver using the correct path
    driver_path = os.getenv("CHROMEDRIVER_PATH", r"C:\chromedriver\chromedriver-win64\chromedriver.exe")
    try:
        driver_service = Service(driver_path)
        driver = webdriver.Chrome(service=driver_service)
        driver.maximize_window()

        # Open the Home Depot website
        driver.get("https://www.homedepot.com")

        # Locate the search bar and input the search query
        search_query = f"{fridge_volume_cubic_feet:.0f} cu. ft. Refrigerator"
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "typeahead-search-field-input"))
        )
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)

        # Wait for search results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//span[@data-testid='attribute-product-label']"))
        )

        # Locate refrigerator descriptions
        fridge_results = driver.find_elements(By.XPATH, "//span[@data-testid='attribute-product-label']")

        # Locate refrigerator brands
        fridge_brands = driver.find_elements(By.XPATH, "//p[@data-testid='attribute-brandname-above']")

        # Locate refrigerator prices
        fridge_prices = driver.find_elements(By.XPATH, "//span[contains(@class, 'sui-font-display')]")

        # Combine and filter results within ±2 cubic feet of the user's desired size
        filtered_results = []
        for i in range(len(fridge_results)):
            description = fridge_results[i].text
            brand = fridge_brands[i].text if i < len(fridge_brands) else "Brand: Not available"
            price = fridge_prices[i].text if i < len(fridge_prices) else "Price: Not available"

            # Extract and check cubic feet
            cubic_feet = extract_cubic_feet(description)
            if cubic_feet and abs(cubic_feet - fridge_volume_cubic_feet) <= 2:
                filtered_results.append((brand, description, price))

            # Stop once we have 5 results
            if len(filtered_results) >= 5:
                break

        # Display the filtered results
        print("\nTop Refrigerator Results from Home Depot (±2 cubic feet of desired size):\n")
        if filtered_results:
            for i, (brand, description, price) in enumerate(filtered_results):
                print(f"{i + 1}. {brand} | {description} | ${price}")
        else:
            print("No results found within ±2 cubic feet of your desired size.")

    except NoSuchElementException as e:
        print(f"An element was not found on the page: {e}")
    except StaleElementReferenceException:
        print("A stale element reference error occurred. Trying again might resolve the issue.")
    except WebDriverException as e:
        print(f"A WebDriver error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Close the browser if the driver is initialized
        if 'driver' in locals():
            driver.quit()


if __name__ == "__main__":
    main()

