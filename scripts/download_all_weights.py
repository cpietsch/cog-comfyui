#!/usr/bin/env python3
import os
import json
import argparse
from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from weights_downloader import WeightsDownloader
from weights_manifest import WeightsManifest

def main():
    parser = argparse.ArgumentParser(description="Download all weights from weights.json or specific types")
    parser.add_argument('--types', nargs='+', help='Specific weight types to download (e.g., CHECKPOINTS LORAS)')
    parser.add_argument('--list-types', action='store_true', help='List all available weight types and exit')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be downloaded without downloading')
    parser.add_argument('--num', type=int, help='Download only a specific number of weights per type')
    parser.add_argument('--base-path', help='Base path for downloaded weights (overrides the default path)')
    args = parser.parse_args()

    downloader = WeightsDownloader()

    weights_manifest = WeightsManifest()
    weights_map = weights_manifest.weights_map

    
    # Load the weights.json file to get all types
    weights_file_path = os.path.join(os.path.dirname(__file__), "weights.json")
    with open(weights_file_path, "r") as f:
        weights_json = json.load(f)
    
    # If --list-types flag is used, show all available types and exit
    if args.list_types:
        print("Available weight types:")
        for weight_type in sorted(weights_json.keys()):
            print(f"  {weight_type} ({len(weights_json[weight_type])} weights)")
        return
    
    # Determine which types to download
    types_to_download = args.types if args.types else weights_json.keys()
    
    # Validate the types
    invalid_types = [t for t in types_to_download if t not in weights_json]
    if invalid_types:
        print(f"Error: Invalid weight types: {', '.join(invalid_types)}")
        print("Use --list-types to see available types")
        return

    # Display summary of what will be downloaded
    total_weights = 0
    for type_name in types_to_download:
        weight_list = weights_json[type_name]
        if args.num is not None:
            weight_list = weight_list[:args.num]
        total_weights += len(weight_list)
    
    print(f"Total: {total_weights} weights")
    
    if args.base_path:
        print(f"Download path: {args.base_path}")
    
    if args.dry_run:
        print("Dry run complete. Use without --dry-run to perform actual downloads.")
        return
    
    # Confirm download
    if input("Continue? (y/n): ").lower() != 'y':
        print("Download cancelled")
        return

    # Download each weight
    for type_name in types_to_download:
        print(f"\nDownloading {type_name}:")
        weight_list = weights_json[type_name]
        
        # Limit number of downloads if specified
        if args.num is not None:
            weight_list = weight_list[:args.num]

        for weight_name in tqdm(weight_list, desc=type_name):
            name = downloader.get_canonical_weight_str(weight_name)
            weight = weights_map[name]
            url = weight["url"]
            dest = weight["dest"]
            if args.base_path:
                dest = os.path.join(args.base_path, dest)
            print(f"Downloading {weight_name} to {dest}")
            try:
                downloader.download_if_not_exists(weight_name, url, dest)
            except Exception as e:
                print(f"Error downloading {weight_name}: {e}")

if __name__ == "__main__":
    main()