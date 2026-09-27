import pandas as pd
from langchain.schema import HumanMessage

from backend.agent.utils.extract_postcode import extract_postcode
from backend.agent.utils.state import State
def load_excel(path="/kaggle/input/house-prices/house_pricing.xlsx"):
    """Load Excel file and return the file object and sheet list (excluding first sheet)."""
    xls = pd.ExcelFile(path)
    sheets = xls.sheet_names[1:]
    return xls, sheets

def flatten_columns(df):
    """Flatten multi-index columns and remove 'Unnamed' entries."""
    df.columns = [
        "_".join([str(c) for c in col if str(c) != "nan"])
        for col in df.columns
    ]
    return df.loc[:, ~df.columns.str.contains("Unnamed")]

def parse_sheet_by_house_type(df):
    """Parse the 'By type' sheet for 2025."""
    df = df.iloc[:, :5]
    df.iloc[:, 0] = df.iloc[:, 0].ffill()

    london_2025 = df[df.iloc[:, 0] == 2025].reset_index(drop=True)
    col_names = ["Year", "Month", "Detached", "Semi Detached", "Terraced", "Flat"]
    london_2025.columns = col_names[:len(london_2025.columns)]
    return london_2025

def _parse_generic(df, value_name):
    """Shared melt-and-filter logic for multiple sheets."""
    df = df.iloc[:, :-15]

    melted = df.melt(
        id_vars=[df.columns[0]],
        var_name="Borough",
        value_name=value_name,
    )

    year_col = df.columns[0]
    melted = (
        melted[melted[year_col].astype(str).str.contains("25")]
        .reset_index(drop=True)
    )
    melted.columns = ["Year_Month", "Borough", value_name]
    return melted

def parse_average_type(df):
    return _parse_generic(df, "Average Price")

def parse_sales_volume(df):
    return _parse_generic(df, "Sales Volume")

def parse_excel( path, borough ): #TODO change the imports and change from camel case to normal case H_a_m_m.... hamm 
    """Parse required sheets and return (London_2025_data, borough_data)."""
    xls, sheets = load_excel(path)

    london_2025 = None
    borough_prices = None
    sales_volumes = None

    for sheet in sheets:
        df = pd.read_excel(xls, sheet_name=sheet)
        df = flatten_columns(df)

        if sheet == "By type":
            london_2025 = parse_sheet_by_house_type(df)
        elif sheet == "Average price":
            borough_prices = parse_average_type(df)
        elif sheet == "Sales Volume":
            sales_volumes = parse_sales_volume(df)

    # Merge borough-level datasets
    if borough_prices is not None and sales_volumes is not None:
        borough_data = pd.merge(
            borough_prices,
            sales_volumes,
            on=["Year_Month", "Borough"],
            how="outer",
        )
    else:
        borough_data = borough_prices or sales_volumes

    # Filter for selected borough
    if borough_data is not None:
        borough_data = borough_data[borough_data["Borough"] == borough].reset_index(drop=True)

    return london_2025, borough_data

def calculate_affordability_metric(mean_income, borough_data):
    """
    Returns (avg_house_price, affordability_metric, latest_row)
    """
    latest_row = None
    avg_house_price = None
    affordability_metric = None

    if borough_data is not None and not borough_data.empty:
        latest_row = borough_data.iloc[-1]
        avg_house_price = latest_row["Average Price"]

        # Handle objects with .text field (e.g., HTML nodes)
        if hasattr(avg_house_price, "text"):
            try:
                avg_house_price = float(avg_house_price.text)
            except:
                avg_house_price = None
        else:
            avg_house_price = float(avg_house_price)

        if avg_house_price is not None and mean_income is not None:
            affordability_metric = avg_house_price / mean_income

    return avg_house_price, affordability_metric, latest_row

def create_housing_prompt(postcode: str, avg_price: float, mean_income: float, affordability: float, london_2025_summary: str) -> str:
    """
    Creates a prompt for the AI model to generate a housing summary.
    """
    avg_price_str = f"£{avg_price}" if avg_price is not None else "N/A"
    mean_income_str = f"£{mean_income}" if mean_income is not None else "N/A"
    affordability_str = f"{affordability:.2f}" if affordability is not None else "N/A"

    return f"""
            You are a housing assistant.
            
            Provide a concise summary for postcode {postcode}:
            
            - Average house price: {avg_price_str}
            - Mean household income: {mean_income_str}
            - Affordability metric (price / income): {affordability_str}
            
            Explain if housing is affordable, moderately expensive, or expensive and compare it with {london_2025_summary} prices.
            Make it readable for a general user in 3-4 sentences.
            """
def housing_agent(state: State, borough) -> State: # change to caml case
    """Generate a natural language housing summary with affordability."""
    if getattr(state, "housing_data", None):
        return state

    postcode = extract_postcode(state)

    london_2025, borough_data = parse_excel()
    mean_income = api.income_api(postcode)
    avg_house_price, affordability_metric, latest_row = calculate_affordability_metric(mean_income, borough_data)
    
    prompt = create_housing_prompt(postcode, avg_house_price, mean_income, affordability_metric, london_2025)
    response = client.models.generate_content(model="gemini-2.0-flash",contents=prompt)

    if hasattr(response, "text"):
        summary_text = response.text.strip()
    elif hasattr(response, "output_text"):
        summary_text = response.output_text.strip()
    elif hasattr(response, "candidates") and response.candidates:
        summary_text = response.candidates[0].content.strip()
    else:
        summary_text = "No summary generated."

    # Store in state
    state["housing"] = [
        HumanMessage(content=f"Data: avg_house_price={avg_house_price}, mean_income={mean_income}, affordability={affordability_metric}"),
        HumanMessage(content=summary_text),
    ]


    return state
