#sample data:
'''
{"filename":"comprehend_training_examples.txt","classes":["EMAIL","NAME","PASSWORD","ADDRESS"],"annotations":[null,null,null,null,null,null,null,null,["(1, 'Daniela Cavaglieri Vidotti.', '17590755826', '', 'Rua Palmeira Imperial', '11', 'Jardim Conceição', 'Hortolândia', '19978200746', '1978200746', '1978200746', '', '', '', 'agendado_web', '', 25, 'Radio 5MB', '', '', 'flavioalmeida1985@gmail.com', '', '', '13185745', NULL),",{"entities":[[8,4,32,"NAME"],[8,54,117,"ADDRESS"],[8,220,248,"EMAIL"]]}],["(2, 'Flavio Alouysio de Almeida.', '33094755810', '', 'Rua Dois', '11', 'Jardim Francisca', 'Campinas', '19987411001', '', '', '', '', '', 'agendado_web', '', 25, 'Fibra 10MB', '', '', 'flavioalmeida1985@gmail.com', '', '54564564654654', '13067812', NULL),",{"entities":[[9,4,32,"NAME"],[9,54,101,"ADDRESS"],[9,185,213,"EMAIL"]]}]]}
'''

import json
import argparse
import os
import datetime
import boto3


def upload_files_to_repo(filename, repo_name):
    print(f'uploading {filename}')

    #accesses boto3 tools
    session = boto3.Session()
    #specifies tools for s3
    repo_s3_client = session.resource('s3')

    #initializes variable with naming convention
    destination_string = repo_name + '/' + filename


    try:
        repo_s3_client.meta.client.upload_file(filename, 'enzoic-comprehend-dev', destination_string)
    except:
        print("failed to upload")
    print("uploaded")
    return True

#removes file extension 
def remove_file_extension(input_string):
    return os.path.splitext(input_string)[0]

# read in a command line arguments for the file to be processed (the json annotations file) and the
# corresponding raw data file (the file that was used to create the annotations file) - the name will be used to
# create the first column in the output csv file
parser = argparse.ArgumentParser()
parser.add_argument("--input_file_name", type=str, help="the name of the file to be read")
parser.add_argument("--data_file_name", type=str, help="the name of the file containing the raw training data")
args = parser.parse_args()
file = args.input_file_name
data_file = args.data_file_name


#open the file and read in the json
with open(file, 'r') as f:
    data = json.load(f)

#construct list for new output format
output_list = []
headers = "File, Line, Begin Offset, End Offset, Type"
output_list.append(headers)

#loop through the data dict and extract each element in the 'entities' list and append to output_list as a new line
for each in data['annotations']:
    if each is not None:
        for item in each[1]['entities']:
            data_string = data_file + ", " + str(item[0]) + ", " + str(item[1]) + ", " + str(item[2]) + ", " + str(item[3])
            output_list.append(data_string)

#removes file extension 
def remove_file_extension(input_string):
    return os.path.splitext(input_string)[0]

#gathers datetime
today = str(datetime.date.today())

#creates 
output_datafile_string = ("enzoic-training-" + remove_file_extension(data_file) + "_" + today +  ".csv")



with open(output_datafile_string , "a" ) as my_file:
    for line in output_list:
        if '\n' not in line:
            my_file.write(line + '\n')
        else:
            my_file.write(line)
    my_file.close()

#print(data_file,'\n',output_datafile_string)

upload_files_to_repo(data_file,'training')

upload_files_to_repo(output_datafile_string,'annotations')
#TODO: add automatic file uploading to s3 once buckets are created
