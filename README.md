# Skate performance analyser

This application aims to provide a graphical tool to analyse the performance of figure skaters with publicly available score cards.
Score cards are collected, parsed and stored in a database. The user can then select a skater, a competition and a club and get access
to a set of graphs and statistics that will help him understand the skater's performance and compare it to other skaters or accross time.

## User documentation

### Prerequisites

### Installation

### Usage

## Development documentation

### Architecture

The application is classically divided into a front-end and a back-end. The front-end is a web application that uses the back-end to
retrieve data and display it to the user. The back-end is a REST API that provides access to the database and the data processing
functions.

Data is stored in a PostgreSQL database. The back-end is written in Python using the Flask framework. The front-end is written in
JavaScript using the React framework.

Score cards are collected from the ISU website using a web scraper. The scraper is written in Python using the Scrapy framework. They
are then parsed from PDF to structured data using the Tabula (or PDFPlumber) library.

The application is deployed on Google Cloud Platform. The database is hosted on Cloud SQL, the back-end is hosted on App Engine and the
front-end is hosted on Firebase Hosting.
