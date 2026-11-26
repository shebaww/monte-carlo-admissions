import argparse
from src.simulator import Operations
from src.loader import DataIngestor

BANNER = r"""
 __  __             _              ____           _       
|  \/  | ___  _ __ | |_ ___       / ___|__ _ _ __| | ___  
| |\/| |/ _ \| '_ \| __/ _ \_____| |   / _` | '__| |/ _ \ 
| |  | | (_) | | | | ||  __/_____| |__| (_| | |  | | (_) |
|_|  |_|\___/|_| |_|\__\___|      \____\__,_|_|  |_|\___/ 

    _       _           _         _
   / \   __| |_ __ ___ (_)___ ___(_) ___  _ __  ___
  / _ \ / _` | '_ ` _ \| / __/ __| |/ _ \| '_ \/ __|
 / ___ \ (_| | | | | | | \__ \__ \ | (_) | | | \__ \
/_/   \_\__,_|_| |_| |_|_|___/___/_|\___/|_| |_|___/


"""

def main():
    print(BANNER)   
    print("Tip: Run 'python project.py --help' to view available command options.\n")
    parser = argparse.ArgumentParser(description="Monte Carlo College Admissions Simulator")
    parser.add_argument("--config", type=str, default="templates/config_template.yaml", help="Path to config YAML")
    parser.add_argument("--colleges", type=str, default="templates/colleges_template.json", help="Path to colleges JSON")
    parser.add_argument("--out", type=str, default="outputs", help="Output directory for plots")
    args = parser.parse_args()


    _Operations = Operations(
        args.out, 
        DataIngestor(
              args.config,
              args.colleges
          ),
        args.config
     ) 
    _Operations.monte_run()



if __name__ == "__main__":
    main()
