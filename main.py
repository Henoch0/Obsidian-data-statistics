import releases
import themes
import plugins
import argparse

if __name__ == '__main__':
    # Create an argument parser to handle command-line arguments
    parser = argparse.ArgumentParser(description='Generate various graphs and manage data.')
    
    # Define command-line arguments for generating specific types of graphs
    parser.add_argument('-r', '--releases', action='store_true', help='Generate release-related graphs')
    parser.add_argument('-t', '--themes', action='store_true', help='Generate theme-related graphs')
    parser.add_argument('-p', '--plugins', action='store_true', help='Generate plugin-related graphs')
    parser.add_argument('-a', '--all', action='store_true', help='Generate all available graphs')
    
    # Define command-line arguments for data management
    parser.add_argument('-s', '--save', action='store_true', help='Save fetched data into "saved-data" folder')
    parser.add_argument('-hi', '--history', action='store_true', help='Generate historical graphs')
    parser.add_argument('-l', '--latest', action='store_true', help='Generate graphs with the latest data')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Define a configuration dictionary based on the provided arguments
    configuration = {
        'plugins': args.plugins and not args.save and not args.history and not args.latest,
        'themes': args.themes and not args.save and not args.history and not args.latest,
        'releases': args.releases and not args.save and not args.history and not args.latest,
        'save': args.save,
        'history': args.history,
        'latest': args.latest,
        'all' : args.plugins and args.themes
    }

    # Execute functions based on the selected graph types
    if args.themes or args.all:
        themes.graph_themes(configuration)
    if args.plugins or args.all:
        plugins.graph_plugins(configuration)
    if args.releases or args.all:
        releases.graph_releases(configuration)