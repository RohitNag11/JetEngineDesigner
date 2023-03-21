![JetEngineDesigner Logo](logo.png)

# JetEngineDesigner

This is a Python package for designing and analyzing jet engines. It includes functions for calculating engine performance, geometry, and thermodynamic properties. The package also includes tools for visualizing engine components and results.

## Table of Contents

- [1. Project Structure](#1-project-structure)
- [2. Dependencies](#2-dependencies)
- [3. Flight Phase Analysis](#3-flight-phase-analysis)
  - [3.1. Main Functions](#31-main-functions)
  - [3.2. Usage](#32-usage)
- [4. Mission Profile Analysis](#4-mission-profile-analysis)
  - [4.1. Mission Profile Analysis Usage](#41-mission-profile-analysis-usage)
- [5. Engine Design Optimisation](#5-engine-design-optimisation)
  - [5.1. Engine Design Optimisation Main Functions](#51-engine-design-optimisation-main-functions)
  - [5.2. Engine Design Optimisation Usage](#52-engine-design-optimisation-usage)
- [6. Engine Design Analysis](#6-engine-design-analysis)
  - [6.1. Code Structure](#61-code-structure)
  - [6.2. Usage](#62-usage)
  - [6.3. Outputs](#63-outputs)
- [7. Acknowledgements](#7-acknowledgements)
- [8. License](#8-license)
  - [8.1. License Summary](#81-license-summary)

## 1. Project Structure

- `LICENSE`: the license file for this package.
- `README.md`: the readme file for this package.
- `JetEngineDesigner`: the main package directory.
  - `engine_design.py`: Contains code for calculating engine properties for a specific set of input variables.
  - `engine_iteration.py`: Contains Code for finding optimal engine variables.
  - `flight_phases_analysis.py`: Contains code for analysing phase-specific conditions.
  - `mission_profile_plot.py`: Visualises the mission profile.

## 2. Dependencies

This project requires the following Python packages to be installed:

- matplotlib==3.7.1
- numpy==1.24.2
- tqdm==4.65.0

You can install these dependencies using pip by running the following command:

```[bash]
pip install -r requirements.txt
```

It's recommended to use a virtual environment to isolate project dependencies from your system's Python installation.

## 3. Flight Phase Analysis

The `flight_phases_analysis.py` script performs flight analysis for different flight phases, such as cruise, top of climb, take off (normal), and take off (failure). It calculates and displays the Mach number, minimum engine diameter, mass flow rate, and corrected mass flow rate for each phase.

### 3.1. Main Functions

#### **`get_constants()`**

This function returns a tuple of constants used in the flight analysis:

1. SPEC_HEAT_RATIO: Specific heat ratio (1.4)
2. GAS_CONST: Gas constant (287)
3. DENSITY_SEA: Air density at sea level (1.225 kg/m³)
4. TEMP_SEA: Air temperature at sea level (288.15 K)
5. PRESSURE_SEA: Air pressure at sea level (101300 Pa)

#### **`get_phases_data()`**

This function returns a dictionary containing data for each flight phase, including:

1. Cruise
2. Top of Climb
3. Take Off (Normal)
4. Take Off (Failure)

For each phase, the following parameters are provided:

- Mach number
- Required thrust
- Specific thrust
- Density, temperature, and pressure ratios (for cruise and top of climb phases)
Velocity freestream (for take off phases)
- Coefficient
- Engine diameter (for top of climb and take off phases)

#### **`main()`**

This is the main function that creates a FlightAnalysis object with the provided constants, adds each flight phase using the add_phase() method, and calculates the required parameters. It then prints the results for each phase, including:

- Mach number
- Minimum engine diameter
- Mass flow rate
- Corrected mass flow rate

### 3.2. Usage

To run the script, simply execute it with Python:

```[bash]
python flight_analysis.py
```

The script will print the results for each flight phase.

## 4. Mission Profile Analysis

The `mission_profile_plot.py` script generates a 3D plot of an aerial route for an aircraft that will fly over a fire. The plot shows the flight path on a 3D coordinate system that shows the distance traveled in kilometers on the x-axis, the altitude in feet on the z-axis, and the position of the aircraft on the y-axis.

### 4.1. Mission Profile Analysis Usage

To use this code, simply run the script using Python:

```[bash]
python mission_profile_plot.py
```

The 3D plot will be displayed on your screen.

## 5. Engine Design Optimisation

`engine_iteration.py` is a Python script that simulates and analyzes different configurations of a gas turbine engine. The script aims to find valid engine configurations that meet specific criteria by iterating through various combinations of engine parameters.

### 5.1. Engine Design Optimisation Main Functions

#### **`read_vars_files(...)`**

This function reads tried and valid variables files and returns their hashed content.

#### **`__run_iteration(...)`**

This function processes each combination of engine parameters, instantiates an `Engine` object, and checks if the configuration is valid. If valid, the configuration is added to the set of valid configurations.

#### **`complete_run(...)`**

This function performs a complete iteration run, updating tried and valid variables files with the new results.

#### **`first_run(...)`**

This function performs the first iteration run using the initial set of variable ranges.

#### **`second_run(...)`**

This function performs the second iteration run using the variable ranges generated from the first run's valid configurations.

#### **`main(...)`**

The main function that calls first_run() and, if required, second_run().

### 5.2. Engine Design Optimisation Usage

To run the script, execute the following command:

```[bash]
python engine_iteration.py
```

The script saves the tried and valid engine configurations in the `./data/VariablesData/Tried` and `./data/VariablesData/Valid` directories, respectively.

## 6. Engine Design Analysis

This code `engine_design.py` designs a turbofan engine based on given specifications and saves the resulting engine object to a JSON file. It also plots the engine design.

### 6.1. Code Structure

The code consists of several functions to define constants, engine constants, and engine variables. It imports an `Engine` class from `turbomach_analyser.py` and some utility functions from `utils.py` to handle formatting and saving data.

The main function `main()` creates an engine object and then saves it to a JSON file and plots the engine design.

The code is designed to run as a standalone script by running `python engine_design.py` in the terminal.

### 6.2. Usage

To run the optimal engine design, specify the `engine_variables_path` parameter as the path to a CSV file containing valid engine variables. The code will then choose the engine variables with the highest score and use those to design the engine. For example:

```[python]
engine_variables_path = './data/VariablesData/Valid/ed_hav_hmbl_hwc_lmbl_lwc_mbl.csv'
main('./data/EngineData', engine_variables_path)
```

To run a test engine design, simply call the main() function with no parameters. This will use default engine variables to design the engine. For example:

```[python]
main('./data/EngineData')
```

### 6.3. Outputs

The `main()` function outputs two things:

1. A JSON file containing the engine object. This file is saved to the specified directory (`engine_data_dir_path`) and named after the engine design.
2. A plot of the engine design.

## 7. Acknowledgements

This project was developed as a supplement for the ME4 Aircraft Engine Technology Course Project.

Supervisor:

- **Prof. Ricardo Martinez-Botas**

Group Members:

- **Areeb Haider**
- **Diderik Evanson**
- **Conor Leo**
- **Rohit Nag**

Developer:

- **Rohit Nag**

## 8. License

This project is licensed under the MIT License - see the LICENSE.md file for details.

### 8.1. License Summary

The MIT License is a permissive open-source license that allows you to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software. It also provides an express disclaimer of liability and warranty, stating that the software is provided "as is" without warranty of any kind.

#### Permissions

- Commercial use
- Modification
- Distribution
- Private use

#### Conditions

- Include license and copyright notice in copies or portions of the software

#### Limitations

- Liability
- Warranty

For more details about the MIT License and its terms, please refer to the full text of the [license](https://opensource.org/license/mit/) itself.
