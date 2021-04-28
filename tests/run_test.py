import subprocess as sp
import json
import pathogenprofiler as pp
import os
import tbprofiler as tbp
import argparse
import sys


sp.call("git clone https://github.com/jodyphelan/tb-profiler-test-data.git",shell=True)


por5_dr_variants = [
    ('rpoB', 'p.Ser450Leu'),
    ('fabG1', 'c.-15C>T'),
    ('inhA', 'p.Ile194Thr'),
    ('pncA', 'p.Val125Gly'),
    ('embB', 'p.Met306Val'),
    ('embB', 'p.Met423Thr'),
    ('gid', 'p.Ala80Pro')
]

collate_text = 'sample\tmain_lineage\tsub_lineage\tDR_type\tnum_dr_variants\tnum_other_variants\trifampicin\tisoniazid\tpyrazinamide\tethambutol\tstreptomycin\tfluoroquinolones\tmoxifloxacin\tofloxacin\tlevofloxacin\tciprofloxacin\taminoglycosides\tamikacin\tkanamycin\tcapreomycin\tethionamide\tpara-aminosalicylic_acid\tcycloserine\tlinezolid\tbedaquiline\tclofazimine\tdelamanid\npor5A_illumina_bwa_freebayes\tlineage4\tlineage4.3.4.2\tMDR\t7\t14\trpoB_p.Ser450Leu\tfabG1_c.-15C>T, inhA_p.Ile194Thr\tpncA_p.Val125Gly\tembB_p.Met306Val, embB_p.Met423Thr\tgid_p.Ala80Pro\t-\t-\t-\t-\t-\t-\t-\t-\t-\tfabG1_c.-15C>T, inhA_p.Ile194Thr\t-\t-\t-\t-\t-\t-\npor5A_illumina_bwa_gatk\tlineage4\tlineage4.3.4.2\tMDR\t7\t14\trpoB_p.Ser450Leu\tfabG1_c.-15C>T, inhA_p.Ile194Thr\tpncA_p.Val125Gly\tembB_p.Met306Val, embB_p.Met423Thr\tgid_p.Ala80Pro\t-\t-\t-\t-\t-\t-\t-\t-\t-\tfabG1_c.-15C>T, inhA_p.Ile194Thr\t-\t-\t-\t-\t-\t-\npor5A_illumina_bwa_bcftools\tlineage4\tlineage4.3.4.2\tMDR\t7\t14\trpoB_p.Ser450Leu\tfabG1_c.-15C>T, inhA_p.Ile194Thr\tpncA_p.Val125Gly\tembB_p.Met306Val, embB_p.Met423Thr\tgid_p.Ala80Pro\t-\t-\t-\t-\t-\t-\t-\t-\t-\tfabG1_c.-15C>T, inhA_p.Ile194Thr\t-\t-\t-\t-\t-\t-\npor5_vcf\tlineage4\tlineage4.3.4.2\tMDR\t7\t15\trpoB_p.Ser450Leu\tfabG1_c.-15C>T, inhA_p.Ile194Thr\tpncA_p.Val125Gly\tembB_p.Met306Val, embB_p.Met423Thr\tgid_p.Ala80Pro\t-\t-\t-\t-\t-\t-\t-\t-\t-\tfabG1_c.-15C>T, inhA_p.Ile194Thr\t-\t-\t-\t-\t-\t-\n'
    
def test_vcf():
    sp.call("tb-profiler vcf_profile tb-profiler-test-data/por5A1.vcf.gz",shell=True)
    results = json.load(open("results/por5_vcf.results.json"))
    assert results["sublin"] == "lineage4.3.4.2"
    assert results["main_lin"] == "lineage4"
    assert len(results["dr_variants"]) == 7
    assert [(v["gene"],v["change"]) for v in results["dr_variants"]] == por5_dr_variants


def illumina_fastq(caller,mapper):
    sp.call(f"tb-profiler profile -1 tb-profiler-test-data/por5A.reduced_1.fastq.gz -2 tb-profiler-test-data/por5A.reduced_2.fastq.gz --mapper {mapper} --caller {caller} -p por5A_illumina_{mapper}_{caller} -t 4 --txt --csv --pdf",shell=True)
    results = json.load(open(f"results/por5A_illumina_{mapper}_{caller}.results.json"))
    return results

