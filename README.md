## 1. Overview

The Trapper Keeper is a collection of scripts that support archiving information from around the web to make it easier to study and use. If you are a researcher working with online material, an educator creating openly licensed content, or a curious person who likes to learn more about different subjects, then Trapper Keeper might be helpful to you. Trapper Keeper can currently archive and clean web pages and pdfs.

Trapper Keeper supports these features:

* Archive data from multiple sources;
* Clean data and save it as text;
* List out embedded media and links;
* Retain a copy of embedded images in the source text;
* Track the source material for changes;
* Organize your cleaned, archived data into arbitrary collections - a "collection" can be anything that unifies a set of information; ie, a set of urls that all relate to a specific topic; or a set of information that will be remixed into chapters;
* Export a list of all tracked URLs.

## 2. Installation

The scripts have some dependencies, including:

* Python
* ImageMagick
* Selenium

## 3. General Use

Identify urls that contain content or data you would like to research or use. Collect those urls into a csv file.

Use `archive.py` to retain a clean copy that you can work with locally. You can run as many imports as you want.

When you want to work with a specific set of content, create a csv that lists the urls you want to examine. Run `collect_texts.py` to get a copy of the specific texts you want.

Periodically, check if any of the urls you have archived have been changed or updated by running `archive.py -p update`.

To see the specific content of any changes, create a csv that lists the urls where you want to examine diffs, and run `show_diffs.py`

A common use case here is developing and maintaining open content. You have researched multiple pages on the web that contain information shared under an open license, and you want to incorporate that information into your own material. Over time, if any of your source materials are updated, you'd like to know. 

## 4. Additional Details

The scripts in Trapper Keeper use csv files to help organize information. Sample csv files are included in the `/samples` directory.

### 4A. Getting Started

Create a list of urls you want to archive. At present, the script processes and extracts text from web pages and pdfs.

For every web page you want to archive, you will need to designate three text snippets: the first phrase/few words of the page you want to archive; the final phrase/words of the section you want to archive, and a phrase in the middle of the text you want to archive.

For every pdf you want to archive, you only need to specify the url to the pdf.

When you have the url and snippet information, save it in a csv with four columns 'source_urls','opening', 'middle', and 'closing'.

Put the csv file in the "source" directory and update the filename in the `archive.py` file. 

Run the intial import by running `archive.py -p csv`.

Running `archive.py -p csv` does a few things:

* for web pages, the script saves three versions of the url: the complete, raw version; a second snippet that contains the html around the opening and closing snippet; and a cleaned version that just contains text. The cleaned version also contains a list of all linked urls in the page, and a list of all images linked in the page.
* for web pages, the script retrieves any images in the page and stores them in a "media" directory
* for pdfs, the script creates a copy of the pdf, and extracts text from the pdf, and stores a copy of both.
* for both web pages and pdfs, the script creates a json file that stores metadata about the url and the content at that url. This metadata includes a hash of the content that is used to track changes over time.

### 4B. Track additional URLs

To track additional urls, create a new csv file with new information about urls, and run `archive.py -p csv`

### 4C. Getting updated content

To retrieve new versions of urls that have been archived, run `archive.py -p update`

### 4D. Check Diffs

To check whether or not a url has been updated, prepare a csv with at least 4 columns: source_urls, yyyy, mm, and dd.

**source_urls** should contain the urls you want to check for updates.
**yyyy**, **mm**, and **dd** are used to designate the cutoff date for diffs. For example, if you wanted to check whether or not updates have happened after September 1, 2021, you would enter 2021 as yyyy, 09 as mm, and 01 as dd.

The cutoff date can be specified for each individual url.

Once you have the csv created, add it to the "source" directory and update the filename in the `show_diffs.py` file.

Running `show_diffs.py` creates a single html page for each changed file that displays the changes side by side. Each html page is stored in the "diffs" directory.

### 4E. Getting data from a subset of URLs; ie, the Point of It All

Saving content and cleaning it is great, but ultimately we need to organize this information and work with it. The `collect_texts.py` allows us to choose exactly the urls we want to work with, and to make a copy of the cleaned text.

To export cleaned text that we have archived, create a csv with two columns: source_urls and collection. 

Once you have the csv created, add it to the "source" directory and update the filename in the `collect_texts.py` file. 

Then, run `collect_texts.py` and the cleaned text will be copied into the "delivery" directory, and the files will be sorted by "collection".

### 4F. Export all data

The `export.py` file allows you to export a csv of all records, or a csv of only the urls that are current.

To export every record, run `export.py -e all`.

To export current records only (ie, only pointer to the latest version of each url), run `export.py -e current`.

### 4G. Housekeeping

The `housekeeping.py` script runs basic maintenance tasks. Currently, it cleans unneeded files and moves them into a "manual_review" directory.

Other housekeeping tasks will be added in the near future.

## 5. Current files:

* `archive.py` - requires a csv - takes two arguments: csv, or update
* `housekeeping.py`
* `show_diffs.py`
* `collect_texts.py` - requires a csv
* `export.py` - requires a csv- takes two arguments: current, or all

