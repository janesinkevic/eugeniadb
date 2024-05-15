VARIANT_ID = "variant_id"
GENE = "gene"
CHROMOSOME = "chromosome"
VARIANT_START = "variant_start"
VARIANT_END = "variant_end"
REFERENCE = "reference"
ALTERNATE = "alternate"
ZYGOSITY = "zygosity"
GNOMAD_TOTAL_AF = "gnomad_total_af"
CADD_PHRED = "cadd_phred"
DBSNP_ID = "dbsnp_id"
CONSEQUENCE = "consequence"
COSMIC_ID = "cosmic_id"
SAMPLES_WITH_VARIANT = "samples_with_variant"

VALUE = "value"
INTERPRETED_BY = "interpreted_by"
INTERPRETATION = "interpretation"
EVAL_DATE = "eval_date"

SAMPLE_NAME = "sample_name"
EXPERIMENT = "experiment"

EXPERIMENT_NAME = "experiment_name"
PATH = "path"

GENVARIANT_COLUMN_NAMES = [
    VARIANT_ID,
    GENE,
    CHROMOSOME,
    VARIANT_START,
    VARIANT_END,
    REFERENCE,
    ALTERNATE,
    ZYGOSITY,
    GNOMAD_TOTAL_AF,
    CADD_PHRED,
    DBSNP_ID,
    CONSEQUENCE,
    COSMIC_ID,
]

EVALUATION_COLUMN_NAMES = (
    VARIANT_ID,
    VALUE,
    INTERPRETED_BY,
    INTERPRETATION,
    EVAL_DATE,
)

SAMPLE_COLUMN_NAMES = [
    SAMPLE_NAME,
    EXPERIMENT,
]

EXPERIMENT_COLUMN_NAMES = (
    EXPERIMENT_NAME,
    PATH,
)

LIST_PER_PAGE = 50

ACMG_VALUES = [
    (1, "Benign"),
    (2, "Likely Benign"),
    (3, "Value of Uncertain Significance"),
    (4, "Likely Pathogenic"),
    (5, "Pathogenic"),
]