def illumina_fastq_single(caller,mapper):
    sp.call(f"tb-profiler profile -1 tb-profiler-test-data/por5A.reduced_1.fastq.gz --mapper {mapper} --caller {caller} -p por5A_illumina_{mapper}_{caller} -t 4 --txt --csv --pdf",shell=True)
    results = json.load(open(f"results/por5A_illumina_{mapper}_{caller}.results.json"))
    return results

def test_bwa_freebayes():
    results = illumina_fastq("freebayes","bwa")
    assert results["sublin"] == "lineage4.3.4.2"
    assert results["main_lin"] == "lineage4"
    assert [(v["gene"],v["change"]) for v in results["dr_variants"]] == por5_dr_variants

def test_bwa_bcftools():
    results = illumina_fastq("bcftools","bwa")
    assert results["sublin"] == "lineage4.3.4.2"
    assert results["main_lin"] == "lineage4"
    assert [(v["gene"],v["change"]) for v in results["dr_variants"]] == por5_dr_variants

def test_bwa_gatk():
    results = illumina_fastq("gatk","bwa")
    assert results["sublin"] == "lineage4.3.4.2"
    assert results["main_lin"] == "lineage4"
    assert [(v["gene"],v["change"]) for v in results["dr_variants"]] == por5_dr_variants

def test_collate():
    with open("samples.txt","w") as O:
        O.write("\n".join(["por5A_illumina_bwa_freebayes","por5A_illumina_bwa_gatk","por5A_illumina_bwa_bcftools","por5_vcf"]))
    sp.call("tb-profiler collate --samples samples.txt",shell=True)
    assert open("tbprofiler.txt").read() == collate_text

def test_bowtie2_freebayes():
    results = illumina_fastq("freebayes","bowtie2")
    assert results["sublin"] == "lineage4.3.4.2"
    assert results["main_lin"] == "lineage4"
    assert [(v["gene"],v["change"]) for v in results["dr_variants"]] == por5_dr_variants

def test_minimap2_freebayes():
    results = illumina_fastq("freebayes","minimap2")
    assert results["sublin"] == "lineage4.3.4.2"
    assert results["main_lin"] == "lineage4"
    assert [(v["gene"],v["change"]) for v in results["dr_variants"]] == por5_dr_variants

def test_bwa_freebayes_single():
    results = illumina_fastq_single("freebayes","minimap2")
    assert results["sublin"] == "lineage4.3.4.2"
    assert results["main_lin"] == "lineage4"
    assert [(v["gene"],v["change"]) for v in results["dr_variants"]] == por5_dr_variants

def test_minimap2_freebayes():
    results = illumina_fastq("freebayes","minimap2")
    assert results["sublin"] == "lineage4.3.4.2"
    assert results["main_lin"] == "lineage4"
    assert [(v["gene"],v["change"]) for v in results["dr_variants"]] == por5_dr_variants

def test_nanopore():
    sp.call(f"tb-profiler profile -1 tb-profiler-test-data/por5A.nanopore_reduced.fastq.gz --platform nanopore -p por5A_illumina_nanopore -t 4 --txt --csv --pdf",shell=True)
    results = json.load(open(f"results/por5A_illumina_nanopore.results.json"))
    assert results["sublin"] == "lineage4.3.4.2"
    assert results["main_lin"] == "lineage4"
    assert [(v["gene"],v["change"]) for v in results["dr_variants"]] == por5_dr_variants

def test_fasta():
    sp.call(f"tb-profiler fasta_profile -f ~/tbprofiler_test_data/por5A1.fasta  -p por5A_fasta",shell=True)
    results = json.load(open(f"results/por5A_fasta.results.json"))
    assert results["sublin"] == "lineage4.3.4.2"
    assert results["main_lin"] == "lineage4"
    assert [(v["gene"],v["change"]) for v in results["dr_variants"]] == por5_dr_variants

def test_db():
    sp.call("git clone https://github.com/jodyphelan/tbdb.git",shell=True)
    os.chdir("tbdb")
    sp.call("tb-profiler create_db",shell=True)
    os.chdir("../")
