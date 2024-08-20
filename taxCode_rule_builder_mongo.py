import streamlit as st
import json
from bson import ObjectId
import pandas as pd
import base64

# Dictionary of US states and their abbreviations
US_STATES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
    "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
    "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
    "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC"
}

def create_jurisdiction_rule(state_name, state_abbr):
    rule = {}
    rule['name'] = state_name
    rule['abbreviation'] = state_abbr
    rule['taxable'] = st.checkbox("Taxable", key=f"taxable_{state_name}")
    rule['specialTreatment'] = st.checkbox("Special Treatment", key=f"special_{state_name}")
    rule['calculationType'] = st.selectbox("Calculation Type", ["FIXED", "PERCENTAGE"], key=f"calc_type_{state_name}")
    rule['description'] = st.text_input("Description", value="description3", key=f"desc_{state_name}")
    rule['calculationValue'] = st.text_input("Calculation Value", value="0", key=f"calc_value_{state_name}")
    
    if state_name in ["Illinois", "Colorado"]:
        rule['cities'] = create_cities(state_name)
    
    return rule

def create_cities(state_name):
    cities = {}
    if state_name == "Illinois":
        cities["Chicago"] = create_city_rule("Chicago")
    elif state_name == "Colorado":
        colorado_cities = [
            "Arvada", "Aspen", "Aurora", "Avon", "Black Hawk", "Boulder", "Breckenridge", "Brighton", "Broomfield",
            "Carbondale", "Castle Pines", "Castle Rock", "Centennial", "Central City", "Cherry Hills Village",
            "Colorado Springs", "Commerce City", "Cortez", "Craig", "Crested Butte", "Dacono", "Delta", "Denver",
            "Durango", "Edgewater", "Englewood", "Evans", "Federal Heights", "Fort Collins", "Frisco", "Glendale",
            "Glenwood Springs", "Golden", "Grand Junction", "Greeley", "Greenwood Village", "Gunnison", "Gypsum",
            "La Junta", "Lafayette", "Lakewood", "Lamar", "Littleton", "Lone Tree", "Longmont", "Louisville",
            "Loveland", "Montrose", "Mountain Village", "Mt Crested Butte", "Northglenn", "Parker", "Pueblo",
            "Ridgeway", "Rifle", "Sheridan", "Silverthorne", "Snowmass Village", "Steamboat Springs", "Sterling",
            "Telluride", "Thornton", "Timnath", "Vail", "Westminster", "Wheat Ridge", "Windsor", "Winter Park",
            "Woodland Park"
        ]
        for city in colorado_cities:
            cities[city] = create_city_rule(city)
    return cities

def create_city_rule(city_name):
    rule = {}
    rule['name'] = city_name
    rule['abbreviation'] = city_name
    rule['taxable'] = st.checkbox(f"Taxable ({city_name})", key=f"taxable_{city_name}")
    rule['specialTreatment'] = st.checkbox(f"Special Treatment ({city_name})", key=f"special_{city_name}")
    rule['calculationType'] = st.selectbox(f"Calculation Type ({city_name})", ["FIXED", "PERCENTAGE"], key=f"calc_type_{city_name}")
    rule['description'] = st.text_input(f"Description ({city_name})", value="description3", key=f"desc_{city_name}")
    rule['calculationValue'] = st.text_input(f"Calculation Value ({city_name})", value="0", key=f"calc_value_{city_name}")
    return rule

def create_document():
    st.set_page_config(layout="wide")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.title("🛠️ Tax Code/Rule Creator ")

        doc = {}
        doc['taxCode'] = st.text_input("Tax Code")
        doc['description'] = st.text_input("Description")
        doc['title'] = st.text_input("Title")
        doc['tangibleCategory'] = st.selectbox("Tangible Category", ["TANGIBLE", "INTANGIBLE"])

        st.subheader("Jurisdictional Sales Tax Rules")
        doc['jurisdictionalSalesTaxRules'] = {}

        for state, abbr in US_STATES.items():
            with st.expander(f"Rules for {state}"):
                doc['jurisdictionalSalesTaxRules'][state] = create_jurisdiction_rule(state, abbr)

        doc['jurisdictionalTaxRules'] = {}  # Empty for now, can be expanded later

        if st.button("Create Document"):
            # Add ObjectId
            doc['_id'] = {'$oid': str(ObjectId())}
            
            # Option to download the document as JSON
            st.download_button(
                label="Download JSON",
                data=json.dumps(doc, indent=2),
                file_name="mongodb_document.json",
                mime="application/json"
            )

    with col2:
        st.title("👀 Document Preview/Table")
        preview_doc = doc.copy()
        preview_doc['_id'] = {'$oid': str(ObjectId())}
        
        # Option to switch between JSON and Table views
        view_option = st.radio("Select View", ["JSON", "State Rules Table", "City Rules Table"])
        
        if view_option == "JSON":
            st.json(json.dumps(preview_doc, indent=2))
        elif view_option == "State Rules Table":
            # Convert the jurisdictional rules to a DataFrame
            rules_data = []
            for state, rule in preview_doc['jurisdictionalSalesTaxRules'].items():
                rules_data.append({
                    "State": state,
                    "Abbreviation": rule['abbreviation'],
                    "Taxable": rule['taxable'],
                    "Special Treatment": rule['specialTreatment'],
                    "Calculation Type": rule['calculationType'],
                    "Description": rule['description'],
                    "Calculation Value": rule['calculationValue']
                })
            
            df_states = pd.DataFrame(rules_data)
            st.dataframe(df_states)
            
            # Option to download as CSV
            csv_states = df_states.to_csv(index=False)
            b64_states = base64.b64encode(csv_states.encode()).decode()
            href_states = f'<a href="data:file/csv;base64,{b64_states}" download="state_tax_rules.csv">Download State Rules CSV</a>'
            st.markdown(href_states, unsafe_allow_html=True)
        else:  # City Rules Table
            # Convert the city rules to a DataFrame
            city_rules_data = []
            for state, rule in preview_doc['jurisdictionalSalesTaxRules'].items():
                if 'cities' in rule:
                    for city, city_rule in rule['cities'].items():
                        city_rules_data.append({
                            "State": state,
                            "City": city,
                            "Taxable": city_rule['taxable'],
                            "Special Treatment": city_rule['specialTreatment'],
                            "Calculation Type": city_rule['calculationType'],
                            "Description": city_rule['description'],
                            "Calculation Value": city_rule['calculationValue']
                        })
            
            df_cities = pd.DataFrame(city_rules_data)
            st.dataframe(df_cities)
            
            # Option to download as CSV
            csv_cities = df_cities.to_csv(index=False)
            b64_cities = base64.b64encode(csv_cities.encode()).decode()
            href_cities = f'<a href="data:file/csv;base64,{b64_cities}" download="city_tax_rules.csv">Download City Rules CSV</a>'
            st.markdown(href_cities, unsafe_allow_html=True)

if __name__ == "__main__":
    create_document()