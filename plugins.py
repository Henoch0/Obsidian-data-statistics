import pandas as pd
import re
import os
import csv
import datetime
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import requests
import json
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, to_rgb

save_path = "saved_plugins"
def graph_plugins(configuration):
    """
    Main function to graph plugins based on the provided configuration.
    """

    # Define the URL for the GitHub commit history and headers for authentication.
    commit_history_url = "https://api.github.com/repos/obsidianmd/obsidian-releases/commits?path=community-plugin-stats.json"
    headers = {
        "Authorization": "Insert your Github token her. You can generate one here https://github.com/settings/tokens"
    }

    # Retrieve plugin data from GitHub and local JSON file.
    monthly_plugin_counts, monthly_downloads = get_plugin_data_from_github(commit_history_url, headers)
    data = get_plugin_stats_from_url("https://raw.githubusercontent.com/obsidianmd/obsidian-releases/master/community-plugin-stats.json")
    
    url = "https://raw.githubusercontent.com/obsidianmd/obsidian-releases/master/community-plugins.json"


    if configuration["themes"] or ["all"]:
        if configuration["save"]:
            # -p -s
            save_data(data, save_path)
            save_monthly_downloads_to_file(monthly_downloads)
            save_monthly_plugin_counts_to_file(monthly_plugin_counts)
        if configuration["latest"]:
            # -p -l
            draw_download_distribution_graph(data)
            #draw_plugin_boxplot(data)
            draw_plugin_kde(data)
        if configuration["history"]:
            # -p -hi
            draw_download_history_graph(monthly_downloads)
            draw_monthly_plugin_counts_graph(monthly_plugin_counts)
            draw_plugin_growth_graph(monthly_plugin_counts)
            draw_combined_stats_graph(monthly_plugin_counts, monthly_downloads)
        if  not any([configuration["save"], configuration["latest"], configuration["history"]]):
            # -p or -all
            save_data(data, save_path)
            save_monthly_downloads_to_file(monthly_downloads)
            save_monthly_plugin_counts_to_file(monthly_plugin_counts)
            draw_download_history_graph(monthly_downloads)
            draw_monthly_plugin_counts_graph(monthly_plugin_counts)
            draw_plugin_growth_graph(monthly_plugin_counts)
            draw_combined_stats_graph(monthly_plugin_counts, monthly_downloads)
            draw_download_distribution_graph(data)
            draw_plugin_boxplot(data)
    

# Function to retrieve plugin data from GitHub and process it.
def get_plugin_data_from_github(commit_history_url, headers):
    def get_all_commits(url, headers):
        """
        Retrieve all commits related to a specific URL from GitHub.
        
        Args:
            url (str): The URL to retrieve commits from.
            headers (dict): HTTP headers for authentication.

        Returns:
            list: A list of commit objects.
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
        Process the retrieved commits to extract monthly plugin counts and downloads.

        Args:
            commits (list): A list of commit objects.

        Returns:
            dict: Monthly plugin counts and monthly downloads as dictionaries.
        """
        monthly_commits = {}
        for commit in commits:
            date = commit["commit"]["committer"]["date"]
            month_year = date[:7]  # Format: YYYY-MM
            if month_year not in monthly_commits:
                monthly_commits[month_year] = commit["sha"]
        
        monthly_plugin_counts = {}
        monthly_downloads = {}
        for month_year, commit_sha in monthly_commits.items():
            file_url = f"https://raw.githubusercontent.com/obsidianmd/obsidian-releases/{commit_sha}/community-plugin-stats.json"
            response = requests.get(file_url)
            data = response.json()
            plugin_count = len(data)
            total_downloads = sum(plugin.get('downloads', 0) for plugin in data.values())
            monthly_plugin_counts[month_year] = plugin_count
            monthly_downloads[month_year] = total_downloads
        
        return monthly_plugin_counts, monthly_downloads

    try:
        commits = get_all_commits(commit_history_url, headers)
        if commits is None:
            raise Exception("Error fetching commit history. Due to rate limit or missing GitHub token. Using local JSON data instead.")
        return process_commits(commits)
    except Exception as e:
        print("Error:", str(e))
        try:
            with open(f'{save_path}/monthly_plugin_downloads.json', 'r') as file:
                monthly_downloads = json.load(file)
            with open(f'{save_path}/monthly_plugin_counts.json', 'r') as file:
                monthly_plugin_counts = json.load(file)
            return monthly_plugin_counts, monthly_downloads
        except FileNotFoundError as e:
            print("File not found:", str(e))
            return None, None


def get_plugin_stats_from_url(url):
    """
    Fetch plugin stats data from a given URL and return it as a dictionary.

    Args:
        url (str): The URL to retrieve plugin stats data from.

    Returns: A dictionary containing the retrieved plugin stats data.
    """ 
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching data from {url}. Status code: {response.status_code}")
        return {}

    data = response.json()
    return data

