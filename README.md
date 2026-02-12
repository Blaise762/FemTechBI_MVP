# FemTech BI Dashboard - Deep South

## Project Overview

This is a regionally focused, equity-centered FemTech Business Intelligence platform that tracks data and insights across six Deep South states (GA, FL, AL, MS, LA, SC). The dashboard spotlights health equity gaps, FemTech innovation deserts, and investment opportunities—centering Black, Indigenous, and underserved women across rural and urban communities and the full reproductive lifespan.

## Features

### 1. Home Page
- Hero section with mission statement
- CTA buttons for dashboard access, snapshot download, and custom insights
- Deep South states list
- Form capture functionality for dashboard access

### 2. Dashboard View
- **Dual Data Upload System**: Separate uploaders for CDC and HRSA data files
- **Deep South State Filter**: Select specific states or all six states (GA, FL, AL, MS, LA, SC)
- **Data Fusion Engine**: Automatic merging of CDC and HRSA data using State fields only (county-level analysis removed)
- **Field Mapping**: Intelligent mapping of raw fields to standardized internal variables
- **KPI Metrics** (based on merged data):
  - Total Market Size: Sum of births across all states
  - Average Gap Severity: Mean HPSA Score across all states
  - States Covered: Number of unique states in the dataset
- **Interactive Charts**:
  - Market & Scale: Pie chart showing births distribution by state
  - Equity Comparison: Bar chart comparing gap severity or prenatal visits by state
  - Mother's Age Distribution: Histogram with mean line (if age data available)
  - Health Improvement Trends: Line chart showing prenatal visits over time
- **Data Overview**: Expandable section showing merged data sample

### 3. Gap & Opportunity Analysis
- **Opportunity Index Calculation**: Formula: (State_Total_Births / Max_State_Births) * State_Average_HPSA_Score
- **Top Opportunity Zones**: Display top 10 states with highest opportunity index
- **Interactive Visualizations**:
  - Opportunity Heatmap: Scatter plot showing state births vs gap score
  - Opportunity Index Distribution: Histogram of state opportunity scores
  - State-Level Analysis: Bar chart comparing opportunity index by state
- **Data-Driven Insights**: Automatic identification of high-need, low-innovation states

### 4. AI Insights
- **Dynamic AI Responses**: Real insights based on actual merged data
- **Smart State Identification**: Automatically finds states with highest HPSA Score and Births
- **Data-Driven Recommendations**: Specific recommendations for top opportunity states
- **Example Queries**: Pre-defined questions for guidance
- **Key Statistics**: Display of key metrics from merged data
- **Top Opportunities**: List of top 3 states by opportunity index

### 5. Download Center
- **PDF Snapshot Download**: Comprehensive snapshot of FemTech innovation and health equity
- **Merged CSV Download**: Complete merged dataset of CDC and HRSA data (highly valuable for investors)
- **Data Preview**: Expandable section showing merged data sample
- **Contact Form**: User feedback and inquiries
- **Email Subscription**: Newsletter signup for latest insights

## Tech Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas
- **Visualization**: Plotly
- **Hosting Options**: Streamlit Cloud or Render (free-tier compatible)

## Getting Started

### Prerequisites

- Python 3.7+
- pip

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Deployment

### Option 1: Streamlit Cloud

