# Written by Emily Taylor for the Michigan Technological University Goetsch Lab - Data/Bioinformatics Team
# Last updated 1/29/2025
# This program finds protein sequences from a fasta file containing mRNA sequences of
# putative orthologs and their seed sequence.
# It then outputs a file with all associated protein sequences, as well as
# a MUSCLE Multiple Sequence Alignment (MSA) of both the mRNA/CDS sequences and Protein sequences
# in future versions, dN/dS analysis and BLAST search will be attached to this program as a subprocess.


# Dependencies: BioPython. To install BioPython,  type 'pip install biopython' in any terminal.
# Dependencies: MUSCLE. To install MUSCLE, download it from the MUSCLE website and ensure it's accessible via the command line


from Bio import Entrez, SeqIO, AlignIO
import os
import subprocess

Entrez.email = "eetaylor@mtu.edu"  # Replace with your email
input_file = "tfdp1_H. sapiens_complete_cds.txt"       # Replace with your input file of CDS
output_file = "tfdp1_H. sapiens_proteins.fasta"      # Replace with your desired output file name for Protein Fasta
msa_output_cds = "tfdp1_H. sapiens_msa_cds.fasta"       # Replace with your desired output file name for CDS MSA output
msa_output_protein = "tfdp1_H. sapiens_msa_protein.fasta"  # Replace with your designed output file name for Protein MSA output
muscle_exe = "C:/Users/emily/muscle-win64.v5.3.exe"  # Replace with full path to the MUSCLE executable in your computer

# Extract mRNA accession numbers
accession_numbers = []
with open(input_file, "r") as f:
    for line in f:
        if line.startswith(">"):  # Identify FASTA headers
            acc = line.split()[0][1:]  # Extract accession number (e.g., XM_...)
            accession_numbers.append(acc)

# Fetch protein sequences corresponding to mRNA accessions
with open(output_file, "w") as out_f:
    for acc in accession_numbers:
        try:
            # Step 1: Link mRNA accession to protein accession
            link_handle = Entrez.elink(dbfrom="nucleotide", db="protein", id=acc)
            link_results = Entrez.read(link_handle)
            link_handle.close()

            # Check if "LinkSetDb" exists and has data
            if not link_results or "LinkSetDb" not in link_results[0] or not link_results[0]["LinkSetDb"]:
                print(f"No linked protein found for {acc}")
                continue

            # Extract linked protein IDs safely
            protein_ids = []
            for linkset in link_results[0]["LinkSetDb"]:
                if "Link" in linkset:
                    protein_ids.extend([link["Id"] for link in linkset["Link"]])

            # Step 2: Fetch protein sequences using linked IDs
            if protein_ids:
                handle = Entrez.efetch(db="protein", id=",".join(protein_ids), rettype="fasta", retmode="text")
                seq_data = handle.read()
                out_f.write(seq_data)
                handle.close()
            else:
                print(f"No valid protein IDs found for {acc}")

        except Exception as e:
            print(f"Error processing {acc}: {e}")

# Align CDS Sequences
# Check if path to MUSCLE.exe is true and accessible
if not os.path.isfile(muscle_exe):
    raise FileNotFoundError("Muscle executable not found. Make sure it's installed and in your PATH")

command = [muscle_exe, "-align", input_file,  "-output", msa_output_cds]
print(f"Running MUSCLE alignment: {command}")

try:
    result = subprocess.run(command, check = True, text = True, capture_output = True)
    print("MUSCLE alignment completed successfully.")
    print(f"Output saved to: {msa_output_cds}")
except subprocess.CalledProcessError as e:
    print(f"Error during MUSCLE alginment:\n{e.stderr}")
    raise
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    raise

# Align Protein Sequences

command = [muscle_exe, "-align", output_file,  "-output", msa_output_protein]
print(f"Running MUSCLE alignment: {command}")

try:
    result = subprocess.run(command, check = True, text = True, capture_output = True)
    print("MUSCLE alignment completed successfully.")
    print(f"Output saved to: {msa_output_protein}")
except subprocess.CalledProcessError as e:
    print(f"Error during MUSCLE alginment:\n{e.stderr}")
    raise
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    raise
