import os

source_file_path = "/Users/higgi135/Projects/vvlbext/vvl_ryan-reconfig-titles.csv"
problem_records = ["14036", "14041", "14042", "14055", "14061", "14073"]

class VvlBext():

    def __init__(self):
        self.record_id = 0
        self.output_csv_data = []


    def process_csv(self, source_file_path, output_file_path):

        with open(source_file_path, "r") as source:

            for line in source:

                if self.new_record(line):
                    print line
                    
                    if self.record_id <> 0:
                        self.create_csv_line()
                    
                    self.format_types = []
                    self.csv_data = {
                                     "digital_wav_id":"",
                                     "digital_mp3_id":"",
                                     "analogue_id":"",
                                     "digital_wav_path": "",
                                     "digital_mp3_path": "",
                                     "source_recording_specs": "",
                    }              
                    self.get_default_fields(line)
                    self.get_addl_fields()
                
                else:

                    self.get_default_fields(line)
                    self.get_addl_fields()

            print self.record_id

        with open(output_file_path, "w") as output:

            output.write("record_id,vvl_number,source_format_id,wav_id,mp3_id,mp3_path,FileName,Description,Originator,OriginationDate,CodingHistory,AllFormats\n")
            for line in self.output_csv_data:
                output.write(line+"\n")



    def get_default_fields(self, line):

        row_items = line.split(",")
        self.record_id = row_items[0].rstrip().replace('"', '').replace("'", "").lstrip()
        self.vvl_number = row_items[1].replace('"', '').replace("'", "").rstrip().lstrip()
        self.format_id = row_items[2].replace('"', '').replace("'", "").rstrip().lstrip()
        self.location_name = row_items[3].replace('"', '').replace("'", "").rstrip().lstrip()
        self.format_type = row_items[4].replace('"', '').replace("'", "").rstrip().lstrip()
        self.format_types.append(self.format_type)

    def get_addl_fields(self):

        if self.format_id.startswith("DB") and self.format_type == "wav":
            self.csv_data["digital_wav_path"] = os.path.join(self.location_name.replace("DarkArchive", "archives"), self.format_id + ".wav")
            self.csv_data["digital_wav_id"] = self.format_id

        elif self.format_type == "mp3":
            self.csv_data["digital_mp3_path"] = os.path.join(self.location_name, self.format_id + ".mp3")
            self.csv_data["digital_mp3_id"] = self.format_id

        elif not self.format_id.startswith("DB"):
            self.csv_data["source_recording_specs"] = self.format_type
            self.csv_data["analogue_id"] = self.format_id

    def new_record(self, line):
        
        if line.split(",")[0].rstrip().replace('"', '').replace("'", "").lstrip() == self.record_id:

            return False

        else:

            return True

    def create_csv_line(self):

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



    def make_description(self):

        description = ""

        if self.csv_data["analogue_id"] <> "":
            description += "File Content: Collection VVL Item {0}. ".format(self.csv_data["analogue_id"])

        description += "File use: Preservation master. "

        if self.vvl_number <> "":
            description += "Title control number: {0}. ".format(self.vvl_number)

        if self.csv_data["digital_wav_id"] <> "":
            description += "Original filename: {0}.".format(self.csv_data["digital_wav_id"] + ".wav")

        return description






