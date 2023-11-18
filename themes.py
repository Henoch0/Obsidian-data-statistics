import pandas as pd
import os
import csv
import datetime
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import json
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, to_rgb


save_path = "saved_themes"

def graph_themes(configuration):
    """
    Main function to graph themes based on the provided configuration.

    Args:
        configuration (dict): A dictionary containing configuration options.

    Returns:
        None
    """
    commit_history_url = "https://api.github.com/repos/obsidianmd/obsidian-releases/commits?path=community-css-themes.json"
    headers = {
        "Authorization": "Insert your Github token here. You can generate one here https://github.com/settings/tokens"
    }

    # Fetch monthly theme counts data from GitHub commit history
    monthly_themes_counts = get_theme_data_from_github(commit_history_url, headers)
    
    # Fetch latest theme statistics data
    data = get_theme_stats_from_url("https://releases.obsidian.md/stats/theme")

    if configuration["themes"] or ["all"]:
        if configuration["save"]:
            # -t -s
            save_monthly_theme_counts_to_file(monthly_themes_counts)
            save_latest_data(data, save_path)
        if configuration["latest"]:
            # -t -l
            draw_download_distribution_graph(data)
            #draw_theme_boxplot(data)
            draw_theme_histogram(data)
            draw_theme_kde(data)
        if configuration["history"]:
            # -t -hi
            draw_monthly_theme_counts_graph(monthly_themes_counts)
            draw_theme_growth_graph(monthly_themes_counts)
        if not any([configuration["save"], configuration["latest"], configuration["history"]]):
            # -t or -all
            save_monthly_theme_counts_to_file(monthly_themes_counts)
            save_latest_data(data, save_path)
            draw_monthly_theme_counts_graph(monthly_themes_counts)
            draw_theme_growth_graph(monthly_themes_counts)
            draw_download_distribution_graph(data)
            draw_theme_boxplot(data)
            draw_theme_histogram(data)
        
def get_theme_data_from_github(commit_history_url, headers):
    """
    Fetch monthly theme counts data from GitHub's commit history and store it locally.

    Args:
        commit_history_url (str): The URL to fetch commit history data.
        headers (dict): Headers for authentication (can be an empty dictionary).

    Returns:
        dict: A dictionary containing monthly theme counts.
    """
    def get_all_commits(url, headers):
        """
        Fetch all commits from a given URL.

        Args:
            url (str): The URL to fetch commits from.
            headers (dict): Headers for authentication (can be an empty dictionary).

        Returns:
            list: A list of commit data.
        """
        all_commits = []
        while url:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return None
            commits = response.json()
            all_commits.extend(commits)
            url = response.links['next']['url'] if 'next' in response.links else None
        return all_commits

    def process_commits(commits):
        """
        Process commit data to extract monthly theme counts.

        Args:
            commits (list): List of commit data.

        Returns:
            dict: A dictionary containing monthly theme counts.
        """
        monthly_commits = {}
        for commit in commits:
            date = commit["commit"]["committer"]["date"]
            month_year = date[:7]  # Format: YYYY-MM
            if month_year not in monthly_commits:
                monthly_commits[month_year] = commit["sha"]
        
        monthly_theme_counts = {}
        for month_year, commit_sha in monthly_commits.items():
            file_url = f"https://raw.githubusercontent.com/obsidianmd/obsidian-releases/{commit_sha}/community-css-themes.json"
            response = requests.get(file_url)
            data = response.json()
            theme_count = len(data)
            monthly_theme_counts[month_year] = theme_count
        
        return monthly_theme_counts

    try:
        commits = get_all_commits(commit_history_url, headers)
        if commits is None:
            raise Exception("Error fetching commit history. Due to rate limit or missing GitHub token. Using local JSON data instead.")
        return process_commits(commits)
    except Exception as e:
        print("Error:", str(e))
        try:
            with open(f'{save_path}/monthly_theme_counts.json', 'r') as file:
                monthly_theme_counts = json.load(file)
            return monthly_theme_counts
        except FileNotFoundError as e:
            print("File not found:", str(e))
            return None
        
