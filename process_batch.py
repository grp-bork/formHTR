import argparse
import os
import shutil
import time

from process_logsheet import main as process_logsheet


SYNONYMS = {'202303_LSI4_SoilSampleDescriptionForm': '202305_LSI4_SoilSampleDescriptionForm',
            '202303_LSI1_SiteDescriptionForm': '202305_LSI1_SiteDescriptionForm',
            '202303_LSI3_SoilTransectDescriptionForm': '202305_LSI3_SoilTransectDescriptionForm',
            '202303_LSI7_SedimentTransectDistributionForm': '202305_LSI7_SedimentTransectDistributionForm', 
            '202303_LSI8_SedimentSampleDistributionForm': '202305_LSI8_SedimentSampleDistributionForm',
            '202303_LSI10_AerosolsSampleDistributionForm': '202305_LSI10_AerosolsSampleDistributionForm'}


def create_output_dir(location):
    os.makedirs(location)


def process_batch(logsheet_folder, template_folder, config_folder, output_location, google_credentials, amazon_credentials, azure_credentials):
    logsheets = os.listdir(logsheet_folder)
    templates = os.listdir(template_folder)
    configs = os.listdir(config_folder)

    for logsheet in logsheets:
        # TODO more complicated
        parts = logsheet.split("_")
        name = "_".join(parts[1:-1])

        number = parts[-1].split(".")[0]
        if not number[0].isdigit() or not number[-1].isdigit():
            name += f'_{number}'
            number = None

        template = f'{name}.pdf'
        if name in SYNONYMS:
            template = f'{SYNONYMS[name]}.pdf'
        config = f'{name}.json'

        # find template and config
        if template not in templates or config not in configs:
            print(f'Template or config {name} is unknown!')
        else:
            print(f'Processing {name} {number if number else ""}')
            # prepare output location
            if number:
                location = f'{output_location}/{name}_{number}'
            else:
                location = f'{output_location}/{name}'
            if not os.path.exists(location):
                create_output_dir(location)
                # store logsheet in output location
                shutil.copy(f'{logsheet_folder}/{logsheet}', f'{location}/logsheet.pdf')

                stats = process_logsheet(f'{logsheet_folder}/{logsheet}', f'{template_folder}/{template}', f'{config_folder}/{config}', f'{location}/metadata.xlsx', 
                                         google_credentials, amazon_credentials, azure_credentials, 
                                         True, True, f'{template_folder}/202303_backside.pdf', f'{config_folder}/202303_backside.json')
                print(stats)
                time.sleep(20)
            else:
                print(f'Skipping existing location: {location}')


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Process logsheets given in a folder.')

    args_parser._action_groups.pop()
    required = args_parser.add_argument_group('required arguments')

    required.add_argument('--folder', type=str, required=True, help='Folder containing loghseets')
    required.add_argument('--templates', type=str, required=True, help='Folder containing templates')
    required.add_argument('--configs', type=str, required=True, help='Folder containing configs')
    required.add_argument('--output_location', type=str, required=True, help='Output location')

    required.add_argument('--google', type=str, required=True, help='Path to Google vision credentials')
    required.add_argument('--amazon', type=str, required=True, help='Path to Amazon vision credentials')
    required.add_argument('--azure', type=str, required=True, help='Path to Azure vision credentials')

    args = args_parser.parse_args()

    process_batch(args.folder, args.templates, args.configs, args.output_location,
                  args.google, args.amazon, args.azure)
