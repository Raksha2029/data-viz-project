import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.express as px
import pandas as pd
import wikipedia

# Load the dataset
df = pd.read_csv('assets/cleaned_dataset_WebMd.csv', encoding='latin1')

# Convert 'Age' column to numeric values
df['Age'] = pd.to_numeric(df['Age'], errors='coerce')

# Bin the age groups
age_bins = pd.cut(df['Age'], bins=[0, 18, 35, 50, 65, 120], labels=['0-18', '19-35', '36-50', '51-65', '66+'])
df['Age'] = age_bins

# Get all unique instances of Drugs and Conditions
all_drugs = df['Drug'].unique()
all_conditions = df['Condition'].unique()

# Create the app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div(
    [
        html.H1("Drug Reviews Dashboard", className='text-center text-primary mb-4'),

        html.Div(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            id='condition-dropdown',
                            options=[{'label': condition, 'value': condition} for condition in all_conditions],
                            value=all_conditions[0],
                            placeholder='Select a condition',
                            multi=False
                        )
                    ],
                    className='col-6'
                ),
                html.Div(
                    [
                        dcc.Dropdown(
                            id='drug-dropdown',
                            placeholder='Select a drug',
                            multi=False
                        )
                    ],
                    className='col-6'
                )
            ],
            className='row justify-content-center'
        ),

        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='male-fig', figure={}),
                    ],
                    className='col-6'
                ),
                html.Div(
                    [
                        dcc.Graph(id='female-fig', figure={}),
                    ],
                    className='col-6'
                )
            ],
            className='row justify-content-center'
        ),

        html.Div(
            [
                html.Div(id='reviews-section', className='col-12 mt-4', style={'paddingTop': '30px'})
            ],
            className='row justify-content-center'
        )
    ]
)


# Define the callbacks
@app.callback(
    Output('drug-dropdown', 'options'),
    Output('drug-dropdown', 'value'),
    Input('condition-dropdown', 'value')
)
def update_drug_dropdown(condition):
    filtered_df = df[df['Condition'] == condition]
    drugs = filtered_df['Drug'].unique()
    options = [{'label': drug, 'value': drug} for drug in drugs]
    value = options[0]['value'] if options else None
    return options, value


@app.callback(
    Output('male-fig', 'figure'),
    Output('female-fig', 'figure'),
    Input('condition-dropdown', 'value'),
    Input('drug-dropdown', 'value')
)
def update_condition_drug_graph(condition, drug):
    filtered_df = df[(df['Condition'] == condition) & (df['Drug'] == drug)]

    male_df = filtered_df[filtered_df['Sex'] == 'Male']
    female_df = filtered_df[filtered_df['Sex'] == 'Female']

    male_fig = px.scatter_3d(male_df, x='Condition', y='Drug', z='Satisfaction', color='Satisfaction',
                             title='Male: Condition vs. Drug vs. Satisfaction', hover_data=['Reviews'])

    female_fig = px.scatter_3d(female_df, x='Condition', y='Drug', z='Satisfaction', color='Satisfaction',
                               title='Female: Condition vs. Drug vs. Satisfaction', hover_data=['Reviews'])

    male_fig.update_traces(marker=dict(size=5), selector=dict(mode='markers'))
    female_fig.update_traces(marker=dict(size=5), selector=dict(mode='markers'))

    return male_fig, female_fig


@app.callback(
    Output('reviews-section', 'children'),
    Input('male-fig', 'clickData'),
    Input('female-fig', 'clickData')
)
def update_review_text(click_data_male, click_data_female):
    reviews = []

    if click_data_male is not None:
        point_data = click_data_male['points'][0]
        condition = point_data['x']
        drug = point_data['y']
        satisfaction = point_data['z']

        review = df.loc[(df['Condition'] == condition) & (df['Drug'] == drug) & (df['Sex'] == 'Male') & (df['Satisfaction'] == satisfaction)]
        if not review.empty:
            reviews.append(html.P(f"Selected Review (Male): {review['Reviews'].values[0]}"))
            reviews.append(html.P(f"Condition: {condition}"))
            reviews.append(html.P(f"Drug: {drug}"))

            # Retrieve information from Wikipedia for condition
            try:
                condition_page = wikipedia.page(condition)
                condition_summary = condition_page.summary
                condition_link = condition_page.url
                reviews.append(html.P(f"Wikipedia Summary (Condition): {condition_summary}"))
                reviews.append(html.A('Read More on Wikipedia (Condition)', href=condition_link, target='_blank'))
            except wikipedia.exceptions.DisambiguationError as e:
                # Handle disambiguation errors
                reviews.append(html.P(f"Multiple Wikipedia options found for condition {condition}. Please refine your search."))
            except wikipedia.exceptions.PageError:
                # Handle page not found errors
                reviews.append(html.P(f"No Wikipedia page found for condition {condition}."))

            # Retrieve information from Wikipedia for drug
            try:
                drug_page = wikipedia.page(drug)
                drug_summary = drug_page.summary
                drug_link = drug_page.url
                reviews.append(html.P(f"Wikipedia Summary (Drug): {drug_summary}"))
                reviews.append(html.A('Read More on Wikipedia (Drug)', href=drug_link, target='_blank'))
            except wikipedia.exceptions.DisambiguationError as e:
                # Handle disambiguation errors
                reviews.append(html.P(f"Multiple Wikipedia options found for drug {drug}. Please refine your search."))
            except wikipedia.exceptions.PageError:
                # Handle page not found errors
                reviews.append(html.P(f"No Wikipedia page found for drug {drug}."))

    if click_data_female is not None:
        point_data = click_data_female['points'][0]
        condition = point_data['x']
        drug = point_data['y']
        satisfaction = point_data['z']

        review = df.loc[(df['Condition'] == condition) & (df['Drug'] == drug) & (df['Sex'] == 'Female') & (df['Satisfaction'] == satisfaction)]
        if not review.empty:
            reviews.append(html.P(f"Selected Review (Female): {review['Reviews'].values[0]}"))
            reviews.append(html.P(f"Condition: {condition}"))
            reviews.append(html.P(f"Drug: {drug}"))

            # Retrieve information from Wikipedia for condition
            try:
                condition_page = wikipedia.page(condition)
                condition_summary = condition_page.summary
                condition_link = condition_page.url
                reviews.append(html.P(f"Wikipedia Summary (Condition): {condition_summary}"))
                reviews.append(html.A('Read More on Wikipedia (Condition)', href=condition_link, target='_blank'))
            except wikipedia.exceptions.DisambiguationError as e:
                # Handle disambiguation errors
                reviews.append(html.P(f"Multiple Wikipedia options found for condition {condition}. Please refine your search."))
            except wikipedia.exceptions.PageError:
                # Handle page not found errors
                reviews.append(html.P(f"No Wikipedia page found for condition {condition}."))

            # Retrieve information from Wikipedia for drug
            try:
                drug_page = wikipedia.page(drug)
                drug_summary = drug_page.summary
                drug_link = drug_page.url
                reviews.append(html.P(f"Wikipedia Summary (Drug): {drug_summary}"))
                reviews.append(html.A('Read More on Wikipedia (Drug)', href=drug_link, target='_blank'))
            except wikipedia.exceptions.DisambiguationError as e:
                # Handle disambiguation errors
                reviews.append(html.P(f"Multiple Wikipedia options found for drug {drug}. Please refine your search."))
            except wikipedia.exceptions.PageError:
                # Handle page not found errors
                reviews.append(html.P(f"No Wikipedia page found for drug {drug}."))

    return reviews


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8000)
