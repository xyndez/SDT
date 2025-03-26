import sys
import base64
import tempfile
import os
import ctypes
import re
import random
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import time
import msvcrt
from datetime import datetime
from collections import OrderedDict, defaultdict
from typing import List, Dict, Tuple, Optional, Union
from colorama import Fore, Style, init  
import qrcode

def set_console_title(title: str):
    if os.name == 'nt':
        ctypes.windll.kernel32.SetConsoleTitleW(title)

import os
import time
import msvcrt
from colorama import Fore, Style, init

def center_text(text, color=Fore.WHITE):
    term_width = os.get_terminal_size().columns
    return color + text.center(term_width)

def show_splash_screen():
    logo = r"""
   _____  ____  ______
  / ___/ / __ \/_  __/
  \__ \ / / / / / /   
 ___/ // /_/ / / /    
/____//_____/ /_/     
""".strip('\n')
    
    os.system('cls' if os.name == 'nt' else 'clear')
    term_width = os.get_terminal_size().columns
    term_height = os.get_terminal_size().lines
    
    logo_height = len(logo.split('\n'))
    total_text_height = logo_height + 6
    padding = max(0, (term_height - total_text_height) // 2)
    
    print('\n' * padding)
    
    for line in logo.split('\n'):
        print(center_text(line, Fore.CYAN))
    
    print("\n")
    
    print(center_text("SDT v1.1 - Simple Data Tool", Fore.CYAN))
    print("\n") 
    print(center_text("by @xyndez", Fore.WHITE))
    print("\n")
    print(center_text("(Press SPACE to skip)", Fore.LIGHTBLACK_EX))
    
    start = time.monotonic()
    while time.monotonic() - start < 3:
        if msvcrt.kbhit() and msvcrt.getch() == b' ':
            break
        time.sleep(0.05)
    
    os.system('cls' if os.name == 'nt' else 'clear')

def set_console_title(title):
    if os.name == 'nt':
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW(title)

set_console_title("SDT. Simple Data Tool v1.1 | Work With DB like a charm. | @xyndez")
init(autoreset=True)

show_splash_screen()

def main_menu():
    pass
    
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('SDT.log'),
        logging.StreamHandler()
    ]
)


