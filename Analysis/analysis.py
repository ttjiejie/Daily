import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template
import argparse
import os
from matplotlib import rcParams

# Data analysis functions
def load_data(file_path):
    """Load CSV data and perform initial cleaning"""
    df = pd.read_csv(file_path)
    
    # Clean column names by stripping whitespace and normalizing
    df.columns = df.columns.str.strip()
    print(f"Actual columns in CSV: {list(df.columns)}")
    
    # Check for required columns
    required_columns = ['sales']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"CSV file is missing required columns: {', '.join(missing_columns)}. Actual columns: {list(df.columns)}")
    
    # Basic data cleaning
    df = df.dropna()  # Remove rows with missing values
    df = df.drop_duplicates()  # Remove duplicate rows
    return df

def analyze_sales(df, group_by='category'):
    """Aggregate sales data by specified column"""
    return df.groupby(group_by)['sales'].sum().reset_index()

def visualize_data(df, title='Sales by Category'):
    """Generate bar plot visualization"""
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x=df.columns[0], y='sales')
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt

def generate_report(data, template_path='report_template.html', output_path='report.html'):
    """Generate HTML report from template"""
    with open(template_path, 'r') as f:
        template = Template(f.read())
    
    html = template.render(
        sales_data=data.to_dict('records'),
        chart_image='sales_chart.png'
    )
    
    with open(output_path, 'w') as f:
        f.write(html)
    return output_path

# Main function
def main():
    parser = argparse.ArgumentParser(description='E-commerce Sales Data Analyzer')
    parser.add_argument('input_file', help='Path to input CSV file')
    parser.add_argument('--group-by', default='category', 
                      help='Column to group sales data by (default: category)')
    parser.add_argument('--output-format', choices=['html', 'pdf'], default='html',
                      help='Output report format (default: html)')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        # Check for CSV files in current directory
        csv_files = [f for f in os.listdir() if f.endswith('.csv')]
        if csv_files:
            print(f"Error: Input file not found. Available CSV files: {', '.join(csv_files)}")
        else:
            print("Error: No input file specified and no CSV files found in current directory")
        parser.print_help()
        return
        
    # Load and clean data
    df = load_data(args.input_file)
    
    # Analyze data
    sales_data = analyze_sales(df, args.group_by)
    
    # Visualize data
    plt = visualize_data(sales_data, f'Sales by {args.group_by}')
    plt.savefig('sales_chart.png')
    
    # Generate report
    if args.output_format == 'html':
        report_path = generate_report(sales_data)
        print(f"Report generated at: {report_path}")
    else:
        print("PDF output not yet implemented")

if __name__ == '__main__':
    main()