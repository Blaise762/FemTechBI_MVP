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
- State-by-state data visualization
- Key metrics: maternal mortality rate, OB-GYN density, FemTech startups, population demographics
- Interactive charts: bar charts, scatter plots
- State-specific summaries

### 3. Gap & Opportunity Analysis
- High-need, low-innovation county identification
- Filters by state, demographic focus, and health condition
- Visualization of need vs innovation scores

### 4. AI Insights (Placeholder)
- Future-ready AI summary box
- GPT-powered insights placeholder

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

The MVP uses sample data for demonstration purposes. To replace with real data:

1. Update the `load_sample_data()` function in `app.py`
2. Ensure data follows the same structure as the sample dataframes

## Form Integration

The app uses an external form (Tally.so) for user registration. To update the form:

1. Create a new form at [tally.so](https://tally.so)
2. Update the form link in the `app.py` file
3. Configure the form to redirect back to your deployed app URL

## Future Enhancements

- Tiered subscription system
- Custom insight generator
- Sponsorship tier integration
- Exportable pitch decks & reports
- Regional founder directory
- Interactive map visualizations
- Real-time data integration
- Advanced AI-powered insights

## License

Demo only – not for redistribution.

## Contact

For questions or customizations, please reach out through the contact form in the app.