def get_theme_stats_from_url(url):
    """
    Fetch theme statistics data from a given URL.

    Args:
        url (str): The URL to fetch theme statistics data from.

    Returns:
        dict: A dictionary containing theme statistics data.
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching data from {url}. Status code: {response.status_code}")
        return {}

    # Load the data as JSON
    data = response.json()
    return data

def save_latest_data(data, save_path):
    """
    Save the latest theme data to a CSV file with the current date in the filename.

    Args:
        data (dict): A dictionary containing theme data.
        save_path (str): The path where the CSV file will be saved.

    Returns:
        None
    """
    # Remove the 'id' key and sort by download count
    sorted_data = {theme: {'download': values['download']} for theme, values in sorted(data.items(), key=lambda item: item[1]['download'], reverse=True)}

    # Ensure that the save_path exists
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Current date for the filename
    current_date = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(save_path, f'themes_{current_date}.csv')

    # Write data to a CSV file
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Download'])  # Write the header
        for theme, values in sorted_data.items():
            writer.writerow([theme, values['download']])

    print(f"Latest theme data saved in {file_path}")

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

def save_monthly_theme_counts_to_file(monthly_theme_counts, file_format="json"):
    """
    Save monthly theme counts to a file in JSON or CSV format.
    """
    # Define the filename based on the specified file format
    filename = os.path.join(save_path, f"monthly_theme_counts.{file_format}")

    if file_format == "json":
        # Save data in JSON format
        with open(filename, "w") as f:
            json.dump(monthly_theme_counts, f, indent=4)
    elif file_format == "csv":
        # Save data in CSV format
        with open(filename, "w") as f:
            f.write("Month,Theme Count\n")
            for month, count in monthly_theme_counts.items():
                f.write(f"{month},{count}\n")
    else:
        # Handle invalid file format
        print(f"Invalid file format: {file_format}")
        return

    # Print a message indicating successful saving
    print(f"Monthly theme counts saved in {filename}.")


def draw_monthly_theme_counts_graph(monthly_theme_counts):
    """
    Plots a bar chart of monthly theme counts.
    """
    # Sort the data so that the oldest data is displayed first
    sorted_data = sorted(monthly_theme_counts.items(), key=lambda x: x[0])

    # Extract months and theme counts
    months = [item[0] for item in sorted_data]
    counts = [item[1] for item in sorted_data]

    # Create a bar chart
    plt.figure(figsize=(15, 7))
    colors = generate_gradient_colors('#773ee9', len(months))[::-1]
    plt.bar(months, counts, color=colors)
    plt.xticks(rotation=45)
    plt.xlabel('Month')
    plt.ylabel('Theme Counts')
    plt.title('Monthly Theme Counts')
    plt.tight_layout()
    plt.show()


def draw_theme_growth_graph(monthly_theme_counts):
    """
    Draw a line graph showing the growth rate of themes over time.

    Args:
        monthly_theme_counts (dict): A dictionary containing monthly theme counts.

    Returns:
        None
    """
    # Sort the months in ascending order
    months = sorted(monthly_theme_counts.keys())
    counts = [monthly_theme_counts[month] for month in months]
    
    # Calculate growth rates (in percentage), starting from the second month
    growth_rates = []
    for i in range(2, len(counts)):
        growth_rate = ((counts[i] - counts[i-1]) / counts[i-1]) * 100
        growth_rates.append(max(growth_rate, 0))
    
    # Create the growth rate graph
    plt.figure(figsize=(15, 7))
    plt.plot(months[2:], growth_rates, marker='o', linestyle='-', color='#773ee9')  # Starts from the second month
    
    # Rotate months on the x-axis for better readability
    plt.xticks(rotation=45)
    
    # Set axis labels and title
    plt.xlabel('Month')
    plt.ylabel('Growth Rate (%)')
    plt.title('Monthly Theme Growth Rate')
    
    # Adjust layout and display grid lines
    plt.tight_layout()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.show()

def draw_download_distribution_graph(data):
    """
    Create a histogram showing the distribution of theme download counts.

    Args:
        data (dict): A dictionary containing theme download data.

    Returns:
        None
    """
    # Extract download counts from the data
    downloads = [theme['download'] for theme in data.values()]

    # Define the bins for the histogram
    bins = 50 # Fixed number of bins

    # Create the histogram
    plt.figure(figsize=(12, 6))
    plt.hist(downloads, bins=bins, edgecolor='black', color='#773ee9', alpha=0.7)

    # Set axis labels and title
    plt.xlabel('Number of Downloads')
    plt.ylabel('Number of Themes')
    plt.title('Distribution of Theme Downloads')
    plt.yscale('log')  # Set y-axis to log scale
    plt.tight_layout()
    plt.show()


def draw_theme_boxplot(data):
    """
    Create a boxplot of download numbers from the provided data for themes.
    """
    # Convert JSON data to a DataFrame
    df = pd.DataFrame.from_dict(data, orient='index')
    
    # Create the boxplot
    plt.figure(figsize=(7, 10))
    sns.boxplot(data=df['download'], color='#773ee9')  # Set the color here

    plt.title("Boxplot of Theme Downloads")
    plt.xlabel("Themes")
    plt.ylabel("Downloads")
    plt.show()

def draw_theme_histogram(data):
    """
    Create a histogram of download numbers from the provided data for themes.
    """
    # Convert JSON data to a DataFrame
    df = pd.DataFrame.from_dict(data, orient='index')
    
    # Create the histogram
    plt.figure(figsize=(7, 10))
    sns.histplot(data=df['download'], color='#773ee9')  # Set the color here

    plt.title("Histogram of Theme Downloads")
    plt.xlabel("Downloads")
    plt.ylabel("Frequency")
    plt.show()

def draw_theme_kde(data):
    """
    Create a KDE plot of download numbers from the provided data for themes.
    """
    # Convert JSON data to a DataFrame
    df = pd.DataFrame.from_dict(data, orient='index')
    
    # Create the KDE plot
    plt.figure(figsize=(10, 7))
    sns.kdeplot(df['download'], color='#773ee9')

    plt.title("KDE Plot of Theme Downloads")
    plt.xlabel("Downloads")
    plt.ylabel("Density")
    plt.show()