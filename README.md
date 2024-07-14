# NightVision Targets Collector

## Description

`NightVision Targets Collector`  is a tool designed to automate the process of collecting subdomains/targets for a particular domain, identifying live HTTP subdomains, and registering them as targets in a project for later scanning. 
The tool is capable of gathering subdomains from various sources using different techniques.


## Installation


1. **Clone the Repository:**
   ```
      git clone https://github.com/jxbt/nightvision_targets_collector.git
      cd nightvision_targets_collector
   ```
1. **Install Dependencies:**
   ```
      chmod +x install.sh && sudo ./install.sh
   ```

## Usage
   To use the NightVision Targets Collector:
   
   ```
     python3 main.py [Flags]

   ```

  ### Flags:

| Flag                                      | Description                                                               |
|-------------------------------------------|---------------------------------------------------------------------------|
| `-t` or `--target` (required)             | A single target to perform reconnaissance on it.                         |
| `-l` or `--list` (required)               | A list of one or more targets.                                            |
| `-o` or `--output` (optional)             | Output folder path.                                                       |
| `-e` or `--excluded` (optional)           | The list of the excluded subdomains.                                      |
| `-h` or `--help` (optional)               | To show the help menu.                                                    |
| `--conf` (optional)                       | Path of the custom configuration file (YAML or JSON).                     |
| `-i` or `--include-subs` (optional)       | A list of additional subdomains to be included in the recon process (e.g., to not be excluded). |
| `--ct` or `--create-nightvision-targets` (optional) | Create nightvision targets from the collected live HTTP/HTTPS subdomains. |
| `--token` (optional)                      | Nightvision API token, used when the `--ct` option is utilized.           |
| `--project-id` (optional)                 | Nightvision project ID.                                                   |
| `--project-name` (optional)               | Nightvision project name.                                                 |


### Example:


   ```bash
   python3 main.py --token $NIGHTVISION_TOKEN --target example.net --project-name your_project_name --ct
   ```


## Docker

You can also run the NightVision Targets Collector using Docker. The following steps outline how to pull the Docker image and run the container with the necessary configurations/options.

1. **Pull the Docker Image:**
   ```bash
   docker pull jxbt/nightvision-targets-collector
   ```

2. **Run the Docker Container:**

   To run the tool using Docker with a direct command:
   ```bash
   docker run jxbt/nightvision-targets-collector --token $NIGHTVISION_TOKEN --target portswigger.net --project-name tx1 --ct
   ```

   Alternatively, you can use environment variables to pass in parameters:
   ```bash
   docker run --env "NV_TOKEN=your_token" --env "NV_TARGET=example.com" --env "NV_PROJECT_NAME=p2" --env "CREATE_TARGETS=true" jxbt/nightvision-targets-collector
   ```
