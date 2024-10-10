#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from datetime import datetime
import sys
from typing import List, Dict
import logging
import os
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dont forget to get your APIs for the below websites.

def apivoid_domain_reputation(domain: str) -> dict:
    """
    Check domain reputation using APIVoid API.

    Args:
        domain (str): The domain to check.

    Returns:
        dict: Reputation data or error message.
    """
    api_key = os.getenv('APIVOID_API_KEY')
    if not api_key:
        logging.error("APIVOID_API_KEY not set in environment variables.")
        return {'error': 'API key not provided'}

    url = 'https://endpoint.apivoid.com/domainrep/v1/pay-as-you-go/'
    params = {
        'key': api_key,
        'domain': domain
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Extract relevant information
        reputation_score = data.get('data', {}).get('reputation', {}).get('score', 'N/A')
        blacklist_status = data.get('data', {}).get('blacklists', 'N/A')
        return {
            'reputation_score': reputation_score,
            'blacklist_status': blacklist_status
        }
    except requests.RequestException as e:
        logging.error(f"APIVoid API request failed for domain {domain}: {e}")
        return {'error': str(e)}
    except json.JSONDecodeError:
        logging.error(f"Failed to parse APIVoid API response for domain {domain}.")
        return {'error': 'Invalid JSON response'}


def ipvoid_domain_reputation(domain: str) -> dict:
    """
    Check domain reputation using IPVoid API.

    Args:
        domain (str): The domain to check.

    Returns:
        dict: Reputation data or error message.
    """
    api_key = os.getenv('IPVVOID_API_KEY')
    if not api_key:
        logging.error("IPVVOID_API_KEY not set in environment variables.")
        return {'error': 'API key not provided'}

    url = f'https://api.ipvoid.com/domain/{domain}/'
    params = {
        'key': api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Extract relevant information
        blacklist_count = data.get('Blacklists', 'N/A')
        return {
            'blacklist_count': blacklist_count,
            'details': data.get('Details', 'N/A')
        }
    except requests.RequestException as e:
        logging.error(f"IPVoid API request failed for domain {domain}: {e}")
        return {'error': str(e)}
    except json.JSONDecodeError:
        logging.error(f"Failed to parse IPVoid API response for domain {domain}.")
        return {'error': 'Invalid JSON response'}


def mxtoolbox_domain_reputation(domain: str) -> dict:
    """
    Check domain reputation using MXToolbox API.

    Args:
        domain (str): The domain to check.

    Returns:
        dict: Reputation data or error message.
    """
    api_key = os.getenv('MXTOOLBOX_API_KEY')
    if not api_key:
        logging.error("MXTOOLBOX_API_KEY not set in environment variables.")
        return {'error': 'API key not provided'}

    url = f'https://api.mxtoolbox.com/api/v1/lookup/health/{domain}'
    headers = {
        'Authorization': f'Bearer {api_key}'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Extract relevant information
        health_status = data.get('Health', 'N/A')
        return {
            'health_status': health_status,
            'details': data.get('Details', 'N/A')
        }
    except requests.RequestException as e:
        logging.error(f"MXToolbox API request failed for domain {domain}: {e}")
        return {'error': str(e)}
    except json.JSONDecodeError:
        logging.error(f"Failed to parse MXToolbox API response for domain {domain}.")
        return {'error': 'Invalid JSON response'}


def aggregate_reputation(domain: str) -> dict:
    """
    Aggregate domain reputation from multiple services.

    Args:
        domain (str): The domain to check.

    Returns:
        dict: Aggregated reputation data.
    """
    reputation_data = {
        'domain': domain,
        'APIVoid': {},
        'IPVoid': {},
        'MXToolbox': {}
    }

    # APIVoid
    apivoid_result = apivoid_domain_reputation(domain)
    reputation_data['APIVoid'] = apivoid_result

    # IPVoid
    ipvoid_result = ipvoid_domain_reputation(domain)
    reputation_data['IPVoid'] = ipvoid_result

    # MXToolbox
    mxtoolbox_result = mxtoolbox_domain_reputation(domain)
    reputation_data['MXToolbox'] = mxtoolbox_result

    # If needed, you can add more checker resources below.

    return reputation_data


def check_reputation(websites: List[str], preset_list_path: str, specific_websites: List[str]) -> Dict[str, dict]:
    """
    Check the reputation of websites against a preset list, specific websites, and external APIs.

    Args:
        websites (List[str]): List of websites to check.
        preset_list_path (str): Path to the preset list file.
        specific_websites (List[str]): Additional websites to mark as unsafe.

    Returns:
        Dict[str, dict]: Dictionary mapping websites to their reputation data.
    """
    results = {}
    try:
        with open(preset_list_path, 'r') as file:
            preset_websites = set(line.strip().lower() for line in file if line.strip())
    except FileNotFoundError:
        logging.error(f"The file {preset_list_path} was not found.")
        sys.exit(1)
    except IOError:
        logging.error(f"Could not read the file {preset_list_path}.")
        sys.exit(1)

    preset_websites.update(site.lower() for site in specific_websites)

    for website in websites:
        normalized_website = website.lower()
        if normalized_website in preset_websites:
            results[website] = {"preset_status": "Unsafe"}
        else:
            # Perform external reputation checks
            reputation = aggregate_reputation(normalized_website)
            results[website] = reputation

    return results


def main() -> None:
    """
    The main function that parses command-line arguments, reads website lists,
    checks their reputation, and prints the results.
    """
    parser = argparse.ArgumentParser(description="Check the reputation of websites.")
    
    # Positional arguments
    parser.add_argument(
        "preset_list",
        type=str,
        help="Path to the file containing the preset list of websites."
    )
    
    # Optional arguments for websites input
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "websites_file",
        type=str,
        nargs='?',
        help="Path to the file containing a list of websites."
    )
    group.add_argument(
        "-w", "--website",
        type=str,
        nargs='+',
        help="List of websites to check directly via command line."
    )
    
    # Additional optional arguments
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Path to the output file."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output."
    )
    
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # List of specific websites
    specific_websites: List[str] = [
        "example1.com",
        "example2.com",
        "example3.com"
    ]

    # Initialize websites list
    websites: List[str] = []

    # Read websites from file if provided
    if args.websites_file:
        try:
            with open(args.websites_file, 'r') as file:
                file_websites = [line.strip() for line in file if line.strip()]
                logging.debug(f"Websites loaded from file: {file_websites}")
                websites.extend(file_websites)
        except FileNotFoundError:
            logging.error(f"The file {args.websites_file} was not found.")
            sys.exit(1)
        except IOError:
            logging.error(f"Could not read the file {args.websites_file}.")
            sys.exit(1)

    # Add websites provided via command line
    if args.website:
        logging.debug(f"Websites provided via command line: {args.website}")
        websites.extend(args.website)

    # Remove potential duplicates by converting to a list of unique items while preserving order
    seen = set()
    unique_websites = []
    for site in websites:
        lower_site = site.lower()
        if lower_site not in seen:
            seen.add(lower_site)
            unique_websites.append(site)

    logging.debug(f"Combined list of unique websites to check: {unique_websites}")

    if not unique_websites:
        logging.error("No websites provided to check. Please specify via a file or command-line arguments.")
        sys.exit(1)

    # Call the function to check reputation
    results = check_reputation(unique_websites, args.preset_list, specific_websites)

    # Get current date and time
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Prepare output lines
    output_lines = [f"Report Generated on {current_datetime}"]
    for website, reputation in results.items():
        output_lines.append(f"\nWebsite: {website}")
        if "preset_status" in reputation:
            output_lines.append(f"  Preset List Status: {reputation['preset_status']}")
        else:
            for service, data in reputation.items():
                output_lines.append(f"  {service} Reputation:")
                if isinstance(data, dict):
                    # Pretty-print the JSON data
                    for key, value in data.items():
                        output_lines.append(f"    {key}: {value}")
                else:
                    output_lines.append(f"    {data}")
    
    output_text = "\n".join(output_lines)

    if args.output:
        try:
            with open(args.output, 'w') as outfile:
                outfile.write(output_text + "\n")
            logging.info(f"Results have been written to {args.output}.")
        except IOError:
            logging.error(f"Could not write to the file {args.output}.")
            sys.exit(1)
    else:
        print(output_text)


if __name__ == "__main__":
        main()
