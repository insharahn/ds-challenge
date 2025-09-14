# Affordability in Motion

This project explores housing affordability across Chicago, Los Angeles, and New York, focusing on how walkability, income, transit, and competition density interact to shape urban housing outcomes.

The repo includes:
- Scrapers: Collect housing, demographic, and amenity data from public sources.
- Cleaner: Processes raw data into a structured format and enriches with extra features.
- Visualization Maker: Jupyter notebook I used to make heatmaps, bubble charts, scatter plots, and trend lines showing affordability dynamics.

## Data Dictionary
| Column Name                    | Description                                                            | Data Type    |
| ------------------------------ | ---------------------------------------------------------------------- | ------------ |
| **address**                    | Full street address of the property                                    | String       |
| **city**                       | City where the property is located                                     | String       |
| **state**                      | State abbreviation (US postal code format)                             | String       |
| **zip\_code**                  | 5-digit ZIP Code                                                       | String/Int   |
| **price**                      | Monthly rent price (USD)                                               | Float        |
| **bedrooms**                   | Number of bedrooms                                                     | Float        |
| **bathrooms**                  | Number of bathrooms                                                    | Float        |
| **square\_feet**               | Living space area (sq. ft.)                                            | Float        |
| **listing\_date**              | Listing date (YYYY-MM-DD)                                              | Date         |
| **latitude**                   | Latitude coordinate of property                                        | Float        |
| **longitude**                  | Longitude coordinate of property                                       | Float        |
| **url**                        | Zillow property listing URL                                            | String (URL) |
| **walkscore**                  | Walkability score (0–100; higher = more walkable)                      | Float        |
| **transit\_score**             | Public transit accessibility score (0–100)                             | Float        |
| **bike\_score**                | Bike-friendliness score (0–100)                                        | Float        |
| **walkscore\_error**           | Missing/error flag for Walk Score (null if no issue)                   | String/Null  |
| **median\_income**             | Median household income in the property’s census area (USD)            | Float        |
| **population**                 | Total population of the census area                                    | Float        |
| **white\_pop**                 | White population count                                                 | Float        |
| **black\_pop**                 | Black/African-American population count                                | Float        |
| **asian\_pop**                 | Asian population count                                                 | Float        |
| **hispanic\_pop**              | Hispanic/Latino population count                                       | Float        |
| **competition\_density**       | Market competition proxy (integer category; higher = more competition) | Int          |
| **population\_density\_proxy** | Approximate population density (population ÷ area estimate)            | Float        |
| **diversity\_index**           | Measure of demographic diversity (0–1, higher = more diverse)          | Float        |
| **affordability\_index**       | Affordability score (lower = more affordable relative to income)       | Float        |
| **price\_per\_sqft**           | Rent price divided by square footage (USD/sq. ft.)                     | Float        |
| **affordability\_ratio**       | Rent-to-income ratio (rent ÷ income, unitless)                         | Float        |
| **rent\_premium**              | Premium/discount vs. expected rent (USD, can be negative)              | Float        |

## Key Insights

- Walkability premiums are strongest in Chicago and New York.
- Income is the biggest affordability driver across cities.
- Competition lowers costs in Chicago but not in LA.
- Transit access often raises prices, creating affordability risks.
- Patterns are city-specific — no one-size-fits-all policy solution.

### How AI Helped
AI tools supported:
- Correlation analysis: testing predictors (walkability, income, density) against affordability.
- Narrative framing: turning data-heavy outputs into memorable insights for presentation.

## API Sources
1. <a href="https://rapidapi.com/s.mahmoud97/api/zillow56/playground/apiendpoint_519bc7c2-98fa-43d7-86c9-f209a2edf6f5"/>Zillow (Unofficial)</a>
2. <a href="https://www.walkscore.com/professional/api.php">WalkScore</a>
3. <a href="https://api.census.gov/data/key_signup.html">US Census Bureau</a>

## Tools
1. Python: core data collection and analysis
2. Pandas & NumPy: cleaning, transformation, correlation analysis
3. Matplotlib & Seaborn: plotting heatmaps, regressions, scatterplots
4. Jupyter Notebooks: reproducible exploration & reports
  
