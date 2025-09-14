# Affordability in Motion

This project explores housing affordability across Chicago, Los Angeles, and New York, focusing on how walkability, income, transit, and competition density interact to shape urban housing outcomes.

The repo includes:
- Scrapers: Collect housing, demographic, and amenity data from public sources.
- Cleaner: Processes raw data into a structured format and enriches with extra features.
- Visualization Maker: Jupyter notebook I used to make heatmaps, bubble charts, scatter plots, and trend lines showing affordability dynamics.

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
  
