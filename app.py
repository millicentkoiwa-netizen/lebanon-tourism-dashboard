import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Lebanon Tourism Infrastructure Dashboard",
    page_icon="🇱🇧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #d4af37;
        text-align: center;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
        border-bottom: 2px solid #d4af37;
        padding-bottom: 0.5rem;
    }
    .insight-box {
        background-color: #f8f9fa;
        border-left: 5px solid #d4af37;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the Lebanon tourism data"""
    url = "https://linked.aub.edu.lb/pkgcube/data/551015b5649368dd2612f795c2a9c2d8_20240902_115953.csv"
    try:
        response = requests.get(url)
        data = pd.read_csv(StringIO(response.text))
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def process_infrastructure_data(df):
    """Process infrastructure data for visualization"""
    infrastructure_mapping = {
        'Hotels': ('Existence of hotels - exists', 'Existence of hotels - does not exist'),
        'Restaurants': ('Existence of restaurants - exists', 'Existence of restaurants - does not exist'),
        'Cafes': ('Existence of cafes - exists', 'Existence of cafes - does not exist'),
        'Guest Houses': ('Existence of guest houses - exists', 'Existence of guest houses - does not exist'),
        'Tourist Attractions': ('Existence of touristic attractions prone to be exploited and developed - exists', 
                               'Existence of touristic attractions that can be expolited and developed - does not exist')
    }
    
    infrastructure_data = []
    for category, (exists_col, not_exists_col) in infrastructure_mapping.items():
        exists_count = df[exists_col].sum() if exists_col in df.columns else 0
        not_exists_count = df[not_exists_col].sum() if not_exists_col in df.columns else 0
        total = exists_count + not_exists_count
        percentage = (exists_count / total * 100) if total > 0 else 0
        
        infrastructure_data.append({
            'Category': category,
            'Exists': exists_count,
            'Does Not Exist': not_exists_count,
            'Total Towns': total,
            'Availability %': percentage
        })
    
    return pd.DataFrame(infrastructure_data)

def create_interactive_bar_chart(df, selected_categories, chart_type):
    """Create interactive bar chart with filtering"""
    filtered_df = df[df['Category'].isin(selected_categories)]
    
    if chart_type == "Stacked":
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Exists',
            x=filtered_df['Category'],
            y=filtered_df['Exists'],
            marker_color='#2ecc71',
            text=filtered_df['Exists'],
            textposition='inside',
            hovertemplate='<b>%{x}</b><br>Exists: %{y}<br><extra></extra>'
        ))
        fig.add_trace(go.Bar(
            name='Does Not Exist',
            x=filtered_df['Category'],
            y=filtered_df['Does Not Exist'],
            marker_color='#e74c3c',
            text=filtered_df['Does Not Exist'],
            textposition='inside',
            hovertemplate='<b>%{x}</b><br>Does Not Exist: %{y}<br><extra></extra>'
        ))
        fig.update_layout(barmode='stack')
    else:  # Side by side
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Exists',
            x=filtered_df['Category'],
            y=filtered_df['Exists'],
            marker_color='#2ecc71',
            text=filtered_df['Exists'],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Exists: %{y}<br><extra></extra>'
        ))
        fig.add_trace(go.Bar(
            name='Does Not Exist',
            x=filtered_df['Category'],
            y=filtered_df['Does Not Exist'],
            marker_color='#e74c3c',
            text=filtered_df['Does Not Exist'],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Does Not Exist: %{y}<br><extra></extra>'
        ))
        fig.update_layout(barmode='group')
    
    fig.update_layout(
        title=f"Tourism Infrastructure Availability - {chart_type} View",
        xaxis_title="Infrastructure Type",
        yaxis_title="Number of Towns",
        font=dict(size=12),
        height=500,
        showlegend=True
    )
    
    return fig

