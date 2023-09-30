#!/usr/bin/env python
"""
A script to generate Rosegarden .rgd instrument files pasring the direcory
structure of Yoshimi banks
"""
import os
import argparse
import io
import tempfile
import gzip
import shutil
import xml.etree.ElementTree as ET

XML_HEADER_STRING = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE rosegarden-data>"""
XML_TEMPLATE_STRING = """<rosegarden-data version="4-0.9.1">
    <studio thrufilter="0" recordfilter="0">
    <device id="0" name="Yoshimi" direction="play" variation="LSB" type="midi">
        <librarian name="Lorenzo Sutton" email="lorenzofsutton@gmail.com"/>
        <controls>
            <control name="Pan" type="controller" description="&lt;none&gt;" min="0" max="127" default="64" controllervalue="10" colourindex="2" ipbposition="0"/>
            <control name="Chorus" type="controller" description="&lt;none&gt;" min="0" max="127" default="0" controllervalue="93" colourindex="3" ipbposition="1"/>
            <control name="Volume" type="controller" description="&lt;none&gt;" min="0" max="127" default="100" controllervalue="7" colourindex="1" ipbposition="2"/>
            <control name="Reverb" type="controller" description="&lt;none&gt;" min="0" max="127" default="0" controllervalue="91" colourindex="3" ipbposition="3"/>
            <control name="Sustain" type="controller" description="&lt;none&gt;" min="0" max="127" default="0" controllervalue="64" colourindex="4" ipbposition="-1"/>
            <control name="Expression" type="controller" description="&lt;none&gt;" min="0" max="127" default="100" controllervalue="11" colourindex="2" ipbposition="-1"/>
            <control name="Modulation" type="controller" description="&lt;none&gt;" min="0" max="127" default="0" controllervalue="1" colourindex="4" ipbposition="-1"/>
            <control name="Cutoff Freq" type="controller" description="&lt;none&gt;" min="0" max="127" default="64" controllervalue="74" colourindex="2" ipbposition="2"/>
            <control name="Resonance" type="controller" description="&lt;none&gt;" min="0" max="127" default="64" controllervalue="71" colourindex="2" ipbposition="2"/>
            <control name="Attack time" type="controller" description="&lt;none&gt;" min="0" max="127" default="64" controllervalue="73" colourindex="2" ipbposition="2"/>
            <control name="Release time" type="controller" description="&lt;none&gt;" min="0" max="127" default="64" controllervalue="72" colourindex="2" ipbposition="2"/>
            <control name="PitchBend" type="pitchbend" description="&lt;none&gt;" min="0" max="16383" default="8192" controllervalue="1" colourindex="4" ipbposition="-1"/>
        </controls>
    </device>
    </studio>
</rosegarden-data>
"""

def make_bank_xml_element(bank_dir, bank_num):
    """ takes the root bank dir and the number (as in yoshimi) and creates
    <bank> and all the <program> elements for each bank
    """
    bank_name = os.path.split(bank_dir)[1]
    b_el = ET.fromstring("""<bank name="" percussion="false" msb=""
    lsb="0"/>""")
    b_el.text = "\n            "
    b_el.attrib['name'] = bank_name
    b_el.attrib['msb'] = bank_num

    prog_template = """<program id="" name="" category=""/>"""
    file_list = sorted(os.listdir(bank_dir))
    for f in file_list:
        if f.find('.xiz') < 0:
            continue
        number = str(int(f[0:4]) - 1)
        try:
            name = f[f.index('-') + 1:f.index('.xiz')]
            name = name.replace("_", " ")
        except ValueError:
            # something wrong with the path name?
            continue
        p_el = ET.fromstring(prog_template)
        p_el.attrib['id'] = number
        p_el.attrib['name'] = name
        p_el.attrib['category'] = bank_name
        p_el.tail = "\n            "
        b_el.append(p_el)
    return b_el

if __name__ == "__main__":
    # Parse arguments in partigular root dir for banks and the output rgd file
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("bank_root_dir")
    arg_parser.add_argument("output_rgd_file")
    arg_parser.add_argument('--debug', action='store_true')
    args = arg_parser.parse_args()

    bank_root_dir = args.bank_root_dir
    out_file = args.output_rgd_file

    print(f"Searching for banks in {bank_root_dir}\n")
    # Set-up XML file
    xml_string = io.StringIO(XML_TEMPLATE_STRING)
    tree = ET.parse(xml_string)
    root = tree.getroot()
    device_el = root.findall(".//device")[0]

    bank_list = sorted(os.listdir(bank_root_dir))
    step = 5
    this_num = 0
    print("Generating XML file structure...\n")
    for b in bank_list:
        this_num += step
        new_bank_el = make_bank_xml_element(
            os.path.join(bank_root_dir, b),
            str(this_num)
            )
        new_bank_el.tail = "\n    "
        device_el.append(new_bank_el)

    eltree_string = ET.tostring(root)
    output_string = XML_HEADER_STRING + eltree_string.decode('utf-8')

    temp_dir = tempfile.gettempdir()
    xml_file = os.path.join(temp_dir, "Yoshimi")
    print(f"Saving to {out_file}")
    with open(xml_file, "w") as f:
        f.write(output_string)

    with open(xml_file, 'rb') as f_in, gzip.open(out_file, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    # If degugging also save the XML file
    if args.debug:
        xml_debug_file = 'rgd_yoshimi_banks.xml'
        print(f'Saving debug XML file: {xml_debug_file}')
        shutil.copy(xml_file, os.path.join('.', xml_debug_file))
