import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="Audit Performance Dashboard", layout="wide")

# Function to process and validate data
def process_data(coder_sheet, project_sheet):
    try:
        # Clean column names
        coder_sheet.columns = coder_sheet.columns.str.strip()
        project_sheet.columns = project_sheet.columns.str.strip()
        
        # Validate column count
        if len(coder_sheet.columns) < 4 or len(project_sheet.columns) < 2:
            st.error("Excel sheets don't have the required number of columns!")
            return None, None
        
        # Convert accuracy values to proper percentages if they're not already
        accuracy_col_coder = coder_sheet.columns[3]
        accuracy_col_project = project_sheet.columns[1]
        
        # Check if values are already in percentage format
        if coder_sheet[accuracy_col_coder].max() <= 1:
            coder_sheet[accuracy_col_coder] = coder_sheet[accuracy_col_coder] * 100
        if project_sheet[accuracy_col_project].max() <= 1:
            project_sheet[accuracy_col_project] = project_sheet[accuracy_col_project] * 100
            
        return coder_sheet, project_sheet
    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None, None

# Main app
st.title("📊 Audit Performance Dashboard")

# File upload section
uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # Read Excel file
        xl = pd.ExcelFile(uploaded_file)
        
        # Show sheet selection if more than 2 sheets
        if len(xl.sheet_names) > 2:
            st.write("Please select the sheets containing coder and project data:")
            coder_sheet_name = st.selectbox("Select Coder Data Sheet:", xl.sheet_names, index=0)
            project_sheet_name = st.selectbox("Select Project Data Sheet:", xl.sheet_names, index=1)
            
            coder_data = pd.read_excel(uploaded_file, sheet_name=coder_sheet_name)
            project_data = pd.read_excel(uploaded_file, sheet_name=project_sheet_name)
        else:
            # If 2 or fewer sheets, use first two sheets
            coder_data = pd.read_excel(uploaded_file, sheet_name=0)
            project_data = pd.read_excel(uploaded_file, sheet_name=1)
        
        # Process and validate data
        coder_data, project_data = process_data(coder_data, project_data)
        
        if coder_data is not None and project_data is not None:
            # Create two columns for the accuracy charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Project-wise Accuracy")
                fig_project = px.bar(
                    project_data,
                    x=project_data.columns[0],
                    y=project_data.columns[1],
                    text=project_data.columns[1],
                    color=project_data.columns[1],
                    color_continuous_scale="Viridis",
                    height=400
                )
                fig_project.update_traces(
                    texttemplate='%{text:.2f}%',
                    textposition='outside'
                )
                fig_project.update_layout(
                    yaxis_range=[0, 100],
                    yaxis_tickformat='.2f'
                )
                st.plotly_chart(fig_project, use_container_width=True)
                
                # Find top project
                top_project_idx = project_data[project_data.columns[1]].idxmax()
                top_project = {
                    'name': project_data.iloc[top_project_idx, 0],
                    'accuracy': project_data.iloc[top_project_idx, 1]
                }
                st.success(f"🏆 Top Performing Project: **{top_project['name']}** with **{top_project['accuracy']:.2f}%** accuracy!")
            
            with col2:
                st.subheader("Coder-wise Accuracy")
                fig_coder = px.bar(
                    coder_data,
                    x=coder_data.columns[0],
                    y=coder_data.columns[3],
                    text=coder_data.columns[3],
                    color=coder_data.columns[3],
                    color_continuous_scale="Viridis",
                    height=400
                )
                fig_coder.update_traces(
                    texttemplate='%{text:.2f}%',
                    textposition='outside'
                )
                fig_coder.update_layout(
                    yaxis_range=[0, 100],
                    yaxis_tickformat='.2f'
                )
                st.plotly_chart(fig_coder, use_container_width=True)
                
                # Find top coder
                top_coder_idx = coder_data[coder_data.columns[3]].idxmax()
                top_coder = {
                    'name': coder_data.iloc[top_coder_idx, 0],
                    'accuracy': coder_data.iloc[top_coder_idx, 3]
                }
                st.success(f"🏆 Top Performing Coder: **{top_coder['name']}** with **{top_coder['accuracy']:.2f}%** accuracy!")
            
            # Error vs No Error Analysis
            st.subheader("Coder-wise Error Analysis")
            fig_error = go.Figure(data=[
                go.Bar(name='No Error', x=coder_data[coder_data.columns[0]], y=coder_data[coder_data.columns[1]]),
                go.Bar(name='Error', x=coder_data[coder_data.columns[0]], y=coder_data[coder_data.columns[2]])
            ])
            
            fig_error.update_layout(
                barmode='group',
                height=400,
                yaxis_title="Number of Cases",
                showlegend=True,
                legend_title_text="Case Type"
            )
            
            st.plotly_chart(fig_error, use_container_width=True)
            
            # Congratulatory Messages
            st.markdown("---")
            st.subheader("🎉 Congratulations to Our Top Performers!")
            
            msg_col1, msg_col2 = st.columns(2)
            
            with msg_col1:
                st.info(f"""
                🌟 **Project Excellence Award**
                
                Congratulations to **{top_project['name']}** for achieving an outstanding accuracy rate of **{top_project['accuracy']:.2f}%**!
                
                Keep up the excellent work!
                """)
            
            with msg_col2:
                st.info(f"""
                🌟 **Coder Excellence Award**
                
                Congratulations to **{top_coder['name']}** for maintaining an impressive accuracy rate of **{top_coder['accuracy']:.2f}%**!
                
                Your attention to detail makes a difference!
                """)
            
            # Additional Insights
            st.markdown("---")
            st.subheader("📈 Key Performance Insights")
            
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                avg_coder_accuracy = coder_data[coder_data.columns[3]].mean()
                st.metric("Average Coder Accuracy", f"{avg_coder_accuracy:.2f}%")
            
            with metric_col2:
                avg_project_accuracy = project_data[project_data.columns[1]].mean()
                st.metric("Average Project Accuracy", f"{avg_project_accuracy:.2f}%")
            
            with metric_col3:
                total_cases = coder_data[coder_data.columns[1]].sum() + coder_data[coder_data.columns[2]].sum()
                st.metric("Total Cases Reviewed", f"{total_cases:,}")
            
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Please ensure your Excel file has the correct structure with coder data and project data sheets.")
else:
    st.info("👆 Please upload an Excel file to generate the dashboard")