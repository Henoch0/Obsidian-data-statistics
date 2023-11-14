# 📊 Obsidian Data Statistics 

Welcome to the Obsidian Data Analysis project! This tool is designed to generate insightful graphs and manage data related to Obsidian, a popular note-taking and knowledge management application.

## Features

Plugin Analysis: Explore various aspects of Obsidian plugins, including download trends, growth rates, and more. 📈

Theme Insights: Dive into the world of Obsidian themes, analyzing their popularity and distribution. 🎨

Release Data: Keep track of Obsidian release statistics, understanding user preferences across different platforms. 🚀

## How to Use

Setup: Ensure you have Python installed and run pip install -r requirements.txt to install dependencies.

### Generate Graphs: 

Use command-line arguments to generate specific types of graphs:

-r, --releases: Generate release-related graphs.

-t, --themes: Generate theme-related graphs.

-p, --plugins: Generate plugin-related graphs.

-a, --all: Generate all available graphs.

### Data Management Options:

-s, --save: Save fetched data into the "saved-data" folder.

-hi, --history: Generate historical graphs.

-l, --latest: Generate graphs with the latest data.

## Contributing

Contributions are welcome! Feel free to fork the repository, make your changes, and submit a pull request. 🤝



## 📝 Additional Notes

The main.py file is the entry point of the application, handling command-line arguments for generating graphs and managing data. View [main.py](https://github.com/Henoch0/Obsidian-data-analysis/blob/master/main.py)

The plugins.py, releases.py, and themes.py files contain the core functionality for each respective feature. View [plugins.py](https://github.com/Henoch0/Obsidian-data-analysis/blob/master/plugins.py), View [releases.py](https://github.com/Henoch0/Obsidian-data-analysis/blob/master/releases.py), View [themes.py](https://github.com/Henoch0/Obsidian-data-analysis/blob/master/themes.py)

The requirements.txt file lists all the necessary Python packages. View [requirements.txt](https://github.com/Henoch0/Obsidian-data-analysis/blob/master/requirements.txt)
