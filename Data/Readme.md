# Data Description for Traffic Study

This document provides a detailed description of the datasets in the study

## Data Sources

### Calibration Data
#### Traffic Volume Data
- **Sensys Data (2018)**: The Sensys data is provided by the Seattle Department of Transportation (SDOT). The data within/close to downtown Seattle was provided by SDOT for Viaduct closure monitoring. The data was collected from the Sensys wireless vehicle detection system that uses magneto-resistive wireless sensors to detect vehicle presence and movement, as well as transmit real-time data for a variety of traffic management applications.
- **Loop Data (2018)**: The loop data is obtained from TRACFLOW of WSDOT (Washington Department of Transportation), a public user interface that archives and provides access to data collected from loop stations or loop groups, including volume, speed, and frequency of congestion.

#### Travel Time Data
- **NPMRDS (2018)**: The National Performance Management Research Data Set (NPMRDS) is an archived speed and travel time data set that includes the National Highway System (NHS) and additional roadways (NPMRDS Analytics Help, 2020). Data provided by the NPMRDS is updated each month and is available from 2011.

## Input Data for SUMO

- **`od.csv`**: This file contains origin-destination inputs for SUMO, which are based on the Puget Sound Regional Council (PSRC) Daysim data (2018).

## Usage

The datasets mentioned are used to calibrate the SUMO models.

## Additional Information

For further details regarding the data and usage, feel free to contact the data analysis team.
