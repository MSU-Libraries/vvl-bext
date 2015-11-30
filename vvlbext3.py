"""Python 3 version of vvlbext.py."""

import os
import csv
from datetime import datetime

problem_records = ["14036", "14041", "14042", "14055", "14061", "14073"]


class VvlBext():
    """Convert data from DBoutput to embed in .wav headers.

    Load MSUL-custom database output into a format suitable for automated
    transfer to .wav file headers.
    """

    def __init__(self):
        """Initialize variables."""
        self.record_id = 0
        self.output_csv_data = []
        self.error_records = []

    def process_csv(self, source_file_path, output_file_path):
        """Reformat CSV files.

        Take initial CSV and read it in order to collapse identical records
        from different lines into 1 line; format output data to work with
        automated tool to add data to .wav headers.

        args:
            source_file_path(str): CSV file to load, has to match particular
                                   (peculiar) format.
            output_file_path(str): any writable file location.
        """
        with open(source_file_path, "r", encoding="latin-1") as csvfile:
            vvlreader = csv.DictReader(csvfile)
            for row in vvlreader:
                if row["record_id"].isdigit():
                    if int(row["record_id"]) % 1000 == 0:
                        print("Processed {0} rows".format(row["record_id"]))
                    if self.new_record(row):

                        if self.record_id != 0:
                            self.create_csv_line()

                        self.format_types = []
                        self.physical_types = []
                        self.csv_data = {
                                         "digital_wav_id": "",
                                         "digital_mp3_id": "",
                                         "analogue_id": "",
                                         "digital_wav_path": "",
                                         "digital_mp3_path": "",
                                         "source_recording_specs": "",
                                         "physical_format": ""}
                        self.get_default_fields(row)
                        self.get_addl_fields()

                    else:

                        self.get_default_fields(row)
                        self.get_addl_fields()

                else:

                    self.error_records.append(row["record_id"])

        with open(output_file_path, "w") as csvfile:
            fieldnames = ["Filename", "Description", "Originator",
                          "CodingHistory", "IARL", "IART", "ICMT",
                          "ICRD", "IMED", "ISRC", "ISRF"]
            csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            csvwriter.writeheader()
            for record in self.output_csv_data:
                csvwriter.writerow(record)

        for error in self.error_records:
            print("Error processing row with ID {0}".format(error))

    def get_default_fields(self, row):
        """Select column data based on line index.

        args:
            line(str): a line of CSV data, as a string.
        """
        self.record_id = row["record_id"].replace('"', '')\
                                         .replace("'", "").strip()
        self.vvl_number = row["vvl_number"].replace('"', '')\
                                           .replace("'", "").strip()
        self.format_id = row["formatid"].replace('"', '')\
                                        .replace("'", "").strip()
        self.location_name = row["location_name"].replace('"', '')\
                                                 .replace("'", "").strip()
        self.format_type = row["formattype_name"].replace('"', '')\
                                                 .replace("'", "").strip()
        self.main_speaker = row["main_speaker"].strip()
        self.addl_speakers = row["additional_speakers"].strip()
        self.summary = row["summary"].strip()
        self.date_fixed = self.get_date(row["date_fixed"])
        self.recording_source = row["recording_source"].strip()
        self.is_physical = row["is_physical"]
        self.format_types.append(self.format_type)

    def get_addl_fields(self):
        """Pull out additional fields based on conditionals."""

        if self.format_id.startswith("DB") and self.format_type == "wav":
            self.csv_data["digital_wav_path"] = os.path.join(self.location_name.replace("DarkArchive", "archives"), self.format_id + ".wav")
            self.csv_data["digital_wav_id"] = self.format_id

        elif self.format_type == "mp3":
            self.csv_data["digital_mp3_path"] = os.path.join(self.location_name, self.format_id + ".mp3")
            self.csv_data["digital_mp3_id"] = self.format_id

        elif not self.format_id.startswith("DB"):
            self.csv_data["source_recording_specs"] = self.format_type
            self.csv_data["analogue_id"] = self.format_id

        if self.is_physical == "1":
            self.physical_types.append(self.format_type)
            self.csv_data["physical_format"] = self.format_type

    def new_record(self, row):
        """Check if each new line ID matches the current record ID.

        If the line doesn't match the record ID established on the previous
        line, then consider this line to be data about a new record.

        args:
            line(str): 1 line (as a string) of CSV data.

        returns:
            (bool): True if the line matches the previous, False if not.
        """
        if row["record_id"].rstrip().replace('"', '').replace("'", "").lstrip() == self.record_id:

            return False

        else:

            return True

    def create_csv_line(self):
        """Create line of output CSV data."""


        self.output_row = {"Filename": self.csv_data["digital_wav_path"],
                           "Description":self.make_description(),
                           "Originator":"Vincent Voice Library, MSU",
                           "CodingHistory": self.get_physical_format(),
                           "IARL": "US, MSU/VVL",
                           "IART": '; '.join([s for s in [self.main_speaker, 
                                              self.addl_speakers] if s != ""]),
                            "ICMT": self.summary,
                            "ICRD": self.date_fixed,
                            "IMED": "; ".join([t for t in self.format_types if t not in ["wav", "mp3"]]),
                            "ISRC": self.recording_source,
                            "ISRF": "; ".join([p for p in self.physical_types if p not in ["cd", "dat-tape"]]),

                           }

        """
        self.output_csv_data.append(",".join([self.record_id, 
                                         self.vvl_number, 
                                         self.csv_data["analogue_id"],
                                         self.csv_data["digital_wav_id"],
                                         self.csv_data["digital_mp3_id"],
                                         self.csv_data["digital_mp3_path"],
                                         self.csv_data["digital_wav_path"],
                                         self.make_description(),
                                         '"Vincent Voice Library, MSU"',
                                         "[YYYY-MM-DD]",
                                         self.csv_data["source_recording_specs"],
                                         "|".join([f for f in set(self.format_types)])
                                         ]))
        """
        self.output_csv_data.append(self.output_row)


    def make_description(self):

        description = ""

        if self.csv_data["analogue_id"] != "":
            description += "File Content: Collection VVL Item {0}. ".format(self.csv_data["analogue_id"])

        description += "File use: Preservation master. "

        if self.vvl_number != "":
            description += "Title control number: {0}. ".format(self.vvl_number)

        if self.csv_data["digital_wav_id"] != "":
            description += "Original filename: {0}.".format(self.csv_data["digital_wav_id"] + ".wav")

        return description

    def get_physical_format(self):

        if len(self.physical_types) > 0:
            # Just grabbing 1 physical format!
            phys_format = self.physical_types[0]
            if phys_format == "cd" or phys_format == "dat-tape":
                phys_codes = {"cd": "compact disc",
                              "dat-tape": "digital audio tape"}
                return "A=DIGITAL-UNKNOWN; {0}".format(phys_codes[phys_format])
            else:
                return "A=ANALOG; {0}".format(phys_format)

        else:
            return "null"

    def get_date(self, date):
        """Process date into correct format.

        args:
            date(str): date string, usually in mm/dd/yyyy format.
        """
        if "-" in date or "unknown" in date or date == "":
            return date.strip()
        else:
            input_format = "%m/%d/%y"
            date_object = datetime.strptime(date, input_format)
            if date_object.year > 15:
                date_object = date_object.replace(year=date_object.year-100)
                print(date_object.isoformat())

        return date_object.isoformat()