def save_data(data, save_path):
    # Remove the 'id' key and sort by download count
    sorted_data = {plugin: {'downloads': values['downloads']} for plugin, values in sorted(data.items(), key=lambda item: item[1]['downloads'], reverse=True)}

    # Ensure that the save_path directory exists
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Get the current date for the file name
    current_date = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(save_path, f'plugins_{current_date}.csv')

    # Write data to a CSV file
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Downloads'])  # Write the header
        for plugin, values in sorted_data.items():
            writer.writerow([plugin, values['downloads']])

    print(f"Latest Data saved in {file_path}")
    
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
    
def save_monthly_downloads_to_file(monthly_downloads, file_format="json"):
    """
    Save monthly download counts to a file in JSON or CSV format.

    Args:
        monthly_downloads (dict): A dictionary containing monthly download counts.
        file_format (str): The desired file format ("json" or "csv").

    Returns:
        None
    """
    # Define the filename based on the specified file format.
    filename = os.path.join(save_path, f"monthly_plugin_downloads.{file_format}")

    if file_format == "json":
        # Save data in JSON format.
        with open(filename, "w") as f:
            json.dump(monthly_downloads, f, indent=4)
    elif file_format == "csv":
        # Save data in CSV format.
        with open(filename, "w") as f:
            f.write("Month,Downloads\n")  # Write the CSV header.
            for month, downloads in monthly_downloads.items():
                f.write(f"{month},{downloads}\n")  # Write CSV rows.
    else:
        # Handle invalid file format.
        print(f"Invalid file format: {file_format}")
        return

    print(f"Monthly download counts saved in {filename}.")

def save_monthly_plugin_counts_to_file(monthly_plugin_counts, file_format="json"):
    """
    Save monthly plugin counts to a file in JSON or CSV format.

    Args:
        monthly_plugin_counts (dict): A dictionary containing monthly plugin counts.
        file_format (str): The desired file format ("json" or "csv").

    Returns:
        None
    """
    
    # Define the filename based on the specified file format.
    filename = os.path.join(save_path, f"monthly_plugin_counts.{file_format}")

    if file_format == "json":
        # Save data in JSON format.
        with open(filename, "w") as f:
            json.dump(monthly_plugin_counts, f, indent=4)
    elif file_format == "csv":
        # Save data in CSV format.
        with open(filename, "w") as f:
            f.write("Month,Plugin Count\n")  # Write the CSV header.
            for month, count in monthly_plugin_counts.items():
                f.write(f"{month},{count}\n")  # Write CSV rows.
    else:
        # Handle invalid file format.
        print(f"Invalid file format: {file_format}")
        return

    print(f"Monthly plugin counts saved in {filename}.")

def draw_download_history_graph(monthly_downloads):
    """
    Create a bar chart of monthly download counts with gradient colors.
    """
    # Sort the data to display the oldest data first.
    sorted_data = sorted(monthly_downloads.items(), key=lambda x: x[0])

    # Extract months and download counts.
    months = [item[0] for item in sorted_data]
    downloads = [item[1] for item in sorted_data]

    # Create a bar chart.
    plt.figure(figsize=(15, 7))
    colors = generate_gradient_colors('#773ee9', len(months))[::-1]  # Generate gradient colors.
    plt.bar(months, [x/1_000_000 for x in downloads], color=colors)  # Convert downloads to millions for readability.
    plt.xticks(rotation=45)
    plt.xlabel('Month')
    plt.ylabel('Downloads (in millions)')
    plt.title('Monthly Download Counts (values in millions)')
    plt.tight_layout()
    
    plt.show()

def draw_monthly_plugin_counts_graph(monthly_plugin_counts):
    """
    Create a bar chart of monthly plugin counts.

    This function sorts the data so that the oldest data is displayed first.
    It extracts months and plugin counts from the input dictionary,
    then creates a bar chart with gradient colors for visual appeal.
    """
    # Sort the data to display the oldest data first.
    sorted_data = sorted(monthly_plugin_counts.items(), key=lambda x: x[0])

    # Extract months and plugin counts.
    months = [item[0] for item in sorted_data]
    counts = [item[1] for item in sorted_data]

    # Create a bar chart.
    plt.figure(figsize=(15, 7))
    colors = generate_gradient_colors('#773ee9', len(months))[::-1]  # Generate gradient colors.
    plt.bar(months, counts, color=colors)
    plt.xticks(rotation=45)
    plt.xlabel('Month')
    plt.ylabel('Plugin Counts')
    plt.title('Monthly Plugin Counts')
    plt.tight_layout()
    plt.show()

