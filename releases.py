from matplotlib.colors import LinearSegmentedColormap, to_rgb
import numpy as np
import pandas as pd
import os
import requests
from datetime import datetime
import matplotlib.pyplot as plt

save_path = "saved_releases"

def graph_releases(configuration):
    # Fetch release data from the URL
    data = get_release_stats_from_url("https://api.github.com/repos/obsidianmd/obsidian-releases/releases")

    if configuration["releases"] or ["all"]:
        if configuration["save"]:
            # Save data to CSV
            save_data(data, save_path)

        if configuration["history"]:
            # Draw charts
            draw_stacked_bar_chart(data)
            draw_cumulative_pie_chart(data)

        if  not any([configuration["save"],configuration["history"]]):
            save_data(data, save_path)
            draw_stacked_bar_chart(data)
            draw_cumulative_pie_chart(data)

def generate_gradient_colors(base_color_hex, num_colors):
    """
    Generate a gradient of colors starting from a base color in hexadecimal format.

    Args:
        base_color_hex (str): The base color in hexadecimal format (e.g., "#RRGGBB").
        num_colors (int): The number of gradient colors to generate.

    Returns:
        list: A list of RGB colors forming the gradient.
    """
    # Convert the hexadecimal base color code to RGB
    base_color_rgb = np.array(to_rgb(base_color_hex))

    # Create a slightly lighter version of the base color for the beginning of the gradient
    light_color = base_color_rgb + (1 - base_color_rgb) * 0.5  # Slightly lighten
    light_color = np.clip(light_color, 0, 1)  # Ensure values are within a valid range

    # Create a gradient from the lighter version of the base color (start) to the base color (end)
    cmap = LinearSegmentedColormap.from_list('custom_gradient', [light_color, base_color_rgb], N=num_colors)
    # Generate color values from the gradient, reversing the order
    colors = cmap(np.linspace(0, 1, num_colors))[::-1]
    return colors
    
    
def save_data(data, save_path):
    # Ensure the save_path exists
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Current date for the filename
    current_date = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(save_path, f'releases_{current_date}.csv')

    # Write data to a CSV file
    data.to_csv(file_path, index=False, encoding='utf-8')
    print(f"Data successfully saved to {file_path}")

def get_release_stats_from_url(url):
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching data from {url}. Status code: {response.status_code}")
        return pd.DataFrame()

    releases_data = response.json()
    processed_data = []

    for release in releases_data:
        version = release['tag_name']
        published_at = release['published_at']
        download_counts = {'Linux': 0, 'Windows': 0, 'MacOS': 0}

        for asset in release['assets']:
            file_name = asset['name']
            if file_name.endswith('asar.gz'):
                continue
            elif file_name.endswith('dmg'):
                download_counts['MacOS'] += asset['download_count']
            elif file_name.endswith('exe'):
                download_counts['Windows'] += asset['download_count']
            else:
                download_counts['Linux'] += asset['download_count']

        processed_data.append({
            'version': version, 
            'published_at': published_at, 
            **download_counts
        })

    df = pd.DataFrame(processed_data)
    df['published_at'] = pd.to_datetime(df['published_at']).dt.date
    df.sort_values(by='published_at', ascending=True, inplace=True)

    return df

def draw_stacked_bar_chart(df):
    # Calculate the percentage share for each platform
    df_percent = df[['Linux', 'Windows', 'MacOS']].div(df[['Linux', 'Windows', 'MacOS']].sum(axis=1), axis=0) * 100

    # Add the version column for the X-axis
    df_percent['version'] = df['version']

    # Create a stacked bar chart
    df_percent.plot(x='version', kind='bar', stacked=True, figsize=(10, 6))
    plt.xlabel('Version')
    plt.ylabel('Percentage of Downloads')
    plt.title('Stacked Bar Chart of Downloads by Version and Platform')
    plt.legend(title='Platform', labels=['Linux', 'Windows', 'MacOS'])
    plt.show()

def draw_cumulative_pie_chart(df):
    # Sum the downloads for each platform
    platform_totals = df[['Linux', 'Windows', 'MacOS']].sum()

    # Generate gradient colors
    base_color_hex = "#773ee9"  # Example base color
    num_platforms = len(platform_totals)
    pie_colors = generate_gradient_colors(base_color_hex, num_platforms)

    # Create a pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(platform_totals, labels=platform_totals.index, autopct='%1.1f%%', startangle=140, colors=pie_colors)
    plt.title('Cumulative Download Numbers by Platform')
    plt.show()