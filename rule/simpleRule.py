import cirpy
import os
import tempfile
import subprocess
import ast
from chemdataextractor.text.normalize import chem_normalize



# transform the biblio information
def transform_biblio(biblio):
    new_biblio = {}
    if 'doi' in biblio:
        new_biblio['doi'] = biblio['doi']
    if 'published_date' in biblio:
        new_biblio['published_date'] = biblio['published_date']
    if 'title' in biblio:
        new_biblio['title'] = biblio['title']
    return new_biblio


# find the item that needed to be validated
def validate_record(record, config):
    items = ast.literal_eval(config.get('validate_record', 'items'))
    for item in items:
        if item in record:
            return True
        else:
            return False


# rebuild the structure for the result
def add_structures(result):
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        for record in result['records']:
            for name in record.get('names', []):
                tf.write(('%s\n' % name).encode('utf-8'))

    subprocess.call(
        ['java', '-jar', '/Users/luoyu/PycharmProjects/protoKG/rule/opsin-cli-2.7.0-jar-with-dependencies.jar', '--allowRadicals', '--wildcardRadicals',
         '--allowAcidsWithoutAcid', '--allowUninterpretableStereo', '--detailedFailureAnalysis', tf.name,
         '%s.result' % tf.name])

    with open('%s.result' % tf.name) as res:
        structures = [line.strip() for line in res]
        i = 0
        for record in result['records']:
            for name in record.get('names', []):
                if 'smiles' not in record:
                    if structures[i]:
                        # print(structures[i])
                        # print('Resolved with OPSIN: %s = %s', name, structures[i])
                        record['smiles'] = structures[i]
                    else:
                        smiles = cirpy.resolve(chem_normalize(name.rstrip("\n\r")).encode('utf-8'), 'smiles')
                        # print(smiles)
                        if smiles:
                            record['smiles'] = smiles
                        else:
                            record['smiles_validation_failed'] = "1"
                i += 1
    os.remove(tf.name)
    os.remove('%s.result' % tf.name)
    return result


# delete some unnecessary values, and validate the range of input values
def apply_rules(records, config):
    new_records = []
    # need users to modify this section
    elec_chem_min_range = float(config.get("validation", "elec_chem_min_range"))
    elec_chem_max_range = float(config.get("validation", "elec_chem_max_range"))
    flur_lif_time_min_range = float(config.get("validation", "flur_lif_time_min_range"))
    flur_lif_time_max_range = float(config.get("validation", "flur_lif_time_max_range"))
    qtum_ylds_min_range = float(config.get("validation", "qtum_ylds_min_range"))
    qtum_ylds_max_range = float(config.get("validation", "qtum_ylds_max_range"))
    uv_spec_pks_extn_min_range = float(config.get("validation", "uv_spec_pks_extn_min_range"))
    uv_spec_pks_extn_max_range = float(config.get("validation", "uv_spec_pks_extn_max_range"))
    uv_spec_pks_units = config.get("validation", "uv_spec_pks_units")
    uv_spec_pks_val_min_range = float(config.get("validation", "uv_spec_pks_val_min_range"))
    uv_spec_pks_val_max_range = float(config.get("validation", "uv_spec_pks_val_max_range"))
    em_spec_pks_val_min_range = float(config.get("validation", "em_spec_pks_val_min_range"))
    em_spec_pks_val_max_range = float(config.get("validation", "em_spec_pks_val_max_range"))

    for record in records:
        delete_record = ast.literal_eval(config.get('delete_record', 'items'))
        if validate_record(record, config):
            for item in delete_record:
                if item in record:
                    del record[item]

            if 'electrochemical_potentials' in record:
                for es in record['electrochemical_potentials']:
                    if 'value' in es:
                        if not elec_chem_min_range <= float(
                                es['value'].replace("–", '-').replace(',', '')) <= elec_chem_max_range:
                            es['value_validation_failed'] = "1"
            if 'fluorescence_lifetimes' in record:
                for fl in record['fluorescence_lifetimes']:
                    if 'value' in fl:
                        if not flur_lif_time_min_range <= float(
                                fl['value'].replace("–", '-').replace(',', '')) <= flur_lif_time_max_range:
                            fl['value_validation_failed'] = "1"

            if 'quantum_yields' in record:
                for qy in record['quantum_yields']:
                    if 'value' in qy:
                        if not qtum_ylds_min_range <= float(
                                qy['value'].replace("–", '-').replace(',', '').replace('10-3', '0.001').replace('<',
                                                                                                                '')) <= qtum_ylds_max_range:
                            qy['value_validation_failed'] = "1"
            if 'uvvis_spectra' in record:
                for uvs in record['uvvis_spectra']:
                    for peaks in uvs['peaks']:
                        if 'extinction' in peaks:
                            if not uv_spec_pks_extn_min_range <= float(
                                    peaks['extinction'].replace("–", '-').replace(',',
                                                                                  '')) <= uv_spec_pks_extn_max_range:
                                peaks['extinction_validation_failed'] = "1"
                        if 'units' in peaks:
                            if not peaks['units'] == uv_spec_pks_units:
                                peaks['units_validation_failed'] = "1"
                        if 'value' in peaks:
                            if not uv_spec_pks_val_min_range <= float(
                                    peaks['value'].replace("–", '-').replace(',', '')) <= uv_spec_pks_val_max_range:
                                peaks['value_validation_failed'] = "1"
            if 'emisn_spectra' in record:
                for ems in record['emisn_spectra']:
                    for peaks in ems['peaks']:
                        if 'value' in peaks:
                            if not em_spec_pks_val_min_range <= float(
                                    peaks['value'].replace("–", '-').replace(',', '')) <= em_spec_pks_val_max_range:
                                peaks['value_validation_failed'] = "1"


            new_records.append(record)
    return new_records
