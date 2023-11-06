import csv
import pandas as pd
import requests
import pprint as pp

# Reading in File
file_path = './Outputs/final_sheet_DE.xlsx'

# specify 'sheet_name='Animalia' once full sheet of data is used
a_df = pd.read_excel(file_path)

# Creating list of unique Organisms
organism_list = a_df['Organism'].unique()

# Creation of Organism Dictionary Items List
organism_dict_list = []

# Creation of Organism Error Dictionaries List
error_organism_list = []

organism_counter = 0

# Looping through the organism list
for organism in organism_list:

    organism_counter = organism_counter+1

    # Creation of Unique Organism Dictionary
    the_organism_dict = {'Organism': organism, 'Present in NCBI Database?': 'No',
                         'accession': '', 'Reference Genome?': '', 'assembly_level': '', 'number_of_contigs': 0,
                         'number_of_scaffolds': 0, 'scaffold_n50 (kb)': 0, 'contig_n50 (kb)': 0}

    # Creation of Unique URL
    base_url = "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/genome/taxon/"
    after_url = "/dataset_report"
    organism_url = organism.replace(" ", "%20")
    final_url = base_url + organism_url + after_url

    # JSON Request
    url = final_url

    payload = {}
    headers = {
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    # Add Error Code + Organism Info to Error List for Manual Cleaning
    if response.status_code != 200:
        error_dict = {'Organism': organism,
                      'Error': response.status_code}
        error_organism_list.append(error_dict)
    else:
        # JSON Report Object Creation
        jsonResponse = response.json()
        # Addition of Necessary Data to Organism Dictionary

        if "reports" in jsonResponse.keys():
            reports = jsonResponse["reports"]
            the_organism_dict['Present in NCBI Database?'] = 'Yes'
            # If there is only one report for the organism, that report is used
            if len(reports) == 1:
                the_report = reports[0]
            else:
                # Selection of the best report if there are multiple

                # Criteria for selecting the best report (if there are multiple):
                # 1. Choose reference/representative genome.
                # 2. If no ref/rep genome, choose based upon level (manually for now)

                priority_reports = []
                report_count = 0
                for report in reports:
                    # If the report is of a reference genome, add to list of 'prioritized reports' (filtering)
                    if 'refseq_category' in report['assembly_info'].keys():
                        if report['assembly_info']['refseq_category'] in ['representative genome', 'reference genome']:
                            priority_reports.append(report)
                    report_count = report_count + 1
                # If there are more than one prioritized reports (more than one ref genome, unlikely)
                if len(priority_reports) >= 2:
                    error_dict = {'Organism': organism,
                                  'Error': f'Incorrect number of priority reports ({len(priority_reports)})'}
                    error_organism_list.append(error_dict)
                    # use the first ref genome as the report
                    the_report = priority_reports[0]
                elif len(priority_reports) == 0:
                    the_report = reports[0]


                else:
                    # If no more than one ref genome, (most likely circumstance), use the only prioritized report
                    the_report = priority_reports[0]

            # designation of accession number for specified organism, addition into organism's dictionary
            accession = the_report["accession"]
            the_organism_dict['accession'] = accession

            # designation of type of refseq category, addition into organism's dictionary
            if 'refseq_category' in the_report['assembly_info'].keys():
                reference = the_report['assembly_info']['refseq_category']
                the_organism_dict['Reference Genome?'] = reference
            else:
                the_organism_dict['Reference Genome?'] = 'Not Present'
                error_dict = {'Organism': organism, 'Error': 'No Ref/Rep Genome Found'}
                error_organism_list.append(error_dict)

            # designation of assembly level for chosen report, addition into organism's dictionary
            if 'assembly_level' in the_report['assembly_info'].keys():
                assembly_level = the_report['assembly_info']['assembly_level']
                the_organism_dict['assembly_level'] = assembly_level
            else:
                error_dict = {'Organism': organism, 'Error': 'No Assembly level info found'}
                error_organism_list.append(error_dict)

            # designation of number of contigs, addition into organism's dictionary
            if 'number_of_contigs' in the_report['assembly_stats'].keys():
                contigs = the_report['assembly_stats']['number_of_contigs']
                the_organism_dict['number_of_contigs'] = contigs
            else:
                error_dict = {'Organism': organism, 'Error': 'No # contigs data found'}
                error_organism_list.append(error_dict)

            # designation of number of scaffolds, addition into organism's dictionary
            if 'number_of_scaffolds' in the_report['assembly_stats'].keys():
                scaffolds = the_report['assembly_stats']['number_of_scaffolds']
                the_organism_dict['number_of_scaffolds'] = scaffolds
            else:
                error_dict = {'Organism': organism, 'Error': 'No # scaffold data found'}
                error_organism_list.append(error_dict)

            # designation of scaffold n50, addition into organism's dictionary
            if 'scaffold_n50' in the_report['assembly_stats'].keys():
                scaffold_n50 = the_report['assembly_stats']['scaffold_n50']
                the_organism_dict['scaffold_n50 (kb)'] = scaffold_n50
            else:
                error_dict = {'Organism': organism, 'Error': 'No scaffold n50 data found'}
                error_organism_list.append(error_dict)

            # designation of contig n50, addition into organism's dictionary
            if 'contig_n50' in the_report['assembly_stats'].keys():
                contig_n50 = the_report['assembly_stats']['contig_n50']
                the_organism_dict['contig_n50 (kb)'] = contig_n50
            else:
                error_dict = {'Organism': organism, 'Error': 'No contig n50 data found'}
                error_organism_list.append(error_dict)

        else:
            # If Report is not found, Organism is added to Error List for manual investigation
            error_dict = {'Organism': organism, 'Error': 'Report Not Found'}
            error_organism_list.append(error_dict)

        # pp.pprint(the_organism_dict)
        organism_dict_list.append(the_organism_dict)
        print(f'Data entry for organism #{organism_counter} finished')

# Merging Organism Dictionary with Cleaned UniProt LINX Sheet
# *Will include all information gathered so far*
my_df = pd.DataFrame(organism_dict_list)
merged_df = pd.merge(a_df, my_df, on='Organism', how='outer')
print(merged_df.info())

# Un-Cleaned Output: 'final_NCBI_sheet.xlsx'
merged_df.to_excel('./Outputs/final_NCBI_sheet.xlsx', index=False)

# Creation of Error List Output for manual cleaning/investigation
if len(error_organism_list) > 0:
    print('Writing our error dictionary...')
    print(f' There were {len(error_organism_list)} error(s)...')
    with open('output_error_file_name.csv', 'w', newline='') as csvfile:
        fieldnames = ['Organism', 'Error']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for the_error_dict in error_organism_list:
            writer.writerow(the_error_dict)
print('Done writing Error dictionary...')
