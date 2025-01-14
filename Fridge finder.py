from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


def convert_to_inches(feet, inches):
    """Convert feet and inches into total inches."""
    return (feet * 12) + inches


def calculate_volume_cubic_feet(length, width, height):
    """Calculate volume in cubic feet from dimensions in inches."""
    volume_cubic_inches = length * width * height
    return volume_cubic_inches / 1728  # 1 cubic foot = 1728 cubic inches


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

    # Start Selenium WebDriver
    driver = webdriver.Chrome()  # Make sure you have the appropriate WebDriver installed
    driver.maximize_window()

    try:
        # Open Home Depot Website
        driver.get("https://www.homedepot.com")

        # Locate the search bar and input the search query
        search_box = driver.find_element(By.ID, "typeahead-search-field-input")
        search_query = f"{fridge_volume_cubic_feet:.2f} cubic feet Refrigerator"
        search_box.send_keys(search_query)

        # Perform the search
        search_box.send_keys(Keys.RETURN)

        # Wait for results to load
        time.sleep(5)

        # Scrape and display fridge results
        print("Top Refrigerator Results from Home Depot:\n")

        # Locate refrigerator descriptions
        fridge_results = driver.find_elements(By.XPATH, "//span[@data-testid='attribute-product-label']")

        # Locate refrigerator brands
        fridge_brands = driver.find_elements(By.XPATH, "//p[@data-testid='attribute-brandname-above']")

        # Combine and display brands and descriptions
        for i in range(min(len(fridge_results), 10)):  # Limit to 10 results
            description = fridge_results[i].text
            brand = fridge_brands[i].text if i < len(fridge_brands) else "Brand: Not available"

            print(f"{i + 1}. {brand} {description}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser
        driver.quit()


if __name__ == "__main__":
    main()