class DomainExtractor:
    
    def __init__(self):
        self.common_domains = {
            'google': ['google.com', 'gmail.com'],
            'microsoft': ['microsoft.com', 'outlook.com', 'hotmail.com'],
            'yahoo': ['yahoo.com'],
            'facebook': ['facebook.com'],
            'twitter': ['twitter.com']
        }
        self.domain_pattern = re.compile(
            r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]',
            re.IGNORECASE
        )

    def extract_domains(self, text: str) -> List[str]:
        return list(set(self.domain_pattern.findall(text.lower()))) 
        
    def get_files_from_folder(self, folder: str) -> List[str]:
        try:
            return [
                os.path.join(root, file) 
                for root, _, files in os.walk(folder) 
                for file in files 
                if file.lower().endswith((".txt", ".csv", ".log"))
            ]
        except Exception as e:
            logging.error(f"Error scanning folder {folder}: {e}")
            return []

    def get_input_files(self, file_choice: str) -> List[str]:
        try:
            if file_choice == "file":
                files = filedialog.askopenfilenames(
                    title="Select input files", 
                    filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), 
                              ("Log files", "*.log"), ("All files", "*.*")]
                )
                return list(files) if files else []
            elif file_choice == "folder":
                folder_path = filedialog.askdirectory(title="Select folder to scan")
                return self.get_files_from_folder(folder_path) if folder_path else []
            return []
        except Exception as e:
            logging.error(f"Error getting input files: {e}")
            return []

    def get_output_folder(self, action_name: str) -> Optional[str]:
        try:
            base_folder = filedialog.askdirectory(title="Select base output folder")
            if not base_folder:
                logging.error("No output folder selected.")
                return None

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_folder = os.path.join(base_folder, f"{action_name}-{timestamp}")
            os.makedirs(output_folder, exist_ok=True)
            return output_folder
        except Exception as e:
            logging.error(f"Error creating output folder: {e}")
            return None

    def remove_duplicates(self, lines: List[str]) -> Tuple[List[str], int]:
        try:
            unique_lines = list(OrderedDict.fromkeys(lines))
            return unique_lines, len(lines) - len(unique_lines)
        except Exception as e:
            logging.error(f"Error removing duplicates: {e}")
            return lines, 0

    def validate_regex(self, pattern: str) -> Optional[re.Pattern]:
        try:
            return re.compile(pattern)
        except re.error as e:
            logging.error(f"Invalid regex pattern '{pattern}': {e}")
            return None
            
    def file_line_count(self, file_path: str) -> int:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for _ in f)
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return 0

    def extract_domains(self, text: str) -> List[str]:
        return list(set(self.domain_pattern.findall(text.lower())))

    def sort_by_domain(self, input_files: List[str], 
                      output_folder: str,
                      custom_domains: List[str] = None,
                      save_as_single: bool = False) -> Dict[str, int]:
        
        if not input_files:
            logging.error("No input files provided.")
            return {}

        domains = defaultdict(list)
        if custom_domains:
            for domain in custom_domains:
                domains[domain] = []

        for category, domain_list in self.common_domains.items():
            for domain in domain_list:
                domains[domain] = []

        domains['other'] = []

        total_lines = 0
        domain_counts = defaultdict(int)

        try:

            for input_file in input_files:
                with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        total_lines += 1
                        found = False
                        extracted_domains = self.extract_domains(line)

                        for domain in domains:
                            if domain in extracted_domains:
                                domains[domain].append(line)
                                domain_counts[domain] += 1
                                found = True
                                break

                        if not found:
                            domains['other'].append(line)
                            domain_counts['other'] += 1

            if save_as_single:
                output_path = os.path.join(output_folder, "sorted_domains.txt")
                with open(output_path, "w", encoding="utf-8") as f:
                    for domain, lines in domains.items():
                        if lines:
                            f.write(f"\n=== Domain: {domain} ===\n")
                            f.write("\n".join(lines) + "\n")
            else:
                for domain, lines in domains.items():
                    if lines:
                        output_path = os.path.join(output_folder, f"{domain.replace('.', '_')}.txt")
                        with open(output_path, "w", encoding="utf-8") as f:
                            f.write("\n".join(lines) + "\n")

            logging.info(f"Processed {total_lines} lines across {len(input_files)} files")
            logging.info(f"Domain distribution: {dict(domain_counts)}")
            return dict(domain_counts)

        except Exception as e:
            logging.error(f"Error during domain sorting: {e}")
            return {}

    def extract_lines_by_regex(self, input_files: List[str], pattern: str, 
                             output_folder: str, extract_before: bool = False, 
                             extract_after: bool = False) -> Tuple[int, int]:
        
        regex = self.validate_regex(pattern)
        if not regex:
            return (0, 0)

        before_lines = []
        after_lines = []

        try:
            for input_file in input_files:
                with open(input_file, "r", encoding="utf-8", errors="ignore") as infile:
                    for line in infile:
                        line = line.strip()
                        if not line:
                            continue

                        match = regex.search(line)
                        if match:
                            if extract_before:
                                before_lines.append(line[:match.start()] + "\n")
                            if extract_after:
                                after_lines.append(line[match.end():] + "\n")

            before_count, after_count = 0, 0

            if extract_before and before_lines:
                before_lines, _ = self.remove_duplicates(before_lines)
                before_count = len(before_lines)
                with open(os.path.join(output_folder, "extracted_before.txt"), "w", encoding="utf-8") as f:
                    f.writelines(before_lines)

            if extract_after and after_lines:
                after_lines, _ = self.remove_duplicates(after_lines)
                after_count = len(after_lines)
                with open(os.path.join(output_folder, "extracted_after.txt"), "w", encoding="utf-8") as f:
                    f.writelines(after_lines)

            logging.info(f"Extracted {before_count} before matches and {after_count} after matches")
            return (before_count, after_count)

        except Exception as e:
            logging.error(f"Error during regex extraction: {e}")
            return (0, 0)

    def sample_lines(self, input_files: List[str], output_folder: str,
                    sample_size: int = 1000, random_sample: bool = True,
                    from_top: bool = False, from_bottom: bool = False,
                    remove_sampled: bool = False) -> int:
      
        if not input_files:
            logging.error("No input files provided.")
            return 0

        if sum([random_sample, from_top, from_bottom]) != 1:
            logging.error("Must select exactly one sampling method")
            return 0

        total_extracted = 0
        all_extracted = []
        remaining_files = []

        try:

            if random_sample:
                file_weights = [self.file_line_count(f) for f in input_files]
                total_lines = sum(file_weights)
                if total_lines == 0:
                    logging.error("All input files are empty")
                    return 0

            for input_file in input_files:
                if total_extracted >= sample_size:
                    remaining_files.append(input_file)
                    continue

                with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                if not lines:
                    continue

                if random_sample:
                    file_weight = file_weights[input_files.index(input_file)]
                    file_sample_size = max(1, round(sample_size * (file_weight / total_lines)))
                    file_sample_size = min(file_sample_size, sample_size - total_extracted, len(lines))
                    extracted = random.sample(lines, file_sample_size)
                elif from_top:
                    file_sample_size = min(sample_size - total_extracted, len(lines))
                    extracted = lines[:file_sample_size]
                else:  
                    file_sample_size = min(sample_size - total_extracted, len(lines))
                    extracted = lines[-file_sample_size:]

                total_extracted += len(extracted)
                all_extracted.extend(extracted)

                if remove_sampled:
                    remaining = [line for line in lines if line not in extracted]
                    with open(input_file, "w", encoding="utf-8") as f:
                        f.writelines(remaining)
                else:
                    remaining_files.append(input_file)

            if all_extracted:
                output_path = os.path.join(output_folder, "sampled_lines.txt")
                with open(output_path, "w", encoding="utf-8") as f:
                    f.writelines(all_extracted)

            logging.info(f"Successfully sampled {total_extracted} lines")
            return total_extracted

        except Exception as e:
            logging.error(f"Error during sampling: {e}")

            if remove_sampled and remaining_files:
                logging.warning("Attempting to restore original files...")

            return 0

    def merge_files(self, input_files: List[str], output_folder: str,
                   remove_duplicates: bool = True) -> int:
       
        if not input_files:
            logging.error("No input files provided.")
            return 0

        all_lines = []

        try:
            for input_file in input_files:
                with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
                    all_lines.extend(line for line in f if line.strip())

            if remove_duplicates:
                all_lines, dup_count = self.remove_duplicates(all_lines)
                logging.info(f"Removed {dup_count} duplicate lines")

            output_path = os.path.join(output_folder, "merged_output.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.writelines(all_lines)

            line_count = len(all_lines)
            logging.info(f"Merged {len(input_files)} files into {output_path} with {line_count} lines")
            return line_count

        except Exception as e:
            logging.error(f"Error during file merging: {e}")
            return 0
            
def get_domain_list() -> List[str]:
    while True:
        domains_input = input("Enter domains to filter (comma or space-separated): ").strip()
        if domains_input:
            domains = re.split(r'[,\s]+', domains_input)
            domains = [domain.strip().lower() for domain in domains if domain.strip()]

            valid_domains = []
            invalid_domains = []
            for domain in domains:
                if DomainExtractor().domain_pattern.fullmatch(domain):
                    valid_domains.append(domain)
                else:
                    invalid_domains.append(domain)

            if invalid_domains:
                print(Fore.YELLOW + f"Warning: These domains may be invalid: {', '.join(invalid_domains)}")
                if input("Continue anyway? (y/n): ").lower() != 'y':
                    continue

            if valid_domains:
                return valid_domains

        print(Fore.RED + "Error: You must enter at least one valid domain" + Style.RESET_ALL)

def contribute(): 
    while True:
        print(Fore.CYAN + "\n=== Support This Project ===" + Style.RESET_ALL)
        print("Telegram: @xyndez ; you can find me on forums as well.")
        print(Fore.CYAN + "1. Visit SDT on GitHub" + Style.RESET_ALL)
        print(Fore.CYAN + "2. Donate me!" + Style.RESET_ALL)
        print(Fore.YELLOW + "0. Return to main menu" + Style.RESET_ALL)
        
        choice = input("\nSelect an option (0-2): ").strip()

        if choice == "0":
            print(Fore.GREEN + "\nReturning to main menu..." + Style.RESET_ALL)
            break
        elif choice == "1":
            github_url = "https://github.com/xyndez/SDT"
            print(Fore.GREEN + "\nOpening GitHub repository..." + Style.RESET_ALL)
            print(f"Please star the repo and contribute at:\n{Fore.BLUE}{github_url}{Style.RESET_ALL}")
            try:
                import webbrowser
                webbrowser.open(github_url)
            except Exception as e:
                print(Fore.YELLOW + f"Couldn't open browser automatically: {e}" + Style.RESET_ALL)
                print(Fore.GREEN + "Please visit the URL manually" + Style.RESET_ALL)
        elif choice == "2":
            show_crypto_donations()
        else:
            print(Fore.RED + "Invalid option, please try again..." + Style.RESET_ALL)

def show_crypto_donations():
    input("\nPress Enter to continue...") 
    os.system('cls' if os.name == 'nt' else 'clear')
    
    crypto_addresses = {
        "1": {"name": "Bitcoin (BTC)", "address": "bc1q0sjlvsv68yfn95qf3jqhrtnssk7e5rvhj98ewn"},
        "2": {"name": "Ethereum (ETH)", "address": "0x51adDbc22358604B8B6412E744C49EEf69B329b5"},
        "3": {"name": "Litecoin (LTC)", "address": "LfjEjnbrj8Sp9NBg5Q4QoM7atVGS1gd73g"},
        "4": {"name": "Monero (XMR)", "address": "447TRPHego4R2E9j2BUmw9HM4yPMAu1sy3Dhr7d72UiNJNoNqEMEArtQRDfzTfytmeKRgKMKytjQbGdj13SKFRAoLjoWNTh"},
        "5": {"name": "USDT (ERC-20)", "address": "0x51adDbc22358604B8B6412E744C49EEf69B329b5"},
    }
    print(Fore.GREEN + "\n Thank you for considering a donation!" + Style.RESET_ALL)
    print("Your support helps maintain and improve this tool.\n")
    
    print(Fore.YELLOW + "Available donation methods:" + Style.RESET_ALL)
    for key, method in crypto_addresses.items():
        print(f"{key}. {method['name']}")
    
    choice = input("\nSelect method (1-5 or any key to cancel: ").strip()
    
    if choice in crypto_addresses:
        method = crypto_addresses[choice]
        if 'url' in method:
            print(Fore.GREEN + f"\nOpening {method['name']}..." + Style.RESET_ALL)
            try:
                import webbrowser
                webbrowser.open(method['url'])
            except Exception as e:
                print(Fore.YELLOW + f"Couldn't open browser automatically: {e}" + Style.RESET_ALL)
                print(f"Please visit: {Fore.BLUE}{method['url']}{Style.RESET_ALL}")
        else:  
            print(Fore.GREEN + f"\n{method['name']} address:" + Style.RESET_ALL)
            print(Fore.WHITE + Style.BRIGHT + method['address'] + Style.RESET_ALL)
            
            try:
                import qrcode
                qr = qrcode.QRCode()
                qr.add_data(method['address'])
                qr.print_ascii(invert=True)
                print("\nScan the QR code above for easy transfer")
            except ImportError:
                print(Fore.YELLOW + "\nInstall 'qrcode' package for QR code display" + Style.RESET_ALL)
            except Exception as e:
                print(Fore.YELLOW + f"\nCouldn't generate QR code: {e}" + Style.RESET_ALL)
            
        print(Fore.GREEN + "\nThank you for your support!" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "Donation cancelled." + Style.RESET_ALL)

def display_stats(stats: Dict[str, Union[int, str]]):
    print(Fore.GREEN + "\n=== Processing Results ===" + Style.RESET_ALL)
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {Fore.CYAN}{value}{Style.RESET_ALL}")
    print()

def main_menu():
    extractor = DomainExtractor()
    tk.Tk().withdraw()  

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(Fore.CYAN + "\n==== SDT v1.1 by @xyndez ====" + Style.RESET_ALL)
        print("1. Sort data by domains")
        print("2. Extract data using regex")
        print("3. Sample lines from files")
        print("4. Merge multiple files")
        print(Fore.MAGENTA + "5. Contribute/Help")
        print(Fore.RED + "6. Exit" + Style.RESET_ALL)

        choice = input("\nEnter your choice (1-6): ").strip()

        os.system('cls' if os.name == 'nt' else 'clear')
        
        if choice == "1":
            handle_sorting(extractor)
        elif choice == "2":
            handle_regex_extraction(extractor)
        elif choice == "3":
            handle_line_sampling(extractor)
        elif choice == "4":
            handle_file_merging(extractor)
        elif choice == "5":
            contribute()
        elif choice == "6":
            print(Fore.YELLOW + "Exiting program. Goodbye!" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "Invalid choice, please try again." + Style.RESET_ALL)
        input("\nPress Enter to return to the main menu...")

def handle_sorting(extractor: DomainExtractor):
    print(Fore.BLUE + "\n=== Domain Sorting ===" + Style.RESET_ALL)

    file_choice = input("Process single file or folder? (file/folder): ").lower()
    input_files = extractor.get_input_files(file_choice)
    if not input_files:
        print(Fore.RED + "No valid input files selected." + Style.RESET_ALL)
        return

    output_folder = extractor.get_output_folder("Sorted-Domains")
    if not output_folder:
        return

    print("\nDomain options:")
    print("1. Use common domains (Google, Microsoft, etc.)")
    print("2. Enter custom domains")
    print("3. Both common and custom domains")
    domain_choice = input("Select domain option (1-3): ").strip()

    custom_domains = None
    if domain_choice in ["2", "3"]:
        custom_domains = get_domain_list()
        if not custom_domains and domain_choice == "2":
            return

    use_common = domain_choice in ["1", "3"]

    save_as_single = input("Save as single file with sections? (y/n): ").lower() == "y"

    stats = extractor.sort_by_domain(
        input_files=input_files,
        output_folder=output_folder,
        custom_domains=custom_domains if domain_choice in ["2", "3"] else None,
        save_as_single=save_as_single
    )

    if stats:
        display_stats({
            "input_files": len(input_files),
            "total_lines_processed": sum(stats.values()),
            "output_folder": output_folder,
            **{"domain_" + k: v for k, v in stats.items()}
        })

def handle_regex_extraction(extractor: DomainExtractor):
    print(Fore.BLUE + "\n=== Regex Extraction ===" + Style.RESET_ALL)

    file_choice = input("Process single file or folder? (file/folder): ").lower()
    input_files = extractor.get_input_files(file_choice)
    if not input_files:
        print(Fore.RED + "No valid input files selected." + Style.RESET_ALL)
        return

    output_folder = extractor.get_output_folder("Regex-Extracted")
    if not output_folder:
        return

    while True:
        syntax = input("\nEnter extraction regex pattern: ").strip()
        if syntax:
            break
        print(Fore.RED + "Error: Pattern cannot be empty" + Style.RESET_ALL)

    print("\nExtraction options:")
    print("1. Extract text BEFORE matches")
    print("2. Extract text AFTER matches")
    print("3. Extract BOTH before and after")
    mode_choice = input("Select extraction mode (1-3): ").strip()

    if mode_choice == "1":
        before, after = True, False
    elif mode_choice == "2":
        before, after = False, True
    else:
        before, after = True, True

    before_count, after_count = extractor.extract_lines_by_regex(
        input_files=input_files,
        pattern=syntax,
        output_folder=output_folder,
        extract_before=before,
        extract_after=after
    )

    display_stats({
        "input_files": len(input_files),
        "output_folder": output_folder,
        "before_matches": before_count,
        "after_matches": after_count,
        "regex_pattern": syntax
    })

def handle_line_sampling(extractor: DomainExtractor):
    print(Fore.BLUE + "\n=== Line Sampling ===" + Style.RESET_ALL)

    file_choice = input("Process single file or folder? (file/folder): ").lower()
    input_files = extractor.get_input_files(file_choice)
    if not input_files:
        print(Fore.RED + "No valid input files selected." + Style.RESET_ALL)
        return

    output_folder = extractor.get_output_folder("Sampled-Lines")
    if not output_folder:
        return

    while True:
        try:
            sample_size = int(input("\nEnter number of lines to sample: ").strip())
            if sample_size > 0:
                break
            print(Fore.RED + "Error: Must be positive number" + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + "Error: Please enter a valid number" + Style.RESET_ALL)

    print("\nSampling method:")
    print("1. Random sample (distributed across files)")
    print("2. From top of files")
    print("3. From bottom of files")
    method_choice = input("Select method (1-3): ").strip()

    if method_choice == "1":
        random_sample, from_top, from_bottom = True, False, False
    elif method_choice == "2":
        random_sample, from_top, from_bottom = False, True, False
    else:
        random_sample, from_top, from_bottom = False, False, True

    modify_original = input("Remove sampled lines from original files? (y/n): ").lower() == "y"

    lines_sampled = extractor.sample_lines(
        input_files=input_files,
        output_folder=output_folder,
        sample_size=sample_size,
        random_sample=random_sample,
        from_top=from_top,
        from_bottom=from_bottom,
        remove_sampled=modify_original
    )

    display_stats({
        "input_files": len(input_files),
        "output_folder": output_folder,
        "lines_sampled": lines_sampled,
        "sampling_method": "Random" if random_sample else "Top" if from_top else "Bottom",
        "original_files_modified": "Yes" if modify_original else "No"
    })

def handle_file_merging(extractor: DomainExtractor):
 
    print(Fore.BLUE + "\n=== File Merging ===" + Style.RESET_ALL)

    file_choice = input("Process single file or folder? (file/folder): ").lower()
    input_files = extractor.get_input_files(file_choice)
    if not input_files:
        print(Fore.RED + "No valid input files selected." + Style.RESET_ALL)
        return

    output_folder = extractor.get_output_folder("Merged-Files")
    if not output_folder:
        return

    remove_dupes = input("Remove duplicate lines during merge? (y/n): ").lower() == "y"

    lines_count = extractor.merge_files(
        input_files=input_files,
        output_folder=output_folder,
        remove_duplicates=remove_dupes
    )

    display_stats({
        "files_merged": len(input_files),
        "output_file": os.path.join(output_folder, "merged_output.txt"),
        "total_lines": lines_count,
        "duplicates_removed": remove_dupes
    })

if __name__ == "__main__":
    main_menu()
