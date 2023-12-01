import pandas as pd
import os
import requests
from datetime import datetime
import matplotlib.pyplot as plt



save_path = "saved_releases"
def graph_releases(configuration):
    data = get_release_stats_from_url("https://api.github.com/repos/obsidianmd/obsidian-releases/releases")
    

    if configuration["releases"] or ["all"]:
        if configuration["save"]:
            save_data(data, save_path)

        if configuration["history"]:
            draw_stacked_bar_chart(data)
def save_data(data, save_path):
    """
    Saves the DataFrame as a CSV file with the current date in the filename.
    """
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
            operation_system = ''

            if file_name.endswith('asar.gz'):
                continue
            elif file_name.endswith('dmg'):
                operation_system = 'MacOS'
            elif file_name.endswith('exe'):
                operation_system = 'Windows'
            else:
                operation_system = 'Linux'

            download_count = asset['download_count']
            download_counts[operation_system] += download_count

        total_downloads = sum(download_counts.values())

        if total_downloads > 0:
            normalized_data = {os: (count / total_downloads) * 100 for os, count in download_counts.items()}
        else:
            normalized_data = {os: 0 for os in download_counts.keys()}

        processed_data.append({'version': version, 'published_at': published_at, **normalized_data})

    df = pd.DataFrame(processed_data)
    df['published_at'] = pd.to_datetime(df['published_at']).dt.date
    df.sort_values(by='published_at', ascending=True, inplace=True)
    #print(df)
    return df

def draw_stacked_bar_chart(df):
    df.plot(x='version', kind='bar', stacked=True, figsize=(10, 6))
    plt.xlabel('Version')
    plt.ylabel('Percentage of Downloads')
    plt.title('Stacked Bar Chart of Downloads by Version and OS')
    plt.legend(title='OS', labels=['Linux', 'Windows', 'MacOS'])
    plt.show()


