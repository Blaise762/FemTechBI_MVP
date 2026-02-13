# FemTech BI Dashboard - Deep South

## Project Overview

A regionally focused, equity-centered FemTech Business Intelligence platform for tracking health equity gaps, innovation opportunities, and investment potential across six Deep South states: Alabama (AL), Florida (FL), Georgia (GA), Louisiana (LA), Mississippi (MS), and South Carolina (SC).

## Key Features

### 📱 Top Navigation
- **Home**: Mission statement, interactive map, and access form
- **Dashboard**: KPI metrics, charts, and data visualizations
- **Gap & Opportunity**: Opportunity index calculation and analysis
- **AI Insights**: Data-driven insights and recommendations
- **Download Center**: Data export and snapshot downloads

### 📊 Core Functionality
- **Dual Data Upload**: Supports CSV and Excel files for CDC and HRSA data
- **Interactive Map**: Deep South 6-state choropleth visualization
- **KPI Metrics**: Total market size, average gap severity, prenatal visits
- **Dynamic Charts**: Bar charts, line charts, pie charts, and histograms
- **Opportunity Index**: Calculated as (State_Total_Births / Max_State_Births) * State_Average_HPSA_Score
- **AI-Powered Insights**: Based on actual uploaded data
- **Data Download**: Merged dataset and state-level summaries

### 🔧 Technical Highlights
- **Smart Data Processing**: Automatic field mapping, state name standardization, and data type conversion
- **Efficient Data Fusion**: Merges CDC and HRSA data at state level (no county analysis)
- **Responsive Design**: Optimized for desktop and tablet viewing
- **Error Handling**: Robust file upload and data processing error management

## Tech Stack

- **Framework**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly Express, Plotly Graph Objects
- **Hosting**: Streamlit Cloud, Render (free-tier compatible)

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

Access at: `http://localhost:8501`

## Data Requirements

### Supported Files
- **Formats**: CSV, Excel (.csv, .xlsx, .xls)
- **Dual Upload**: Separate uploaders for CDC and HRSA data

### Recommended Data Structure

#### CDC Data
- State column (e.g., "State", "state")
- Births column (e.g., "Births", "births")
- Prenatal visits column (e.g., "Prenatal Visits", "prenatal")
- Year column (for trend analysis)
- Mother's age column (for age distribution)

#### HRSA Data
- State column (e.g., "State", "state")
- HPSA Score column (e.g., "HPSA Score", "hpsa_score")

## Data Processing

- **State Standardization**: Converts full state names to abbreviations
- **Field Mapping**: Automatically maps raw fields to standardized variables
- **Data Fusion**: Merges CDC and HRSA data by state to avoid Cartesian product
- **Missing Values**: Fills missing HPSA scores with 0 for states present in CDC but not HRSA
- **Aggregation**: Calculates state-level metrics for consistent analysis

## Usage Notes

1. **Data Upload**: Upload both CDC and HRSA files for full functionality
2. **State Filter**: Select specific states or all six Deep South states
3. **Form Access**: Complete the form on the Home page to unlock the dashboard
4. **Chart Interactivity**: Hover over charts for detailed information
5. **Data Download**: Export merged data and state summaries from the Download Center

## Limitations

- **Testing Only**: Data upload is for internal testing (production will auto-load CDC/HRSA data)
- **Simulated AI**: AI Insights uses data-driven responses (real GPT integration planned)
- **Session-Based**: No persistent data storage (data lost when session ends)
- **Form Access**: No user authentication (form-based access control only)

## License

Demo only – not for redistribution.

## Contact

For questions or customizations, please reach out through the contact form in the app.