def create_interactive_pie_chart(df, selected_categories, view_type):
    """Create interactive pie chart with different view options"""
    filtered_df = df[df['Category'].isin(selected_categories)]
    
    if view_type == "Individual Categories":
        # Create subplots for individual pie charts
        rows = (len(selected_categories) + 2) // 3
        cols = min(3, len(selected_categories))
        
        fig = make_subplots(
            rows=rows, cols=cols,
            specs=[[{"type": "domain"}] * cols for _ in range(rows)],
            subplot_titles=selected_categories
        )
        
        for i, category in enumerate(selected_categories):
            row = (i // cols) + 1
            col = (i % cols) + 1
            
            cat_data = filtered_df[filtered_df['Category'] == category].iloc[0]
            values = [cat_data['Exists'], cat_data['Does Not Exist']]
            labels = ['Exists', 'Does Not Exist']
            
            fig.add_trace(
                go.Pie(
                    labels=labels,
                    values=values,
                    name=category,
                    marker_colors=['#2ecc71', '#e74c3c'],
                    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            title="Infrastructure Availability by Category",
            height=400 * rows,
            showlegend=True
        )
        
    else:  # Combined view
        # Create combined data
        all_data = []
        colors = []
        color_map = {'Hotels': '#3498db', 'Restaurants': '#e67e22', 'Cafes': '#9b59b6', 
                    'Guest Houses': '#1abc9c', 'Tourist Attractions': '#f39c12'}
        
        for _, row in filtered_df.iterrows():
            all_data.extend([row['Exists'], row['Does Not Exist']])
            colors.extend([color_map.get(row['Category'], '#95a5a6'), 
                          color_map.get(row['Category'], '#95a5a6') + '80'])
        
        labels = []
        for _, row in filtered_df.iterrows():
            labels.extend([f"{row['Category']} (Exists)", f"{row['Category']} (Does Not Exist)"])
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=all_data,
            hole=0.3,
            marker_colors=colors,
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title="Combined Infrastructure Distribution",
            height=600,
            annotations=[dict(text='Infrastructure<br>Distribution', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
    
    return fig

# Main app
def main():
    # Header
    st.markdown('<div class="main-header">🇱🇧 Lebanon Tourism Infrastructure Dashboard</div>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading Lebanon tourism data..."):
        raw_data = load_data()
    
    if raw_data is None:
        st.error("Failed to load data. Please check your internet connection.")
        return
    
    # Process data
    infrastructure_df = process_infrastructure_data(raw_data)
    
    # Sidebar controls
    st.sidebar.header("🎛️ Interactive Controls")
    
    # Category filter
    st.sidebar.subheader("Select Infrastructure Categories")
    all_categories = infrastructure_df['Category'].tolist()
    selected_categories = st.sidebar.multiselect(
        "Choose categories to analyze:",
        options=all_categories,
        default=all_categories,
        help="Select one or more infrastructure categories to display"
    )
    
    if not selected_categories:
        st.warning("Please select at least one category to display visualizations.")
        return
    
    # Chart type controls
    st.sidebar.subheader("Visualization Options")
    bar_chart_type = st.sidebar.selectbox(
        "Bar Chart Display:",
        ["Side by Side", "Stacked"],
        help="Choose how to display the bar chart data"
    )
    
    pie_chart_view = st.sidebar.selectbox(
        "Pie Chart View:",
        ["Individual Categories", "Combined View"],
        help="Choose between individual pie charts or a combined view"
    )
    
    # Display insights threshold
    st.sidebar.subheader("Analysis Threshold")
    availability_threshold = st.sidebar.slider(
        "Highlight categories with availability above:",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
        format="%d%%",
        help="Categories above this threshold will be highlighted in insights"
    )
    
    # Main content
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Total Towns Analyzed", len(raw_data))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        total_exists = infrastructure_df['Exists'].sum()
        total_possible = infrastructure_df['Total Towns'].sum()
        overall_percentage = (total_exists / total_possible * 100) if total_possible > 0 else 0
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Overall Infrastructure Availability", f"{overall_percentage:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        best_category = infrastructure_df.loc[infrastructure_df['Availability %'].idxmax(), 'Category']
        best_percentage = infrastructure_df['Availability %'].max()
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Best Available Infrastructure", f"{best_category} ({best_percentage:.1f}%)")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Visualizations
    st.markdown('<div class="sub-header">📊 Interactive Visualizations</div>', unsafe_allow_html=True)
    
    # Bar chart
    st.subheader("Infrastructure Availability Comparison")
    bar_fig = create_interactive_bar_chart(infrastructure_df, selected_categories, bar_chart_type)
    st.plotly_chart(bar_fig, use_container_width=True)
    
    # Pie chart
    st.subheader("Infrastructure Distribution Overview")
    pie_fig = create_interactive_pie_chart(infrastructure_df, selected_categories, pie_chart_view)
    st.plotly_chart(pie_fig, use_container_width=True)
    
    # Dynamic insights
    st.markdown('<div class="sub-header">🔍 Dynamic Insights</div>', unsafe_allow_html=True)
    
    filtered_df = infrastructure_df[infrastructure_df['Category'].isin(selected_categories)]
    
    # High availability categories
    high_availability = filtered_df[filtered_df['Availability %'] >= availability_threshold]
    if not high_availability.empty:
        st.markdown(f'<div class="insight-box"><b>🟢 High Availability Infrastructure (≥{availability_threshold}%):</b><br>', unsafe_allow_html=True)
        for _, row in high_availability.iterrows():
            st.markdown(f"• <b>{row['Category']}</b>: {row['Availability %']:.1f}% ({row['Exists']}/{row['Total Towns']} towns)")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Low availability categories
    low_availability = filtered_df[filtered_df['Availability %'] < availability_threshold]
    if not low_availability.empty:
        st.markdown(f'<div class="insight-box"><b>🔴 Lower Availability Infrastructure (<{availability_threshold}%):</b><br>', unsafe_allow_html=True)
        for _, row in low_availability.iterrows():
            st.markdown(f"• <b>{row['Category']}</b>: {row['Availability %']:.1f}% ({row['Exists']}/{row['Total Towns']} towns)")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Data table
    with st.expander("📋 Detailed Data Table"):
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("**Data Source:** American University of Beirut - Lebanon Tourism Infrastructure Study")
    st.markdown("**Dashboard Features:** Interactive filtering, dynamic visualizations, and real-time insights")

if __name__ == "__main__":
    main()
    