def draw_download_distribution_graph(data):
    """
    Create a line plot of the percentage of downloads for the top N plugins.
    """
    # Define a list of top N values to analyze
    top_n_values = [0, 20, 50, 100, 200, 500, 700, 1000, 1200]

    # Extract plugin names and total download counts
    # Sort the data by total download count in descending order
    sorted_data = sorted(data.items(), key=lambda item: item[1]['downloads'], reverse=True)

    # Calculate the total number of downloads
    total_downloads = sum([item[1]['downloads'] for item in sorted_data])

    # Calculate the percentage of downloads for the top N plugins
    cumulative_percentages = []
    for n in top_n_values:
        top_n_downloads = sum([item[1]['downloads'] for item in sorted_data[:n]])
        cumulative_percentage = (top_n_downloads / total_downloads) * 100
        cumulative_percentages.append(cumulative_percentage)

    # Create a line plot
    plt.figure(figsize=(10, 6))
    plt.plot(top_n_values, cumulative_percentages, marker='o', linestyle='-', color='#773ee9')

    # Adjust the x-axis and y-axis limits
    plt.xlim(0, max(top_n_values) + 50)  # Add some space to the right
    plt.ylim(0, max(cumulative_percentages) + 10)  # Ensure the Y-axis starts at 0

    # Define custom tick values for the x-axis
    plt.xticks([0, 20, 50, 100, 200, 500, 700, 1000, 1200])

    plt.title('Percentage of downloads for top N plugins')
    plt.xlabel('Top N Plugins')
    plt.ylabel('Percentage of downloads')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def draw_plugin_growth_graph(monthly_plugin_counts):
    """
    Draw a line graph showing the growth rate of plugins over time.
    """
    # Sort the months in ascending order
    months = sorted(monthly_plugin_counts.keys())
    counts = [monthly_plugin_counts[month] for month in months]
    
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
    plt.title('Monthly Plugin Growth Rate')
    
    # Adjust layout and display grid lines
    plt.tight_layout()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.show()

def draw_combined_stats_graph(monthly_plugin_counts, monthly_downloads):
    """
    Create a line graph showing the monthly plugin counts, monthly downloads, and total downloads.
    """
    # Sort the months in ascending order
    months = sorted(monthly_plugin_counts.keys())
    plugin_counts = [monthly_plugin_counts[month] for month in months]
    download_counts = [monthly_downloads[month] for month in months]

    # Create the graph
    fig, ax1 = plt.subplots(figsize=(25, 7))
    
    # Plugin counts as a line on the left Y-axis
    ax1.plot(months, plugin_counts, marker='o', linestyle='-', color='#773ee9', label='Plugin Counts')
    ax1.set_ylabel('Plugin Counts', color='#773ee9')  # Y-axis label for plugin counts
    ax1.tick_params(axis='y', labelcolor='#773ee9')
    
    # Monthly downloads as a line on the right Y-axis
    ax2 = ax1.twinx()  # Create a second Y-axis
    ax2.plot(months, download_counts, marker='s', linestyle='--', color='grey', label='Monthly Downloads')
    ax2.set_ylabel('Monthly Downloads', color='grey')  # Y-axis label for monthly downloads
    ax2.tick_params(axis='y', labelcolor='grey')
    
    # Total downloads as a dashed line
    # total_downloads = 31306961  # Insert the actual value for total downloads here
    # ax2.axhline(y=total_downloads, color='red', linestyle='--', label='Total Downloads')
    
    # Rotate months on the x-axis to save space
    plt.xticks(rotation=90)
    
    # Set axis labels and title
    plt.xlabel('Month')
    plt.title('Monthly Plugin Counts and Downloads')
    
    # Adjust the legend and place it below the graph
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
    
    # Adjust layout and display grid lines
    plt.tight_layout()
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.show()

def draw_plugin_boxplot(data):
    """
    Create a boxplot of download numbers from the provided data.
    """
    # Convert JSON data to a DataFrame
    df = pd.DataFrame.from_dict(data, orient='index')
    
    # Calculate the median
    median = df['downloads'].median()
    
    # Calculate the average of all downloads
    average_downloads = df['downloads'].mean()
    
    # Create the boxplot
    plt.figure(figsize=(7, 10))
    sns.boxplot(data=df['downloads'], color='#773ee9')  # Set the color here

    # Add labels for the median, plugins below Q1, and average above the title
    plt.title(f"Boxplot (Median: {median:.0f}, Average: {average_downloads:.2f})", y=1.03)  # Raise the title on the Y-axis

    plt.xlabel("Plugins")
    plt.ylabel("Downloads in Millions")
    plt.show()


def draw_plugin_kde(data):
    """
    Create a KDE plot of download numbers from the provided data.
    """
    # Convert JSON data to a DataFrame
    df = pd.DataFrame.from_dict(data, orient='index')
    
    # Calculate the median
    median = df['downloads'].median()
    
    # Calculate the average of all downloads
    average_downloads = df['downloads'].mean()
    
    # Create the KDE plot
    plt.figure(figsize=(7, 10))
    sns.kdeplot(df['downloads'], color='#773ee9')

    # Add labels for the median, plugins below Q1, and average above the title
    plt.title(f"KDE Plot (Median: {median:.0f}, Average: {average_downloads:.2f})", y=1.03)  # Raise the title on the Y-axis

    plt.xlabel("Downloads")
    plt.ylabel("Density")
    plt.show()