1. Create a Streamlit Cloud account at [streamlit.io](https://streamlit.io)
2. Connect your GitHub repository
3. Deploy the app with the following settings:
   - Main file path: `app.py`
   - Python version: 3.9+
   - Dependencies: `requirements.txt`

### Option 2: Render

1. Create a Render account at [render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Configure the service:
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run app.py --server.port=8000 --server.address=0.0.0.0`
   - Environment variables: Add any necessary environment variables

## Data

The MVP uses a dual data upload system for CDC and HRSA data fusion. Users can upload their own CSV or Excel files for analysis.

### Data Upload

- **Dual Upload System**: Separate uploaders for CDC and HRSA data files
- **Supported Formats**: CSV and Excel files (.csv, .xlsx, .xls)
- **Automatic Data Fusion**: Merges CDC and HRSA data using State fields only
- **Field Mapping**: Intelligent mapping of raw fields to standardized internal variables
- **State Filter**: Select specific Deep South states or all six states (GA, FL, AL, MS, LA, SC)
- **Missing Value Handling**: Fills missing HPSA scores with 0 for states present in CDC but not HRSA

### Expected Data Structure

For optimal analysis, uploaded data should contain:

#### CDC Data
- State column (e.g., "State", "state")
- Births column (e.g., "Births", "births")
- Prenatal visits column (e.g., "Prenatal Visits", "prenatal")
- Year column (optional, for trend analysis)
- Age of Mother column (optional, for age distribution)

#### HRSA Data
- State column (e.g., "State", "state")
- HPSA Score column (e.g., "HPSA Score", "hpsa_score")
- Designation type (optional, e.g., "Primary Care", "Dental")

### Merged Data Structure

After fusion, the merged dataset contains:
- `state`: State name
- `total_births`: Total births from CDC data (sum by state)
- `prenatal_visits`: Average prenatal visits from CDC data (mean by state)
- `gap_score`: HPSA score from HRSA data (mean by state, 0 if missing)
- `opportunity_index`: Calculated opportunity score (State_Total_Births / Max_State_Births) * State_Average_HPSA_Score
- `year`: Latest year from CDC data (max by state)
- `mother_age`: Average mother's age from CDC data (mean by state)
- Additional columns from source datasets

## Form Integration

The app uses an in-app form for user registration and dashboard access control.

### Form Features

- Required fields: Name and Email
- Optional fields: Organization and Purpose
- Form submission grants access to the dashboard
- Session state management for access control

### Access Control

- Users must complete the form before accessing the dashboard
- Form completion status is maintained in session state
- Dashboard access is restricted until form is submitted

## MVP Status

This is a Minimum Viable Product (MVP) designed for demonstration and testing purposes.

### Current Limitations

- Data upload is for internal testing only – Production will auto-load CDC/HRSA data
- AI Insights uses simulated responses based on actual data – Real GPT integration coming in future updates
- Opportunity Index calculation is based on available data – More sophisticated algorithms in future updates
- No persistent data storage – Data is lost when session ends
- No user authentication – Form-based access control only

### Testing Notes

- The app accepts any CSV/Excel file format for flexibility during testing
- Dual data upload system requires both CDC and HRSA files for full functionality
- Error handling is simplified for MVP – Production will have more robust validation
- Some features use placeholder data when specific columns are not available

### Recent Updates

- **State-Only Analysis**: Removed all county-level analysis, focusing exclusively on state-level insights for the six Deep South states (GA, FL, AL, MS, LA, SC)
- **Data Fusion Engine**: Updated to merge CDC and HRSA data using State fields only, ensuring clean state-level aggregation
- **Enhanced Data Aggregation**: Implemented state-level aggregation of core metrics (total births, average prenatal visits, mean gap score, average mother's age)
- **Opportunity Index Refinement**: Updated calculation to use state-level aggregated metrics: (State_Total_Births / Max_State_Births) * State_Average_HPSA_Score
- **Dashboard KPI Refactoring**: Updated KPI metrics to reflect state-level analysis (Total Market Size, Average Gap Severity, States Covered)
- **Chart Consistency**: Ensured all charts use consistent state-level data sources, eliminating data source conflicts
- **Navigation Optimization**: Fixed button and sidebar navigation to ensure single-click page transitions
- **AI Insights Enhancement**: Updated to provide state-level insights and recommendations
- **Download Center Enhancement**: Added merged CSV download for investors with state-level aggregated data

## Future Enhancements

- Gap & Opportunity Analysis with HRSA data integration (Phase 2)
- Real AI-powered insights integration (GPT API)
- Interactive map visualizations
- Real-time data integration with CDC/HRSA APIs
- Tiered subscription system
- Custom insight generator
- Sponsorship tier integration
- Exportable pitch decks & reports
- Regional founder directory
- Advanced data validation and error handling

## License

Demo only – not for redistribution.

## Contact

For questions or customizations, please reach out through the contact form in the app.
