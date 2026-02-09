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
- Data upload functionality supporting CSV and Excel files
- State-by-state data visualization
- Key metrics: prenatal visits, birth rates, mother's age distribution
- Interactive charts: line charts, bar charts, histograms
- FemTech core metrics analysis with race-based comparisons
- Dynamic data adaptation for different file formats

### 3. Gap & Opportunity Analysis
- Placeholder page for future implementation
- Planned features: high-need, low-innovation county identification
- Expected data structure display
- Integration with HRSA HPSA dataset (Phase 2)

### 4. AI Insights
- Interactive Q&A functionality for data exploration
- Simulated AI responses based on uploaded data
- Example queries for guidance
- Data-driven insights extraction
- Loading animations for better user experience

### 5. Download Center
- PDF snapshot download
- Contact form
- Email subscription

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

The MVP uses a flexible data upload system for testing purposes. Users can upload their own CSV or Excel files for analysis.

### Data Upload

- Supports CSV and Excel file formats (.csv, .xlsx, .xls)
- Flexible data structure adaptation
- Automatic column detection for key metrics
- For internal testing only – Production will auto-load CDC/HRSA data

### Expected Data Structure

For optimal analysis, uploaded data should contain:
- State column (for state-level analysis)
- Year column (for trend analysis)
- Race/Single Race column (for demographic analysis)
- Prenatal visits column (for prenatal care analysis)
- Birth Rate column (for birth rate analysis)
- Age of Mother column (for age distribution analysis)

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
- AI Insights uses simulated responses – Real GPT integration coming in future updates
- Gap & Opportunity Analysis is a placeholder – Full implementation in Phase 2
- No persistent data storage – Data is lost when session ends
- No user authentication – Form-based access control only

### Testing Notes

- The app accepts any CSV/Excel file format for flexibility during testing
- Error handling is simplified for MVP – Production will have more robust validation
- Some features are placeholders to demonstrate the intended user flow

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
