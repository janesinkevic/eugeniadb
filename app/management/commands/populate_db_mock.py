import os
import sys
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
import pandas as pd
from app.models import GenVariant
import tqdm
import re


class Command(BaseCommand):
    help = "Read Excel files and populate database"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the Excel file",
            default="genetic_variants_mock_data.csv",
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]

        self.stdout.write(
            self.style.SUCCESS(f"Successfully processed file: {file_path}")
        )

        df = pd.read_csv(file_path, encoding="utf-8")

        df.columns = df.columns.str.strip()
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        existing_columns = [
            col
            for col in [
                "variant_id",
                "gene",
                "chromosome",
                "variant_start",
                "variant_end",
                "reference",
                "alternate",
                "zygosity",
                "gnomad_total_af",
                "cadd_phred",
                "dbsnp_id",
                "consequence",
                "cosmic_id",
            ]
            if col in df.columns
        ]
        df = df[existing_columns]
        df.replace("", None, inplace=True)

        for index, row in df.iterrows():
            try:
                variant_id = row["variant_id"]
                details = {
                    "gene": row["gene"] if pd.notna(row["gene"]) else None,
                    "chromosome": (
                        row["chromosome"] if pd.notna(row["chromosome"]) else None
                    ),
                    "variant_start": (
                        row["variant_start"] if pd.notna(row["variant_start"]) else None
                    ),
                    "variant_end": (
                        row["variant_end"] if pd.notna(row["variant_end"]) else None
                    ),
                    "reference": (
                        row["reference"] if pd.notna(row["reference"]) else None
                    ),
                    "alternate": (
                        row["alternate"] if pd.notna(row["alternate"]) else None
                    ),
                    "zygosity": row["zygosity"] if pd.notna(row["zygosity"]) else None,
                    "gnomad_total_af": (
                        row["gnomad_total_af"]
                        if pd.notna(row["gnomad_total_af"])
                        else None
                    ),
                    "cadd_phred": (
                        row["cadd_phred"] if pd.notna(row["cadd_phred"]) else None
                    ),
                    "dbsnp_id": row["dbsnp_id"] if pd.notna(row["dbsnp_id"]) else None,
                    "consequence": (
                        row["consequence"] if pd.notna(row["consequence"]) else None
                    ),
                    "cosmic_id": (
                        row["cosmic_id"] if pd.notna(row["cosmic_id"]) else None
                    ),
                }

                gen_variant, created = GenVariant.objects.get_or_create(
                    variant_id=variant_id, defaults={**details}
                )

                if not created:
                    for key, value in details.items():
                        setattr(gen_variant, key, value)

                gen_variant.full_clean()
                gen_variant.save()

            except ValidationError as ve:
                print(f"Skipping variant {variant_id} due to validation error: {ve}")
            except Exception as e:
                print(f"Error processing {variant_id}: {e}")
